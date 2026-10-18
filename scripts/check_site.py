from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse,unquote
import re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
files=[ROOT/'index.html',ROOT/'article.html']+list((ROOT/'docs').glob('*.html'))
for file in files:
 if not file.exists():errors.append('missing '+str(file));continue
 soup=BeautifulSoup(file.read_text(encoding='utf8'),'html.parser')
 for el in soup.find_all(['a','img','script','link']):
  key='href' if el.name in ('a','link') else 'src'
  value=el.get(key,'').strip()
  if not value or value.startswith(('#','http:','https:','mailto:','tel:','data:')):continue
  loc=unquote(urlparse(value).path)
  resolved=(file.parent/loc).resolve()
  if not resolved.is_relative_to(ROOT.resolve()) or not resolved.exists():errors.append(f'{file.name} broken path {value}')
 assert soup.title is not None
 if file.name=='index.html':
  for value in ['metaver.vip','AIPMAndy','article.html','assets/site.css','data-contact','中国人赚美金']:
   if value not in file.read_text(encoding='utf8'):errors.append('index lacks '+value)
 if file.name=='article.html':
  titles=[x.get_text(' ',strip=True) for x in soup.find_all('h2')]
  if len(titles)<10:errors.append('not enough sections in article')
  if len(soup.select('img.info-image'))!=4:errors.append('expected 4 article infographics')
text=(ROOT/'GUIDE.md').read_text(encoding='utf8')
if len(text)<9000:errors.append('guide too short')
for title in ['专业咨询','AI 自动化','供应链','收款','税务','十、一个月以后']:
 if title not in text:errors.append('guide missing '+title)
if not (ROOT/'assets/cover.svg').exists():errors.append('missing cover')
for name in ['01-生意闭环','02-八种模式','03-资金闭环','04-长期经营']:
 if not (ROOT/'assets'/f'{name}.svg').exists():errors.append('missing figure '+name+'.svg')
 # PNGs are optional offline exports; GitHub Pages uses lossless SVG.
for f in ['README.md','README_EN.md','docs/SOURCES.md','docs/01-business-paths.md','docs/02-payment-tax.md','docs/03-customers-and-delivery.md','examples/outreach-messages.md']:
 if not (ROOT/f).is_file():errors.append('missing '+f)
if errors:
 print('FAILED',*errors,sep='\n - ');sys.exit(1)
print('PASS — full article, local links, four SVG figures, site and docs')

# v1.1: findable and trustworthy landing pages, proper on-site navigation.
from urllib.parse import urldefrag
from xml.etree import ElementTree as ET
for f in [ROOT/'robots.txt',ROOT/'sitemap.xml',ROOT/'docs/START-HERE.md',ROOT/'templates/first-order-checklist.md',ROOT/'templates/payment-records.md',ROOT/'templates/service-quote.md',ROOT/'.github/ISSUE_TEMPLATE/real-case.yml',ROOT/'.github/ISSUE_TEMPLATE/fact-check.yml',ROOT/'.github/ISSUE_TEMPLATE/idea.yml',ROOT/'.github/ISSUE_TEMPLATE/config.yml']:
 if not f.is_file():errors.append('missing discoverability resource '+str(f.relative_to(ROOT)))
for f in files:
 if not f.is_file():continue
 soup=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 if f.name != '404.html':
  if not soup.select_one('link[rel="canonical"]'):errors.append('no canonical '+str(f))
  for prop in ['og:title','og:description','og:url','og:image']:
   if not soup.select_one(f'meta[property="{prop}"]'):errors.append('missing open graph '+prop+' '+str(f))
  if not soup.select_one('script[type="application/ld+json"]'):errors.append('missing structured data '+str(f))
 for a in soup.select('a[href]'):
  url=a['href']
  if not url or url.startswith(('http:','https:','mailto:','tel:')):continue
  path,frag=urldefrag(url)
  linked=(f.parent / unquote(urlparse(path).path)).resolve() if path else f
  if frag and linked.suffix=='.html' and linked.is_file():
   doc=BeautifulSoup(linked.read_text(encoding='utf8'),'html.parser')
   if not doc.find(id=frag):errors.append(f'{f.name} missing target #{frag} in {linked.name}')
for file in (ROOT/'README.md',ROOT/'README_EN.md'):
 if file.is_file():
  content=file.read_text(encoding='utf8')
  for link in ['docs/SOURCES.md','templates/first-order-checklist.md']:
   if link not in content:errors.append('README missing '+link)
try:
 x=ET.parse(ROOT/'sitemap.xml')
 if len(x.getroot())<7:errors.append('sitemap missing main pages')
except Exception as e:errors.append('invalid sitemap '+str(e))
if errors:
 print('FAILED',*errors,sep='\n - ');sys.exit(1)
print('PASS — SEO metadata, navigation targets, templates and sitemap')

# v2 source and interactive-site requirements
v2=(ROOT/'GUIDE.md').read_text(encoding='utf8')
for phrase in ['## 十六、','## 十五、','D01','D30','第一笔订单完成的标准','微信 **AIPMAndy**']:
 if phrase not in v2: errors.append('v2 missing '+phrase)
for page in ['choose-your-path','first-dollar','30-day-plan','deliver-payment','avoid-pitfalls']:
 if not (ROOT/'docs'/f'{page}.html').is_file() or not (ROOT/'docs'/f'{page}.md').is_file():errors.append('missing v2 topic '+page)
front=(ROOT/'index.html').read_text(encoding='utf8')
for token in ['hero-glass','glass-panel','routeSkill','routeAnswerTitle','30-day-plan.html','data-contact']:
 if token not in front:errors.append('v2 landing missing '+token)
client=(ROOT/'assets/site.js').read_text(encoding='utf8')
if 'routeAnswerTitle' not in client or 'change' not in client:errors.append('route matcher is not functional')
if errors:
 print('FAILED v2',*errors,sep='\n - ');sys.exit(1)
print('PASS — v2 16 chapters, 30 daily steps, glass UI, 5 standalone topics and contact entry points')
