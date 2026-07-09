"""从方案 Markdown 中提取生图所需文本。"""

import re


def _normalizeLine(line: str) -> str:
    """清理 Markdown 列表行中的格式符号。"""
    text = line.strip()
    if text.startswith("- "):
        text = text[2:].strip()
    # 去掉 **粗体** 标记，保留文字
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text.strip()


def extractSectionLines(markdown: str, sectionTitle: str) -> list[str]:
    """提取 Markdown 中指定二级标题下的所有有效行。"""
    lines = markdown.split("\n")
    inSection = False
    items: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if inSection:
                break
            heading = stripped[3:].strip()
            if heading == sectionTitle or heading.startswith(sectionTitle):
                inSection = True
            continue
        if not inSection or not stripped:
            continue
        if stripped.startswith("- "):
            items.append(_normalizeLine(stripped))
        elif not stripped.startswith("#") and not stripped.startswith(">"):
            # 段落文本也纳入
            items.append(_normalizeLine(stripped))

    return [i for i in items if i]


def extractEffectDescription(markdown: str) -> str:
    """仅提取「效果描述」段落内容作为生图提示词核心。"""
    items = extractSectionLines(markdown, "效果描述")
    if items:
        return "，".join(items)
    return ""


def extractExpandDescription(markdown: str) -> str:
    """提取「扩图说明」中与画面相关的描述（排除 SD/LoRA 技术参数）。"""
    items = extractSectionLines(markdown, "扩图说明")
    # 过滤掉明显的 Stable Diffusion / LoRA 技术行
    skipKeywords = (
        "lora", "vae", "cfg", "webui", "controlnet", "esrgan", "safetensors",
        "anything-v5", "novelai", "采样", "推荐底模", "推荐VAE", "负面提示",
        "正向提示", "权重", "分辨率", "放大", "安装", "文件夹", "HuggingFace",
    )
    visualItems: list[str] = []
    for item in items:
        lower = item.lower()
        if any(kw in lower or kw in item for kw in skipKeywords):
            continue
        if len(item) > 120:
            continue
        visualItems.append(item)
    return "，".join(visualItems[:3])


def buildImagePromptFromScheme(markdown: str, level: str, levelLabel: str) -> str:
    """用「效果描述」作为豆包图生图 prompt（效果描述即提示词）。"""
    effectDesc = extractEffectDescription(markdown)
    if not effectDesc:
        raise ValueError("方案中未找到「## 效果描述」段落，请在管理后台补充")

    return (
        f"基于参考图中的男生照片进行图生图，将其变身为可爱萝莉女生，{level}（{levelLabel}）等级。"
        f"效果描述：{effectDesc}。"
        f"核心要求：严格保留参考图人物面部身份（眉眼、鼻型、唇形、脸型可辨认，禁止换脸）；"
        f"整体风格必须偏可爱、偏萝莉、偏 kawaii（软萌、幼态、粉色系、蝴蝶结蕾丝洛丽塔元素，等级越高萝莉感越强）；"
        f"同时呈现明显女生特征（萝莉妆、可爱发型、萝莉女装、女性体态）；"
        f"真人写实摄影质感（真实人像，非平涂二次元插画），高质量可爱萝莉人像成片，不要只做简单滤镜。"
    )
