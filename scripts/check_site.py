from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
pages = [ROOT/'index.html', ROOT/'article.html', *sorted((ROOT/'docs').glob('*.html'))]
for file in pages:
    if not file.exists():
        errors.append(f'Missing page {file}')
        continue
    html = file.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    if not soup.title:
        errors.append(f'Missing title {file.name}')
    for element in soup.find_all(['a','img','script','link']):
        value = (element.get('href') if element.name in ('a','link') else element.get('src')) or ''
        value = value.strip()
        if not value or value.startswith(('#','http:','https:','mailto:','tel:','data:','javascript:')):
            continue
        local = unquote(urlparse(value).path)
        target = (file.parent / local).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
            errors.append(f'{file.name} invalid local resource {value}')
    if file.name=='index.html':
        for term in ['article.html','assets/site.css','data-contact','AIPMAndy','metaver.vip','中国人赚美金']:
            if term not in html:errors.append('Index missing '+term)
    if file.name=='article.html':
        if len(soup.find_all('h2')) < 10:errors.append('Article must contain 10 sections')
        if len(soup.select('img.info-image')) != 4:errors.append('Article must contain four infographics')

guide=(ROOT/'GUIDE.md').read_text(encoding='utf-8')
if len(guide)<9000:errors.append('Guide unexpectedly short')
for keyword in ['专业咨询','AI 自动化','供应链','收款','税务','十、一个月以后']:
    if keyword not in guide:errors.append('Guide missing '+keyword)
for name in ['01-生意闭环','02-八种模式','03-资金闭环','04-长期经营','cover']:
    path=ROOT/'assets'/f'{name}.svg'
    if not path.is_file():errors.append(f'Missing SVG illustration {path.name}')
for name in ['README.md','README_EN.md','docs/SOURCES.md','docs/01-business-paths.md','docs/02-payment-tax.md','docs/03-customers-and-delivery.md','docs/FAQ.html','examples/outreach-messages.md','LICENSE-CHOICES.md']:
    if not (ROOT/name).is_file():errors.append(f'Missing document {name}')
if errors:
    print('FAIL\n'+'\n'.join(errors))
    sys.exit(1)
print('PASS — 10 chapters, 8 business paths, site links, 4 SVG infographics, payments and tax materials')
