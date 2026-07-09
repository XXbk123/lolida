"""从 Claude settings.json 同步 AI 配置到 .env 文件。"""

import json
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
ENV_PATH = Path(__file__).parent / ".env"


def syncEnvFromClaude() -> None:
    """读取 Claude settings 并写入 .env。"""
    envLines: list[str] = []
    existing: dict[str, str] = {}

    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key, _, val = line.partition("=")
                existing[key.strip()] = val.strip()

    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        claudeEnv = data.get("env", {})
        if claudeEnv.get("ANTHROPIC_AUTH_TOKEN"):
            existing["OPENAI_API_KEY"] = claudeEnv["ANTHROPIC_AUTH_TOKEN"]
        if claudeEnv.get("ANTHROPIC_BASE_URL"):
            existing["OPENAI_BASE_URL"] = claudeEnv["ANTHROPIC_BASE_URL"]

    defaults = {
        "HOST": "0.0.0.0",
        "PORT": "8765",
        "ADMIN_PASSWORD": "lolida666",
        "DATABASE_URL": "sqlite:///./lolida.db",
    }
    for k, v in defaults.items():
        existing.setdefault(k, v)

    envLines.append("# AI API 配置")
    envLines.append(f"OPENAI_API_KEY={existing.get('OPENAI_API_KEY', '')}")
    envLines.append(f"OPENAI_BASE_URL={existing.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')}")
    envLines.append("")
    envLines.append("# 服务配置")
    for k in ["HOST", "PORT", "ADMIN_PASSWORD", "DATABASE_URL"]:
        envLines.append(f"{k}={existing[k]}")

    ENV_PATH.write_text("\n".join(envLines) + "\n", encoding="utf-8")
    print(f"已同步配置到 {ENV_PATH}")


if __name__ == "__main__":
    syncEnvFromClaude()
