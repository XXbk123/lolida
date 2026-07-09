# 安全说明

## 切勿提交的内容

- `server/.env`（含 API Key、管理员密码）
- `server/*.db`（含用户反馈与方案数据）
- `server/static/uploads/`、`server/static/generated/`（用户图片）

以上路径已在 `.gitignore` 中配置。

## 部署建议

1. 复制 `server/.env.example` 为 `server/.env`，填入**你自己的**密钥
2. 将 `ADMIN_PASSWORD` 改为强密码
3. 若 API Key 曾在聊天、截图或旧提交中泄露，请在火山方舟控制台**轮换 Key**
4. 生产环境不要将管理后台暴露到公网，或增加反向代理与 IP 限制

## 报告漏洞

请通过 GitHub Issue 说明（勿在 Issue 中粘贴真实 API Key）。
