"""Create distinct photo-based WebP visuals for pro-v2 editorial guides."""
import json,hashlib,random
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
POSTS=json.loads((ROOT/'data/posts.json').read_text(encoding='utf-8'))
DIMS=json.loads((ROOT/'data/image-dimensions.json').read_text(encoding='utf-8'))
OUT=ROOT/'assets/generated';OUT.mkdir(parents=True,exist_ok=True)
TARGETS={p['slug'] for p in POSTS if p.get('qualityStandard')=='pro-v2'}

PATTERNS={
'nails':['milky-lilac-nails-*.webp','rhinestone-nail-ideas-*.webp','plaid-nail-designs-autumn-*.webp','brown-french-tip-nail-ideas-*.webp','deer-print-nail-ideas-*.webp','minimal-halloween-nail-ideas-*.webp','short-fall-nail-colors*.webp','olive-gold-nails.webp','cherry-jam-nails.webp'],
'hair':['90s-hair-accessory-looks-*.webp','feminine-pixie-cut-ideas-*.webp','crochet-parandi-hair-accessory*.webp'],
'fragrance':['perfume-layering-ideas-*.webp','perfume-discovery-set-guide-*.webp','small-fragrance-wardrobe-guide-*.webp','fragrance-notes-testing-journal-*.webp'],
'room':['warm-*.webp','cozy-fall-balcony-ideas-small-spaces-*.webp','trinket-shelf-styling-ideas*.webp','gaming-room-*.webp','small-gaming-room-setup-ideas*.webp'],
'wallpaper':['warm-*.webp','cozy-fall-balcony-ideas-small-spaces-*.webp','trinket-shelf-styling-ideas*.webp','gaming-room-*.webp','small-gaming-room-setup-ideas*.webp'],
'food':['apple-cinnamon-desserts-fall-*.webp','slow-cooker-fall-dinner-ideas-*.webp','burger-bowl-recipes*.webp','ground-beef-stuffed-peppers*.webp']
}
PRIORITY={
'pumpkin-chrome-nail-ideas-october-2026':['brown-french-tip-nail-ideas-*.webp','olive-gold-nails.webp','plaid-nail-designs-autumn-*.webp','minimal-halloween-nail-ideas-*.webp','rhinestone-nail-ideas-*.webp'],
'dark-red-cat-eye-nail-ideas-fall-2026':['cherry-jam-nails.webp','milky-lilac-nails-*.webp','rhinestone-nail-ideas-*.webp','plaid-nail-designs-autumn-*.webp'],
'tortoiseshell-french-tip-nail-ideas-fall':['deer-print-nail-ideas-*.webp','brown-french-tip-nail-ideas-*.webp','plaid-nail-designs-autumn-*.webp','olive-gold-nails.webp','rhinestone-nail-ideas-*.webp'],
'cherry-mocha-plum-nail-ideas-fall':['cherry-jam-nails.webp','milky-lilac-nails-*.webp','plaid-nail-designs-autumn-*.webp','rhinestone-nail-ideas-*.webp'],
'cherry-cola-hair-color-ideas-fall':['90s-hair-accessory-looks-*.webp','feminine-pixie-cut-ideas-*.webp','crochet-parandi-hair-accessory*.webp'],
'textured-french-bob-ideas-fall':['90s-hair-accessory-looks-*.webp','feminine-pixie-cut-ideas-*.webp','crochet-parandi-hair-accessory*.webp']
}

def seed(slug,i):return int(hashlib.sha256(f'{slug}:{i}'.encode()).hexdigest()[:16],16)
def rgb(h):h=h.lstrip('#');return tuple(int(h[i:i+2],16) for i in (0,2,4))
def hsv_of(c):return Image.new('RGB',(1,1),c).convert('HSV').getpixel((0,0))
def pool(style,slug):
 pats=PRIORITY.get(slug,PATTERNS.get(style,PATTERNS['room']));out=[]
 for pat in pats:
  for f in sorted(OUT.glob(pat)):
   if f.suffix.lower()=='.webp' and not any(f.name.startswith(t+'-') for t in TARGETS) and f not in out:out.append(f)
 if not out:out=[f for f in sorted(OUT.glob('*.webp')) if not any(f.name.startswith(t+'-') for t in TARGETS)]
 return out

def fit(im,size,i):
 im=im.convert('RGB');W,H=size;sw,sh=im.size
 scale=max(W/sw,H/sh);nw,nh=max(W,int(sw*scale)),max(H,int(sh*scale))
 im=im.resize((nw,nh),Image.Resampling.LANCZOS);dx,dy=max(0,nw-W),max(0,nh-H)
 x=int(dx*((i*37)%101)/100) if dx else 0;y=int(dy*((i*53)%101)/100) if dy else 0
 if i%4==3:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT);x=max(0,dx-x)
 return im.crop((x,y,x+W,y+H))

