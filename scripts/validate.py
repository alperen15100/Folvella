"""Check publication source, structured data and local link/asset integrity."""
import json,re,hashlib
from pathlib import Path
from urllib.parse import urlparse,unquote
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
from site_config import ROOT, BASE, BASE_PATH, LEGACY_BASES
root=ROOT;base=BASE;base_path=BASE_PATH
enc=lambda u:u.replace(':','%3A').replace('/','%2F')
posts=json.loads((root/'data/posts.json').read_text());slugs=[p['slug'] for p in posts];assert len(slugs)==len(set(slugs)),'Duplicate slug'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.h1=0;self.canon=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='h1':self.h1+=1
  if a.get('id'):self.ids.append(a['id'])
  if tag=='link' and a.get('rel')=='canonical':self.canon.append(a['href'])
  for key in ['href','src']:
   if a.get(key):self.refs.append(a[key])
  if tag=='img':assert a.get('alt') is not None,'Image without alt'
files=[root/'index.html']+list(root.glob('*/index.html'))+list(root.glob('category/*/index.html'))+[root/(slug+'.html') for slug in json.loads((root/'data/pages.json').read_text())]
for f in files:
 text=f.read_text()
 for stale in LEGACY_BASES:
  if stale!=base:assert stale not in text and enc(stale) not in text,(f,'stale site URL',stale)
 p=Page();p.feed(text)
 assert len(p.canon)==1,(f,'canonical');assert p.canon[0].startswith(base),(f,'canonical base',p.canon[0],base);assert len(p.ids)==len(set(p.ids)),(f,'duplicate IDs')
 if f.name!='article.html':assert p.h1==1,(f,'h1')
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):json.loads(raw)
 for ref in p.refs:
  if ref.startswith(base):target=root/unquote(urlparse(ref).path[len(base_path):])
  elif ref.startswith(('http:','https:','mailto:','tel:','#')):continue
  else:target=f.parent/unquote(urlparse(ref).path)
  if target.is_dir():target=target/'index.html'
  assert target.exists(),(f,'missing target',ref)
for batch_file in root.glob('data/asset-batch-*.json'):
 batch=json.loads(batch_file.read_text());records=batch['images']
 assert len(records)==batch['imageCount'],'Incomplete image batch'
 assert len({x['path'] for x in records})==len(records),'Repeated batch image path'
 assert len({x['sha256'] for x in records})==len(records),'Repeated batch image bytes'
 for record in records:
  assert hashlib.sha256((root/record['path']).read_bytes()).hexdigest()==record['sha256'],'Changed batch artwork'
section_batch=root/'data/asset-batch-section-photos-2026-10-04.json'
if section_batch.exists():
 batch=json.loads(section_batch.read_text());affected={r['slug'] for r in batch['images']}
 assert len(affected)==15 and batch['imageCount']==49,'Incomplete October photo update'
 for p in [p for p in posts if p['slug'] in affected]:
  assert all(s.get('image') for s in p['sections']),('Missing section photo',p['slug'])
  page=(root/p['slug']/'index.html').read_text()
  assert page.count('class="articleFigure"')==len(p['sections']),('Missing rendered figure',p['slug'])
  assert not re.search(r'Pinterest Hobbies Trend Report|Sources and further reading|Practical references|newsroom\.pinterest\.com|fsis\.usda\.gov',page),('Reference section returned',p['slug'])
for p in posts:
 assert p.get('generatedImages'),('Original imagery required',p['slug'])
 assert p['cover'].startswith('assets/generated/'),('Nonlocal cover',p['slug'])
 for source in p.get('sources',[]):
  domain=urlparse(source['url']).hostname or ''
  assert domain=='pinterest.com' or domain.endswith('.pinterest.com'),('Non-Pinterest source',domain)
 if p.get('generatedImages'):
  refs=[s['image'] for s in p['sections'] if s.get('image')];assert all(ref.startswith('assets/generated/') and (root/ref).stat().st_size>0 for ref in refs),'Missing original image';assert len(refs)==len(set(refs)),p['slug']
  hashes=[hashlib.sha256((root/ref).read_bytes()).hexdigest() for ref in refs];assert len(hashes)==len(set(hashes)),'Duplicate illustration'
manifest_path=root/'data/image-manifest.json'
if manifest_path.exists():
 manifest=json.loads(manifest_path.read_text())
 records=manifest['images'];assert len(records)==manifest['replacedSectionImages']
 assert len({r['image'] for r in records})==len(records),'Repeated replacement image path'
 assert len({r['sha256'] for r in records})==len(records),'Repeated replacement artwork'
 for record in records:
  post=next(p for p in posts if p['slug']==record['slug'])
  assert post['sections'][record['section']-1]['image']==record['image'],'Stale image manifest'
  assert hashlib.sha256((root/record['image']).read_bytes()).hexdigest()==record['sha256'],'Changed image bytes'
for extra in [root/'robots.txt',root/'sitemap.xml',root/'feed.xml',root/'llms.txt',root/'pinterest/index.html',root/'pinterest-kit-2026-10-04.html',root/'pinterest-kit-fall-2026-10-04.html']:
 if extra.exists():
  text=extra.read_text()
  for stale in LEGACY_BASES:
   if stale!=base:assert stale not in text and enc(stale) not in text,(extra,'stale site URL',stale)
ET.parse(root/'sitemap.xml');ET.parse(root/'feed.xml')
print(f'PASS: {len(posts)} posts, {len(files)} pages; local links, assets, schemas, image uniqueness and XML.')
