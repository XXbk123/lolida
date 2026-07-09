# 萝莉dao

> 今天的兄弟还会是兄弟吗？嘿嘿~

帮爱玩游戏的同学与朋友增进友谊的整蛊神器：上传兄弟照片，选择萝莉等级 L1–L5，一键 AI 变身生成可爱萝莉风格图片。

[![License: MIT](https://img.shields.io/badge/License-MIT-pink.svg)](LICENSE)

## 功能

- **桌面 Web 端**：上传照片、选择等级、一键变身、重新生成、下载、反馈
- **管理后台**：编辑 L1–L5 方案「效果描述」（即 AI 生图提示词）、查看用户反馈
- **豆包 Seedream 图生图**：保留原脸 + 男生变萝莉 + 真人可爱风格

## 项目结构

```
lolida/
├── server/     # Python FastAPI 后端
├── admin/      # Web 管理后台 (React + Vite)
├── desktop/    # 桌面 Web 端 (React + Vite，可打包 Electron)
├── LICENSE
└── PROGRESS.md
```

## 快速启动

### 1. 配置环境变量

```bash
cd server
copy .env.example .env   # Windows
# cp .env.example .env   # Mac/Linux
```

编辑 `server/.env`，**至少填写**：

| 变量 | 说明 |
|------|------|
| `DOUBAO_API_KEY` | [火山方舟](https://console.volcengine.com/ark) API Key |
| `DOUBAO_IMAGE_MODEL` | 已开通的 Seedream 模型 ID |
| `ADMIN_PASSWORD` | 管理后台登录密码（生产环境务必修改） |

> ⚠️ **切勿将 `.env` 提交到 Git。** 仓库已忽略该文件。

### 2. 后端

```bash
cd server
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8765 --reload
```

### 3. 桌面端

```bash
cd desktop
npm install
npm run dev
# http://localhost:5174 （localhost / 127.0.0.1 均可）
```

### 4. 管理后台

```bash
cd admin
npm install
npm run dev
# http://localhost:5180
```

## 浏览器说明

开发模式下 API 走 Vite 同源代理，**任意浏览器**用 `localhost:5174` 或 `127.0.0.1:5174` 均可。请保持后端 8765 端口运行。

## 用户反馈

桌面端右下角 **「意见反馈」**，或变身完成后 **👍 有效** / **👎 无效**。管理员在后台 **用户反馈** 标签查看。

## AI 配置

### 获取豆包 API Key

1. [火山方舟控制台](https://console.volcengine.com/ark) → API Key 管理
2. 模型推理 → 开通 **Seedream 4.0/4.5** 图片生成
3. 将模型 ID 填入 `DOUBAO_IMAGE_MODEL`

### 生图逻辑

- **参考图**：用户上传照片（自动压缩至豆包尺寸限制）
- **提示词**：方案 Markdown 的 **「效果描述」** 段落 + 系统模板
- 管理后台编辑「效果描述」即可调整各等级风格

| 变量 | 说明 |
|------|------|
| `DOUBAO_API_KEY` | 火山方舟 API Key（必填） |
| `DOUBAO_IMAGE_SIZE` | `2K` / `4K` |
| `ALLOW_LOCAL_FALLBACK` | 默认 `false`，豆包失败时不静默降级 |

## 打包

```bash
cd desktop && npm run dist   # Electron 桌面端（需网络下载 Electron）
cd admin && npm run build    # 管理后台静态站
```

## API 文档

http://127.0.0.1:8765/docs

## 开源与安全

- 许可证：[MIT](LICENSE)
- **不要提交**：`server/.env`、API Key、数据库 `*.db`、用户上传/生成图片
- 部署前请修改 `ADMIN_PASSWORD` 并轮换已泄露的 API Key

## 贡献

欢迎 Issue / PR。提交前请确认未包含密钥或个人数据。

发布到 GitHub 见 [docs/GITHUB_PUBLISH.md](docs/GITHUB_PUBLISH.md)。
