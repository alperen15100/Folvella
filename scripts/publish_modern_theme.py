"""Publish the approved Modern Creative Folvella theme as crawlable live pages."""
import json, re, html, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from site_config import ROOT, BASE

posts=[p for p in json.loads((ROOT/'data/posts.json').read_text(encoding='utf-8')) if p.get('status')=='published']
cats=list(json.loads((ROOT/'data/category-covers.json').read_text(encoding='utf-8')))
e=lambda x:html.escape(str(x or ''),quote=True)
absurl=lambda x:x if str(x).startswith('https://') else BASE+str(x)
slugcat=lambda x:re.sub(r'[^a-z0-9]+','-',x.lower()).strip('-')
font='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600;700&display=swap" rel="stylesheet">'

def schema(obj):
    return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False).replace('<','\\u003c')+'</script>'

def live_header(home=False):
    home_href=BASE
    slogan='<div class="top-slogan" aria-label="Small ideas. Beautiful days."><span>Small ideas.</span><strong>Beautiful days.</strong></div>'
    social='<div class="social"><span>p</span><span>◎</span><span>▶</span><span>♪</span><a class="sub" href="'+BASE+'contact.html">✉ Subscribe</a></div>' if home else '<div class="social"><a class="sub" href="'+BASE+'">← Home</a></div>'
    return '<header class="top"><div class="shell head"><a class="logo" href="'+home_href+'">Folvella <i>♡</i><small>by Ecrin Labs</small></a>'+slogan+social+'</div></header>'

def live_footer():
    return '<footer class="full-footer"><div class="shell footer-grid"><div><div class="footer-brand">Folvella ♡</div><p>Beautiful ideas to make, wear, try and keep. A lifestyle project by Ecrin Labs.</p></div><div><b>Explore</b><a href="'+BASE+'#trending">Trending Now</a><a href="'+BASE+'#collections">Collections</a><a href="'+BASE+'#more">More to Love</a><a href="'+BASE+'october-2026/">October Issue</a><a href="'+BASE+'pinterest/">Pinterest images</a></div><div><b>Trust & Legal</b><a href="'+BASE+'editorial-policy.html">Editorial Policy</a><a href="'+BASE+'about.html">About</a><a href="'+BASE+'privacy.html">Privacy</a><a href="'+BASE+'affiliate-disclosure.html">Affiliate Disclosure</a><a href="'+BASE+'contact.html">Contact</a></div></div><div class="shell footer-bottom"><span>© 2026 Folvella</span><span><strong>Ecrin Labs</strong> · Created with care</span></div></footer>'

def mobilebar():
    return '<nav class="mobilebar" aria-label="Mobile navigation"><a href="'+BASE+'">⌂<br>Home</a><a href="'+BASE+'pinterest/">P<br>Pinterest</a><a href="'+BASE+'#collections">◇<br>Collections</a><a href="'+BASE+'#trending">↗<br>Trending</a><a href="'+BASE+'#more">•••<br>More</a></nav>'

def convert_preview(page, path, title, desc, image=None, home=False):
    page=re.sub(r'<head>[\s\S]*?</head>','__HEAD__',page,count=1)
    page=page.replace('../assets/',BASE+'assets/').replace('href="./"', 'href="'+BASE+'"')
    page=page.replace('href="./#', 'href="'+BASE+'#')
    page=page.replace('href="../pinterest/"','href="'+BASE+'pinterest/"')
    page=page.replace('href="../contact.html"','href="'+BASE+'contact.html"')
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
    hd='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(title)+' — Folvella</title><meta name="description" content="'+e(desc)+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+canonical+'"><meta property="og:type" content="website"><meta property="og:site_name" content="Folvella"><meta property="og:title" content="'+e(title)+'"><meta property="og:description" content="'+e(desc)+'"><meta property="og:url" content="'+canonical+'"><meta property="og:image" content="'+ogimg+'"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="'+e(title)+'"><meta name="twitter:description" content="'+e(desc)+'"><meta name="twitter:image" content="'+ogimg+'"><link rel="icon" href="'+BASE+'assets/favicon.svg">'+font+'<link rel="stylesheet" href="'+BASE+'assets/modern-creative.css?v=20261006-live">'+schema({'@context':'https://schema.org','@type':'WebSite','name':'Folvella','url':BASE})+(schema(itemlist) if home else '')+'</head>'
    page=page.replace('<!doctype html><html lang="en">__HEAD__',hd)
    return page

# Live homepage: approved preview, converted to production URLs/SEO.
preview=(ROOT/'theme-preview-modern-creative/index.html').read_text(encoding='utf-8')
home=convert_preview(preview,'','Folvella — Ideas for a More Beautiful Life','Beauty, style, home, DIY, food and grooming ideas worth reading, saving and coming back to.',posts[0]['cover'],True)
(ROOT/'index.html').write_text(home,encoding='utf-8')

# Live October issue.
issue_src=(ROOT/'theme-preview-modern-creative/october-2026.html').read_text(encoding='utf-8')
issue=convert_preview(issue_src,'october-2026/','October 2026 Issue','Everything Folvella published in October 2026, collected across beauty, hair, style, home, DIY, food, fragrance and grooming.',posts[0]['cover'],False)
issue_dir=ROOT/'october-2026'; issue_dir.mkdir(exist_ok=True)
(issue_dir/'index.html').write_text(issue,encoding='utf-8')

