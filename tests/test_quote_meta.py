#!/usr/bin/env python3
"""Focused structural QA of the standalone estimator (not a substitute for screen readers)."""
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
page=ROOT/"quote.html"
soup=BeautifulSoup(page.read_text(encoding="utf-8"),"html.parser")
assert len(soup.find_all("h1"))==1
assert soup.select_one('link[rel="canonical"]')["href"]=="https://aipmandy.github.io/how-to-earn-usd-from-china/quote.html"
data=json.loads(soup.select_one('script[type="application/ld+json"]').string)
assert data["@type"]=="WebApplication"
assert data["author"]["url"]=="https://metaver.vip/"
assert data["publisher"]["url"]=="https://www.a6no1.cn/"
assert data["dateModified"]=="2026-11-22"
for field in ("quote","percent","fixed","direct","fx","bank","hours","target"):
    assert soup.select_one('input[name="'+field+'"]')
assert len(soup.select('input[name="fx"][value]')) == 0, "Must not imply real-time FX"
for link in soup.select("a[href]"):
    href=link.get("href","")
    if href.startswith(("https://","http://","#","mailto:")):
        continue
    assert (ROOT/href).exists(), "broken relative URL: "+href
assert "quote.html" in (ROOT/"sitemap.xml").read_text(encoding="utf-8")
assert 'href="quote.html"' in (ROOT/"index.html").read_text(encoding="utf-8")
assert (ROOT/"pdf/how-to-earn-usd-from-china-guide.pdf").is_file()
assert "2026-11-13" in page.read_text(encoding="utf-8"), "Preserve historic source cutoff"
print("PASS quote SEO/JSON-LD, required fields, historic date, links & PDF")
