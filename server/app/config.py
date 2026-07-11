"""应用配置模块，读取环境变量与 Claude settings.json。"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# Claude settings 路径
CLAUDE_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"


def _loadClaudeEnv() -> dict[str, str]:
    """从 Claude settings.json 读取 env 字段。"""
    if not CLAUDE_SETTINGS_PATH.exists():
        return {}
    try:
        with open(CLAUDE_SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        env = data.get("env", {})
        return {k: str(v) for k, v in env.items()}
    except (json.JSONDecodeError, OSError):
        return {}


_claudeEnv = _loadClaudeEnv()

# 豆包 / 火山方舟生图配置（推荐）
DOUBAO_API_KEY: str = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_BASE_URL: str = os.getenv(
    "DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"
).rstrip("/")
DOUBAO_IMAGE_MODEL: str = os.getenv("DOUBAO_IMAGE_MODEL", "doubao-seedream-4-0-250828")
DOUBAO_IMAGE_SIZE: str = os.getenv("DOUBAO_IMAGE_SIZE", "2K")

# 生图 provider: doubao / openai
IMAGE_GEN_PROVIDER: str = os.getenv("IMAGE_GEN_PROVIDER", "doubao")

# 豆包失败时是否允许本地粉色滤镜降级（默认关闭，避免用户误以为 AI 已生效）
ALLOW_LOCAL_FALLBACK: bool = os.getenv("ALLOW_LOCAL_FALLBACK", "false").lower() in ("1", "true", "yes")

# DeepSeek（可选，用于优化 prompt）
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

# 兼容 OpenAI 格式配置
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY") or _claudeEnv.get("ANTHROPIC_AUTH_TOKEN", "")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL") or _claudeEnv.get("ANTHROPIC_BASE_URL", "https://api.openai.com/v1")

# 服务配置
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lolida.db")
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "lolida666")
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8765"))

# 静态文件目录（Vercel 等 serverless 环境 /var/task 只读，改用 /tmp）
def _resolveStaticDir() -> Path:
    """解析可写的静态文件根目录。"""
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return Path("/tmp/lolida-static")
    return Path(__file__).parent.parent / "static"


def _ensureDir(path: Path) -> None:
    """创建目录，serverless 只读文件系统时忽略失败。"""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass


STATIC_DIR = _resolveStaticDir()
UPLOAD_DIR = STATIC_DIR / "uploads"
GENERATED_DIR = STATIC_DIR / "generated"

_ensureDir(UPLOAD_DIR)
_ensureDir(GENERATED_DIR)

# 萝莉等级定义
LEVELS = ["L1", "L2", "L3", "L4", "L5"]

LEVEL_LABELS: dict[str, str] = {
    "L1": "萌新萝莉",
    "L2": "可爱加倍",
    "L3": "萌系觉醒",
    "L4": "魅力全开",
    "L5": "终极变身",
}

# 软件信息默认值
SOFTWARE_INFO = {
    "name": "萝莉dao",
    "slogan": "今天的兄弟还会是兄弟吗？嘿嘿~",
    "version": "1.0.0",
    "description": "帮爱玩游戏的同学与朋友增进友谊的整蛊神器！上传兄弟照片，一键变身萝莉，友谊的小船说翻就翻~",
}
