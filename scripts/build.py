"""Rebuild crawlable InspoMint pages using the checked-in editorial source."""
import json,re,html,xml.etree.ElementTree as ET
from home_design import render_home, pin_link, pin_url
from pathlib import Path
from site_config import ROOT, BASE
from datetime import datetime,timezone
from email.utils import format_datetime
posts=[p for p in json.loads((ROOT/'data/posts.json').read_text()) if p.get('status')=='published']
e=lambda x:html.escape(str(x),quote=True)
absurl=lambda x:x if x.startswith('https://') else BASE+x
cat_slug=lambda x:re.sub(r'[^a-z0-9]+','-',x.lower()).strip('-')

def _svg_text(x):
 return html.escape(str(x or ''),quote=True)

def _editorial_svg(p,section,index):
 colors=(p.get('visualPalette') or ['#7C9C82','#0F2B25','#F1E6D8','#A8CBB6','#FDFBF6'])
 while len(colors)<5: colors=colors+colors
 c1,c2,c3,c4,c5=colors[:5]
 title=_svg_text(section.get('heading','Idea'))
 cat=_svg_text(p.get('category','InspoMint'))
 style=p.get('visualStyle','editorial')
 common=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800"><rect width="1200" height="800" fill="#FDFBF6"/><circle cx="1080" cy="90" r="170" fill="{c3}" opacity=".35"/><circle cx="120" cy="720" r="180" fill="{c4}" opacity=".28"/><text x="70" y="72" font-family="Arial,sans-serif" font-size="22" font-weight="700" letter-spacing="3" fill="#6F9178">{cat.upper()}</text>'''
 if style=='nails':
  art=f'''<g transform="translate(150 150)"><rect x="0" y="80" width="150" height="390" rx="74" fill="{c1}"/><rect x="185" y="20" width="150" height="450" rx="74" fill="{c2}"/><rect x="370" y="55" width="150" height="415" rx="74" fill="{c3}"/><rect x="555" y="10" width="150" height="460" rx="74" fill="{c4}"/><rect x="740" y="90" width="150" height="380" rx="74" fill="{c5}"/><path d="M35 135 C70 105 110 105 135 145" stroke="white" stroke-width="16" opacity=".68" fill="none"/><path d="M220 85 C250 55 295 55 320 95" stroke="white" stroke-width="16" opacity=".58" fill="none"/><path d="M405 115 C440 85 480 85 505 125" stroke="white" stroke-width="16" opacity=".55" fill="none"/><path d="M590 75 C625 45 665 45 690 85" stroke="white" stroke-width="16" opacity=".6" fill="none"/></g>'''
 elif style=='hair':
  art=f'''<g transform="translate(250 125)"><circle cx="350" cy="260" r="190" fill="#E8D2C3"/><path d="M165 290 C120 80 260 15 385 35 C550 55 590 180 525 395 C475 305 450 190 335 165 C275 150 220 205 165 290Z" fill="{c1}"/><path d="M190 320 C245 235 315 205 385 220 C440 230 485 285 515 370" stroke="{c2}" stroke-width="44" fill="none" stroke-linecap="round"/><path d="M235 365 C300 325 385 330 455 390" stroke="{c3}" stroke-width="28" fill="none" stroke-linecap="round"/><circle cx="300" cy="280" r="8" fill="#5A4038"/><circle cx="408" cy="280" r="8" fill="#5A4038"/></g>'''
 elif style=='fragrance':
  art=f'''<g transform="translate(185 155)"><rect x="40" y="140" width="230" height="330" rx="34" fill="{c1}" opacity=".88"/><rect x="100" y="80" width="110" height="80" rx="18" fill="{c2}"/><rect x="330" y="80" width="260" height="390" rx="42" fill="{c3}" opacity=".9"/><rect x="405" y="20" width="110" height="85" rx="16" fill="{c4}"/><rect x="650" y="160" width="210" height="310" rx="30" fill="{c2}" opacity=".82"/><rect x="705" y="110" width="100" height="65" rx="14" fill="{c1}"/><path d="M75 205 L235 205" stroke="white" stroke-width="6" opacity=".7"/><path d="M375 160 L545 160" stroke="white" stroke-width="6" opacity=".7"/></g>'''
 elif style=='room':
  art=f'''<g transform="translate(105 125)"><rect x="0" y="0" width="990" height="500" rx="28" fill="{c5}"/><rect x="0" y="0" width="990" height="315" rx="28" fill="{c4}" opacity=".6"/><rect x="165" y="245" width="520" height="190" rx="48" fill="{c1}"/><rect x="220" y="200" width="180" height="100" rx="32" fill="{c3}"/><rect x="445" y="205" width="175" height="95" rx="32" fill="{c2}"/><rect x="740" y="195" width="110" height="240" rx="20" fill="{c2}"/><circle cx="795" cy="145" r="72" fill="#F4E6B5"/><rect x="80" y="400" width="820" height="70" rx="35" fill="#D9C7AD" opacity=".8"/></g>'''
 elif style=='wallpaper':
  leaves=''.join(f'<g transform="translate({120+(i%5)*205} {145+(i//5)*150}) rotate({-25+(i%4)*18})"><ellipse cx="0" cy="0" rx="56" ry="24" fill="{[c1,c2,c3,c4][i%4]}" opacity=".85"/><path d="M-60 0 L65 0" stroke="#6B5A48" stroke-width="5" opacity=".45"/></g>' for i in range(15))
  art=f'''<rect x="80" y="115" width="1040" height="510" rx="30" fill="{c5}" stroke="#E5DDD2" stroke-width="3"/>{leaves}<rect x="120" y="530" width="420" height="70" rx="35" fill="#FDFBF6" opacity=".86"/>'''
 elif style=='food':
  art=f'''<g transform="translate(195 120)"><circle cx="405" cy="275" r="245" fill="{c3}"/><circle cx="405" cy="275" r="185" fill="#FFF9EE"/><circle cx="355" cy="245" r="70" fill="{c1}"/><circle cx="465" cy="210" r="58" fill="{c2}"/><circle cx="475" cy="335" r="75" fill="{c4}"/><path d="M70 60 L170 480" stroke="{c2}" stroke-width="24" stroke-linecap="round"/><path d="M735 70 L660 485" stroke="{c1}" stroke-width="24" stroke-linecap="round"/></g>'''
 else:
  art=f'''<rect x="115" y="145" width="970" height="450" rx="36" fill="{c3}"/><circle cx="400" cy="365" r="150" fill="{c1}"/><circle cx="700" cy="325" r="120" fill="{c2}" opacity=".8"/>'''
 return common+art+f'''<rect x="70" y="645" width="1060" height="105" rx="28" fill="#FFFFFF" opacity=".94"/><text x="105" y="690" font-family="Georgia,serif" font-size="34" font-weight="700" fill="#0F2B25">{title[:56]}</text><text x="105" y="725" font-family="Arial,sans-serif" font-size="18" fill="#6C756F">InspoMint · Fresh ideas worth saving · {index:02d}</text></svg>'''

