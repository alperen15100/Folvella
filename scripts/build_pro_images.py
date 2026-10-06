"""Generate distinct raster editorial visuals for pro-v2 posts."""
import json, hashlib, random, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
POSTS=json.loads((ROOT/"data/posts.json").read_text(encoding="utf-8"))
DIMS=json.loads((ROOT/"data/image-dimensions.json").read_text(encoding="utf-8"))
OUT=ROOT/"assets/generated"; OUT.mkdir(parents=True,exist_ok=True)

def rgb(h):
    h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def mix(a,b,t):
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
def seed_for(slug,idx):
    return int(hashlib.sha256(f"{slug}:{idx}".encode()).hexdigest()[:16],16)
def bg(size,c1,c2):
    w,h=size
    g=Image.new("RGB",(1,h))
    px=g.load()
    for y in range(h):
        t=y/max(1,h-1); px[0,y]=mix(c1,c2,t)
    return g.resize(size)
def texture(im,amount=7):
    n=Image.effect_noise(im.size,28).convert("L").filter(ImageFilter.GaussianBlur(0.5))
    n=ImageEnhance.Contrast(n).enhance(0.35)
    lay=Image.new("RGB",im.size,(255,255,255))
    lay.putalpha(n.point(lambda x:int(x*amount/100)))
    return Image.alpha_composite(im.convert("RGBA"),lay).convert("RGB")
def rr(draw,box,r,fill,outline=None,w=1):
    draw.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=w)

