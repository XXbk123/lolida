# 发布到 GitHub

仓库已做好开源准备（`.gitignore`、`LICENSE`、`SECURITY.md`、`.env.example` 无真实密钥）。按下列步骤推送即可。

## 1. 登录 GitHub CLI

```powershell
gh auth login
```

选择 GitHub.com → HTTPS → 浏览器登录。

## 2. 创建公开仓库并推送

在 `lolida` 目录下执行：

```powershell
cd c:\web-summarizer\lolida
gh repo create lolida --public --source=. --remote=origin --description "萝莉dao - 兄弟照片 AI 变身可爱萝莉整蛊神器" --push
```

若仓库名已被占用，可改成 `lolida-prank` 等：

```powershell
gh repo create lolida-prank --public --source=. --remote=origin --push
```

## 3. 已有空仓库时

```powershell
git remote add origin https://github.com/你的用户名/lolida.git
git push -u origin main
```

## 推送前自检

```powershell
git check-ignore -v server/.env
git status
git log --oneline -5
```

确认：

- `.env`、`*.db`、`node_modules`、`static/uploads`、`static/generated` **未**出现在待提交列表
- 历史中无 `server/.env`（`git log --all -- server/.env` 应无输出）

## 4. 部署者必做

1. 复制 `server/.env.example` → `server/.env`，填入**你自己的** API Key
2. 修改 `ADMIN_PASSWORD` 为强密码
3. 若 Key 曾在聊天/截图中泄露，请在[火山方舟控制台](https://console.volcengine.com/ark)轮换 Key
