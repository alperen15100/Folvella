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
october=root/'data/pinterest-pins-october-2026-10-05.json'
if october.exists(): pins+=json.loads(october.read_text())['pins']
fall_eight=root/'data/pinterest-pins-fall-eight-2026-10-05.json'
if fall_eight.exists(): pins+=json.loads(fall_eight.read_text())['pins']
grooming=root/'data/pinterest-pins-grooming-2026-10-05.json'
if grooming.exists(): pins+=json.loads(grooming.read_text())['pins']
covered={p['slug'] for p in pins}
for p in posts:
 if p['slug'] not in covered:
  image=p.get('pinCover') or p['cover']
  pins.append(dict(slug=p['slug'],category=p['category'],image=image,download=image,title=p['title'],description=p.get('pinDescription') or p['excerpt']))
for p in pins:
 p['url']=base+p['slug']+'/';p['status']='prepared-not-posted'
 assert (root/p['image']).is_file() and (root/p['download']).is_file()
post_order={p['slug']:i for i,p in enumerate(posts)}
# The published feed resolves ties between guides added on the same day.
pins.sort(key=lambda p:(-int(lookup[p['slug']]['datePublished'].replace('-','')),post_order[p['slug']]))
metadata=dict(preparedAt='2026-10-04',articleCount=len(posts),pinCount=len(pins),sortOrder='newest-first',status='prepared-not-posted',pins=pins)
(root/'data/pinterest-catalog.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
body='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Folvella Pin Collection</title><meta name="description" content="Original Folvella images and ready-to-share Pinterest designs for every published guide."><meta name="robots" content="noindex,follow"><link rel="canonical" href="'+base+'pinterest/"><link rel="stylesheet" href="'+base+'assets/style.css?v=20261004-complete"><link rel="icon" href="'+base+'assets/favicon.svg"></head><body><header class="topbar"><div class="shell nav"><a class="brand" href="'+base+'">Folvella</a><div></div><nav aria-label="Main navigation"><a href="'+base+'">Discover</a><a href="'+base+'fall-ideas/">Fall edit</a></nav></div></header><main class="shell section" id="main"><h1 class="seasonTitle">Ideas worth sharing.</h1><p class="articleDek">'+str(len(pins))+' original images and prepared designs for '+str(len(posts))+' guides. Choose an image and save it on Pinterest.</p><p class="pinNote">These designs are ready to share; they have not been posted to your account. AI-generated illustrations, with a mix of vertical Pin designs and guide images.</p><nav class="seasonJump" aria-label="Pin categories">'
body+='<button class="pinFilter" type="button" data-filter="all" aria-pressed="true">All topics</button>'
for c in dict.fromkeys(p['category'] for p in posts):body+='<button class="pinFilter" type="button" data-filter="'+e(c)+'" aria-pressed="false">'+e(c)+'</button>'
body+='</nav><p class="pinNote" id="pinStatus" role="status" aria-live="polite">'+str(len(pins))+' images · Newest guides first</p><section class="seasonGroup"><h2>Newest first</h2><div class="pinCatalogGrid">'
for p in pins:
  url='https://www.pinterest.com/pin/create/button/?'+urlencode(dict(url=p['url'],media=base+p['download'],description=p['description']))
  body+='<article class="pinCatalogCard" data-slug="'+e(p['slug'])+'" data-category="'+e(p['category'])+'"><a href="'+e(p['url'])+'"><img loading="lazy" decoding="async" src="'+base+e(p['image'])+'" alt="'+e(p['title'])+' — original Folvella illustration"></a><div><h3>'+e(p['title'])+'</h3><p>'+e(p['description'])+'</p><div class="pinCatalogActions"><a class="pinPrimary" href="'+e(url)+'" target="_blank" rel="noopener noreferrer">Save to Pinterest ↗</a><a href="'+base+e(p['download'])+'" download>Download image</a><a href="'+e(p['url'])+'">Read guide</a></div></div></article>'
body+='</div></section>'
body+='''<style>.pinFilter{font:inherit;font-size:13px;border:1px solid var(--line);border-radius:6px;padding:9px 13px;background:white;color:inherit;cursor:pointer}.pinFilter[aria-pressed="true"]{background:#29241e;color:white}.pinFilter:focus-visible{outline:3px solid #a51635;outline-offset:3px}.pinCatalogCard[hidden]{display:none}</style><script>
const filters=[...document.querySelectorAll('.pinFilter')],cards=[...document.querySelectorAll('.pinCatalogCard')];
filters.forEach(button=>button.addEventListener('click',()=>{const category=button.dataset.filter;filters.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));let count=0;cards.forEach(card=>{card.hidden=category!=='all'&&card.dataset.category!==category;if(!card.hidden)count++});document.getElementById('pinStatus').textContent=count+' images · Newest guides first'}));
</script>'''
body+='</main><footer><div class="shell"><a href="'+base+'">Back to Folvella</a><p>© 2026 Folvella</p></div></footer></body></html>'
(root/'pinterest').mkdir(exist_ok=True);(root/'pinterest/index.html').write_text(body)
print(f'Built unified catalog: {len(pins)} designs across {len(posts)} guides.')
