"""AI 客户端：豆包 Seedream 图生图，prompt 直接来自方案「效果描述」。"""

import base64
import logging
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from app.config import (
    ALLOW_LOCAL_FALLBACK,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    DOUBAO_API_KEY,
    DOUBAO_BASE_URL,
    DOUBAO_IMAGE_MODEL,
    DOUBAO_IMAGE_SIZE,
    IMAGE_GEN_PROVIDER,
    LEVEL_LABELS,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
)
from app.scheme_parser import buildImagePromptFromScheme
from app.image_utils import prepareImageForDoubao

logger = logging.getLogger(__name__)


class DoubaoModelNotActivatedError(RuntimeError):
    """豆包 Seedream 模型未在控制台开通。"""

    pass


class AiClient:
    """统一 AI 调用客户端。"""

    def __init__(self) -> None:
        """初始化客户端。"""
        self.doubaoKey = DOUBAO_API_KEY
        self.doubaoBase = DOUBAO_BASE_URL
        self.doubaoModel = DOUBAO_IMAGE_MODEL
        self.doubaoSize = DOUBAO_IMAGE_SIZE
        self.deepseekKey = DEEPSEEK_API_KEY
        self.deepseekBase = DEEPSEEK_BASE_URL
        self.deepseekModel = DEEPSEEK_MODEL
        self.imageProvider = IMAGE_GEN_PROVIDER
        self.openaiKey = OPENAI_API_KEY
        self.openaiBase = OPENAI_BASE_URL.rstrip("/")
        self.allowLocalFallback = ALLOW_LOCAL_FALLBACK

    @property
    def isConfigured(self) -> bool:
        """是否已配置豆包 API Key。"""
        return bool(self.doubaoKey)

    def _encodeImageBase64(self, imagePath: Path) -> str:
        """将上传图片编码为 base64 data URL。"""
        suffix = imagePath.suffix.lower().lstrip(".")
        mime = "jpeg" if suffix in ("jpg", "jpeg") else suffix or "png"
        with open(imagePath, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:image/{mime};base64,{b64}"

    async def _downloadBytes(self, url: str) -> bytes:
        """下载豆包返回的图片 URL。"""
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content

    def buildTransformPrompt(self, schemeMarkdown: str, level: str) -> str:
        """用方案「效果描述」构建生图 prompt。"""
        levelLabel = LEVEL_LABELS.get(level, level)
        return buildImagePromptFromScheme(schemeMarkdown, level, levelLabel)

    def _parseDoubaoError(self, statusCode: int, body: str) -> str:
        """解析豆包 API 错误信息。"""
        if "ModelNotOpen" in body or "not activated the model" in body:
            return (
                f"豆包生图模型「{self.doubaoModel}」未开通。"
                "请登录火山方舟控制台 → 模型推理 → 开通 Seedream 4.0/4.5 图片生成模型。"
            )
        if "expected the pixel to be at most" in body:
            return "上传的照片像素过高（豆包上限约 6000×6000），请换一张较小的照片，或重新上传让系统自动压缩。"
        if "InvalidParameter" in body:
            return f"豆包参数错误: {body[:150]}"
        if statusCode == 401:
            return "豆包 API Key 无效，请检查 server/.env 中的 DOUBAO_API_KEY"
        return f"豆包生图失败 ({statusCode}): {body[:200]}"

    async def checkDoubaoImageModel(self) -> tuple[bool, str]:
        """检查豆包生图模型是否可用（发送最小图生图请求）。"""
        if not self.doubaoKey:
            return False, "未配置 DOUBAO_API_KEY"

        # 1x1 白色 JPEG 最小参考图
        tinyB64 = (
            "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof"
            "Hh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwh"
            "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAAR"
            "CAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAA"
            "AAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oA"
            "DAMBAAIRAxEAPwCwAA//2Q=="
        )
        url = f"{self.doubaoBase}/images/generations"
        headers = {"Authorization": f"Bearer {self.doubaoKey}", "Content-Type": "application/json"}
        payload = {
            "model": self.doubaoModel,
            "prompt": "测试连通性",
            "image": f"data:image/jpeg;base64,{tinyB64}",
            "size": self.doubaoSize,
            "sequential_image_generation": "disabled",
            "response_format": "url",
            "watermark": False,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                return True, "生图模型可用"
            msg = self._parseDoubaoError(resp.status_code, resp.text)
            if "ModelNotOpen" in resp.text or "not activated" in resp.text:
                return False, msg
            # 其他错误（如图片过小）说明模型已开通
            if resp.status_code in (400, 422):
                return True, "生图模型已开通"
            return False, msg

    async def generateImageDoubao(self, prompt: str, sourcePath: Path) -> bytes:
        """调用豆包 Seedream 图生图：参考图 + 效果描述 prompt。"""
        if not self.doubaoKey:
            raise RuntimeError("豆包 API Key 未配置，请在 server/.env 填写 DOUBAO_API_KEY")

        # 发送前再次压缩，防止热重载期间漏掉预处理
        safePath = prepareImageForDoubao(sourcePath)
        with Image.open(safePath) as img:
            logger.info("豆包参考图尺寸: %dx%d (%s)", img.width, img.height, safePath.name)

        url = f"{self.doubaoBase}/images/generations"
        dataUrl = self._encodeImageBase64(safePath)
        payload = {
            "model": self.doubaoModel,
            "prompt": prompt[:800],
            "image": dataUrl,
            "size": self.doubaoSize,
            "sequential_image_generation": "disabled",
            "response_format": "url",
            "watermark": False,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.doubaoKey}",
            "Content-Type": "application/json",
        }

        logger.info("豆包图生图 | model=%s | prompt=%s", self.doubaoModel, prompt)

        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                errMsg = self._parseDoubaoError(resp.status_code, resp.text)
                logger.error("豆包生图失败: %s", errMsg)
                if "未开通" in errMsg:
                    raise DoubaoModelNotActivatedError(errMsg)
                raise RuntimeError(errMsg)

            data = resp.json()
            if "error" in data:
                raise RuntimeError(data["error"].get("message", "豆包生图失败"))

            item = data["data"][0]
            if item.get("b64_json"):
                return base64.b64decode(item["b64_json"])
            if item.get("url"):
                imageBytes = await self._downloadBytes(item["url"])
                if len(imageBytes) < 5000:
                    raise RuntimeError("豆包返回的图片过小，可能生成失败")
                return imageBytes
            raise RuntimeError("豆包 API 未返回图片数据")

    async def _deepseekChat(self, messages: list[dict[str, Any]], max_tokens: int = 4096) -> str:
        """DeepSeek Chat（管理后台用）。"""
        if not self.deepseekKey:
            raise RuntimeError("DeepSeek API Key 未配置")
        url = f"{self.deepseekBase}/chat/completions"
        payload = {"model": self.deepseekModel, "messages": messages, "max_tokens": max_tokens}
        headers = {"Authorization": f"Bearer {self.deepseekKey}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def chatCompletion(
        self,
        messages: list[dict[str, Any]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 4096,
    ) -> str:
        """Chat 入口。"""
        if self.deepseekKey:
            return await self._deepseekChat(messages, max_tokens)
        if not self.openaiKey:
            raise RuntimeError("未配置 Chat API Key")
        url = f"{self.openaiBase}/chat/completions"
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
        headers = {"Authorization": f"Bearer {self.openaiKey}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def generateSchemeMarkdown(self, level: str, levelLabel: str) -> str:
        """AI 生成方案 Markdown。"""
        return await self.chatCompletion(
            messages=[
                {
                    "role": "system",
                    "content": "你是萝莉dao方案设计师，这是一款男生变可爱萝莉的整蛊工具。"
                    "输出 Markdown，必须包含 ## 效果描述（列表项）。"
                    "强调：保留参考图男生面部可识别，风格偏可爱、偏萝莉、kawaii；"
                    "粉色系、蝴蝶结、蕾丝洛丽塔、双马尾等萝莉元素，真人写真质感。"
                },
                {"role": "user", "content": f"为【{level}-{levelLabel}】生成安装方案。"},
            ]
        )

    async def generatePromptTemplate(self, level: str, levelLabel: str) -> str:
        """生成 prompt 模板占位。"""
        return f"{levelLabel}：见方案效果描述"

    async def transformImage(
        self,
        sourcePath: Path,
        level: str,
        schemeMarkdown: str,
        outputPath: Path,
    ) -> Path:
        """图生图：上传人物 + 效果描述 → 豆包 API，返回全新生成图。"""
        prompt = self.buildTransformPrompt(schemeMarkdown, level)

        if not self.doubaoKey:
            raise RuntimeError("请先在 server/.env 配置 DOUBAO_API_KEY")

        imageBytes = await self.generateImageDoubao(prompt, sourcePath)
        outputPath.write_bytes(imageBytes)
        return outputPath

    def applyLocalEffect(self, sourcePath: Path, level: str) -> bytes:
        """本地降级特效（仅开发调试用，效果有限）。"""
        intensity = {"L1": 0.2, "L2": 0.4, "L3": 0.6, "L4": 0.8, "L5": 1.0}.get(level, 0.5)
        img = Image.open(sourcePath).convert("RGBA")
        width, height = img.size
        expandRatio = 1.0 + intensity * 0.3
        newW = int(width * expandRatio)
        newH = int(height * expandRatio)
        canvas = Image.new("RGBA", (newW, newH), (255, 182, 193, 255))
        canvas.paste(img, ((newW - width) // 2, (newH - height) // 2))
        rgb = canvas.convert("RGB")
        rgb = ImageEnhance.Color(rgb).enhance(1.0 + intensity * 0.5)
        result = rgb.convert("RGBA")
        draw = ImageDraw.Draw(result)
        try:
            font = ImageFont.truetype("arial.ttf", max(20, int(newW * 0.04)))
        except OSError:
            font = ImageFont.load_default()
        draw.text((20, 20), f"萝莉dao {level} [本地降级]", fill=(255, 105, 180, 230), font=font)
        buf = BytesIO()
        result.save(buf, format="PNG")
        return buf.getvalue()


aiClient = AiClient()
