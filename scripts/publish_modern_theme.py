"""Publish the approved Modern Creative InspoMint theme as crawlable live pages."""
import json, re, html, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from site_config import ROOT, BASE

posts=[p for p in json.loads((ROOT/'data/posts.json').read_text(encoding='utf-8')) if p.get('status')=='published']
ordered_posts=sorted(posts,key=lambda p:p.get('datePublished',''),reverse=True)
cats=list(json.loads((ROOT/'data/category-covers.json').read_text(encoding='utf-8')))
e=lambda x:html.escape(str(x or ''),quote=True)
absurl=lambda x:x if str(x).startswith('https://') else BASE+str(x)
slugcat=lambda x:re.sub(r'[^a-z0-9]+','-',x.lower()).strip('-')
font='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600;700&display=swap" rel="stylesheet">'

def schema(obj):
    return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False).replace('<','\\u003c')+'</script>'

def replace_between(text,start,end,inner):
    i=text.find(start)
    if i<0: raise ValueError('Missing start marker: '+start)
    j=text.find(end,i+len(start))
    if j<0: raise ValueError('Missing end marker: '+end)
    return text[:i+len(start)]+inner+text[j:]

def live_header(home=False):
    home_href=BASE
    social='<div class="social"><span>p</span><span>◎</span><span>▶</span><span>♪</span><a class="sub" href="'+BASE+'blog/">Blog</a><a class="sub" href="'+BASE+'contact.html">✉ Subscribe</a></div>' if home else '<div class="social"><a class="sub" href="'+BASE+'blog/">Blog</a><a class="sub" href="'+BASE+'">← Home</a></div>'
    return '<header class="top"><div class="shell head"><a class="brand-lockup" href="'+home_href+'"><img src="'+BASE+'assets/inspomint-wordmark.svg" alt="InspoMint — Fresh ideas worth saving."><small>by Ecrin Labs</small></a><div class="head-spacer"></div>'+social+'</div></header>'

def live_footer():
    return '<footer class="full-footer"><div class="shell footer-grid"><div><a class="footer-brand-img" href="'+BASE+'"><img src="'+BASE+'assets/inspomint-wordmark.svg" alt="InspoMint — Fresh ideas worth saving."></a><p>Beautiful ideas to make, wear, try and keep. A lifestyle project by Ecrin Labs.</p></div><div><b>Explore</b><a href="'+BASE+'#trending">Trending Now</a><a href="'+BASE+'#collections">Collections</a><a href="'+BASE+'blog/">Blog</a><a href="'+BASE+'#more">More to Love</a><a href="'+BASE+'october-2026/">October Issue</a><a href="'+BASE+'pinterest/">Pinterest images</a></div><div><b>Trust & Legal</b><a href="'+BASE+'editorial-policy.html">Editorial Policy</a><a href="'+BASE+'about.html">About</a><a href="'+BASE+'privacy.html">Privacy</a><a href="'+BASE+'affiliate-disclosure.html">Affiliate Disclosure</a><a href="'+BASE+'contact.html">Contact</a></div></div><div class="shell footer-bottom"><span>© 2026 InspoMint</span><span><strong>Ecrin Labs</strong> · Created with care</span></div></footer>'

def mobilebar():
    return '<nav class="mobilebar" aria-label="Mobile navigation"><a href="'+BASE+'">⌂<br>Home</a><a href="'+BASE+'blog/">✦<br>Blog</a><a href="'+BASE+'pinterest/">P<br>Pinterest</a><a href="'+BASE+'#collections">◇<br>Collections</a><a href="'+BASE+'#trending">↗<br>Trending</a></nav>'

