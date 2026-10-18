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
        if not target.is_relative_to(ROOT.resolve()) or not (target.is_file() or target.is_dir()):
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


# Growth metadata, sharing, contributor templates and SEO checks
from xml.etree import ElementTree as ET
for path in ['robots.txt','sitemap.xml','404.html','docs/START-HERE.md','templates/first-order-checklist.md','templates/payment-records.md','templates/service-quote.md','.github/ISSUE_TEMPLATE/config.yml','.github/ISSUE_TEMPLATE/real-case.yml','.github/ISSUE_TEMPLATE/fact-check.yml','.github/ISSUE_TEMPLATE/idea.yml']:
 if not (ROOT/path).is_file():errors.append('missing contributor/SEO resource '+path)
for f in files:
 if not f.is_file():continue
 html=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 if not html.select_one('link[rel="canonical"]'):errors.append('missing canonical '+f.name)
 if not html.select_one('meta[property="og:title"]'):errors.append('missing sharing metadata '+f.name)
 if not html.select_one('script[type="application/ld+json"]'):errors.append('missing structured data '+f.name)
try:
 if len(ET.parse(ROOT/'sitemap.xml').getroot())<7:errors.append('sitemap is incomplete')
except Exception as e:errors.append('sitemap XML error '+str(e))
for path in ['README.md','README_EN.md']:
 text=(ROOT/path).read_text(encoding='utf8')
 for link in ['docs/SOURCES.md','templates/first-order-checklist.md']:
  if link not in text:errors.append(path+' lacks '+link)
if errors:
 print('FAILED extended checks',*errors,sep='\n - ');sys.exit(1)
print('PASS — SEO, share metadata and contributor resources')
