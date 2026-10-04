"""Integrate the original October expansion without replacing earlier guides."""
import json,math,re,hashlib,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def save(path,data): (ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main(paths):
 old=json.loads((ROOT/'data/posts.json').read_text())
 new=json.loads((ROOT/'data/new-posts-october-expansion.json').read_text())
 newslugs={p['slug'] for p in new}
 old=[p for p in old if p['slug'] not in newslugs]
 categories=list(dict.fromkeys(p['category'] for p in old))
 save('data/category-covers.json',{c:next(p['cover'] for p in old if p['category']==c) for c in categories})
 dims=json.loads((ROOT/'data/image-dimensions.json').read_text())
 alts={
 'habit':'Minimal notebook habit tracker with small grids on a cream writing desk',
 'cyberdeck':'Retro portable cyberdeck concept with a compact screen and mechanical keyboard',
 'ceramic':'Handmade ceramic serving platter with softly irregular glazed edges',
 'military':'Fall outfit with an olive military jacket and neutral separates',
 'blind':'Handmade folded paper surprise bags arranged with small paper gifts',
 'book':'Reading journal with book log layouts and a book on a writing desk',
 'goth':'Dark sculptural pottery displayed on a quiet dramatic shelf',
 'trash':'Small handmade furniture made from clean recycled packaging',
 'pleated':'Fall outfit with a flowing pleated skirt and warm layered clothing',
 'miniroom':'Handmade cardboard miniature room with a sofa and paper furnishings',
 'watercolor':'Small watercolor studies of fruit, leaves and landscapes on a painting table',
 'tunnel':'Layered paper woodland tunnel with folded supports and an open central view',
 'korean':'Ground beef rice bowl with cucumber, scallions and sesame seeds',
 'deer':'Cream and caramel manicure with pale fawn spots on brown accent nails',
 'cups':'Rhinestone celestial pattern on a removable exterior tumbler sleeve'}
 images=[]
 for p in new:
  key=p.pop('assetKey');target=ROOT/p['cover']
  with Image.open(paths[key]) as im: im.save(target,'WEBP',quality=85,method=6);dims[p['cover']]=list(im.size)
  p['coverAlt']=alts[key]
  words=' '.join(p['intro']+[x for s in p['sections'] for x in s['paragraphs']]+[f['a'] for f in p['faq']])
  p['readMinutes']=max(2,math.ceil(len(re.findall(r'\S+',words))/200))
  candidates=[q for q in new+old if q['slug']!=p['slug'] and q['category']==p['category']]
  p['relatedSlugs']=[q['slug'] for q in candidates[:3]]
  images.append(dict(path=p['cover'],sha256=hashlib.sha256(target.read_bytes()).hexdigest(),width=dims[p['cover']][0],height=dims[p['cover']][1],bytes=target.stat().st_size,slug=p['slug'],type='cover',original=True))
 save('data/posts.json',new+old)
 save('data/image-dimensions.json',dims)
 save('data/asset-batch-october-expansion-2026-10-04.json',dict(date='2026-10-04',imageCount=len(images),images=images))
 print(f'Integrated {len(new)} new guides and {len(images)} original images; {len(new)+len(old)} articles total.')
if __name__=='__main__': main(json.load(sys.stdin))