def render_nails(size,pal,rng,idx):
    skin=(224,184,158); cream=mix(pal[4],(255,255,255),0.72)
    im=texture(bg(size,cream,mix(cream,(235,220,205),0.35)),5).convert("RGBA")
    d=ImageDraw.Draw(im,"RGBA"); W,H=size
    for i in range(5):
        cx=int(W*(.19+i*.155)+rng.randint(-18,18)); cy=int(H*(.57+abs(i-2)*.018))
        fw=int(W*.115); fh=int(H*.54); x0=cx-fw//2; y0=cy-fh//2
        rr(d,(x0,y0,x0+fw,y0+fh),fw//2,skin+(255,))
        nh=int(fh*.33); ny=y0+int(fh*.05); col=pal[(idx+i)%len(pal)]
        rr(d,(x0+10,ny,x0+fw-10,ny+nh),int(fw*.35),col+(255,))
        d.arc((x0+18,ny+10,x0+fw-18,ny+nh-10),190,345,fill=(255,255,255,125),width=max(2,fw//18))
        if idx%3==0: d.ellipse((cx-10,ny+nh//2-10,cx+10,ny+nh//2+10),fill=pal[(idx+2)%len(pal)]+(180,))
        if idx%3==1: d.line((x0+20,ny+nh-22,x0+fw-20,ny+25),fill=(255,224,180,160),width=5)
        if idx%3==2: d.arc((x0+20,ny+15,x0+fw-20,ny+nh-15),10,170,fill=(45,28,24,120),width=5)
    return im.convert("RGB").filter(ImageFilter.GaussianBlur(.35))

def render_hair(size,pal,rng,idx):
    W,H=size; base=mix(pal[2],(245,232,220),.78)
    im=texture(bg(size,base,mix(base,(210,192,180),.22)),5).convert("RGBA"); d=ImageDraw.Draw(im,"RGBA")
    cx=W//2+rng.randint(-40,40); cy=int(H*.44)
    d.ellipse((cx-int(W*.16),cy-int(H*.23),cx+int(W*.16),cy+int(H*.23)),fill=(226,185,158,255))
    hair=pal[idx%len(pal)]; hi=pal[(idx+2)%len(pal)]
    d.pieslice((cx-int(W*.27),cy-int(H*.36),cx+int(W*.27),cy+int(H*.34)),180,360,fill=hair+(255,))
    d.polygon([(cx-int(W*.26),cy-int(H*.05)),(cx-int(W*.2),int(H*.83)),(cx-int(W*.04),int(H*.76)),(cx,cy-int(H*.1))],fill=hair+(245,))
    d.polygon([(cx+int(W*.26),cy-int(H*.05)),(cx+int(W*.2),int(H*.83)),(cx+int(W*.04),int(H*.76)),(cx,cy-int(H*.1))],fill=hair+(245,))
    for k in range(9):
        off=int((k-4)*W*.035)
        d.arc((cx-int(W*.23)+off,cy-int(H*.28),cx+int(W*.17)+off,cy+int(H*.42)),195,325,fill=hi+(95,),width=max(5,W//130))
    d.ellipse((cx-int(W*.07),cy-int(H*.03),cx-int(W*.05),cy-int(H*.01)),fill=(70,48,42,180))
    d.ellipse((cx+int(W*.05),cy-int(H*.03),cx+int(W*.07),cy-int(H*.01)),fill=(70,48,42,180))
    return im.convert("RGB").filter(ImageFilter.GaussianBlur(.45))

def render_fragrance(size,pal,rng,idx):
    W,H=size; wall=mix(pal[4],(250,245,238),.55)
    im=texture(bg(size,wall,mix(wall,(215,195,176),.18)),4).convert("RGBA"); d=ImageDraw.Draw(im,"RGBA")
    d.rectangle((0,int(H*.7),W,H),fill=mix(pal[2],(115,78,52),.45)+(255,))
    for i in range(3):
        bw=int(W*(.16+.025*i)); bh=int(H*(.33+.04*((idx+i)%3))); x=int(W*(.18+i*.25)); y=int(H*.68-bh)
        c=pal[(idx+i)%len(pal)]
        rr(d,(x,y,x+bw,y+bh),int(bw*.12),c+(190,))
        rr(d,(x+int(bw*.27),y-int(H*.07),x+int(bw*.73),y+int(H*.02)),int(bw*.06),pal[(idx+i+1)%len(pal)]+(230,))
        d.rectangle((x+int(bw*.12),y+int(bh*.46),x+int(bw*.88),y+int(bh*.64)),fill=(250,245,235,175))
        d.line((x+15,y+20,x+bw-20,y+20),fill=(255,255,255,120),width=5)
    return im.convert("RGB").filter(ImageFilter.GaussianBlur(.3))

def render_room(size,pal,rng,idx,wallpaper=False):
    W,H=size; wall=mix(pal[2],(246,240,231),.7)
    im=texture(bg(size,wall,mix(wall,(225,214,199),.18)),4).convert("RGBA"); d=ImageDraw.Draw(im,"RGBA")
    if wallpaper:
        for y in range(60,int(H*.63),105):
            for x in range(45,W,115):
                col=pal[(x//115+y//105+idx)%len(pal)]
                d.ellipse((x-28,y-12,x+28,y+12),fill=col+(80,))
                d.line((x-34,y+20,x+34,y-20),fill=(96,77,58,65),width=3)
    d.rectangle((0,int(H*.66),W,H),fill=mix(pal[3],(118,83,55),.45)+(255,))
    sx=int(W*.16); sy=int(H*.48); sw=int(W*.58); sh=int(H*.26)
    rr(d,(sx,sy,sx+sw,sy+sh),34,pal[idx%len(pal)]+(255,))
    rr(d,(sx+40,sy-65,sx+int(sw*.45),sy+35),28,pal[(idx+2)%len(pal)]+(245,))
    rr(d,(sx+int(sw*.52),sy-55,sx+sw-40,sy+35),28,pal[(idx+3)%len(pal)]+(245,))
    d.ellipse((int(W*.1),int(H*.75),int(W*.78),int(H*.98)),fill=(218,198,168,150))
    lx=int(W*.82); d.rectangle((lx,int(H*.38),lx+12,int(H*.77)),fill=(70,58,48,220)); d.ellipse((lx-58,int(H*.27),lx+70,int(H*.45)),fill=(244,213,154,220))
    for k in range(6):
        px=int(W*.9+rng.randint(-30,30)); py=int(H*.46+k*24)
        d.ellipse((px-35,py-18,px+20,py+18),fill=pal[(idx+k)%len(pal)]+(160,))
    return im.convert("RGB").filter(ImageFilter.GaussianBlur(.25))

def render_food(size,pal,rng,idx):
    W,H=size; cloth=mix(pal[3],(248,239,224),.58)
    im=texture(bg(size,cloth,mix(cloth,(221,199,172),.22)),5).convert("RGBA"); d=ImageDraw.Draw(im,"RGBA")
    cx,cy=W//2,int(H*.53); r=int(min(W,H)*.31)
    d.ellipse((cx-r-18,cy-r-18,cx+r+18,cy+r+18),fill=(181,151,119,90))
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(248,243,232,255))
    d.ellipse((cx-int(r*.77),cy-int(r*.77),cx+int(r*.77),cy+int(r*.77)),fill=pal[idx%len(pal)]+(240,))
    for k in range(7):
        a=2*math.pi*k/7+rng.random()*.35; rr0=int(r*.48)
        x=cx+int(math.cos(a)*rr0); y=cy+int(math.sin(a)*rr0)
        c=pal[(idx+k+1)%len(pal)]
        d.ellipse((x-45,y-32,x+45,y+32),fill=c+(230,))
    d.line((int(W*.12),int(H*.2),int(W*.2),int(H*.84)),fill=(90,74,62,190),width=14)
    d.line((int(W*.85),int(H*.18),int(W*.78),int(H*.86)),fill=(90,74,62,190),width=14)
    return im.convert("RGB").filter(ImageFilter.GaussianBlur(.4))

def render_default(size,pal,rng,idx):
    im=texture(bg(size,mix(pal[0],(255,255,255),.78),mix(pal[2],(255,255,255),.55)),5).convert("RGBA")
    d=ImageDraw.Draw(im,"RGBA"); W,H=size
    for i in range(8):
        x=rng.randint(40,W-260); y=rng.randint(40,H-240); w=rng.randint(120,300); h=rng.randint(120,260)
        rr(d,(x,y,x+w,y+h),30,pal[(idx+i)%len(pal)]+(110,))
    return im.convert("RGB")

def make_scene(style,palette,slug,idx,size):
    pal=[rgb(x) for x in palette]; rng=random.Random(seed_for(slug,idx))
    if style=="nails": im=render_nails(size,pal,rng,idx)
    elif style=="hair": im=render_hair(size,pal,rng,idx)
    elif style=="fragrance": im=render_fragrance(size,pal,rng,idx)
    elif style=="room": im=render_room(size,pal,rng,idx,False)
    elif style=="wallpaper": im=render_room(size,pal,rng,idx,True)
    elif style=="food": im=render_food(size,pal,rng,idx)
    else: im=render_default(size,pal,rng,idx)
    return ImageEnhance.Sharpness(im).enhance(1.12)

count=0
for p in POSTS:
    if p.get("qualityStandard")!="pro-v2": continue
    style=p.get("visualStyle","default"); palette=p.get("visualPalette") or ["#7C9C82","#0F2B25","#F1E6D8","#A8CBB6","#FDFBF6"]
    cover=p["cover"]; ci=make_scene(style,palette,p["slug"],0,(1200,900)); ci.save(ROOT/cover,"WEBP",quality=90,method=6); DIMS[cover]=[1200,900]; count+=1
    for i,s in enumerate(p.get("sections",[]),1):
        path=s.get("image")
        if not path: continue
        im=make_scene(style,palette,p["slug"],i,(1200,900)); im.save(ROOT/path,"WEBP",quality=88,method=6); DIMS[path]=[1200,900]; count+=1
(ROOT/"data/image-dimensions.json").write_text(json.dumps(DIMS,indent=2)+"\n",encoding="utf-8")
print(f"Generated {count} distinct WebP editorial images.")
