"""图片生成 API。"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from app.image_utils import prepareImageForDoubao
from app.ai_client import DoubaoModelNotActivatedError, aiClient
from app.config import ALLOW_LOCAL_FALLBACK, GENERATED_DIR, LEVELS, UPLOAD_DIR
from app.database import getDb
from app.models import LevelStat, Scheme
from app.schemas import GenerateOut

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def _normalizeImage(sourcePath: Path) -> Path:
    """校验并压缩图片，满足豆包 API 尺寸限制。"""
    try:
        return prepareImageForDoubao(sourcePath)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图片处理失败: {e}") from e


@router.post("/generate", response_model=GenerateOut)
async def generateImage(
    level: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(getDb),
):
    """上传图片并生成萝莉特效图（豆包图生图，prompt 来自方案效果描述）。"""
    if level not in LEVELS:
        raise HTTPException(status_code=400, detail=f"无效等级: {level}")

    if not image.filename and not image.content_type:
        raise HTTPException(status_code=400, detail="请上传图片文件")

    scheme = db.query(Scheme).filter(Scheme.level == level).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="方案未找到")

    if not scheme.markdown or "## 效果描述" not in scheme.markdown:
        raise HTTPException(status_code=400, detail="该等级方案缺少「效果描述」，请在管理后台编辑")

    suffix = Path(image.filename or "photo.jpg").suffix.lower()
    if suffix and suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"不支持的格式 {suffix}，请用 JPG/PNG/WebP")

    fileId = uuid.uuid4().hex
    uploadPath = UPLOAD_DIR / f"{fileId}{suffix or '.jpg'}"
    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="图片文件为空")

    uploadPath.write_bytes(content)
    uploadPath = _normalizeImage(uploadPath)
    with Image.open(uploadPath) as normalizedImg:
        logger.info(
            "上传图片已预处理: %dx%d -> %s",
            *normalizedImg.size,
            uploadPath.name,
        )
    outputPath = GENERATED_DIR / f"{fileId}_{level}.png"

    usedFallback = False

    try:
        if aiClient.isConfigured:
            try:
                await aiClient.transformImage(
                    sourcePath=uploadPath,
                    level=level,
                    schemeMarkdown=scheme.markdown,
                    outputPath=outputPath,
                )
            except DoubaoModelNotActivatedError as e:
                raise HTTPException(status_code=503, detail=str(e)) from e
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            except Exception as aiErr:
                if ALLOW_LOCAL_FALLBACK:
                    logger.warning("豆包生图失败，启用本地降级: %s", aiErr)
                    imageBytes = aiClient.applyLocalEffect(uploadPath, level)
                    outputPath.write_bytes(imageBytes)
                    usedFallback = True
                else:
                    logger.error("豆包生图失败: %s", aiErr)
                    raise HTTPException(
                        status_code=502,
                        detail=str(aiErr),
                    ) from aiErr
        elif ALLOW_LOCAL_FALLBACK:
            imageBytes = aiClient.applyLocalEffect(uploadPath, level)
            outputPath.write_bytes(imageBytes)
            usedFallback = True
        else:
            raise HTTPException(
                status_code=503,
                detail="未配置豆包 API Key。请在 server/.env 填写 DOUBAO_API_KEY 并开通 Seedream 生图模型。",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("图片生成异常")
        raise HTTPException(status_code=500, detail=f"生成失败: {e}") from e

    if not outputPath.exists() or outputPath.stat().st_size == 0:
        raise HTTPException(status_code=500, detail="生成结果为空，请重试")

    stat = db.query(LevelStat).filter(LevelStat.level == level).first()
    if stat:
        stat.generate_count += 1
    db.commit()

    message = f"{level} 变身完成！今天的兄弟还会是兄弟吗？嘿嘿~"
    if usedFallback:
        message = f"{level} 使用了本地降级特效（非 AI 生图）。请开通豆包 Seedream 模型以获得真实效果。"

    return GenerateOut(
        success=True,
        image_url=f"/static/generated/{outputPath.name}",
        image_path=str(outputPath),
        message=message,
    )
