#!/usr/bin/env python3
"""把 Markdown 模板渲染成与站点一致的 HTML 页面。

内容唯一来源是 Markdown；HTML 由本脚本生成，不要手改。
CI 用 `--check` 校验仓库中的 HTML 是否与 Markdown 同步，防止再次出现
「同一段内容维护两份、其中一份带着 Markdown 残留」的问题。

用法：
    python scripts/build_docs.py           # 生成 / 覆盖 HTML
    python scripts/build_docs.py --check   # 只校验，不写文件（CI 用）
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://aipmandy.github.io/how-to-earn-usd-from-china/"
SITE = "中国人赚美金保姆级攻略"
AUTHOR = "AI 酋长 Andy"

# Markdown 源 → HTML 目标，以及页面元数据
PAGES = [
    {
        "src": "templates/service-quote.md",
        "out": "templates/service-quote.html",
        "title": "海外服务范围与报价模板",
        "eyebrow": "TEMPLATE / SCOPE AND QUOTE",
        "desc": "可直接改用的英文服务范围与报价模板，包含范围、排除项、交付物、里程碑、验收标准、修改次数与付款条件。",
    },
    {
        "src": "templates/first-order-checklist.md",
        "out": "templates/first-order-checklist.html",
        "title": "海外第一单交付清单",
        "eyebrow": "TEMPLATE / FIRST ORDER",
        "desc": "从签约前到交付前逐项核对：主体身份、服务范围、验收标准、修改次数、付款节点与保密授权。",
    },
    {
        "src": "templates/payment-records.md",
        "out": "templates/payment-records.html",
        "title": "美元收款后的凭证清单",
        "eyebrow": "TEMPLATE / PAYMENT RECORDS",
        "desc": "按报价、签约、履约、收款、退款、记账、申报七个时点整理应保存的凭证，便于核对与备查。",
    },
    {
        "src": "docs/START-HERE.md",
        "out": "docs/START-HERE.html",
        "title": "第一次看这份攻略，直接找答案",
        "eyebrow": "START HERE",
        "desc": "按当前状态直接跳转：还没有客户、客户已询价、马上要收美元、准备做长期业务，各自该看哪一页。",
    },
]

# 站内 Markdown 链接 → 网站可读页面
HREF_MAP = {
    "GUIDE.md": "article.html",
    "../GUIDE.md": "../article.html",
    "docs/SOURCES.md": "docs/SOURCES.html",
    "../docs/SOURCES.md": "../docs/SOURCES.html",
}


def href_for(target: str) -> str:
    if target in HREF_MAP:
        return HREF_MAP[target]
    if target.startswith(("http://", "https://", "#", "mailto:")):
        return target
    if target.endswith(".md"):
        return target[:-3] + ".html"
    return target


def inline(text: str) -> str:
    """行内语法。先转义，再按 code → link → strong 的顺序处理。"""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{href_for(html.unescape(m.group(2)))}">{m.group(1)}</a>',
        out,
    )
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return out


def render(md: str) -> tuple[str, str]:
    """返回 (页面标题, 正文 HTML)。Markdown 的一级标题作为页面标题，不再重复输出。"""
    lines = md.splitlines()
    title = ""
    body: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        if line.startswith("# ") and not title:
            title = line[2:].strip()
            i += 1
            continue

        if line.startswith("### "):
            body.append(f"<h3>{inline(line[4:])}</h3>")
            i += 1
            continue

        if line.startswith("## "):
            body.append(f"<h2>{inline(line[3:])}</h2>")
            i += 1
            continue

        if line == "---":
            body.append("<hr>")
            i += 1
            continue

        # 表格：| a | b |  紧跟 | --- | --- |
        if line.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            header = [c.strip() for c in line.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in header)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            body.append(
                '<div class="table-wrap"><table class="guide-table">'
                f"<thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>"
            )
            continue

        # 任务清单与无序列表
        if re.match(r"^[-*] ", line):
            items: list[str] = []
            checklist = False
            while i < n and re.match(r"^[-*] ", lines[i].strip()):
                item = lines[i].strip()[2:].strip()
                if item.startswith("[ ] "):
                    checklist = True
                    items.append(f'<li class="todo">{inline(item[4:])}</li>')
                elif item.lower().startswith("[x] "):
                    checklist = True
                    items.append(f'<li class="todo done">{inline(item[4:])}</li>')
                else:
                    items.append(f"<li>{inline(item)}</li>")
                i += 1
            cls = ' class="checklist"' if checklist else ""
            body.append(f"<ul{cls}>" + "".join(items) + "</ul>")
            continue

        # 段落：连续非空行合并
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(
            r"^(#{1,3} |[-*] |\||---$)", lines[i].strip()
        ):
            para.append(lines[i].strip())
            i += 1
        body.append(f"<p>{inline(' '.join(para))}</p>")

    return title, "\n".join(body)


def shell(page: dict, title: str, body: str) -> str:
    url = BASE + page["out"]
    desc = html.escape(page["desc"], quote=True)
    head_title = f"{page['title']}｜{SITE}"
    ld = (
        '{"@context":"https://schema.org","@type":"Article",'
        f'"headline":"{page["title"]}","url":"{url}","inLanguage":"zh-CN",'
        f'"description":"{page["desc"]}",'
        f'"isPartOf":{{"@type":"WebSite","name":"{SITE}","url":"{BASE}"}},'
        f'"author":{{"@type":"Person","name":"{AUTHOR}","url":"https://metaver.vip/"}},'
        '"dateModified":"2026-10-19"}'
    )
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#101a23">
<meta name="description" content="{desc}">
<title>{html.escape(head_title)}</title>
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="zh_CN">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{html.escape(page['title'], quote=True)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}assets/social-preview.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(page['title'], quote=True)}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{BASE}assets/social-preview.png">
<script type="application/ld+json">{ld}</script>
<link rel="stylesheet" href="../assets/site.css">
</head><body>
<nav class="navbar"><div class="container nav-inside"><a class="wordmark" href="../">AI酋长 Andy <span>美元收入攻略</span></a><div class="navlinks"><a href="../article.html">完整文章</a><a href="../docs/START-HERE.html">快速开始</a><a href="https://metaver.vip/">个人网站</a></div></div></nav>
<header class="simple-head"><div class="container"><span class="eyebrow">{page['eyebrow']}</span><h1>{html.escape(page['title'])}</h1></div></header>
<main class="page-body">
{body}
</main>
<footer class="foot"><div class="container foot-row"><span>AI酋长 Andy · {SITE}</span><a href="../article.html">完整文章 ↗</a><a href="../docs/SOURCES.html">官方来源 ↗</a><a href="https://metaver.vip/">个人网站 ↗</a></div></footer>
</body></html>
"""


def main() -> int:
    check = "--check" in sys.argv
    stale: list[str] = []
    for page in PAGES:
        src = ROOT / page["src"]
        out = ROOT / page["out"]
        if not src.is_file():
            print(f"FAILED 缺少 Markdown 源：{page['src']}")
            return 1
        md = src.read_text(encoding="utf8")
        title, body = render(md)
        expected = shell(page, title or page["title"], body)
        current = out.read_text(encoding="utf8") if out.is_file() else None
        if current == expected:
            print(f"  ok   {page['out']}")
            continue
        if check:
            stale.append(page["out"])
            print(f"  STALE {page['out']}")
        else:
            out.write_text(expected, encoding="utf8")
            print(f"  build {page['out']}")
    if check and stale:
        print("\n以下页面与 Markdown 源不一致，请运行 python scripts/build_docs.py 重新生成：")
        for s in stale:
            print("  -", s)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
