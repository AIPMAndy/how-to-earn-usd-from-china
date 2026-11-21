#!/usr/bin/env python3
"""After GitHub Pages deployment, compare public URL bytes to checked-out main files.
A successful deploy action alone is NOT an online delivery acceptance.
"""
from __future__ import annotations
import hashlib
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://aipmandy.github.io/how-to-earn-usd-from-china/"
FILES = (
    "index.html",
    "quote.html",
    "assets/quote.js",
    "assets/quote.css",
    "robots.txt",
    "sitemap.xml",
    "pdf/how-to-earn-usd-from-china-guide.pdf",
)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> int:
    errors = []
    for path in FILES:
        local = ROOT / path
        if not local.is_file():
            errors.append(f"MISSING local file: {path}")
            continue
        expected = digest(local.read_bytes())
        url = BASE + ("" if path == "index.html" else path)
        reason = "never attempted"
        for attempt in range(1, 9):
            try:
                request = urllib.request.Request(
                    url, headers={"User-Agent": "Andy-Pages-Integrity-Check/1.0",
                                  "Cache-Control": "no-cache"})
                with urllib.request.urlopen(request, timeout=25) as response:
                    body = response.read()
                    status = response.status
                actual = digest(body)
                if status == 200 and expected == actual:
                    print(f"PASS {path} HTTP {status} bytes={len(body)} SHA256={actual}")
                    reason = ""
                    break
                reason = f"HTTP={status}, expected={expected}, received={actual}"
            except (OSError, urllib.error.URLError) as exc:
                reason = repr(exc)
            if attempt < 8:
                time.sleep(10)
        if reason:
            errors.append(f"FAIL {path}: {reason}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(FILES)}/{len(FILES)} deployed files byte-for-byte verified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
