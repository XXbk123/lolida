# 发布到 GitHub（首次）

在 `lolida` 目录下执行。

## 1. 登录 GitHub CLI

```powershell
gh auth login
```

按提示选择 GitHub.com → HTTPS → 浏览器登录。

## 2. 创建公开仓库并推送

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
```

确认 `.env`、`.db`、`node_modules` 未出现在待提交列表中。
