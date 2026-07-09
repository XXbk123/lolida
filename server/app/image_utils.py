"""图片预处理，满足豆包 Seedream 图生图限制。"""

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

# 豆包限制：总像素 ≤ 3600万（约 6000×6000），单边 ≤ 6000，宽高比 [1/3, 3]
MAX_PIXELS = 36_000_000
MAX_SIDE = 6000
MIN_RATIO = 1 / 3
MAX_RATIO = 3
MAX_FILE_BYTES = 10 * 1024 * 1024


def _clampAspectRatio(width: int, height: int) -> tuple[int, int]:
    """将宽高比限制在 [1/3, 3] 范围内。"""
    ratio = width / height
    if ratio > MAX_RATIO:
        width = int(height * MAX_RATIO)
    elif ratio < MIN_RATIO:
        height = int(width / MIN_RATIO)
    return max(width, 1), max(height, 1)


def _fitPixelLimit(width: int, height: int) -> tuple[int, int]:
    """将图片尺寸限制在像素上限内。"""
    width, height = _clampAspectRatio(width, height)
    if width > MAX_SIDE:
        height = int(height * MAX_SIDE / width)
        width = MAX_SIDE
    if height > MAX_SIDE:
        width = int(width * MAX_SIDE / height)
        height = MAX_SIDE
    while width * height > MAX_PIXELS:
        width = int(width * 0.9)
        height = int(height * 0.9)
    return max(width, 1), max(height, 1)


def _saveAsJpeg(rgb: Image.Image, targetPath: Path) -> None:
    """将 RGB 图保存为符合大小限制的 JPEG。"""
    width, height = rgb.size
    quality = 92
    while quality >= 55:
        buf = BytesIO()
        rgb.save(buf, format="JPEG", quality=quality, optimize=True)
        if buf.tell() <= MAX_FILE_BYTES:
            targetPath.write_bytes(buf.getvalue())
            return
        quality -= 7

    # 仍超限则继续缩小尺寸
    smaller = rgb.resize((max(width // 2, 1), max(height // 2, 1)), Image.Resampling.LANCZOS)
    buf = BytesIO()
    smaller.save(buf, format="JPEG", quality=85, optimize=True)
    targetPath.write_bytes(buf.getvalue())


def prepareImageForDoubao(sourcePath: Path) -> Path:
    """校验、旋转 EXIF、缩放并标准化图片，输出 JPEG 供豆包 API 使用。"""
    try:
        with Image.open(sourcePath) as img:
            img.verify()
        with Image.open(sourcePath) as img:
            # 先按 EXIF 旋转，避免「显示尺寸」与「实际像素」不一致
            rgb = ImageOps.exif_transpose(img).convert("RGB")
            origW, origH = rgb.size
            newW, newH = _fitPixelLimit(origW, origH)

            if (newW, newH) != (origW, origH):
                rgb = rgb.resize((newW, newH), Image.Resampling.LANCZOS)

            normalized = sourcePath.with_suffix(".jpg")
            _saveAsJpeg(rgb, normalized)

            if normalized != sourcePath and sourcePath.exists():
                sourcePath.unlink(missing_ok=True)
            return normalized
    except UnidentifiedImageError as e:
        raise ValueError("无法识别图片格式，请上传 JPG/PNG/WebP") from e
