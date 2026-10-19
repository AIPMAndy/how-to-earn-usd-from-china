#!/usr/bin/env python3
"""站点与配套资源校验。

覆盖四类问题：
  1. 结构   —— 页面是否具备 title / H1 / canonical / OG / 结构化数据
  2. 链接   —— 站内相对路径、锚点、图片资源是否真实存在
  3. 渲染   —— HTML 里是否残留未渲染的 Markdown 语法
  4. 一致性 —— 站点地图、README、章节数量、生成页面是否与源同步

用法：python scripts/check_site.py
退出码 0 表示全部通过；1 表示存在失败项（错误会全部列出，不只第一条）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlparse
from xml.etree import ElementTree as ET

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    sys.exit("缺少依赖：pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://aipmandy.github.io/how-to-earn-usd-from-china/"
RASTER = (".png", ".jpg", ".jpeg", ".webp")
errors: list[str] = []
checks = 0


def fail(msg: str) -> None:
    errors.append(msg)


def ok() -> None:
    global checks
    checks += 1


def pages() -> list[Path]:
    found = sorted(ROOT.glob("*.html"))
    for sub in ("docs", "examples", "templates"):
        found += sorted((ROOT / sub).glob("*.html"))
    return [p for p in found if p.is_file()]


# ── 1. 必备文件 ────────────────────────────────────────────────────────────
REQUIRED = [
    "index.html", "article.html", "404.html", "robots.txt", "sitemap.xml",
    "README.md", "README_EN.md", "GUIDE.md", "CONTRIBUTING.md", "SECURITY.md",
    "CHANGELOG.md", "PUBLISH.md", "LICENSING.md", "LICENSE", "LICENSE-CONTENT",
    "assets/site.css", "assets/site.js", "assets/cover.svg", "assets/social-preview.png",
    "assets/01-business-loop.svg", "assets/02-eight-routes.svg",
    "assets/03-money-flow.svg", "assets/04-long-term.svg",
    "docs/START-HERE.md", "docs/FAQ.md", "docs/SOURCES.md", "docs/ROADMAP.md",
    "templates/service-quote.md", "templates/first-order-checklist.md",
    "templates/payment-records.md", "examples/outreach-messages.md",
    "scripts/build_docs.py", "scripts/check_site.py", "requirements.txt",
]
for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        fail(f"缺少必备文件 {rel}")
    else:
        ok()

# ── 2. 每个页面的结构与元数据 ──────────────────────────────────────────────
for page in pages():
    rel = page.relative_to(ROOT).as_posix()
    soup = BeautifulSoup(page.read_text(encoding="utf8"), "html.parser")

    h1s = soup.find_all("h1")
    if len(h1s) != 1:
        fail(f"{rel}: 应恰好 1 个 H1，实际 {len(h1s)} 个")
    else:
        ok()

    if not (soup.title and soup.title.get_text(strip=True)):
        fail(f"{rel}: 缺少 <title>")
    else:
        ok()

    if not soup.select_one('meta[name="description"]'):
        fail(f"{rel}: 缺少 meta description")
    else:
        ok()

    if page.name != "404.html":
        if not soup.select_one('link[rel="canonical"]'):
            fail(f"{rel}: 缺少 canonical")
        else:
            ok()
        for prop in ("og:title", "og:description", "og:url", "og:image", "og:type"):
            if not soup.select_one(f'meta[property="{prop}"]'):
                fail(f"{rel}: 缺少 {prop}")
            else:
                ok()
        if not soup.select_one('meta[name="twitter:card"]'):
            fail(f"{rel}: 缺少 twitter:card")
        else:
            ok()
        if not soup.select_one('script[type="application/ld+json"]'):
            fail(f"{rel}: 缺少结构化数据")
        else:
            ok()

    if not soup.select_one('meta[name="theme-color"]'):
        fail(f"{rel}: 缺少 theme-color")
    else:
        ok()

    # og:image 必须是社交平台能渲染的位图，且文件真实存在
    og = soup.select_one('meta[property="og:image"]')
    if og:
        value = og.get("content", "")
        if not value.startswith("https://"):
            fail(f"{rel}: og:image 必须是绝对地址")
        elif not value.endswith(RASTER):
            fail(f"{rel}: og:image 必须用 PNG/JPEG（社交平台不渲染 SVG）：{value}")
        else:
            tail = unquote(value.replace(SITE, ""))
            if not (ROOT / tail).is_file():
                fail(f"{rel}: og:image 指向不存在的文件 {tail}")
            else:
                ok()

# ── 3. 链接、锚点与资源路径 ────────────────────────────────────────────────
for page in pages():
    rel = page.relative_to(ROOT).as_posix()
    soup = BeautifulSoup(page.read_text(encoding="utf8"), "html.parser")

    for el in soup.find_all(["a", "img", "script", "link", "source"]):
        attr = "href" if el.name in ("a", "link") else "src"
        value = (el.get(attr) or "").strip()
        if not value or value.startswith(("http:", "https:", "mailto:", "tel:", "data:", "#")):
            continue
        path, frag = urldefrag(value)
        target = (page.parent / unquote(urlparse(path).path)).resolve() if path else page.resolve()
        if not target.is_relative_to(ROOT.resolve()):
            fail(f"{rel}: 链接越出仓库 {value}")
            continue
        if not target.exists():
            fail(f"{rel}: 指向不存在的文件 {value}")
            continue
        ok()
        if frag and target.suffix == ".html":
            linked = BeautifulSoup(target.read_text(encoding="utf8"), "html.parser")
            if not linked.find(id=frag) and not linked.find("a", attrs={"name": frag}):
                fail(f"{rel}: 锚点 #{frag} 在 {target.name} 中不存在")
            else:
                ok()

    # 站内不应把原始 Markdown 当作网页链接
    for a in soup.find_all("a", href=True):
        if a["href"].endswith(".md") and not a["href"].startswith("http"):
            fail(f"{rel}: 站内链接指向原始 Markdown {a['href']}（应指向同名 .html）")
        else:
            ok()

    if not (soup.select_one("nav.navbar") or page.name == "404.html"):
        fail(f"{rel}: 缺少站点导航")
    else:
        ok()

# ── 4. 渲染残留：Markdown 语法不该出现在成品 HTML 的正文里 ─────────────────
RESIDUE = [
    (r"!\[[^\]]*\]\([^)]*\)", "Markdown 图片语法"),
    (r"(?<!\*)\*\*[^*\n]{2,}\*\*(?!\*)", "Markdown 粗体语法"),
    (r"^\s*---\s*$", "裸 --- 分隔线"),
    (r"^\s*#{1,6}\s+\S", "Markdown 标题语法"),
    (r"^\s*\|.*\|\s*$", "Markdown 表格行"),
]
for page in pages():
    rel = page.relative_to(ROOT).as_posix()
    soup = BeautifulSoup(page.read_text(encoding="utf8"), "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = "\n".join(
        t.get_text() for t in soup.find_all(["p", "li", "td", "th", "h1", "h2", "h3", "h4", "span"])
    )
    for pattern, label in RESIDUE:
        hit = re.search(pattern, text, re.M)
        if hit:
            fail(f"{rel}: 正文残留{label} -> {hit.group(0)[:60]!r}")
        else:
            ok()

# ── 5. 站点地图与 robots ──────────────────────────────────────────────────
try:
    tree = ET.parse(ROOT / "sitemap.xml")
    locs = [e.text.strip() for e in tree.getroot().iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if len(locs) != len(set(locs)):
        fail("sitemap.xml 存在重复 URL")
    else:
        ok()
    listed = {unquote(u.replace(SITE, "")) for u in locs}
    for page in pages():
        rel = page.relative_to(ROOT).as_posix()
        if page.name == "404.html":
            continue
        # 首页在站点地图里以根路径出现
        expected = "" if rel == "index.html" else rel
        if expected not in listed:
            fail(f"sitemap.xml 未收录 {rel}")
        else:
            ok()
    for entry in tree.getroot():
        if entry.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod") is None:
            fail("sitemap.xml 有条目缺少 lastmod")
        else:
            ok()
except ET.ParseError as exc:
    fail(f"sitemap.xml 不是合法 XML：{exc}")

robots = (ROOT / "robots.txt").read_text(encoding="utf8")
if f"Sitemap: {SITE}sitemap.xml" not in robots:
    fail("robots.txt 未声明 sitemap 地址")
else:
    ok()

# ── 6. 内容与文档口径一致性 ──────────────────────────────────────────────
guide = (ROOT / "GUIDE.md").read_text(encoding="utf8")
chapters = re.findall(r"^## ([一二三四五六七八九十]+)、", guide, re.M)
if len(chapters) != 16:
    fail(f"GUIDE.md 章节数应为 16，实际 {len(chapters)}")
else:
    ok()

for rel in ("README.md", "docs/ROADMAP.md", "docs/PROMOTE.md", "RELEASE-NOTES.md"):
    text = (ROOT / rel).read_text(encoding="utf8")
    # 只拦「当前篇幅是 10 章」这类过期表述；「把原先的十章扩展为十六章」属于历史叙述，允许保留
    stale = re.search(
        r"(?:全文|正文|攻略|长文)\s*(?:10\s*章|十章)|(?:10\s*章|十章)\s*(?:正文|攻略|中文长文)", text
    )
    if stale:
        fail(f"{rel}: 仍有过期的章节数表述「{stale.group(0)}」，正文实际为 16 章")
    else:
        ok()

changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf8")
if not changelog.lstrip().startswith("#"):
    fail("CHANGELOG.md 应以一级标题开头")
else:
    ok()

readme = (ROOT / "README.md").read_text(encoding="utf8")
for img in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", readme):
    if img.startswith("http"):
        continue
    if not (ROOT / unquote(img)).is_file():
        fail(f"README.md 引用了不存在的图片 {img}")
    else:
        ok()

# ── 6b. 许可证一致性 ─────────────────────────────────────────────────────
license_text = (ROOT / "LICENSE").read_text(encoding="utf8")
if "MIT License" not in license_text:
    fail("LICENSE 不是 MIT 文本")
elif not license_text.strip().endswith("SOFTWARE.") or "\n---" in license_text:
    # 在许可证正文后追加说明会破坏 GitHub 的许可证指纹识别（显示为 Other/NOASSERTION）
    fail("LICENSE 末尾有附加内容，会破坏 GitHub 的 MIT 识别；适用范围说明请放到 LICENSING.md")
else:
    ok()

content_license = (ROOT / "LICENSE-CONTENT").read_text(encoding="utf8")
for token in ("CC BY-NC 4.0", "by-nc/4.0/legalcode"):
    if token not in content_license:
        fail(f"LICENSE-CONTENT 缺少「{token}」")
    else:
        ok()

for rel, needed in {
    "README.md": ["LICENSING.md", "LICENSE-CONTENT"],
    "README_EN.md": ["LICENSING.md", "LICENSE"],
    "LICENSING.md": ["CC BY-NC 4.0", "MIT"],
}.items():
    text = (ROOT / rel).read_text(encoding="utf8")
    for token in needed:
        if token not in text:
            fail(f"{rel} 未提及授权信息 {token}")
        else:
            ok()

# 已废弃的旧文件名不应再被引用。CHANGELOG 记录历史、本脚本自身包含该字符串，故跳过。
DEPRECATED = "LICENSE-" + "CHOICES"
SKIP = {"CHANGELOG.md", "scripts/check_site.py"}
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    if path.suffix not in {".md", ".html", ".py", ".yml", ".txt"}:
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel in SKIP:
        continue
    if DEPRECATED in path.read_text(encoding="utf8", errors="ignore"):
        fail(f"{rel} 仍引用已删除的 {DEPRECATED}.md")
    else:
        ok()

# ── 7. 生成页面是否与 Markdown 源同步 ────────────────────────────────────
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import build_docs

    for page in build_docs.PAGES:
        src, out = ROOT / page["src"], ROOT / page["out"]
        if not src.is_file() or not out.is_file():
            fail(f"生成页缺失：{page['src']} -> {page['out']}")
            continue
        title, body = build_docs.render(src.read_text(encoding="utf8"))
        if out.read_text(encoding="utf8") != build_docs.shell(page, title or page["title"], body):
            fail(f"{page['out']} 与 {page['src']} 不同步，请运行 python scripts/build_docs.py")
        else:
            ok()
except ImportError as exc:
    fail(f"无法导入 build_docs：{exc}")

# ── 8. 资产命名应为 ASCII，避免百分号编码在各处出错 ──────────────────────
for asset in (ROOT / "assets").iterdir():
    if asset.name != asset.name.encode("ascii", "ignore").decode():
        fail(f"assets/{asset.name}: 文件名应使用 ASCII，避免 URL 编码问题")
    else:
        ok()

# ── 汇总 ─────────────────────────────────────────────────────────────────
print(f"执行 {checks} 项检查，{len(pages())} 个页面")
if errors:
    print(f"\n失败 {len(errors)} 项：")
    for e in errors:
        print("  ✗", e)
    sys.exit(1)
print("PASS — 结构、链接、渲染、站点地图、文档口径与生成页面全部通过")
