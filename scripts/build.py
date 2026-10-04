"""Rebuild crawlable Trendora pages using the checked-in editorial source."""
import json,re,html,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from email.utils import format_datetime
ROOT=Path(__file__).resolve().parents[1]
BASE='https://alperen15100.github.io/Trendora/'
posts=[p for p in json.loads((ROOT/'data/posts.json').read_text()) if p.get('status')=='published']
e=lambda x:html.escape(str(x),quote=True)
absurl=lambda x:x if x.startswith('https://') else BASE+x
cat_slug=lambda x:re.sub(r'[^a-z0-9]+','-',x.lower()).strip('-')
image_dimensions=json.loads((ROOT/'data/image-dimensions.json').read_text())
categories=list(dict.fromkeys(p['category'] for p in posts))
def js(x):return json.dumps(x,ensure_ascii=False).replace('<','\\u003c')
def schema(x):return '<script type="application/ld+json">'+js(x)+'</script>'
def head(title,description,path,image=None,schemas=[]):
 url=BASE+path
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(title)+' — Trendora</title><meta name="description" content="'+e(description)+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+url+'"><link rel="alternate" type="application/rss+xml" title="Trendora RSS" href="'+BASE+'feed.xml"><meta property="og:type" content="'+('article' if any(path==p['slug']+'/' for p in posts) else 'website')+'"><meta property="og:title" content="'+e(title)+'"><meta property="og:description" content="'+e(description)+'"><meta property="og:url" content="'+url+'"><meta property="og:site_name" content="Trendora"><meta name="twitter:card" content="summary_large_image">'+ ('<meta property="og:image" content="'+e(absurl(image))+'"><meta name="twitter:image" content="'+e(absurl(image))+'">' if image else '')+'<meta name="twitter:title" content="'+e(title)+'"><meta name="twitter:description" content="'+e(description)+'"><link rel="icon" type="image/svg+xml" href="'+BASE+'assets/favicon.svg"><link rel="stylesheet" href="'+BASE+'assets/style.css?v=20261004-seven-guides">'+''.join(schema(s) for s in schemas)+'</head>'
def nav():return '<header class="topbar"><div class="shell nav"><a class="brand" href="'+BASE+'"><span>🍁</span><b>Trendora</b></a><div></div><nav><a href="'+BASE+'#fresh">Ideas</a><a href="'+BASE+'categories/">Categories</a><a href="'+BASE+'about.html">About</a></nav></div></header>'
def footer():return '<footer><div class="shell footGrid"><div><a class="brand" href="'+BASE+'">Trendora</a><p>Beautiful ideas for everyday living.</p></div><div><b>Explore</b>'+''.join('<a href="'+BASE+'category/'+cat_slug(c)+'/">'+e(c)+'</a>' for c in categories)+'</div><div><b>Trust & Legal</b>'+''.join('<a href="'+BASE+f+'.html">'+t+'</a>' for f,t in [('editorial-policy','Editorial Policy'),('about','About'),('privacy','Privacy'),('affiliate-disclosure','Affiliate Disclosure'),('contact','Contact')])+'</div></div><div class="shell copyright">© 2026 Trendora</div></footer>'
def img(src,alt,lead=False):
 # Use intrinsic dimensions to reserve space before images load.
 size=image_dimensions.get(src)
 dimensions=(' width="'+str(size[0])+'" height="'+str(size[1])+'"') if size else ''
 return '<img src="'+e(absurl(src))+'" alt="'+e(alt)+'" decoding="async"'+dimensions+(' fetchpriority="high"' if lead else ' loading="lazy"')+'>'
def cards(items):return ''.join('<article class="ideaCardWrap" data-cat="'+e(p['category'])+'" data-title="'+e(p['title'].lower())+'"><a class="ideaCard" href="'+BASE+p['slug']+'/">'+img(p['cover'],p['coverAlt'])+'<div class="cardText"><small>'+e(p['category'])+'</small><h3>'+e(p['title'])+'</h3><span>Read ideas</span></div></a></article>' for p in items)
def write(path,text):
 f=ROOT/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text,encoding='utf-8')
