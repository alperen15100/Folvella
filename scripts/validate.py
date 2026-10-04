"""Check publication source, structured data and local link/asset integrity."""
import json,re,hashlib
from pathlib import Path
from urllib.parse import urlparse,unquote
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];base='https://alperen15100.github.io/Trendora/'
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
files=[root/'index.html']+list(root.glob('*/index.html'))+list(root.glob('category/*/index.html'))
for f in files:
 text=f.read_text();p=Page();p.feed(text)
 assert len(p.canon)==1,(f,'canonical');assert len(p.ids)==len(set(p.ids)),(f,'duplicate IDs')
 if f.name=='index.html' and f.parent!=root:assert p.h1==1,(f,'h1')
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):json.loads(raw)
 for ref in p.refs:
  if ref.startswith(base):target=root/unquote(urlparse(ref).path[len('/Trendora/'):])
  elif ref.startswith(('http:','https:','mailto:','tel:','#')):continue
  else:target=f.parent/unquote(urlparse(ref).path)
  if target.is_dir():target=target/'index.html'
  assert target.exists(),(f,'missing target',ref)
for p in posts:
 if p.get('generatedImages'):
  refs=[s['image'] for s in p['sections'] if s.get('image')];assert len(refs)==len(set(refs)),p['slug']
  hashes=[hashlib.sha256((root/ref).read_bytes()).hexdigest() for ref in refs];assert len(hashes)==len(set(hashes)),'Duplicate illustration'
ET.parse(root/'sitemap.xml');ET.parse(root/'feed.xml')
print(f'PASS: {len(posts)} posts, {len(files)} pages; local links, assets, schemas, image uniqueness and XML.')