for _p in posts:
 if _p.get('qualityStandard')=='pro-v2':
  for _i,_s in enumerate(_p.get('sections',[]),1):
   _src=_s.get('image','')
   if _src.endswith('.svg'):
    _f=ROOT/_src
    _f.parent.mkdir(parents=True,exist_ok=True)
    _f.write_text(_editorial_svg(_p,_s,_i),encoding='utf-8')

image_dimensions=json.loads((ROOT/'data/image-dimensions.json').read_text())
categories=list(json.loads((ROOT/'data/category-covers.json').read_text()))
def js(x):return json.dumps(x,ensure_ascii=False).replace('<','\\u003c')
def schema(x):return '<script type="application/ld+json">'+js(x)+'</script>'
def head(title,description,path,image=None,schemas=[]):
 url=BASE+path
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(title)+' — InspoMint</title><meta name="description" content="'+e(description)+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+url+'"><link rel="alternate" type="application/rss+xml" title="InspoMint RSS" href="'+BASE+'feed.xml"><meta property="og:type" content="'+('article' if any(path==p['slug']+'/' for p in posts) else 'website')+'"><meta property="og:title" content="'+e(title)+'"><meta property="og:description" content="'+e(description)+'"><meta property="og:url" content="'+url+'"><meta property="og:site_name" content="InspoMint"><meta name="twitter:card" content="summary_large_image">'+ ('<meta property="og:image" content="'+e(absurl(image))+'"><meta name="twitter:image" content="'+e(absurl(image))+'">' if image else '')+'<meta name="twitter:title" content="'+e(title)+'"><meta name="twitter:description" content="'+e(description)+'"><meta name="theme-color" content="#7C9C82"><link rel="icon" type="image/svg+xml" href="'+BASE+'assets/inspomint-mark.svg?v=20261006"><link rel="icon" type="image/png" sizes="32x32" href="'+BASE+'assets/favicon-32x32.png?v=20261006"><link rel="apple-touch-icon" sizes="180x180" href="'+BASE+'assets/apple-touch-icon.png?v=20261006"><link rel="manifest" href="'+BASE+'site.webmanifest"><link rel="stylesheet" href="'+BASE+'assets/style.css?v=20261004-complete">'+''.join(schema(s) for s in schemas)+'</head>'
def nav():return '<header class="topbar"><div class="shell nav"><a class="brand" href="'+BASE+'"><img src="'+BASE+'assets/inspomint-mark.svg" alt="" aria-hidden="true"><b>InspoMint</b></a><div></div><nav><a href="'+BASE+'#fresh">Ideas</a><a href="'+BASE+'categories/">Categories</a><a href="'+BASE+'about.html">About</a></nav></div></header>'
def footer():return '<footer><div class="shell footGrid"><div><a class="brand" href="'+BASE+'"><img src="'+BASE+'assets/inspomint-mark.svg" alt="" aria-hidden="true"><b>InspoMint</b></a><p>Beautiful ideas for everyday living.</p></div><div><b>Explore</b>'+''.join('<a href="'+BASE+'category/'+cat_slug(c)+'/">'+e(c)+'</a>' for c in categories)+'</div><div><b>Trust & Legal</b>'+''.join('<a href="'+BASE+f+'.html">'+t+'</a>' for f,t in [('editorial-policy','Editorial Policy'),('about','About'),('privacy','Privacy'),('affiliate-disclosure','Affiliate Disclosure'),('contact','Contact')])+'<a href="'+BASE+'pinterest/">Pinterest images</a><a href="'+BASE+'fall-ideas/">The fall edit</a></div></div><div class="shell copyright">© 2026 InspoMint</div></footer>'
def img(src,alt,lead=False):
 # Use intrinsic dimensions to reserve space before images load.
 size=image_dimensions.get(src)
 dimensions=(' width="'+str(size[0])+'" height="'+str(size[1])+'"') if size else ''
 return '<img src="'+e(absurl(src))+'" alt="'+e(alt)+'" decoding="async"'+dimensions+(' fetchpriority="high"' if lead else ' loading="lazy"')+'>'
