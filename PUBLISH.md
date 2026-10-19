# 网站发布与 GitHub 项目设置

## 网站

GitHub Pages 采用 `main` 分支的 GitHub Actions 部署。网页 https://aipmandy.github.io/how-to-earn-usd-from-china/

每次更新后检查 Check content and links、Publish GitHub Pages 是否成功，分别测试网站首页、文章、收款税务页、SVG 图和微信按钮。

## 仓库元数据

以下三项已通过 GitHub API 设置完成，改动时可用 `gh api -X PATCH repos/AIPMAndy/how-to-earn-usd-from-china` 更新：

- Description：`中国人赚美金保姆级攻略｜8 种海外收入路线、获客、报价、交付、合规收款与税务`
- Website：`https://aipmandy.github.io/how-to-earn-usd-from-china/`
- Topics：`china`、`freelancing`、`side-hustle`、`remote-work`、`cross-border`、`ai-tools`、`payments`、`chinese-guide`

## 仍需在 GitHub 页面手动完成

- **Social preview**：在 Settings → General 上传 `assets/social-preview.png`（1200×630，已按平台推荐尺寸生成）。这一步无法通过 API 完成，不设置则仓库卡片与分享链接没有缩略图。
- **Discussions**：如需要社区讨论，在 Settings → Features 启用。Issue 模板已准备，启用前先确认有人力维护。

许可证已确定：内容 CC BY-NC 4.0、代码 MIT。GitHub 会依据 `LICENSE` 自动识别为 MIT，无需手动设置；注意不要在 `LICENSE` 正文后追加说明，否则会退化成 `Other / NOASSERTION`（`check_site.py` 已对此断言）。

## 本地检查流程

改动内容或页面后，按顺序执行：

```bash
pip install -r requirements.txt
python scripts/build_docs.py      # 只有改到 templates/*.md 或 docs/START-HERE.md 时需要
python scripts/check_site.py      # 必须输出 PASS
```

`check_site.py` 会校验页面结构、站内链接与锚点、Markdown 渲染残留、站点地图覆盖率、文档口径和生成页面是否与源文件同步。CI 跑的是同一套检查。

## 让项目被看见

先发布解决一个具体问题的内容，再链接到本攻略的对应页面。例如海外第一单怎么报价、个人收美元必须保留哪些资料、Stripe 支持哪些地区。

邀请读者提供有授权的真实经验和官方来源，认真维护 Issues。避免承诺保证月收入和制造虚假的 Star 互动。