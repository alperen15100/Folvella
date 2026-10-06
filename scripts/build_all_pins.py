"""Build the InspoMint Pinterest sharing page from one branded 3-photo Pin per published guide."""
import json,html
from pathlib import Path
from urllib.parse import urlencode
from site_config import ROOT, BASE

root=ROOT
base=BASE
posts=[p for p in json.loads((root/'data/posts.json').read_text(encoding='utf-8')) if p.get('status')=='published']
e=lambda x:html.escape(str(x),quote=True)

# Newest-first, preserving source order within the same date.
pins=[]
for p in posts:
    image=f"assets/pins/inspomint/{p['slug']}.jpg"
    assert (root/image).is_file(), image
    desc=(p.get('pinDescription') or p.get('excerpt') or '').strip()
    if desc:
        desc=f"{p['title']}. {desc} Discover more on InspoMint."
    else:
        desc=f"{p['title']} — fresh ideas worth saving on InspoMint."
    pins.append(dict(
        slug=p['slug'],
        category=p['category'],
        image=image,
        download=image,
        title=p['title'],
        description=desc,
        url=base+p['slug']+'/',
        date=p.get('datePublished','')
    ))

pins.sort(key=lambda x:x['date'],reverse=True)
metadata=dict(
    preparedAt='2026-10-06',
    articleCount=len(posts),
    pinCount=len(pins),
    layout='one branded 3-photo pin per guide',
    brand='InspoMint',
    status='prepared-not-posted',
    pins=pins,
)
(root/'data/pinterest-catalog.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

body='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>InspoMint Pinterest Pin Collection</title>
<meta name="description" content="Ready-to-share InspoMint 3-photo Pinterest designs for every published guide.">
<meta name="robots" content="noindex,follow"><link rel="canonical" href="'''+base+'''pinterest/">
<meta name="theme-color" content="#7C9C82"><link rel="icon" type="image/svg+xml" href="'''+base+'''assets/inspomint-mark.svg">
<link rel="stylesheet" href="'''+base+'''assets/style.css?v=20261006-inspomint-pins">
<style>
:root{--pin-ink:#0f2b25;--pin-sage:#7c9c82;--pin-bg:#fdfbf6;--pin-line:#e4ded3}
body{background:var(--pin-bg)}
.pinPageHead{padding:42px 0 8px}.pinPageHead h1{font:800 clamp(42px,7vw,76px)/.92 Georgia,serif;letter-spacing:-.045em;color:var(--pin-ink);margin:10px 0 14px}.pinPageHead h1 em{font-family:Georgia,serif;color:var(--pin-sage);font-style:normal}.pinPageHead p{max-width:780px;color:#66716a}
.pinBrand{display:flex;align-items:center;gap:12px;text-decoration:none}.pinBrand img{width:44px;height:44px}.pinBrand strong{font:700 26px Georgia,serif;color:var(--pin-ink)}
.pinFilter{font:inherit;font-size:12px;border:1px solid var(--pin-line);border-radius:999px;padding:9px 13px;background:#fff;color:var(--pin-ink);cursor:pointer}.pinFilter[aria-pressed=true]{background:var(--pin-sage);border-color:var(--pin-sage);color:white}.pinFilter:focus-visible{outline:3px solid #9cb6a4;outline-offset:3px}
.pinCatalogGrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.pinCatalogCard{background:white;border:1px solid var(--pin-line);border-radius:20px;overflow:hidden;box-shadow:0 12px 32px rgba(15,43,37,.06)}.pinCatalogCard[hidden]{display:none}.pinCatalogCard>a{display:block;background:#f6f2e9}.pinCatalogCard img{display:block;width:100%;height:auto;aspect-ratio:2/3;object-fit:cover}.pinCatalogCard>div{padding:16px}.pinCatalogCard h3{font:750 20px/1.08 Georgia,serif;color:var(--pin-ink);margin:0 0 9px}.pinCatalogCard p{font-size:12px;line-height:1.48;color:#66716a;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}.pinCatalogActions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}.pinCatalogActions a{display:flex;align-items:center;justify-content:center;text-align:center;border:1px solid var(--pin-line);border-radius:11px;padding:10px 8px;text-decoration:none;font-size:12px;font-weight:800;color:var(--pin-ink);background:#fff}.pinCatalogActions .pinPrimary{grid-column:1/-1;background:#bd1739;color:#fff;border-color:#bd1739}.pinStatus{font-size:13px;color:#6e756f;margin:14px 0 22px}.seasonJump{display:flex;flex-wrap:wrap;gap:8px}
@media(max-width:980px){.pinCatalogGrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:640px){.pinCatalogGrid{grid-template-columns:1fr 1fr;gap:10px}.pinCatalogCard{border-radius:14px}.pinCatalogCard>div{padding:11px}.pinCatalogCard h3{font-size:15px}.pinCatalogCard p{display:none}.pinCatalogActions{grid-template-columns:1fr}.pinCatalogActions .pinPrimary{grid-column:auto}.pinCatalogActions a{font-size:11px;padding:9px 5px}.pinPageHead{padding-top:28px}.pinPageHead h1{font-size:44px}}
</style></head><body>
<header class="topbar"><div class="shell nav"><a class="pinBrand" href="'''+base+'''"><img src="'''+base+'''assets/inspomint-mark.svg" alt=""><strong>InspoMint</strong></a><div></div><nav aria-label="Main navigation"><a href="'''+base+'''">Discover</a><a href="'''+base+'''october-2026/">October Issue</a></nav></div></header>
<main class="shell" id="main"><section class="pinPageHead"><span class="introKicker">PINTEREST STUDIO</span><h1>Fresh Pins,<br><em>ready to share.</em></h1><p>One new 3-photo InspoMint Pin for every published guide. All destinations point directly to inspomint.com. Choose a Pin, save it to Pinterest, or download the JPG.</p></section>
<nav class="seasonJump" aria-label="Pin categories"><button class="pinFilter" type="button" data-filter="all" aria-pressed="true">All topics</button>'''

for c in dict.fromkeys(p['category'] for p in posts):
    body+='<button class="pinFilter" type="button" data-filter="'+e(c)+'" aria-pressed="false">'+e(c)+'</button>'

body+='</nav><p class="pinStatus" id="pinStatus" role="status" aria-live="polite">'+str(len(pins))+' Pins · one 3-photo design per guide · newest first</p><section class="section"><div class="pinCatalogGrid">'

for p in pins:
    share='https://www.pinterest.com/pin/create/button/?'+urlencode(dict(url=p['url'],media=base+p['image'],description=p['description']))
    body+='<article class="pinCatalogCard" data-category="'+e(p['category'])+'"><a href="'+e(p['url'])+'"><img loading="lazy" decoding="async" width="1000" height="1500" src="'+base+e(p['image'])+'" alt="'+e(p['title'])+' — InspoMint 3-photo Pinterest design"></a><div><h3>'+e(p['title'])+'</h3><p>'+e(p['description'])+'</p><div class="pinCatalogActions"><a class="pinPrimary" href="'+e(share)+'" target="_blank" rel="noopener noreferrer">Save to Pinterest ↗</a><a href="'+base+e(p['download'])+'" download>Download JPG</a><a href="'+e(p['url'])+'">Read guide</a></div></div></article>'

body+='''</div></section></main><footer><div class="shell"><a href="'''+base+'''">Back to InspoMint</a><p>© 2026 InspoMint · Ecrin Labs</p></div></footer><script>
const filters=[...document.querySelectorAll('.pinFilter')],cards=[...document.querySelectorAll('.pinCatalogCard')];
filters.forEach(button=>button.addEventListener('click',()=>{const category=button.dataset.filter;filters.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));let count=0;cards.forEach(card=>{card.hidden=category!=='all'&&card.dataset.category!==category;if(!card.hidden)count++});document.getElementById('pinStatus').textContent=count+' Pins · one 3-photo design per guide · newest first'}));
</script></body></html>'''

(root/'pinterest').mkdir(exist_ok=True)
(root/'pinterest/index.html').write_text(body,encoding='utf-8')
print(f'Built InspoMint Pinterest catalog: {len(pins)} branded 3-photo Pins across {len(posts)} guides.')