def natural_grade(im,palette,style,i):
 if style in ('nails','hair'):return ImageEnhance.Sharpness(ImageEnhance.Contrast(im).enhance(1.03)).enhance(1.08)
 target=rgb(palette[i%len(palette)]);wash=Image.new('RGB',im.size,target)
 alpha=.035 if style=='food' else .07
 im=Image.blend(im,wash,alpha)
 im=ImageEnhance.Contrast(im).enhance(1.04);im=ImageEnhance.Color(im).enhance(1.06)
 return ImageEnhance.Sharpness(im).enhance(1.08)

def recolor_nails(im,slug,palette,i):
 if 'tortoiseshell' in slug:return im
 hsv=np.array(im.convert('HSV'),dtype=np.uint8);h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
 # Most source manicures use cool/lilac polish. Excluding warm skin tones protects fingers.
 mask=((h>120)&(h<245)&(s>14)&(v>65))
 if mask.mean()<.01:return im
 target=rgb(palette[i%len(palette)]);th,ts,tv=hsv_of(target)
 nh=hsv.copy();nh[...,0]=th;nh[...,1]=np.maximum(s,np.uint8(max(90,ts)));nh[...,2]=np.clip(v.astype(np.int16)*.82+20,0,255).astype(np.uint8)
 recol=np.array(Image.fromarray(nh,'HSV').convert('RGB'),dtype=np.float32);orig=np.array(im,dtype=np.float32)
 m=Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.GaussianBlur(2))
 ma=np.array(m,dtype=np.float32)/255.0*.82
 out=orig*(1-ma[...,None])+recol*ma[...,None]
 base=Image.fromarray(np.clip(out,0,255).astype('uint8'))
 if 'cat-eye' in slug:
  # Reflective streaks are clipped to the detected polish mask.
  lay=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(lay,'RGBA');W,H=im.size
  for k in range(5):
   x=int(W*(.18+k*.16));d.line((x-45,int(H*.72),x+85,int(H*.18)),fill=(255,225,230,110),width=7)
  streak=np.array(lay)[...,3].astype(np.float32)/255.0
  clipped=np.minimum(streak,np.array(m,dtype=np.float32)/255.0)
  white=np.full_like(orig,255)
  b=np.array(base,dtype=np.float32);out=b*(1-clipped[...,None]*.32)+white*(clipped[...,None]*.32)
  base=Image.fromarray(np.clip(out,0,255).astype('uint8'))
 return base

def recolor_hair(im,slug,palette,i):
 if 'cherry-cola' not in slug:return im
 hsv=np.array(im.convert('HSV'),dtype=np.uint8);h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
 mask=(v<165)&(s>24)&((h<48)|(h>228))
 target=rgb(palette[i%len(palette)]);th,ts,tv=hsv_of(target)
 nh=hsv.copy();nh[...,0]=th;nh[...,1]=np.maximum(s,np.uint8(max(80,ts)));nh[...,2]=np.clip(v.astype(np.int16)+4,0,255).astype(np.uint8)
 recol=np.array(Image.fromarray(nh,'HSV').convert('RGB'),dtype=np.float32);orig=np.array(im,dtype=np.float32)
 m=Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.GaussianBlur(3));ma=np.array(m,dtype=np.float32)/255.0*.68
 out=orig*(1-ma[...,None])+recol*ma[...,None]
 return Image.fromarray(np.clip(out,0,255).astype('uint8'))

def botanical(im,palette,i):
 lay=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(lay,'RGBA');W,H=im.size;pal=[rgb(x) for x in palette]
 for y in range(55,int(H*.55),105):
  for x in range(45,W,120):
   c=pal[(x//120+y//105+i)%len(pal)];d.ellipse((x-30,y-10,x+30,y+10),fill=c+(18,));d.line((x-26,y+20,x+26,y-20),fill=(70,55,42,20),width=3)
 return Image.alpha_composite(im.convert('RGBA'),lay).convert('RGB')

def render(p,i,path):
 style=p.get('visualStyle','room');pal=p.get('visualPalette') or ['#7C9C82','#0F2B25','#F1E6D8','#A8CBB6','#FDFBF6'];srcs=pool(style,p['slug'])
 src=srcs[i%len(srcs)];im=fit(Image.open(src),(1024,768),i);im=natural_grade(im,pal,style,i)
 if style=='nails':im=recolor_nails(im,p['slug'],pal,i)
 if style=='hair':im=recolor_hair(im,p['slug'],pal,i)
 if style=='wallpaper':im=botanical(im,pal,i)
 im.save(ROOT/path,'WEBP',quality=89,method=4);DIMS[path]=[1024,768]

count=0
for p in POSTS:
 if p.get('qualityStandard')!='pro-v2':continue
 render(p,0,p['cover']);count+=1
 for i,s in enumerate(p.get('sections',[]),1):
  if s.get('image'):render(p,i,s['image']);count+=1
(ROOT/'data/image-dimensions.json').write_text(json.dumps(DIMS,indent=2)+'\n',encoding='utf-8')
print(f'Generated {count} distinct photo-based WebP editorial images.')