def convert_preview(page, path, title, desc, image=None, home=False):
    page=re.sub(r'<head>[\s\S]*?</head>','__HEAD__',page,count=1)
    page=page.replace('../assets/',BASE+'assets/').replace('href="./"', 'href="'+BASE+'"')
    page=page.replace('href="./#', 'href="'+BASE+'#')
    page=page.replace('href="../pinterest/"','href="'+BASE+'pinterest/"')
    page=page.replace('href="../contact.html"','href="'+BASE+'contact.html"')
    page=page.replace('<div class="social">','<div class="social"><a class="sub" href="'+BASE+'blog/">Blog</a>',1)
    page=page.replace('href="../editorial-policy.html"','href="'+BASE+'editorial-policy.html"')
    page=page.replace('href="../about.html"','href="'+BASE+'about.html"')
    page=page.replace('href="../privacy.html"','href="'+BASE+'privacy.html"')
    page=page.replace('href="../affiliate-disclosure.html"','href="'+BASE+'affiliate-disclosure.html"')
    page=re.sub(r'href="article\.html\?slug=([^"&]+)"',lambda m:'href="'+BASE+urllib.parse.unquote(m.group(1))+'/"',page)
    page=page.replace('href="october-2026.html"','href="'+BASE+'october-2026/"')
    page=page.replace('class="preview"','class="preview" hidden')
    page=page.replace('Preview only — the live Folvella homepage remains unchanged until you approve this design.','')
    canonical=BASE+path
    ogimg=absurl(image or posts[0]['cover'])
    itemlist={'@context':'https://schema.org','@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'name':p['title'],'url':BASE+p['slug']+'/'} for i,p in enumerate(posts)]}
    hd='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(title)+' — InspoMint</title><meta name="description" content="'+e(desc)+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+canonical+'"><meta property="og:type" content="website"><meta property="og:site_name" content="InspoMint"><meta property="og:title" content="'+e(title)+'"><meta property="og:description" content="'+e(desc)+'"><meta property="og:url" content="'+canonical+'"><meta property="og:image" content="'+ogimg+'"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="'+e(title)+'"><meta name="twitter:description" content="'+e(desc)+'"><meta name="twitter:image" content="'+ogimg+'"><meta name="theme-color" content="#7C9C82"><link rel="icon" type="image/svg+xml" href="'+BASE+'assets/inspomint-mark.svg?v=20261006"><link rel="icon" type="image/png" sizes="32x32" href="'+BASE+'assets/favicon-32x32.png?v=20261006"><link rel="apple-touch-icon" sizes="180x180" href="'+BASE+'assets/apple-touch-icon.png?v=20261006"><link rel="manifest" href="'+BASE+'site.webmanifest">'+font+'<link rel="stylesheet" href="'+BASE+'assets/modern-creative.css?v=20261006-pro2">'+schema({'@context':'https://schema.org','@type':'WebSite','name':'InspoMint','url':BASE})+(schema(itemlist) if home else '')+'</head>'
    page=page.replace('<!doctype html><html lang="en">__HEAD__',hd)
    return page

# Live homepage: approved preview, converted to production URLs/SEO.
preview=(ROOT/'theme-preview-modern-creative/index.html').read_text(encoding='utf-8')
home=convert_preview(preview,'','InspoMint — Fresh Ideas Worth Saving','Beauty, style, home, DIY, food and grooming ideas worth reading, saving and coming back to.','assets/inspomint-og.svg',True)

# Keep every content surface on the homepage synced with posts.json.
home_posts=ordered_posts
pin_svg='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.6 19.3c0-.8.1-1.8.3-2.6l1.3-5.5s-.3-.7-.3-1.6c0-1.5.9-2.6 2-2.6.9 0 1.4.7 1.4 1.5 0 .9-.6 2.3-.9 3.6-.3 1.1.5 2 1.6 2 1.9 0 3.4-2 3.4-5 0-2.6-1.9-4.4-4.5-4.4-3.1 0-4.9 2.3-4.9 4.7 0 .9.4 1.9.8 2.5l-.3 1.2c-1.4-.6-2.2-2.6-2.2-4.2 0-3.4 2.5-6.6 7.2-6.6 3.8 0 6.7 2.7 6.7 6.3 0 3.7-2.4 6.8-5.7 6.8-1.1 0-2.1-.6-2.5-1.2l-.7 2.6c-.2 1-.9 2.1-1.4 2.9A10 10 0 1 0 12 2z"/></svg>'

trend_cards=''
for p in home_posts[:5]:
    share='https://www.pinterest.com/pin/create/button/?'+urllib.parse.urlencode({'url':BASE+p['slug']+'/','media':absurl(p['cover']),'description':p.get('pinDescription') or p['excerpt']})
    trend_cards+='<article class="trend"><a href="'+BASE+p['slug']+'/"><img src="'+absurl(p['cover'])+'" alt="'+e(p['title'])+'"></a><a class="pin" href="'+e(share)+'" target="_blank" rel="noopener noreferrer" aria-label="Save '+e(p['title'])+' to Pinterest">'+pin_svg+'</a><a class="trend-copy" href="'+BASE+p['slug']+'/"><b>'+e(p['category'])+'</b><h3>'+e(p['title'])+'</h3></a></article>'
home=replace_between(home,'<div class="trend-track" id="trendTrack">','</div></div><div class="trend-nav">',trend_cards)

latest_cards=''.join('<a class="mini" href="'+BASE+p['slug']+'/"><img src="'+absurl(p['cover'])+'" alt="'+e(p['title'])+'" loading="lazy"><h3>'+e(p['title'])+'</h3></a>' for p in home_posts[:6])
home=replace_between(home,'<div class="latest">','<section class="shell october-issue">',latest_cards+'</div></div></section>\n\n')
home=home.replace('href="#more">View All →</a>','href="'+BASE+'blog/">View All →</a>')

issue_peeks=''.join('<a class="issue-peek" href="'+BASE+p['slug']+'/"><img src="'+absurl(p['cover'])+'" alt="'+e(p['title'])+'" loading="lazy"><span>'+e(p['category'])+'</span></a>' for p in home_posts[:4])
issue_home='<section class="shell october-issue"><div class="issue-copy"><span class="kicker2">InspoMint Monthly</span><h2>October <span class="script-word">Issue</span></h2><p>Everything we published this October — beauty, hair, style, home, DIY, food and grooming — collected in one place.</p><div class="issue-stats"><strong>'+str(len(home_posts))+' stories</strong><span>•</span><strong>'+str(len(cats))+' collections</strong></div><a class="issue-cta" href="'+BASE+'october-2026/">Explore the October Issue ↗</a></div><div class="issue-peeks">'+issue_peeks+'</div></section>'
home=re.sub(r'<section class="shell october-issue">[\\s\\S]*?</section>',issue_home,home,count=1)

# Refresh the "Your next inspiration" collections with current posts and a richer editorial layout.
def latest_for_categories(names,limit=3):
    items=[p for p in home_posts if p['category'] in names]
    return items[:limit]

collection_specs=[
    ('Beauty worth saving',['Beauty & Nails'],'Glossy color, small details and manicure ideas to keep.','Beauty & Nails'),
    ('A fresh hair chapter',["Women's Hair"],'Cuts, color and texture ideas for your next salon visit.',"Women's Hair"),
    ('Make home feel warmer',['Home Decor','Home & DIY'],'Cozy rooms, thoughtful details and little projects.','Home Decor'),
    ('Something cozy to make',['Food & Drinks'],'Seasonal baking, comfort dinners and slow-morning recipes.','Food & Drinks')
]
collection_cards=''
for idx,(title,names,desc,filter_cat) in enumerate(collection_specs):
    items=latest_for_categories(names,3)
    if not items: continue
    imgs=''.join('<img src="'+absurl(p['cover'])+'" alt="'+e(p['title'])+'" loading="lazy">' for p in items)
    collection_cards+='<a class="collection-card'+(' collection-card-featured' if idx==0 else '')+'" href="?cat='+urllib.parse.quote(filter_cat)+'#more"><div class="collection-kicker">'+e(names[0])+'</div><div class="collection-images">'+imgs+'</div><div class="collection-copy"><h3>'+e(title)+'</h3><p>'+e(desc)+'</p><span class="collection-count">'+str(sum(1 for p in home_posts if p['category'] in names))+' ideas</span></div><span class="arrow">↗</span></a>'
collection_section='<section class="collection-section" id="collections"><div class="shell"><div class="section-title collection-title"><div><span class="collection-eyebrow">CURATED FOR YOU</span><h2>Your next <span class="script-word">inspiration</span></h2><p>Four fresh ways to keep exploring InspoMint.</p></div><a href="'+BASE+'blog/">Browse all ideas ↗</a></div><div class="collection-grid">'+collection_cards+'</div></div></section>'
collection_start='<section class="collection-section" id="collections">'
collection_end='<section class="section" id="more">'
i=home.find(collection_start)
j=home.find(collection_end,i+len(collection_start))
if i<0 or j<0:
    raise ValueError('Collection section markers not found')
home=home[:i]+collection_section+'\n\n'+home[j:]

more_cards=''.join('<article class="more-card" data-cat="'+e(p['category'])+'"><a href="'+BASE+p['slug']+'/"><img src="'+absurl(p['cover'])+'" alt="'+e(p['title'])+'" loading="lazy"><div class="more-copy"><small>'+e(p['category'])+'</small><h3>'+e(p['title'])+'</h3></div></a></article>' for p in home_posts)
home=replace_between(home,'<div class="more-grid">','</div><div class="preview"',more_cards)
(ROOT/'index.html').write_text(home,encoding='utf-8')

# Live October issue, generated directly from posts.json so new articles can never be omitted.
issue_posts=[p for p in ordered_posts if p.get('datePublished','').startswith('2026-10')]
issue_counts={c:sum(1 for p in issue_posts if p['category']==c) for c in cats}
issue_path='october-2026/'
issue_desc='Everything InspoMint published in October 2026, collected across beauty, hair, style, home, DIY, food, fragrance and grooming.'
issue_schema={'@context':'https://schema.org','@type':'CollectionPage','name':'October 2026 Issue','url':BASE+issue_path,'description':issue_desc,'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'name':p['title'],'url':BASE+p['slug']+'/'} for i,p in enumerate(issue_posts)]}}
issue_hd='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>October 2026 Issue — InspoMint</title><meta name="description" content="'+e(issue_desc)+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+BASE+issue_path+'"><meta property="og:type" content="website"><meta property="og:site_name" content="InspoMint"><meta property="og:title" content="October 2026 Issue"><meta property="og:description" content="'+e(issue_desc)+'"><meta property="og:url" content="'+BASE+issue_path+'"><meta property="og:image" content="'+absurl(issue_posts[0]['cover'])+'"><meta name="twitter:card" content="summary_large_image"><link rel="icon" type="image/svg+xml" href="'+BASE+'assets/inspomint-mark.svg">'+font+'<link rel="stylesheet" href="'+BASE+'assets/modern-creative.css?v=20261006-issue4">'+schema(issue_schema)+'</head>'
issue_summary=''.join('<span>'+e(c)+' · '+str(issue_counts[c])+'</span>' for c in cats if issue_counts[c])
issue_filters='<button type="button" data-issue-filter="all" class="active">All October ('+str(len(issue_posts))+')</button>'+''.join('<button type="button" data-issue-filter="'+e(c)+'">'+e(c)+' ('+str(issue_counts[c])+')</button>' for c in cats if issue_counts[c])
issue_cards=''.join('<article class="issue-card" data-cat="'+e(p['category'])+'" data-search="'+e((p['title']+' '+p['category']+' '+p.get('excerpt','')).lower())+'"><a href="'+BASE+p['slug']+'/"><img src="'+absurl(p['cover'])+'" alt="'+e(p.get('coverAlt',p['title']))+'" loading="lazy"><div class="issue-card-copy"><small>'+e(p['category'])+'</small><h2>'+e(p['title'])+'</h2><p>'+e(p['excerpt'])+'</p></div></a></article>' for p in issue_posts)
issue_js='''<script>(function(){const btns=[...document.querySelectorAll('[data-issue-filter]')],cards=[...document.querySelectorAll('.issue-card')],input=document.getElementById('issueSearch'),count=document.getElementById('issueCount');let cat='all';function apply(){const q=(input.value||'').trim().toLowerCase();let n=0;cards.forEach(card=>{const show=(cat==='all'||card.dataset.cat===cat)&&(!q||card.dataset.search.includes(q));card.hidden=!show;if(show)n++});count.textContent='Showing '+n+' '+(n===1?'story':'stories')+'.'}btns.forEach(b=>b.addEventListener('click',()=>{cat=b.dataset.issueFilter;btns.forEach(x=>x.classList.toggle('active',x===b));apply()}));input.addEventListener('input',apply);apply()})();</script>'''
issue_body=issue_hd+'<body>'+live_header(False)+'<main><section class="issue-page-hero"><div class="shell"><span class="issue-eyebrow">InspoMint Monthly · October 2026</span><h1>October <span>Issue</span></h1><p>'+e(issue_desc)+'</p><div class="issue-summary">'+issue_summary+'</div></div></section><section class="section"><div class="shell"><div class="section-title"><div><h2>'+str(len(issue_posts))+' October <span class="script-word">stories</span></h2><p class="issue-page-count" id="issueCount">Showing all '+str(len(issue_posts))+' stories.</p></div><a href="'+BASE+'blog/">All articles →</a></div><form class="issue-search" role="search" onsubmit="return false"><input id="issueSearch" type="search" placeholder="Search October stories…" aria-label="Search October stories"></form><div class="filters">'+issue_filters+'</div><div class="issue-grid" id="issueGrid">'+issue_cards+'</div></div></section></main>'+mobilebar()+live_footer()+issue_js+'</body></html>'
issue_dir=ROOT/'october-2026'; issue_dir.mkdir(exist_ok=True)
(issue_dir/'index.html').write_text(issue_body,encoding='utf-8')

# Full Blog hub: all published guides, newest first, with category filters.
blog_posts=sorted(posts,key=lambda p:p.get('datePublished',''),reverse=True)
blog_path='blog/'
blog_desc='Browse every InspoMint article across beauty, nails, hair, fragrance, home, DIY, food, style and grooming.'
blog_schema={'@context':'https://schema.org','@type':'CollectionPage','name':'InspoMint Blog','url':BASE+blog_path,'description':blog_desc,'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'name':p['title'],'url':BASE+p['slug']+'/'} for i,p in enumerate(blog_posts)]}}
blog_hd='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Blog — InspoMint</title><meta name="description" content="'+e(blog_desc)+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+BASE+blog_path+'"><meta property="og:type" content="website"><meta property="og:site_name" content="InspoMint"><meta property="og:title" content="InspoMint Blog"><meta property="og:description" content="'+e(blog_desc)+'"><meta property="og:url" content="'+BASE+blog_path+'"><meta property="og:image" content="'+absurl(posts[0]['cover'])+'"><meta name="twitter:card" content="summary_large_image"><link rel="icon" type="image/svg+xml" href="'+BASE+'assets/inspomint-mark.svg">'+font+'<link rel="stylesheet" href="'+BASE+'assets/modern-creative.css?v=20261006-blog4">'+schema(blog_schema)+'<style>.blog-hero{padding:56px 0 30px}.blog-hero h1{font:800 clamp(48px,8vw,88px)/.9 Georgia,serif;letter-spacing:-.055em;margin:10px 0;color:#0f2b25}.blog-hero h1 span{color:#7c9c82}.blog-hero p{max-width:720px;color:#6f625d;font-size:18px;line-height:1.65}.blog-count{font-size:13px;color:#7c9c82;font-weight:800;text-transform:uppercase;letter-spacing:.12em}.blog-filters{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0 28px}.blog-filters button{border:1px solid #ded6ca;background:#fff;border-radius:999px;padding:9px 14px;font:700 12px Arial,sans-serif;cursor:pointer;color:#0f2b25}.blog-filters button.active{background:#7c9c82;border-color:#7c9c82;color:#fff}.blog-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;padding-bottom:70px}.blog-card{background:#fff;border:1px solid #e7e0d5;border-radius:18px;overflow:hidden}.blog-card[hidden]{display:none}.blog-card a{text-decoration:none;color:inherit}.blog-card img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}.blog-card-copy{padding:16px}.blog-card small{color:#7c9c82;font-weight:800;text-transform:uppercase;letter-spacing:.07em}.blog-card h2{font:700 22px/1.08 Georgia,serif;margin:8px 0;color:#0f2b25}.blog-card p{font-size:13px;line-height:1.5;color:#6f625d;margin:0}.blog-search{margin:0 0 22px;display:flex;max-width:560px}.blog-search input{width:100%;border:1px solid #ded6ca;border-radius:999px;padding:12px 16px;background:#fff;font:inherit}.blog-empty{display:none;padding:30px 0 70px;color:#6f625d}@media(max-width:900px){.blog-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.blog-grid{grid-template-columns:1fr}.blog-hero{padding-top:34px}}</style></head>'
blog_filters='<div class="blog-filters"><button type="button" class="active" data-blog-filter="all">All</button>'+''.join('<button type="button" data-blog-filter="'+e(c)+'">'+e(c)+'</button>' for c in cats)+'</div>'
blog_cards=''.join('<article class="blog-card" data-cat="'+e(p['category'])+'" data-search="'+e((p['title']+' '+p['category']+' '+p.get('excerpt','')).lower())+'"><a href="'+BASE+p['slug']+'/"><img src="'+absurl(p['cover'])+'" alt="'+e(p.get('coverAlt',p['title']))+'" loading="lazy"><div class="blog-card-copy"><small>'+e(p['category'])+' · '+e(p.get('dateLabel',p.get('datePublished','')))+'</small><h2>'+e(p['title'])+'</h2><p>'+e(p.get('excerpt',''))+'</p></div></a></article>' for p in blog_posts)
blog_js='''<script>(function(){const btns=[...document.querySelectorAll('[data-blog-filter]')],cards=[...document.querySelectorAll('.blog-card')],input=document.getElementById('blogSearch'),status=document.getElementById('blogStatus'),empty=document.getElementById('blogEmpty');let cat='all';function apply(){const q=(input.value||'').trim().toLowerCase();let n=0;cards.forEach(card=>{const show=(cat==='all'||card.dataset.cat===cat)&&(!q||card.dataset.search.includes(q));card.hidden=!show;if(show)n++});status.textContent=n+' articles';empty.style.display=n?'none':'block'}btns.forEach(b=>b.addEventListener('click',()=>{cat=b.dataset.blogFilter;btns.forEach(x=>x.classList.toggle('active',x===b));apply()}));input.addEventListener('input',apply);apply()})();</script>'''
blog_body=blog_hd+'<body>'+live_header(False)+'<main><section class="shell blog-hero"><div class="blog-count">THE INS POMINT JOURNAL</div><h1>Fresh ideas,<br><span>all in one place.</span></h1><p>'+e(blog_desc)+'</p></section><section class="shell"><form class="blog-search" role="search" onsubmit="return false"><input id="blogSearch" type="search" placeholder="Search the blog…" aria-label="Search the blog"></form>'+blog_filters+'<p id="blogStatus" class="blog-count">'+str(len(blog_posts))+' articles</p><div class="blog-grid">'+blog_cards+'</div><p id="blogEmpty" class="blog-empty">No articles match that search.</p></section></main>'+mobilebar()+live_footer()+blog_js+'</body></html>'
blog_dir=ROOT/'blog'; blog_dir.mkdir(exist_ok=True); (blog_dir/'index.html').write_text(blog_body,encoding='utf-8')

# Static, SEO-friendly Modern Creative article pages.
for p in posts:
    path=p['slug']+'/'
    catpath='category/'+slugcat(p['category'])+'/'
    faq=p.get('faq',[])
    related=[next((x for x in posts if x['slug']==s),None) for s in p.get('relatedSlugs',[])]
    related=[x for x in related if x][:3]
    if not related:
        related=sorted([x for x in posts if x['slug']!=p['slug']],key=lambda x:x['category']!=p['category'])[:3]
    article_images=[absurl(x) for x in dict.fromkeys([p['cover']]+[sec.get('image') for sec in p.get('sections',[]) if sec.get('image')])]
    article_words=len(re.findall(r'\S+',' '.join(p.get('intro',[])+[t for sec in p.get('sections',[]) for t in sec.get('paragraphs',[])]+[q.get('a','') for q in faq])))
    article_schema={'@context':'https://schema.org','@type':'BlogPosting','headline':p['title'],'description':p['excerpt'],'image':article_images,'mainEntityOfPage':BASE+path,'datePublished':p['datePublished'],'dateModified':p['dateModified'],'author':{'@type':'Organization','name':'InspoMint Editorial','url':BASE+'about.html'},'publisher':{'@type':'Organization','name':'InspoMint','url':BASE},'articleSection':p['category'],'inLanguage':'en','wordCount':article_words}
    breadcrumb={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE},{'@type':'ListItem','position':2,'name':p['category'],'item':BASE+catpath},{'@type':'ListItem','position':3,'name':p['title'],'item':BASE+path}]}
    schemas=[article_schema,breadcrumb]
    if p.get('qualityStandard')=='pro-v2':
        schemas.append({'@context':'https://schema.org','@type':'ItemList','name':p['title'],'numberOfItems':len(p['sections']),'itemListElement':[{'@type':'ListItem','position':i+1,'name':sec['heading'],'url':BASE+path+'#idea-'+str(i+1)} for i,sec in enumerate(p['sections'])]})
    if faq:
        schemas.append({'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q['q'],'acceptedAnswer':{'@type':'Answer','text':q['a']}} for q in faq]})
    hd='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(p['title'])+' — InspoMint</title><meta name="description" content="'+e(p['excerpt'])+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+BASE+path+'"><meta property="og:type" content="article"><meta property="og:site_name" content="InspoMint"><meta property="og:title" content="'+e(p['title'])+'"><meta property="og:description" content="'+e(p['excerpt'])+'"><meta property="og:url" content="'+BASE+path+'"><meta property="og:image" content="'+absurl(p['cover'])+'"><meta property="og:image:alt" content="'+e(p.get('coverAlt',p['title']))+'"><meta property="article:published_time" content="'+e(p['datePublished'])+'"><meta property="article:modified_time" content="'+e(p['dateModified'])+'"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="'+BASE+'assets/favicon.svg">'+font+'<link rel="stylesheet" href="'+BASE+'assets/modern-creative.css?v=20261006-pro2">'+''.join(schema(x) for x in schemas)+'</head>'
    intro=''.join('<p>'+e(x)+'</p>' for x in p.get('intro',[]))
    toc='<nav class="article-toc" aria-label="In this guide"><span>In this guide</span><ol>'+''.join('<li><a href="#idea-'+str(i+1)+'">'+e(sec['heading'])+'</a></li>' for i,sec in enumerate(p.get('sections',[])))+'</ol></nav>'
    secs=''
    for i,sec in enumerate(p.get('sections',[]),1):
        secs+='<section class="article-section" id="idea-'+str(i)+'"><h2>'+e(sec['heading'])+'</h2>'+''.join('<p>'+e(x)+'</p>' for x in sec.get('paragraphs',[]))
        if sec.get('image'):
            cap=sec.get('caption','')
            if re.search(r'AI[- ]generated|artificial intelligence|editorial visual|styling illustration',cap,re.I):
                cap=sec['heading']+' — '+p['category']+' inspiration.'
            secs+='<figure class="articleFigure"><img src="'+absurl(sec['image'])+'" alt="'+e(sec.get('alt',sec['heading']))+'" loading="lazy">'+('<figcaption>'+e(cap)+'</figcaption>' if cap else '')+'</figure>'
        secs+='</section>'
    faqhtml=''
    if faq:
        faqhtml='<section class="faq"><h2>Frequently Asked Questions</h2>'+''.join('<details><summary>'+e(q['q'])+'</summary><p>'+e(q['a'])+'</p></details>' for q in faq)+'</section>'
    relatedhtml='<section class="article-section"><h2>More to <span class="script-word">explore</span></h2><div class="related-preview">'+''.join('<a href="'+BASE+x['slug']+'/"><img src="'+absurl(x['cover'])+'" alt="'+e(x['title'])+'" loading="lazy"><b>'+e(x['title'])+'</b></a>' for x in related)+'</div></section>'
    body=hd+'<body>'+live_header(False)+'<main><div class="article-shell article-top"><span class="article-crumb">'+e(p['category'])+'</span><h1>'+e(p['title'])+'</h1><p class="article-dek">'+e(p['excerpt'])+'</p><div class="article-meta">'+e(p.get('dateLabel',p['datePublished']))+' · '+e(p.get('readMinutes',3))+' min read · InspoMint by Ecrin Labs</div></div><div class="article-shell article-layout"><article class="article-main"><img class="article-cover" src="'+absurl(p['cover'])+'" alt="'+e(p.get('coverAlt',p['title']))+'" fetchpriority="high"><div class="intro">'+intro+'</div>'+toc+secs+faqhtml+relatedhtml+'</article><aside><div class="article-side"><h3>InspoMint ♡</h3><p style="color:#6f625d;line-height:1.55">Ideas worth reading, saving and coming back to.</p><a href="'+BASE+'">← Home</a><a href="'+BASE+'blog/">Blog</a><a href="'+BASE+'#trending">Trending Now</a><a href="'+BASE+'#collections">Collections</a><a href="'+BASE+'october-2026/">October Issue</a><a href="'+BASE+'pinterest/">Pinterest images</a></div></aside></div></main>'+mobilebar()+live_footer()+'</body></html>'
    out=ROOT/path; out.mkdir(parents=True,exist_ok=True); (out/'index.html').write_text(body,encoding='utf-8')

# Ensure October issue is discoverable in the sitemap generated earlier in the build.
sm=ROOT/'sitemap.xml'
if sm.exists():
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('',ns)
    tree=ET.parse(sm); root=tree.getroot()
    locs={n.text for n in root.findall('{'+ns+'}url/{'+ns+'}loc')}
    for url in [BASE+'october-2026/',BASE+'blog/']:
        if url not in locs:
            u=ET.SubElement(root,'{'+ns+'}url'); ET.SubElement(u,'{'+ns+'}loc').text=url
    tree.write(sm,encoding='utf-8',xml_declaration=True)

print(f'Published InspoMint Modern Creative live theme for {len(posts)} articles.')