for p in posts:
 path=p['slug']+'/'
 catpath='category/'+cat_slug(p['category'])+'/'
 faq=p.get('faq',[])
 article={'@context':'https://schema.org','@type':'BlogPosting','@id':BASE+path+'#article','headline':p['title'],'description':p['excerpt'],'image':[absurl(p['cover'])],'mainEntityOfPage':BASE+path,'datePublished':p['datePublished'],'dateModified':p['dateModified'],'author':{'@type':'Organization','name':'Trendora Editorial','url':BASE+'about.html'},'publisher':{'@type':'Organization','name':'Trendora','url':BASE},'inLanguage':'en','articleSection':p['category']}
 breadcrumb={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE},{'@type':'ListItem','position':2,'name':p['category'],'item':BASE+catpath},{'@type':'ListItem','position':3,'name':p['title'],'item':BASE+path}]}
 schemas=[article,breadcrumb]
 if faq:schemas.append({'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q['q'],'acceptedAnswer':{'@type':'Answer','text':q['a']}} for q in faq]})
 related=sorted([x for x in posts if x['slug']!=p['slug']],key=lambda x:x['category']!=p['category'])[:3]
 if p.get('relatedSlugs'):related=[next(x for x in posts if x['slug']==slug) for slug in p['relatedSlugs']]
 body=head(p['title'],p['excerpt'],path,p['cover'],schemas).replace('</head>','<meta property="article:published_time" content="'+e(p['datePublished'])+'"><meta property="article:modified_time" content="'+e(p['dateModified'])+'"><meta property="og:image:alt" content="'+e(p['coverAlt'])+'"></head>')+'<body>'+nav()+'<main id="main"><section class="articleHero shell"><div class="crumb"><a href="'+BASE+'">Home</a> / <a href="'+BASE+catpath+'">'+e(p['category'])+'</a></div><h1>'+e(p['title'])+'</h1><p class="articleDek">'+e(p['excerpt'])+'</p><div class="meta">By <a href="'+BASE+'about.html">Trendora Editorial</a> · <time datetime="'+e(p['dateModified'])+'">Updated '+e(p['dateModified'])+'</time> · '+str(p.get('readMinutes',6))+' min read</div></section><section class="shell articleLayout"><article class="articleMain"><div class="articleCoverWrap">'+img(p['cover'],p['coverAlt'],True)+'<button id="articlePin" class="articlePin" type="button">Save to Pinterest</button></div>'
 if p.get('generatedImages'):body+='<p class="disclosure">Images are original AI-generated styling illustrations, not product or service photographs.</p>'
 body+=''.join('<p>'+e(t)+'</p>' for t in p.get('intro',[]))
 body+='<nav class="contents" aria-label="In this guide"><h2>In this guide</h2><ol>'+''.join('<li><a href="#idea-'+str(i+1)+'">'+e(s['heading'])+'</a></li>' for i,s in enumerate(p['sections']))+'</ol></nav>'
 for i,s in enumerate(p['sections']):
  body+='<section class="longSection" id="idea-'+str(i+1)+'"><h2>'+e(s['heading'])+'</h2>'+''.join('<p>'+e(t)+'</p>' for t in s.get('paragraphs',[]))
  if s.get('image'):body+='<figure class="articleFigure">'+img(s['image'],s.get('alt',s['heading']))+('<figcaption>'+e(s['caption'])+'</figcaption>' if s.get('caption') else '')+'</figure>'
  body+='</section>'
 if faq:body+='<section class="longSection"><h2>Frequently asked questions</h2>'+''.join('<h3>'+e(q['q'])+'</h3><p>'+e(q['a'])+'</p>' for q in faq)+'</section>'
 if p.get('sources'):body+='<section class="longSection"><h2>Sources and further reading</h2><ul>'+''.join('<li><a href="'+e(s['url'])+'" rel="noopener noreferrer">'+e(s['title'])+'</a> · Checked '+e(s['accessed'])+'</li>' for s in p['sources'])+'</ul></section>'
 body+='</article><aside class="articleAside"><div class="sideCard"><h3>More to explore</h3><div class="sideLinks">'+''.join('<a href="'+BASE+x['slug']+'/">'+e(x['title'])+'</a>' for x in related)+'<a href="'+BASE+catpath+'">All '+e(p['category'])+' guides</a></div></div></aside></section><section class="section shell"><h2>You may also like</h2><div class="ideaGrid">'+cards(related)+'</div></section></main>'+footer()
 payload={'url':BASE+path,'media':absurl(p.get('pinCover',p['cover'])),'description':p.get('pinDescription',p['excerpt'])}
 body+='<script>const pin='+js(payload)+';document.getElementById("articlePin").addEventListener("click",()=>{const q=new URLSearchParams(pin);window.open("https://www.pinterest.com/pin/create/button/?"+q,"_blank","noopener,noreferrer")});</script></body></html>'
 write(path+'index.html',body)
for c in categories:
 items=[p for p in posts if p['category']==c];path='category/'+cat_slug(c)+'/'
 desc='Explore '+c.lower()+' ideas, visual references and practical guides from Trendora.'
 collection={'@context':'https://schema.org','@type':'CollectionPage','name':c+' Ideas','url':BASE+path,'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':BASE+p['slug']+'/','name':p['title']} for i,p in enumerate(items)]}}
 write(path+'index.html',head(c+' Ideas',desc,path,items[0]['cover'],[collection,{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE},{'@type':'ListItem','position':2,'name':'Categories','item':BASE+'categories/'},{'@type':'ListItem','position':3,'name':c,'item':BASE+path}]}])+'<body>'+nav()+'<main class="shell section"><div class="crumb"><a href="'+BASE+'">Home</a> / '+e(c)+'</div><h1>'+e(c)+' Ideas</h1><p>'+e(desc)+'</p><div class="ideaGrid">'+cards(items)+'</div></main>'+footer()+'</body></html>')
