"""Collect every prepared design and one original image for every other guide."""
import json,html
from pathlib import Path
from urllib.parse import urlencode
root=Path(__file__).resolve().parents[1]
base='https://alperen15100.github.io/Trendora/'
posts=json.loads((root/'data/posts.json').read_text());lookup={p['slug']:p for p in posts}
e=lambda x:html.escape(str(x),quote=True)
pins=[]
for record in json.loads((root/'data/pinterest-pins-2026-10-04.json').read_text()):
 p=lookup[record['slug']];image=record['path'];jpg=image.replace('.webp','.jpg')
 pins.append(dict(slug=p['slug'],category=p['category'],image=image,download=jpg if (root/jpg).exists() else image,title=record['headline'],description=record['headline']+'. '+p['excerpt']))
pins+=json.loads((root/'data/pinterest-pins-fall-2026-10-04.json').read_text())['pins']
covered={p['slug'] for p in pins}
for p in posts:
 if p['slug'] not in covered:
  image=p.get('pinCover') or p['cover']
  pins.append(dict(slug=p['slug'],category=p['category'],image=image,download=image,title=p['title'],description=p.get('pinDescription') or p['excerpt']))
for p in pins:
 p['url']=base+p['slug']+'/';p['status']='prepared-not-posted'
 assert (root/p['image']).is_file() and (root/p['download']).is_file()
metadata=dict(preparedAt='2026-10-04',articleCount=len(posts),pinCount=len(pins),status='prepared-not-posted',pins=pins)
(root/'data/pinterest-catalog.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
body='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Folvella Pin Collection</title><meta name="description" content="Original Folvella images and ready-to-share Pinterest designs for every published guide."><meta name="robots" content="noindex,follow"><link rel="canonical" href="'+base+'pinterest/"><link rel="stylesheet" href="'+base+'assets/style.css?v=20261004-complete"><link rel="icon" href="'+base+'assets/favicon.svg"></head><body><header class="topbar"><div class="shell nav"><a class="brand" href="'+base+'">Folvella</a><div></div><nav aria-label="Main navigation"><a href="'+base+'">Discover</a><a href="'+base+'fall-ideas/">Fall edit</a></nav></div></header><main class="shell section" id="main"><h1 class="seasonTitle">Ideas worth sharing.</h1><p class="articleDek">'+str(len(pins))+' original images and prepared designs for '+str(len(posts))+' guides. Choose an image and save it on Pinterest.</p><p class="pinNote">These designs are ready to share; they have not been posted to your account. AI-generated illustrations, with a mix of vertical Pin designs and guide images.</p><nav class="seasonJump" aria-label="Pin categories">'
for c in dict.fromkeys(p['category'] for p in posts):body+='<a href="#'+str(list(dict.fromkeys(x['category'] for x in posts)).index(c))+'">'+e(c)+'</a>'
body+='</nav>'
for ci,c in enumerate(dict.fromkeys(p['category'] for p in posts)):
 body+='<section class="seasonGroup" id="'+str(ci)+'"><h2>'+e(c)+'</h2><div class="pinCatalogGrid">'
 for p in [x for x in pins if x['category']==c]:
  url='https://www.pinterest.com/pin/create/button/?'+urlencode(dict(url=p['url'],media=base+p['download'],description=p['description']))
  body+='<article class="pinCatalogCard"><a href="'+e(p['url'])+'"><img loading="lazy" decoding="async" src="'+base+e(p['image'])+'" alt="'+e(p['title'])+' — original Folvella illustration"></a><div><h3>'+e(p['title'])+'</h3><p>'+e(p['description'])+'</p><div class="pinCatalogActions"><a class="pinPrimary" href="'+e(url)+'" target="_blank" rel="noopener noreferrer">Save to Pinterest ↗</a><a href="'+base+e(p['download'])+'" download>Download image</a><a href="'+e(p['url'])+'">Read guide</a></div></div></article>'
 body+='</div></section>'
body+='</main><footer><div class="shell"><a href="'+base+'">Back to Folvella</a><p>© 2026 Folvella</p></div></footer></body></html>'
(root/'pinterest').mkdir(exist_ok=True);(root/'pinterest/index.html').write_text(body)
print(f'Built unified catalog: {len(pins)} designs across {len(posts)} guides.')
