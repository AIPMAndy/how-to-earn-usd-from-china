# 网站发布与 GitHub 项目设置

## 网站

GitHub Pages 采用 `main` 分支的 GitHub Actions 部署。网页 https://aipmandy.github.io/how-to-earn-usd-from-china/

每次更新后检查 Check content and links、Publish GitHub Pages 是否成功，分别测试网站首页、文章、收款税务页、SVG 图和微信按钮。

## 需本人在 GitHub 页面完成的元数据

- 仓库 Description 建议填写 `中国人赚美金保姆级攻略｜8种海外收入路线、获客、报价、交付、合规收款与税务`
- Website 填写 `https://aipmandy.github.io/how-to-earn-usd-from-china/`
- Topics 建议 `china`、`freelancing`、`side-hustle`、`remote-work`、`cross-border`、`ai-tools`、`payments`、`chinese-guide`。
- Social preview 直接上传仓库里的 `assets/social-preview.png`（1200×630，已按平台推荐尺寸生成），在 Settings → General 的 Social preview 上传。
- 如需要社区讨论，可在 Settings → Features 启用 Discussions。Issue 模板已准备。
- 作者未明确选择内容和代码许可证前，不要擅自添加 MIT 或 CC BY 标识。

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