"""Create section-aware WebP visuals for pro-v2 editorial guides."""
import json,hashlib,random,re,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
POSTS=json.loads((ROOT/'data/posts.json').read_text(encoding='utf-8'))
DIMS=json.loads((ROOT/'data/image-dimensions.json').read_text(encoding='utf-8'))
OUT=ROOT/'assets/generated';OUT.mkdir(parents=True,exist_ok=True)
TARGETS={p['slug'] for p in POSTS if p.get('qualityStandard')=='pro-v2'}

BASE_PATTERNS={
'nails':['brown-french-tip-nail-ideas-*.webp','milky-lilac-nails-*.webp','rhinestone-nail-ideas-*.webp','plaid-nail-designs-autumn-*.webp','deer-print-nail-ideas-*.webp','minimal-halloween-nail-ideas-*.webp','short-fall-nail-colors*.webp','olive-gold-nails.webp','cherry-jam-nails.webp','chocolate-short-nails.webp'],
'hair':['90s-hair-accessory-looks-*.webp','feminine-pixie-cut-ideas-*.webp','korean-two-block-haircut-guide-*.webp','crochet-parandi-hair-accessory*.webp'],
'fragrance':['perfume-layering-ideas-*.webp','perfume-discovery-set-guide-*.webp','small-fragrance-wardrobe-guide-*.webp','fragrance-notes-testing-journal-*.webp'],
'room':['warm-reading-corner.webp','warm-bedroom-lighting.webp','warm-kitchen-nook.webp','cozy-fall-balcony-ideas-small-spaces-*.webp','trinket-shelf-styling-ideas*.webp'],
'wallpaper':['warm-bedroom-lighting.webp','warm-reading-corner.webp','warm-kitchen-nook.webp','cozy-fall-balcony-ideas-small-spaces-*.webp'],
'food':['apple-cinnamon-desserts-fall-*.webp','slow-cooker-fall-dinner-ideas-*.webp','burger-bowl-recipes*.webp','ground-beef-stuffed-peppers*.webp','home-cafe-coffee-ideas-*.webp']
}

def seed(slug,i,heading=''):
    return int(hashlib.sha256(f'{slug}:{i}:{heading}'.encode()).hexdigest()[:16],16)
def rgb(h):
    h=h.lstrip('#');return tuple(int(h[i:i+2],16) for i in (0,2,4))
def mix(a,b,t):
    return tuple(int(a[k]*(1-t)+b[k]*t) for k in range(3))
def hsv_of(c):
    return Image.new('RGB',(1,1),c).convert('HSV').getpixel((0,0))
def clean_heading(h):
    return re.sub(r'^\s*\d+\.\s*','',h or '').strip()
def source_pool(patterns):
    out=[]
    for pat in patterns:
        for x in sorted(OUT.glob(pat)):
            if x.suffix.lower()=='.webp' and not any(x.name.startswith(t+'-') for t in TARGETS) and x not in out:
                out.append(x)
    return out

def patterns_for(style,slug,heading):
    h=heading.lower()
    if style=='nails':
        if 'tortoiseshell' in h or 'tortoiseshell' in slug:
            return ['brown-french-tip-nail-ideas-*.webp','deer-print-nail-ideas-*.webp','chocolate-short-nails.webp']
        if 'french' in h or 'half-moon' in h:
            return ['brown-french-tip-nail-ideas-*.webp','milky-lilac-nails-*.webp']
        if 'cat-eye' in h or 'magnetic' in h or 'velvet' in h:
            return ['rhinestone-nail-ideas-*.webp','milky-lilac-nails-*.webp','cherry-jam-nails.webp']
        if 'short' in h or 'square' in h:
            return ['short-fall-nail-colors*.webp','chocolate-short-nails.webp','milky-lilac-nails-*.webp']
        return BASE_PATTERNS['nails']
    if style=='hair':
        if any(k in h for k in ['bob','bixie','jaw-length','micro-fringe']):
            return ['feminine-pixie-cut-ideas-*.webp','korean-two-block-haircut-guide-*.webp','90s-hair-accessory-looks-*.webp']
        if any(k in h for k in ['long','layers','balayage','ribbons','highlights','underlayer']):
            return ['90s-hair-accessory-looks-*.webp','crochet-parandi-hair-accessory*.webp']
        return BASE_PATTERNS['hair']
    return BASE_PATTERNS.get(style,BASE_PATTERNS['room'])