# Category hub and trust pages share the same navigation and SEO conventions.
hubitems=[{'slug':'category/'+cat_slug(c),'category':c,'title':c+' · '+str(sum(p['category']==c for p in posts))+(' guide' if sum(p['category']==c for p in posts)==1 else ' guides'),'cover':next(p['cover'] for p in posts if p['category']==c),'coverAlt':c+' visual guide'} for c in categories]
write('categories/index.html',head('Explore Categories','Browse original visual guides for home, beauty, grooming and food.','categories/')+'<body>'+nav()+'<main class="shell section"><h1>Explore Categories</h1><p>Choose a topic and find practical guides with original visual ideas.</p><div class="ideaGrid">'+cards(hubitems)+'</div></main>'+footer()+'</body></html>')
for slug,page in json.loads((ROOT/'data/pages.json').read_text()).items():
 path=slug+'.html'
 body=head(page['title'],page['description'],path,schemas=[{'@context':'https://schema.org','@type':'AboutPage' if slug=='about' else 'ContactPage' if slug=='contact' else 'WebPage','name':page['title'],'url':BASE+path}])+'<body>'+nav()+'<main class="legal shell" id="main"><h1>'+e(page['title'])+'</h1><p class="meta">Updated October 4, 2026</p>'
 for section in page['sections']:
  body+='<section><h2>'+e(section['heading'])+'</h2>'+''.join('<p>'+e(t)+'</p>' for t in section['paragraphs'])
  body+=''.join('<p><a href="'+e(link['url'])+'" rel="noopener noreferrer">'+e(link['label'])+'</a></p>' for link in section.get('links',[]))+'</section>'
 write(path,body+'</main>'+footer()+'</body></html>')

