# 如何发布到 AIPMAndy GitHub

建议新仓库名 `how-to-earn-usd-from-china`，可选择公开仓库。

## 方式一　让 ChatGPT 继续完成上线（更简单）

1. 登录 GitHub，打开 https://github.com/new ，创建一个**公开仓库** `how-to-earn-usd-from-china`。这次请**勾选 Add a README file**，让默认分支初始化。
2. 把新仓库链接发回当前 ChatGPT 对话。我可以通过已连接的 GitHub 将本包内容提交进该仓库。
3. 进入 `Settings → Pages → Build and deployment`，选择 **GitHub Actions**，等项目文件发布以后检查部署结果。
4. 文稿和配图的许可方案仍需由作者确认，参见 `LICENSE-CHOICES.md`。

## 方式二　自己使用 Git 命令上传

1. 登录 GitHub，打开 https://github.com/new ，创建名称为 `how-to-earn-usd-from-china` 的空仓库。**不要勾选自动创建 README、.gitignore 或 License**。
2. 解压本 ZIP，在项目根目录打开终端，按顺序运行下面命令。

```bash
git init
git add .
git commit -m "docs: publish China earn USD handbook and website"
git branch -M main
git remote add origin https://github.com/AIPMAndy/how-to-earn-usd-from-china.git
git push -u origin main
```

3. 打开仓库 `Settings → Pages → Build and deployment`，选择 **GitHub Actions**。
4. 打开仓库 `Actions`，查看 `Check content and links` 和 `Publish GitHub Pages` 是否成功。
5. 部署成功后预计可使用 `https://aipmandy.github.io/how-to-earn-usd-from-china/`。只有 GitHub Pages 完成部署后该地址才有效。

项目包含网站首页、完整文章、四组信息图、官方资料索引和中文/英文 README。发布前请在 `LICENSE-CHOICES.md` 中确定许可方式，然后添加正式 LICENSE 文件。

如果你的 GitHub 账号启用了设备验证、SSO 等登录措施，请按 GitHub 真实界面完成认证，不要把个人密码或 Token 写进仓库。