def fit(im,size,i):
    im=im.convert('RGB');W,H=size;sw,sh=im.size
    scale=max(W/sw,H/sh);nw,nh=max(W,int(sw*scale)),max(H,int(sh*scale))
    im=im.resize((nw,nh),Image.Resampling.LANCZOS);dx,dy=max(0,nw-W),max(0,nh-H)
    x=int(dx*((i*37)%101)/100) if dx else 0;y=int(dy*((i*53)%101)/100) if dy else 0
    if i%4==3:
        im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT);x=max(0,dx-x)
    return im.crop((x,y,x+W,y+H))

def polish_color(palette,heading,i):
    h=heading.lower()
    named=[
      (('pumpkin','apricot'),(206,105,42)),(('burnt orange',),(181,74,28)),(('cinnamon',),(166,88,55)),
      (('copper',),(184,94,50)),(('espresso',),(83,46,34)),(('burgundy',),(103,19,35)),
      (('black cherry',),(73,12,28)),(('wine',),(112,28,45)),(('garnet',),(124,20,37)),
      (('cranberry',),(129,28,44)),(('ruby',),(155,28,44)),(('plum',),(91,34,75)),
      (('cherry mocha','mocha'),(98,36,42)),(('berry',),(117,39,69)),(('cocoa',),(94,58,46)),
      (('chocolate',),(91,57,39)),(('caramel','honey','amber'),(185,123,58)),(('gold',),(190,144,60))
    ]
    for keys,c in named:
        if any(k in h for k in keys):return c
    return rgb(palette[i%len(palette)])

def recolor_mask(im,target,mask,strength=.85):
    hsv=np.array(im.convert('HSV'),dtype=np.uint8);s,v=hsv[...,1],hsv[...,2]
    th,ts,tv=hsv_of(target);nh=hsv.copy();nh[...,0]=th;nh[...,1]=np.maximum(s,np.uint8(max(78,ts)));nh[...,2]=np.clip(v.astype(np.int16)*.88+14,0,255).astype(np.uint8)
    recol=np.array(Image.fromarray(nh,'HSV').convert('RGB'),dtype=np.float32);orig=np.array(im,dtype=np.float32)
    m=Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.GaussianBlur(2));ma=np.array(m,dtype=np.float32)/255.0*strength
    out=orig*(1-ma[...,None])+recol*ma[...,None]
    return Image.fromarray(np.clip(out,0,255).astype('uint8')),m

def nail_semantics(im,palette,slug,heading,i):
    h=heading.lower(); hsv=np.array(im.convert('HSV'),dtype=np.uint8)
    hue,sat,val=hsv[...,0],hsv[...,1],hsv[...,2]
    mask=((sat>18)&(val>65)&(((hue>115)&(hue<245))|((hue<35)&(sat>55))))
    if mask.mean()<.015:
        mask=(sat>28)&(val>55)
    target=polish_color(palette,heading,i)
    # French looks start with a sheer nude base, then color only the free-edge region.
    yy=np.indices(mask.shape)[0]
    ys=np.where(mask)[0]
    if len(ys):
        q=np.quantile(ys,.34)
        tip=(mask & (yy<=q))
    else: tip=mask
    if 'french' in h:
        nude=(225,190,170)
        im,_=recolor_mask(im,nude,mask,.55)
        im,m= recolor_mask(im,target,tip,.94)
    else:
        im,m=recolor_mask(im,target,mask,.88)
    arr=np.array(m,dtype=np.uint8)>20
    lay=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(lay,'RGBA');W,H=im.size
    if any(k in h for k in ['cat-eye','magnetic','velvet']):
        for k in range(6):
            x=int(W*(.10+k*.17))
            d.line((x-70,int(H*.80),x+110,int(H*.08)),fill=(255,235,225,130),width=8)
    if any(k in h for k in ['chrome','mirror','glass','shimmer','gloss']):
        for k in range(5):
            x=int(W*(.16+k*.18))
            d.line((x-25,int(H*.72),x+35,int(H*.18)),fill=(255,255,255,105),width=12)
    if 'gold' in h:
        for k in range(5):
            x=int(W*(.16+k*.17));d.arc((x-45,int(H*.19),x+65,int(H*.67)),190,350,fill=(235,190,82,145),width=4)
    if 'tortoiseshell' in h:
        rng=random.Random(seed(slug,i,heading))
        for k in range(38):
            x=rng.randrange(W);y=rng.randrange(int(H*.12),int(H*.72));r=rng.randrange(8,25)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(67,36,24,rng.randrange(35,80)))
    if 'micro-glitter' in h or 'foil' in h:
        rng=random.Random(seed(slug,i,'sparkle'))
        for k in range(85):
            x=rng.randrange(W);y=rng.randrange(H);r=rng.randrange(1,4);d.ellipse((x-r,y-r,x+r,y+r),fill=(242,207,117,110))
    alpha=np.array(lay)[...,3]
    alpha=np.minimum(alpha,np.array(m,dtype=np.uint8))
    la=np.array(lay);la[...,3]=alpha
    out=Image.alpha_composite(im.convert('RGBA'),Image.fromarray(la,'RGBA')).convert('RGB')
    if 'matte' in h:out=ImageEnhance.Contrast(out).enhance(.96)
    if 'evening' in h or 'holiday' in h:out=ImageEnhance.Contrast(out).enhance(1.10)
    return out