def cards(items):return ''.join('<article class="ideaCardWrap" data-cat="'+e(p['category'])+'" data-title="'+e(p['title'].lower())+'"><a class="ideaCard" href="'+BASE+p['slug']+'/">'+img(p['cover'],p['coverAlt'])+'<div class="cardText"><small>'+e(p['category'])+'</small><h3>'+e(p['title'])+'</h3><span>Read ideas</span></div></a>'+ (pin_link(p) if not p['slug'].startswith('category/') else '')+'</article>' for p in items)
def write(path,text):
 f=ROOT/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text,encoding='utf-8')
for p in posts:
 path=p['slug']+'/'
 catpath='category/'+cat_slug(p['category'])+'/'
 faq=p.get('faq',[])
 article={'@context':'https://schema.org','@type':'BlogPosting','@id':BASE+path+'#article','headline':p['title'],'description':p['excerpt'],'image':[absurl(p['cover'])],'mainEntityOfPage':BASE+path,'datePublished':p['datePublished'],'dateModified':p['dateModified'],'author':{'@type':'Organization','name':'InspoMint Editorial','url':BASE+'about.html'},'publisher':{'@type':'Organization','name':'InspoMint','url':BASE},'inLanguage':'en','articleSection':p['category']}
 article['image']=[({'@type':'ImageObject','url':absurl(src),'width':image_dimensions[src][0],'height':image_dimensions[src][1]} if src in image_dimensions else {'@type':'ImageObject','url':absurl(src)}) for src in dict.fromkeys([p['cover']]+[s['image'] for s in p['sections'] if s.get('image')])]
 article['wordCount']=len(re.findall(r'\S+',' '.join(p.get('intro',[])+[t for s in p['sections'] for t in s.get('paragraphs',[])])))
 breadcrumb={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':BASE},{'@type':'ListItem','position':2,'name':p['category'],'item':BASE+catpath},{'@type':'ListItem','position':3,'name':p['title'],'item':BASE+path}]}
 schemas=[article,breadcrumb]
 if p.get('qualityStandard')=='pro-v2':
  schemas.append({'@context':'https://schema.org','@type':'ItemList','name':p['title'],'numberOfItems':len(p['sections']),'itemListElement':[{'@type':'ListItem','position':i+1,'name':s['heading'],'url':BASE+path+'#idea-'+str(i+1)} for i,s in enumerate(p['sections'])]})
 if faq:schemas.append({'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q['q'],'acceptedAnswer':{'@type':'Answer','text':q['a']}} for q in faq]})
 related=sorted([x for x in posts if x['slug']!=p['slug']],key=lambda x:x['category']!=p['category'])[:3]
 if p.get('relatedSlugs'):related=[next(x for x in posts if x['slug']==slug) for slug in p['relatedSlugs']]
 body=head(p['title'],p['excerpt'],path,p['cover'],schemas).replace('</head>','<meta property="article:published_time" content="'+e(p['datePublished'])+'"><meta property="article:modified_time" content="'+e(p['dateModified'])+'"><meta property="og:image:alt" content="'+e(p['coverAlt'])+'"></head>')+'<body>'+nav()+'<main id="main"><section class="articleHero shell"><div class="crumb"><a href="'+BASE+'">Home</a> / <a href="'+BASE+catpath+'">'+e(p['category'])+'</a></div><h1>'+e(p['title'])+'</h1><p class="articleDek">'+e(p['excerpt'])+'</p><div class="meta">By <a href="'+BASE+'about.html">InspoMint Editorial</a> · <time datetime="'+e(p['dateModified'])+'">Updated '+e(p['dateModified'])+'</time> · '+str(p.get('readMinutes',6))+' min read</div></section><section class="shell articleLayout"><article class="articleMain"><div class="articleCoverWrap">'+img(p['cover'],p['coverAlt'],True)+'<button id="articlePin" class="articlePin" type="button">Save to Pinterest</button></div>'
 body+=''.join('<p>'+e(t)+'</p>' for t in p.get('intro',[]))
 body+='<nav class="contents" aria-label="In this guide"><h2>In this guide</h2><ol>'+''.join('<li><a href="#idea-'+str(i+1)+'">'+e(s['heading'])+'</a></li>' for i,s in enumerate(p['sections']))+'</ol></nav>'
 for i,s in enumerate(p['sections']):
  body+='<section class="longSection" id="idea-'+str(i+1)+'"><h2>'+e(s['heading'])+'</h2>'+''.join('<p>'+e(t)+'</p>' for t in s.get('paragraphs',[]))
  if s.get('image'):
   cap=s.get('caption','')
   if re.search(r'AI[- ]generated|artificial intelligence|editorial visual|styling illustration',cap,re.I):cap=s['heading']+' — '+p['category']+' inspiration.'
   body+='<figure class="articleFigure">'+img(s['image'],s.get('alt',s['heading']))+'<figcaption>'+e(cap)+' <a class="figurePin" href="'+e(pin_url(p,s['image'],s['heading']+'. '+p['excerpt']))+'" target="_blank" rel="noopener noreferrer" aria-label="Save '+e(s['heading'])+' to Pinterest">Save this idea to Pinterest ↗</a></figcaption></figure>'
  body+='</section>'
 if faq:body+='<section class="longSection"><h2>Frequently asked questions</h2>'+''.join('<h3>'+e(q['q'])+'</h3><p>'+e(q['a'])+'</p>' for q in faq)+'</section>'
 body+='</article><aside class="articleAside"><div class="sideCard"><h3>More to explore</h3><div class="sideLinks">'+''.join('<a href="'+BASE+x['slug']+'/">'+e(x['title'])+'</a>' for x in related)+'<a href="'+BASE+catpath+'">All '+e(p['category'])+' guides</a></div></div></aside></section><section class="section shell"><h2>You may also like</h2><div class="ideaGrid">'+cards(related)+'</div></section></main>'+footer()
 body=body.replace('<button id="articlePin" class="articlePin" type="button">Save to Pinterest</button>','<a class="articlePin" href="'+e(pin_url(p))+'" target="_blank" rel="noopener noreferrer">Save to Pinterest</a>')
 body+='</body></html>'
 write(path+'index.html',body)
for c in categories:
 items=[p for p in posts if p['category']==c];path='category/'+cat_slug(c)+'/'
 desc='Explore '+c.lower()+' ideas, visual references and practical guides from InspoMint.'
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
home=home.replace('</head>','<meta property="og:image" content="'+absurl(posts[0]['cover'])+'"><meta name="twitter:image" content="'+absurl(posts[0]['cover'])+'"><meta name="twitter:card" content="summary_large_image">'+schema({'@context':'https://schema.org','@type':'WebSite','name':'InspoMint','url':BASE})+schema({'@context':'https://schema.org','@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'name':p['title'],'url':BASE+p['slug']+'/'} for i,p in enumerate(posts)]})+'</head>')
home=render_home(home,posts,home.split('</head>')[0].replace('20261004-folvella','20261004-complete').replace('20261004-discovery','20261004-complete')+'</head>',footer,img,cards)
write('index.html',home)
# Sitemap uses only actual publication/update dates, never the build date.
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9');ET.register_namespace('image','http://www.google.com/schemas/sitemap-image/1.1')
ns='http://www.sitemaps.org/schemas/sitemap/0.9';ins='http://www.google.com/schemas/sitemap-image/1.1';sm=ET.Element('{'+ns+'}urlset')
paths=['','categories/','fall-ideas/']+[p['slug']+'/' for p in posts]+['category/'+cat_slug(c)+'/' for c in categories]+['about.html','contact.html','editorial-policy.html','privacy.html','affiliate-disclosure.html']
for path in paths:
 u=ET.SubElement(sm,'{'+ns+'}url');ET.SubElement(u,'{'+ns+'}loc').text=BASE+path
 p=next((p for p in posts if path==p['slug']+'/'),None)
 if p:
  ET.SubElement(u,'{'+ns+'}lastmod').text=p['dateModified']
  for src in dict.fromkeys([p['cover']]+[s['image'] for s in p['sections'] if s.get('image')]):
   image=ET.SubElement(u,'{'+ins+'}image');ET.SubElement(image,'{'+ins+'}loc').text=absurl(src)
ET.ElementTree(sm).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
rss=ET.Element('rss',version='2.0');channel=ET.SubElement(rss,'channel')
for tag,value in [('title','InspoMint'),('link',BASE),('description','Practical lifestyle guides and original visual inspiration'),('language','en')]:ET.SubElement(channel,tag).text=value
for p in posts:
 item=ET.SubElement(channel,'item')
 for tag,value in [('title',p['title']),('link',BASE+p['slug']+'/'),('guid',BASE+p['slug']+'/'),('description',p['excerpt']),('pubDate',format_datetime(datetime.fromisoformat(p['datePublished']).replace(tzinfo=timezone.utc)))]:ET.SubElement(item,tag).text=value
ET.ElementTree(rss).write(ROOT/'feed.xml',encoding='utf-8',xml_declaration=True)
write('llms.txt','# InspoMint\n\nPractical lifestyle guides with original visual references and structured editorial content.\n\n## Guides\n'+''.join('- ['+p['title']+']('+BASE+p['slug']+'/): '+p['excerpt']+'\n' for p in posts)+'\n## Editorial standards\n- [Editorial policy]('+BASE+'editorial-policy.html)\n')
print(f'Built {len(posts)} articles, {len(categories)} categories, sitemap and RSS feed.')

# A crawlable seasonal collection links to existing original guides.
clusters=[
 ('New for October','Fresh Halloween details and small autumn rituals.',['minimal-halloween-nail-ideas','no-carve-pumpkin-decorating-ideas','cozy-fall-balcony-ideas-small-spaces','easy-halloween-party-snacks','brown-french-tip-nail-ideas','thrifted-halloween-table-decor-ideas','apple-cinnamon-desserts-fall','plaid-nail-designs-autumn']),
 ('Warm corners','Small changes that make home feel more inviting.',['warm-lighting-burrowcore-ideas','trinket-shelf-styling-ideas','kitchen-witch-herbal-apothecary']),
 ('Your home café','A house special, a cozy corner and something sweet.',['coffee-station-party-ideas','banana-syrup-for-coffee','blueberry-latte-recipe','biscoff-latte-recipe','marshmallow-cold-foam','carrot-cake-latte']),
 ('Make something small','Tactile projects to enjoy a little at a time.',['crochet-parandi-hair-accessory','ribbon-rosette-diy','clay-bag-charms-diy','beaded-bag-charms-diy','sashiko-denim-mending','pressed-flower-frame-diy']),
 ('Little beauty details','Soft color, sparkle and nostalgic finishing touches.',['short-fall-nail-colors','milky-lilac-nails','rhinestone-nail-ideas','90s-hair-accessory-looks']),
 ('Fall dressing & Halloween','Easy layers and playful seasonal ideas.',['barn-jacket-outfits-women','easy-halloween-costume-ideas','fawn-halloween-makeup-outfit-ideas']),
 ('Comfort at the table','Recipes and dinner inspiration for slower evenings.',['slow-cooker-fall-dinner-ideas','ground-beef-stuffed-peppers','burger-bowl-recipes'])]
selected=[next(p for p in posts if p['slug']==s) for _,_,ss in clusters for s in ss]
path='fall-ideas/'
collection={'@context':'https://schema.org','@type':'CollectionPage','name':'The Fall Edit','url':BASE+path,'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'name':p['title'],'url':BASE+p['slug']+'/'} for i,p in enumerate(selected)]}}
body=head('The Fall Edit: Cozy Home, Coffee, Crafts & Style','Explore original fall inspiration: warm corners, home café drinks, handmade crafts, nail ideas and easy seasonal outfits.',path,selected[0]['cover'],[collection])+'<body>'+nav()+'<main class="shell section" id="main"><p class="introKicker">THE OCTOBER EDIT</p><h1 class="seasonTitle">Make room for a slower season.</h1><p class="articleDek">Original ideas to make, wear, try and share. Start with whatever feels like you.</p><nav class="seasonJump" aria-label="Fall collections">'+''.join('<a href="#'+cat_slug(title)+'">'+e(title)+'</a>' for title,_,_ in clusters)+'</nav>'
for title,description,ss in clusters:
 items=[next(p for p in posts if p['slug']==s) for s in ss]
 body+='<section class="seasonGroup" id="'+cat_slug(title)+'"><div class="sectionHead"><div><h2>'+e(title)+'</h2><p>'+e(description)+'</p></div></div><div class="ideaGrid">'+cards(items)+'</div></section>'
write(path+'index.html',body+'</main>'+footer()+'</body></html>')