# Static, SEO-friendly Modern Creative article pages.
for p in posts:
    path=p['slug']+'/'
    catpath='category/'+slugcat(p['category'])+'/'
    faq=p.get('faq',[])
    related=[next((x for x in posts if x['slug']==s),None) for s in p.get('relatedSlugs',[])]
    related=[x for x in related if x][:3]
    if not related:
        related=sorted([x for x in posts if x['slug']!=p['slug']],key=lambda x:x['category']!=p['category'])[:3]
    article_schema={'@context':'https://schema.org','@type':'BlogPosting','headline':p['title'],'description':p['excerpt'],'image':[absurl(p['cover'])],'mainEntityOfPage':BASE+path,'datePublished':p['datePublished'],'dateModified':p['dateModified'],'author':{'@type':'Organization','name':'Folvella Editorial','url':BASE+'about.html'},'publisher':{'@type':'Organization','name':'Folvella','url':BASE},'articleSection':p['category'],'inLanguage':'en'}
    breadcrumb={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE},{'@type':'ListItem','position':2,'name':p['category'],'item':BASE+catpath},{'@type':'ListItem','position':3,'name':p['title'],'item':BASE+path}]}
    schemas=[article_schema,breadcrumb]
    if faq:
        schemas.append({'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q['q'],'acceptedAnswer':{'@type':'Answer','text':q['a']}} for q in faq]})
    hd='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(p['title'])+' — Folvella</title><meta name="description" content="'+e(p['excerpt'])+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+BASE+path+'"><meta property="og:type" content="article"><meta property="og:site_name" content="Folvella"><meta property="og:title" content="'+e(p['title'])+'"><meta property="og:description" content="'+e(p['excerpt'])+'"><meta property="og:url" content="'+BASE+path+'"><meta property="og:image" content="'+absurl(p['cover'])+'"><meta property="og:image:alt" content="'+e(p.get('coverAlt',p['title']))+'"><meta property="article:published_time" content="'+e(p['datePublished'])+'"><meta property="article:modified_time" content="'+e(p['dateModified'])+'"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="'+BASE+'assets/favicon.svg">'+font+'<link rel="stylesheet" href="'+BASE+'assets/modern-creative.css?v=20261006-live">'+''.join(schema(x) for x in schemas)+'</head>'
    intro=''.join('<p>'+e(x)+'</p>' for x in p.get('intro',[]))
    secs=''
    for s in p.get('sections',[]):
        secs+='<section class="article-section"><h2>'+e(s['heading'])+'</h2>'+''.join('<p>'+e(x)+'</p>' for x in s.get('paragraphs',[]))
        if s.get('image'):
            secs+='<figure class="articleFigure"><img src="'+absurl(s['image'])+'" alt="'+e(s.get('alt',s['heading']))+'" loading="lazy">'+('<figcaption>'+e(s.get('caption',''))+'</figcaption>' if s.get('caption') else '')+'</figure>'
        secs+='</section>'
    faqhtml=''
    if faq:
        faqhtml='<section class="faq"><h2>Frequently Asked Questions</h2>'+''.join('<details><summary>'+e(q['q'])+'</summary><p>'+e(q['a'])+'</p></details>' for q in faq)+'</section>'
    relatedhtml='<section class="article-section"><h2>More to <span class="script-word">explore</span></h2><div class="related-preview">'+''.join('<a href="'+BASE+x['slug']+'/"><img src="'+absurl(x['cover'])+'" alt="'+e(x['title'])+'" loading="lazy"><b>'+e(x['title'])+'</b></a>' for x in related)+'</div></section>'
    body=hd+'<body>'+live_header(False)+'<main><div class="article-shell article-top"><span class="article-crumb">'+e(p['category'])+'</span><h1>'+e(p['title'])+'</h1><p class="article-dek">'+e(p['excerpt'])+'</p><div class="article-meta">'+e(p.get('dateLabel',p['datePublished']))+' · '+e(p.get('readMinutes',3))+' min read · Folvella by Ecrin Labs</div></div><div class="article-shell article-layout"><article class="article-main"><img class="article-cover" src="'+absurl(p['cover'])+'" alt="'+e(p.get('coverAlt',p['title']))+'" fetchpriority="high"><div class="intro">'+intro+'</div>'+secs+faqhtml+relatedhtml+'</article><aside><div class="article-side"><h3>Folvella ♡</h3><p style="color:#6f625d;line-height:1.55">Ideas worth reading, saving and coming back to.</p><a href="'+BASE+'">← Home</a><a href="'+BASE+'#trending">Trending Now</a><a href="'+BASE+'#collections">Collections</a><a href="'+BASE+'october-2026/">October Issue</a><a href="'+BASE+'pinterest/">Pinterest images</a></div></aside></div></main>'+mobilebar()+live_footer()+'</body></html>'
    out=ROOT/path; out.mkdir(parents=True,exist_ok=True); (out/'index.html').write_text(body,encoding='utf-8')

# Ensure October issue is discoverable in the sitemap generated earlier in the build.
sm=ROOT/'sitemap.xml'
if sm.exists():
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('',ns)
    tree=ET.parse(sm); root=tree.getroot()
    locs={n.text for n in root.findall('{'+ns+'}url/{'+ns+'}loc')}
    url=BASE+'october-2026/'
    if url not in locs:
        u=ET.SubElement(root,'{'+ns+'}url'); ET.SubElement(u,'{'+ns+'}loc').text=url
    tree.write(sm,encoding='utf-8',xml_declaration=True)

print(f'Published Modern Creative live theme for {len(posts)} articles.')