def hair_mask(im):
    hsv=np.array(im.convert('HSV'),dtype=np.uint8);s,v=hsv[...,1],hsv[...,2]
    # hair tends to be darker/more saturated than skin/background in our source set
    return (v<175)&(s>20)

def hair_semantics(im,palette,slug,heading,i):
    h=heading.lower();mask=hair_mask(im)
    target=polish_color(palette,heading,i) if 'cherry' in h or 'cola' in h or 'wine' in h else rgb(palette[i%len(palette)])
    base,_=recolor_mask(im,target,mask,.70)
    m=Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.GaussianBlur(3))
    W,H=im.size;lay=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(lay,'RGBA')
    def streak(x0,x1,col=(196,58,78,95),width=16):
        d.line((x0,int(H*.18),x1,int(H*.83)),fill=col,width=width)
    if any(k in h for k in ['balayage','ribbons','highlights']):
        for k in range(7):
            x=int(W*(.23+k*.085));streak(x,x+(-35 if k%2 else 35),(205,65,80,90),14)
    if 'face-framing' in h:
        streak(int(W*.43),int(W*.37),(220,74,92,125),20);streak(int(W*.57),int(W*.63),(220,74,92,125),20)
    if 'underlayer' in h:
        d.rectangle((0,int(H*.62),W,H),fill=(152,32,58,45))
    if 'copper' in h:
        d.rectangle((0,0,W,H),fill=(195,86,48,28))
    if 'cool wine' in h:
        d.rectangle((0,0,W,H),fill=(94,30,72,32))
    if 'high-gloss' in h or 'gloss' in h:
        for k in range(5):streak(int(W*(.28+k*.10)),int(W*(.31+k*.10)),(255,235,230,68),9)
    # fringe-specific light/dark framing makes the silhouette correspond to the heading.
    if any(k in h for k in ['fringe','bangs']):
        d.polygon([(int(W*.38),int(H*.12)),(int(W*.62),int(H*.12)),(int(W*.56),int(H*.38)),(int(W*.44),int(H*.38))],fill=target+(85,))
    alpha=np.minimum(np.array(lay)[...,3],np.array(m,dtype=np.uint8))
    la=np.array(lay);la[...,3]=alpha
    out=Image.alpha_composite(base.convert('RGBA'),Image.fromarray(la,'RGBA')).convert('RGB')
    if 'sleek' in h:out=ImageEnhance.Sharpness(out).enhance(1.25)
    if 'tousled' in h or 'curly' in h:out=ImageEnhance.Contrast(out).enhance(1.06)
    return out

