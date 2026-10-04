"""Build the ready-to-share Pin kit from its checked-in metadata."""
import json,html
from pathlib import Path
from urllib.parse import urlencode

root=Path(__file__).resolve().parents[1]
base='https://alperen15100.github.io/Trendora/'
metadata=json.loads((root/'data/pinterest-pins-fall-2026-10-04.json').read_text())
posts={p['slug']:p for p in json.loads((root/'data/posts.json').read_text())}
pins=metadata['pins'];escape=lambda x:html.escape(str(x),quote=True)
categories=list(dict.fromkeys(p['category'] for p in pins))
body='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>48 Fresh Pinterest Pins — Trendora</title><meta name="description" content="48 original vertical Pin designs for 16 craft, home, fall style and coffee guides, with JPG downloads and ready-to-use descriptions."><meta name="robots" content="noindex,follow"><link rel="canonical" href="'''+base+'''pinterest-kit-fall-2026-10-04.html"><link rel="icon" href="assets/favicon.svg"><style>
*{box-sizing:border-box}body{margin:0;background:#faf7f1;color:#29241e;font-family:Arial,sans-serif;line-height:1.6}.wrap{max-width:1200px;margin:auto;padding:32px 24px}a{color:#744633}.brand{font:700 25px Georgia,serif;text-decoration:none}h1{font:500 clamp(32px,5vw,56px)/1.1 Georgia,serif;margin:24px 0 16px}h2{font:500 30px/1.25 Georgia,serif}h3{font:600 22px/1.3 Georgia,serif}p{max-width:760px}.filters{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0}.filters button{border:1px solid #d7cbbb;border-radius:24px;background:white;color:#29241e;padding:10px 18px;font:inherit;cursor:pointer}.filters button[aria-pressed=true]{background:#29241e;color:white}.filters button:focus-visible,a:focus-visible{outline:3px solid #93662e;outline-offset:3px}.pinGroup{border-top:1px solid #dfd6c8;padding:24px 0 40px}.pinGroup[hidden]{display:none}.pinGrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;margin-top:22px}.pinAsset{min-width:0;background:#fff;border:1px solid #e5ddcf;border-radius:15px;overflow:hidden;padding-bottom:20px}.pinAsset img{display:block;width:100%;height:auto;aspect-ratio:2/3}.pinAsset h3,.pinAsset p,.pinActions{margin:16px 18px}.pinAsset p{font-size:14px}.pinActions{display:flex;flex-wrap:wrap;gap:10px}.pinActions a{padding:9px 12px;border:1px solid #d7cbbb;border-radius:8px;text-decoration:none;font-size:14px}.pinActions a:first-child{background:#29241e;color:#fff;border-color:#29241e}.note{color:#6c6257}.topLink{display:block;margin-bottom:10px}footer{padding:30px 0;border-top:1px solid #dfd6c8}@media(max-width:750px){.pinGrid{grid-template-columns:1fr}.wrap{padding:24px 18px}.pinAsset{max-width:440px;width:100%;margin:auto}h2{font-size:25px}}
</style></head><body><main class="wrap" id="main"><a class="brand" href="'''+base+'''">Trendora</a><h1>48 fresh Pins, ready to share</h1><p>Three distinct vertical designs for each of 16 original guides. Download a JPG, copy the description and use the linked article as your destination. “Save to Pinterest” opens Pinterest's own creation page for you to review.</p><p class="note">Prepared October 4, 2026. These assets have not been posted to your Pinterest account. Images are original AI-generated illustrations.</p><nav class="filters" aria-label="Filter Pin topics"><button type="button" data-filter="all" aria-pressed="true">All topics</button>'''
for c in categories:body+='<button type="button" data-filter="'+escape(c)+'" aria-pressed="false">'+escape(c)+'</button>'
body+='</nav><p id="kitStatus" role="status" aria-live="polite">48 Pins across 16 guides</p>'
for slug in dict.fromkeys(p['slug'] for p in pins):
    post=posts[slug];group=[p for p in pins if p['slug']==slug]
    body+='<section class="pinGroup" id="'+slug+'" data-category="'+escape(post['category'])+'"><h2>'+escape(post['title'])+'</h2><a class="topLink" href="'+base+slug+'/">Read the full guide →</a><div class="pinGrid">'
    for pin in group:
        share='https://www.pinterest.com/pin/create/button/?'+urlencode({'url':pin['url'],'media':base+pin['download'],'description':pin['description']})
        body+='<article class="pinAsset"><img loading="lazy" decoding="async" width="1024" height="1536" src="'+escape(pin['image'])+'" alt="'+escape(pin['title'])+' — original illustrated Pinterest design"><h3>'+escape(pin['title'])+'</h3><p>'+escape(pin['description'])+'</p><div class="pinActions"><a href="'+escape(pin['download'])+'" download>Download JPG</a><a href="'+escape(share)+'" target="_blank" rel="noopener noreferrer">Save to Pinterest</a></div></article>'
    body+='</div></section>'
body+='''<footer><a href="pinterest-kit-2026-10-04.html">Previous coffee &amp; food Pin kit</a> · <a href="'''+base+'''">Back to Trendora</a></footer></main><script>
const buttons=[...document.querySelectorAll('[data-filter]')];const groups=[...document.querySelectorAll('[data-category]')];buttons.forEach(button=>button.addEventListener('click',()=>{const category=button.dataset.filter;buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));let count=0;groups.forEach(group=>{group.hidden=category!=='all'&&group.dataset.category!==category;if(!group.hidden)count++});document.getElementById('kitStatus').textContent=(count*3)+' Pins across '+count+' guides'}));
</script></body></html>'''
(root/'pinterest-kit-fall-2026-10-04.html').write_text(body)
print('Built 48-Pin kit with JPG downloads, topic filters and article destinations.')