# Keep the established interactive homepage, but provide the complete initial HTML for crawlers and no-JS visitors.
home=(ROOT/'index.html').read_text()
home=re.sub(r'<script type="application/ld\+json">.*?</script>','',home,flags=re.S)
home=re.sub(r'<meta property="og:image"[^>]*>|<meta name="twitter:(?:card|image)"[^>]*>','',home)
home=home.replace('</head>','<meta property="og:image" content="'+absurl(posts[0]['cover'])+'"><meta name="twitter:image" content="'+absurl(posts[0]['cover'])+'"><meta name="twitter:card" content="summary_large_image">'+schema({'@context':'https://schema.org','@type':'WebSite','name':'Trendora','url':BASE})+schema({'@context':'https://schema.org','@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'name':p['title'],'url':BASE+p['slug']+'/'} for i,p in enumerate(posts)]})+'</head>')
hero='<section class="hero">'+img(posts[0]['cover'],posts[0]['coverAlt'],True)+'<div class="heroShade"></div><div class="shell heroContent"><span class="eyebrow">'+e(posts[0]['category'])+'</span><h1>'+e(posts[0]['title'])+'</h1><p>'+e(posts[0]['excerpt'])+'</p><a class="cta" href="'+posts[0]['slug']+'/">Read the guide</a></div></section>'
home=re.sub(r'<div id="heroMount">.*?</div>\s*(?=<section class="categoryStrip")','<div id="heroMount">'+hero+'</div>\n\n  ',home,flags=re.S)
home=re.sub(r'<div class="ideaGrid" id="ideaGrid">.*?</div>\s*<div class="emptyState"', '<div class="ideaGrid" id="ideaGrid">'+cards(posts)+'</div>\n      <div class="emptyState"',home,flags=re.S)
home=home.replace('<div class="emptyState" id="emptyState">','<div class="emptyState" id="emptyState" hidden>')
home=re.sub(r'<div class="shell categoryRow" id="categoryRow">.*?</div>', '<div class="shell categoryRow" id="categoryRow">'+''.join('<a href="category/'+cat_slug(c)+'/"><span>'+e(c)+'</span></a>' for c in categories)+'</div>',home,flags=re.S)
home=re.sub(r'<section class="newsletter">.*?</section>','<section class="newsletter"><div class="shell newsletterIn"><div><h2>Keep your favorite ideas close</h2><p>Follow new guides in your RSS reader or save an idea to Pinterest.</p></div><a class="cta" href="feed.xml">Follow the RSS feed</a></div></section>',home,flags=re.S)
home=re.sub(r'href="assets/style\.css(?:\?[^"]*)?"','href="assets/style.css?v=20261004-seven-guides"',home)
home=re.sub(r'assets/app\.js(?:\?[^"]*)?', 'assets/app.js?v=20261004-seven-guides',home)
home=re.sub(r'<link rel="preconnect"[^>]*>|<script async defer src="https://assets.pinterest.com/js/pinit.js"></script>','',home)
home=home.replace('href="#categories">Categories','href="categories/">Categories').replace('Popular Categories','Explore Categories')
home=home.replace('<input id="searchInput"','<input aria-label="Search article titles" id="searchInput"') if 'aria-label="Search article titles"' not in home else home
home=home.replace('<main>','<main id="main">')
if 'id="searchStatus"' not in home:home=home.replace('<div class="ideaGrid" id="ideaGrid">','<p id="searchStatus" role="status" aria-live="polite"></p><div class="ideaGrid" id="ideaGrid">')
home=re.sub(r'<footer>.*?</footer>',footer(),home,flags=re.S)
if 'favicon.svg' not in home:home=home.replace('</head>','<link rel="icon" type="image/svg+xml" href="assets/favicon.svg"></head>')
write('index.html',home)
# Sitemap uses only actual publication/update dates, never the build date.
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9');ET.register_namespace('image','http://www.google.com/schemas/sitemap-image/1.1')
ns='http://www.sitemaps.org/schemas/sitemap/0.9';ins='http://www.google.com/schemas/sitemap-image/1.1';sm=ET.Element('{'+ns+'}urlset')
paths=['','categories/']+[p['slug']+'/' for p in posts]+['category/'+cat_slug(c)+'/' for c in categories]+['about.html','contact.html','editorial-policy.html','privacy.html','affiliate-disclosure.html']
for path in paths:
 u=ET.SubElement(sm,'{'+ns+'}url');ET.SubElement(u,'{'+ns+'}loc').text=BASE+path
 p=next((p for p in posts if path==p['slug']+'/'),None)
 if p:
  ET.SubElement(u,'{'+ns+'}lastmod').text=p['dateModified']
  for src in dict.fromkeys([p['cover']]+[s['image'] for s in p['sections'] if s.get('image')]):
   image=ET.SubElement(u,'{'+ins+'}image');ET.SubElement(image,'{'+ins+'}loc').text=absurl(src)
ET.ElementTree(sm).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
rss=ET.Element('rss',version='2.0');channel=ET.SubElement(rss,'channel')
for tag,value in [('title','Trendora'),('link',BASE),('description','Practical lifestyle guides and original visual inspiration'),('language','en')]:ET.SubElement(channel,tag).text=value
for p in posts:
 item=ET.SubElement(channel,'item')
 for tag,value in [('title',p['title']),('link',BASE+p['slug']+'/'),('guid',BASE+p['slug']+'/'),('description',p['excerpt']),('pubDate',format_datetime(datetime.fromisoformat(p['datePublished']).replace(tzinfo=timezone.utc)))]:ET.SubElement(item,tag).text=value
ET.ElementTree(rss).write(ROOT/'feed.xml',encoding='utf-8',xml_declaration=True)
write('llms.txt','# Trendora\n\nPractical lifestyle guides. AI-generated illustration use is disclosed on applicable pages.\n\n## Guides\n'+''.join('- ['+p['title']+']('+BASE+p['slug']+'/): '+p['excerpt']+'\n' for p in posts)+'\n## Editorial standards\n- [Editorial policy]('+BASE+'editorial-policy.html)\n')
print(f'Built {len(posts)} articles, {len(categories)} categories, sitemap and RSS feed.')