def ingredient_props(im,heading,slug,i):
    h=heading.lower();W,H=im.size
    im=im.filter(ImageFilter.GaussianBlur(.22)).convert('RGBA');lay=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(lay,'RGBA')
    y=int(H*.80);rng=random.Random(seed(slug,i,heading))
    # neutral tray/shadow to integrate props
    d.ellipse((int(W*.15),int(H*.73),int(W*.88),int(H*.96)),fill=(70,42,28,22))
    def beans():
        for k in range(10):
            x=int(W*(.24+.045*k))+rng.randint(-9,9);yy=y+rng.randint(-25,20)
            d.ellipse((x-12,yy-8,x+12,yy+8),fill=(73,41,26,210));d.line((x-5,yy+2,x+6,yy-3),fill=(145,91,54,160),width=2)
    def vanilla():
        for off in [-10,10]:d.line((int(W*.28)+off,int(H*.73),int(W*.48)+off,int(H*.91)),fill=(62,43,29,220),width=8)
    def wood():
        for k in range(3):d.rounded_rectangle((int(W*.24)+k*32,int(H*.76)-k*8,int(W*.52)+k*18,int(H*.80)+18-k*8),8,fill=(122,78,43,190))
    def rose():
        for k in range(9):
            x=int(W*.28)+rng.randint(-50,150);yy=y+rng.randint(-30,30);d.ellipse((x-14,yy-7,x+14,yy+7),fill=(164,53,72,170))
    def leaves():
        for k in range(8):
            x=int(W*.30)+rng.randint(-60,130);yy=y+rng.randint(-30,30);d.ellipse((x-18,yy-7,x+18,yy+7),fill=(77,106,61,170))
    def amber():
        for k in range(7):
            x=int(W*.28)+rng.randint(-45,140);yy=y+rng.randint(-25,25);r=rng.randint(8,18);d.polygon([(x-r,yy),(x-r//3,yy-r),(x+r,yy-r//4),(x+r//2,yy+r),(x-r//2,yy+r)],fill=(199,120,40,170))
    def spice():
        for k in range(6):
            x=int(W*.30)+rng.randint(-45,130);yy=y+rng.randint(-25,25)
            d.ellipse((x-9,yy-16,x+9,yy+16),fill=(142,88,45,190));d.line((x,yy-10,x,yy+10),fill=(82,52,32,160),width=2)
    if 'coffee' in h:beans()
    if 'vanilla' in h:vanilla()
    if any(k in h for k in ['sandalwood','cedar','woods']):wood()
    if 'rose' in h:rose()
    if 'patchouli' in h:leaves()
    if 'amber' in h:amber()
    if any(k in h for k in ['cardamom','spice']):spice()
    if 'cocoa' in h:
        for k in range(6):
            x=int(W*.34)+rng.randint(-70,100);yy=y+rng.randint(-20,25);d.rectangle((x-14,yy-12,x+14,yy+12),fill=(83,48,34,190))
    if 'tonka' in h:
        for k in range(8):
            x=int(W*.33)+rng.randint(-70,100);yy=y+rng.randint(-20,25);d.ellipse((x-16,yy-8,x+16,yy+8),fill=(89,58,41,190))
    if 'musk' in h:
        d.ellipse((int(W*.20),int(H*.77),int(W*.48),int(H*.91)),fill=(242,235,224,150))
    return Image.alpha_composite(im,lay).convert('RGB')

def room_semantics(im,palette,heading,slug,i,wallpaper=False):
    h=heading.lower();W,H=im.size
    base=Image.blend(im,Image.new('RGB',im.size,rgb(palette[i%len(palette)])),.055).convert('RGBA')
    lay=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(lay,'RGBA')
    moss=(92,111,70,90);brown=(83,54,39,85);cream=(235,225,208,85);brass=(190,145,73,155)
    if wallpaper:
        region=(0,0,W,int(H*.62))
        if 'half-wall' in h:region=(0,0,W,int(H*.36))
        if 'panels' in h:
            panels=[(40,40,int(W*.31),int(H*.56)),(int(W*.35),40,int(W*.65),int(H*.56)),(int(W*.69),40,W-40,int(H*.56))]
        else:panels=[region]
        dark='dark' in h or 'moody' in h
        light='light' in h or 'small rooms' in h
        bg=(54,71,45,105) if dark else ((238,232,215,86) if light else (140,125,92,70))
        for bx in panels:
            d.rectangle(bx,fill=bg)
            x0,y0,x1,y1=bx
            step=80 if 'mural' not in h else 130
            for yy in range(y0+35,y1,step):
                for xx in range(x0+30,x1,step):
                    col=(80,106,65,110) if not dark else (155,174,133,105)
                    d.ellipse((xx-25,yy-9,xx+25,yy+9),fill=col);d.line((xx-28,yy+18,xx+28,yy-18),fill=(75,63,45,75),width=3)
        if 'framed' in h:
            for bx in panels:d.rectangle(bx,outline=(96,74,50,165),width=8)
    else:
        if 'moss accent wall' in h or 'moss built-ins' in h:d.rectangle((0,0,int(W*.42),int(H*.66)),fill=moss)
        if 'chocolate walls' in h:d.rectangle((0,0,W,int(H*.62)),fill=brown)
        if 'moss curtains' in h:
            d.rectangle((0,0,int(W*.16),int(H*.75)),fill=moss);d.rectangle((int(W*.84),0,W,int(H*.75)),fill=moss)
        if 'rug' in h:d.ellipse((int(W*.15),int(H*.72),int(W*.82),int(H*.98)),fill=brown)
        if 'green armchairs' in h:
            d.rounded_rectangle((int(W*.12),int(H*.47),int(W*.35),int(H*.78)),35,fill=moss);d.rounded_rectangle((int(W*.65),int(H*.47),int(W*.88),int(H*.78)),35,fill=moss)
        if 'brown leather' in h or 'chocolate brown sofa' in h:
            d.rounded_rectangle((int(W*.23),int(H*.50),int(W*.77),int(H*.76)),40,fill=brown)
        elif 'moss green sofa' in h or 'moss velvet' in h:
            d.rounded_rectangle((int(W*.23),int(H*.50),int(W*.77),int(H*.76)),40,fill=moss)
        if 'cream seating' in h:d.rounded_rectangle((int(W*.23),int(H*.50),int(W*.77),int(H*.76)),40,fill=cream)
        if 'brass' in h:
            d.line((int(W*.82),int(H*.38),int(W*.82),int(H*.78)),fill=brass,width=9);d.ellipse((int(W*.76),int(H*.30),int(W*.88),int(H*.44)),fill=brass)
        if 'walnut' in h or 'natural wood' in h:
            d.rectangle((int(W*.12),int(H*.70),int(W*.88),int(H*.76)),fill=(103,67,43,100))
        if 'layered lighting' in h:
            for x in [int(W*.22),int(W*.52),int(W*.80)]:d.ellipse((x-55,int(H*.25),x+55,int(H*.40)),fill=(248,214,151,65))
    return Image.alpha_composite(base,lay).convert('RGB')

def draw_food_scene(size,heading,slug,i,palette):
    h=heading.lower();W,H=size;rng=random.Random(seed(slug,i,heading));cloth=mix(rgb(palette[3]),(246,238,225),.72)
    base=Image.new('RGB',size,cloth).filter(ImageFilter.GaussianBlur(.1)).convert('RGBA')
    d=ImageDraw.Draw(base,'RGBA')
    # subtle linen texture
    for y in range(0,H,18):d.line((0,y,W,y),fill=(120,90,65,9),width=1)
    for x in range(0,W,22):d.line((x,0,x,H),fill=(120,90,65,7),width=1)
    cx,cy=W//2,int(H*.52)
    def plate(fill=(245,239,225,255),rim=(200,180,155,110)):
        d.ellipse((cx-270,cy-220,cx+270,cy+220),fill=rim);d.ellipse((cx-250,cy-200,cx+250,cy+200),fill=fill)
    if 'pumpkin bread' in h:
        d.rounded_rectangle((cx-240,cy-110,cx+240,cy+130),35,fill=(166,91,44,255))
        for k in range(4):d.line((cx-170+k*110,cy-90,cx-130+k*110,cy+95),fill=(224,150,85,120),width=8)
        if 'maple-glazed' in h:d.rounded_rectangle((cx-225,cy-120,cx+225,cy-65),28,fill=(236,197,145,210))
    elif 'crumble bars' in h:
        d.rounded_rectangle((cx-290,cy-190,cx+290,cy+190),28,fill=(108,74,52,80))
        for rr in range(2):
            for cc in range(3):
                x=cx-240+cc*180;y=cy-120+rr*150
                d.rounded_rectangle((x,y,x+145,y+115),18,fill=(205,157,93,255))
                for k in range(10):
                    xx=x+rng.randint(10,135);yy=y+rng.randint(8,105);r=rng.randint(3,8);d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=(138,81,46,130))
    elif 'baked cinnamon apples' in h:
        plate()
        for k in range(5):
            x=cx-160+k*80+rng.randint(-12,12);y=cy+rng.randint(-45,55);r=55
            d.ellipse((x-r,y-r,x+r,y+r),fill=(177,58,42,255));d.line((x,y-r,x+8,y-r-35),fill=(83,55,35,255),width=6)
            d.ellipse((x-18,y-10,x+18,y+20),fill=(116,65,38,130))
    elif 'apple oat crisp' in h:
        d.rounded_rectangle((cx-280,cy-180,cx+280,cy+180),30,fill=(214,174,112,255))
        for k in range(90):
            x=rng.randint(cx-250,cx+250);y=rng.randint(cy-150,cy+150);r=rng.randint(3,9);d.ellipse((x-r,y-r,x+r,y+r),fill=(132,91,55,rng.randint(90,170)))
    elif 'soup' in h:
        plate((246,242,232,255))
        bowl=(cx-210,cy-150,cx+210,cy+190);d.ellipse(bowl,fill=(240,236,228,255))
        soup=(cx-180,cy-125,cx+180,cy+155)
        col=(206,117,42,255) if 'pumpkin' in h or 'squash' in h else (188,64,48,255)
        d.ellipse(soup,fill=col)
        d.ellipse((cx-60,cy-25,cx+70,cy+30),fill=(236,226,194,90))
        if 'grilled cheese' in h:
            d.polygon([(cx+235,cy-90),(cx+420,cy-15),(cx+270,cy+90)],fill=(203,149,70,255));d.polygon([(cx+245,cy-78),(cx+390,cy-18),(cx+278,cy+70)],fill=(238,205,101,255))
    elif 'pasta' in h or 'mac and cheese' in h:
        plate()
        col=(222,185,95,255) if 'mac' in h else (219,194,145,255)
        for k in range(80):
            a=rng.random()*math.tau;rad=rng.random()*175;x=cx+int(math.cos(a)*rad);y=cy+int(math.sin(a)*rad*.65)
            d.arc((x-28,y-14,x+28,y+14),0,300,fill=col,width=7)
        if 'mushroom' in h:
            for k in range(10):
                x=cx+rng.randint(-150,150);y=cy+rng.randint(-90,90)
                d.pieslice((x-30,y-25,x+30,y+25),180,360,fill=(150,119,91,255));d.rectangle((x-5,y,x+5,y+25),fill=(130,102,80,255))
    elif 'sheet-pan' in h:
        d.rounded_rectangle((cx-330,cy-210,cx+330,cy+210),24,fill=(95,84,75,255))
        for k in range(30):
            x=rng.randint(cx-290,cx+290);y=rng.randint(cy-170,cy+170)
            if k%2:d.ellipse((x-25,y-12,x+25,y+12),fill=(150,69,48,255))
            else:d.rectangle((x-20,y-20,x+20,y+20),fill=(206,118,50,255))
    elif 'chicken and rice' in h:
        d.rounded_rectangle((cx-300,cy-190,cx+300,cy+190),28,fill=(235,211,160,255))
        for k in range(160):
            x=rng.randint(cx-270,cx+270);y=rng.randint(cy-160,cy+160);d.ellipse((x,y,x+4,y+2),fill=(244,232,200,180))
        for k in range(5):
            x=cx-190+k*95;y=cy+rng.randint(-60,60);d.ellipse((x-55,y-35,x+55,y+35),fill=(177,111,66,240))
    elif 'sausage' in h and 'skillet' in h:
        d.ellipse((cx-300,cy-210,cx+300,cy+210),fill=(58,54,50,255))
        for k in range(24):
            x=rng.randint(cx-220,cx+220);y=rng.randint(cy-140,cy+140)
            if k%2:d.ellipse((x-35,y-20,x+35,y+20),fill=(148,68,49,255))
            else:d.rectangle((x-22,y-22,x+22,y+22),fill=(94,128,64,230))
    elif 'muffins' in h:
        for r0 in range(2):
            for c0 in range(3):
                x=cx-220+c0*210;y=cy-110+r0*190
                d.polygon([(x-55,y-20),(x+55,y-20),(x+42,y+75),(x-42,y+75)],fill=(151,83,47,255));d.ellipse((x-65,y-65,x+65,y+20),fill=(194,113,60,255))
    elif 'dessert cups' in h:
        for k in range(4):
            x=cx-240+k*160;d.rounded_rectangle((x-55,cy-145,x+55,cy+150),22,outline=(220,220,215,190),width=5)
            for q in range(5):d.rectangle((x-38,cy+80-q*42,x+38,cy+105-q*42),fill=((197,126,58,190) if q%2 else (236,211,166,190)))
    elif 'dinner board' in h:
        d.rounded_rectangle((cx-350,cy-225,cx+350,cy+225),35,fill=(124,82,51,255))
        for k in range(14):
            x=rng.randint(cx-290,cx+290);y=rng.randint(cy-170,cy+170);r=rng.randint(22,48)
            d.ellipse((x-r,y-r,x+r,y+r),fill=[(208,128,62,230),(132,77,49,230),(191,165,105,230),(94,125,68,230)][k%4])
    else:
        plate();d.ellipse((cx-170,cy-120,cx+170,cy+120),fill=rgb(palette[i%len(palette)])+(230,))
    # small side props / shadows
    d.ellipse((70,80,240,250),fill=(160,100,60,28));d.ellipse((W-230,H-230,W-70,H-70),fill=(110,80,55,22))
    return base.convert('RGB').filter(ImageFilter.GaussianBlur(.25))

def natural_grade(im,palette,style,i):
    if style in ('nails','hair'):return ImageEnhance.Sharpness(ImageEnhance.Contrast(im).enhance(1.025)).enhance(1.08)
    target=rgb(palette[i%len(palette)]);wash=Image.new('RGB',im.size,target)
    alpha=.025 if style=='food' else .055
    im=Image.blend(im,wash,alpha);im=ImageEnhance.Contrast(im).enhance(1.035);im=ImageEnhance.Color(im).enhance(1.045)
    return ImageEnhance.Sharpness(im).enhance(1.06)

def render(p,i,path,heading):
    style=p.get('visualStyle','room');pal=p.get('visualPalette') or ['#7C9C82','#0F2B25','#F1E6D8','#A8CBB6','#FDFBF6']
    if style=='food':
        im=draw_food_scene((1024,768),heading,p['slug'],i,pal)
    else:
        srcs=source_pool(patterns_for(style,p['slug'],heading))
        if not srcs:srcs=source_pool(BASE_PATTERNS.get(style,BASE_PATTERNS['room']))
        src=srcs[(seed(p['slug'],i,heading)+i)%len(srcs)]
        im=fit(Image.open(src),(1024,768),i);im=natural_grade(im,pal,style,i)
        if style=='nails':im=nail_semantics(im,pal,p['slug'],heading,i)
        elif style=='hair':im=hair_semantics(im,pal,p['slug'],heading,i)
        elif style=='fragrance':im=ingredient_props(im,heading,p['slug'],i)
        elif style=='room':im=room_semantics(im,pal,heading,p['slug'],i,False)
        elif style=='wallpaper':im=room_semantics(im,pal,heading,p['slug'],i,True)
    im.save(ROOT/path,'WEBP',quality=90,method=4);DIMS[path]=[1024,768]

count=0
for p in POSTS:
    if p.get('qualityStandard')!='pro-v2':continue
    cover_heading=p['title']
    render(p,0,p['cover'],cover_heading);count+=1
    for i,s in enumerate(p.get('sections',[]),1):
        if s.get('image'):
            render(p,i,s['image'],clean_heading(s.get('heading','')));count+=1
(ROOT/'data/image-dimensions.json').write_text(json.dumps(DIMS,indent=2)+'\n',encoding='utf-8')
print(f'Generated {count} section-aware WebP editorial images.')
