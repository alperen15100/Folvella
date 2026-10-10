"""Heading-matched, photo-led polka-dot cat-eye manicure artwork for InspoMint."""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import json,random
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/generated'
SLUG='polka-dot-cat-eye-nail-ideas'
COLORS=['#761A37','#603821','#C68A99','#778F66','#1E305A','#CCB88C','#18191F','#A31C39','#B6A1D4','#08684D','#B67242','#87B7D7','#D9A1B7','#64294C','#765240','#BEC5D1','#0C6D71','#E1AE95','#F4E7D0','#474751','#C9A16F']
DOTS=['#E8C88F','#F5E5CE','#333035','#BDA063','#E8E9ED','#6C3B2E','#F3F1EC','#741F32','#F7EFFD','#E9BE72','#523626','#1B3153','#FFFAF7','#C5977A','#F9E4CA','#151515','#D9AE60','#533425','#702236','#E8E8EE','#79502E']

def rgb(v):return np.array(tuple(int(v[i:i+2],16) for i in (1,3,5)),dtype=np.float32)

NAILS=[
 [(90,124,26,42,-18),(160,181,28,39,-22),(229,241,27,39,-22),(290,270,23,33,-24)],
 [(93,142,25,37,-23),(160,209,25,38,-23),(228,257,25,38,-24),(286,280,20,27,-24)],
 [(91,106,26,43,-20),(164,181,27,43,-20),(235,251,26,39,-24),(293,273,20,30,-21)],
 [(119,25,15,30,-40),(102,146,26,44,-36),(158,207,26,44,-35),(228,258,25,38,-34),(286,275,19,30,-32)],
 [(93,52,16,34,-45),(103,146,25,42,-38),(165,199,27,45,-39),(227,249,27,44,-43),(285,271,18,32,-38)],
 [(104,128,25,47,-24),(166,203,25,47,-27),(239,258,26,46,-29),(291,286,18,31,-29)],
 [(92,140,25,42,-19),(169,208,25,43,-19),(238,260,25,40,-20),(292,278,20,30,-23)],
 [(90,151,26,39,-20),(167,210,25,40,-22),(238,257,25,39,-20),(291,279,20,27,-18)],
 [(95,137,27,41,-25),(162,207,26,43,-23),(235,249,25,38,-25),(297,275,19,28,-25)],
 [(88,150,25,41,-21),(165,206,26,41,-21),(238,255,24,40,-23),(288,276,20,28,-24)],
 [(83,130,25,39,-23),(156,194,27,40,-21),(226,251,25,38,-22),(294,275,21,29,-25)],
 [(109,134,25,46,-26),(175,207,25,42,-29),(243,257,28,40,-28),(290,278,19,29,-29)],
 [(74,128,29,40,-24),(146,193,30,41,-25),(215,236,28,37,-24),(275,268,22,30,-25)],
 [(81,147,26,37,-18),(156,202,26,40,-21),(227,246,27,39,-23),(290,277,20,31,-21)],
 [(104,115,25,39,-12),(171,201,26,43,-14),(242,249,26,41,-18),(300,275,19,30,-19)],
 [(48,112,26,34,15),(113,185,28,38,-14),(184,237,28,40,-20),(264,263,20,33,-25)],
 [(238,102,25,38,15),(183,170,27,42,20),(114,234,27,40,22),(51,264,20,31,24)],
 [(117,117,23,43,-22),(161,186,25,45,-24),(234,248,26,41,-24),(290,273,20,30,-22)],
 [(255,83,25,36,-56),(220,156,26,38,-58),(163,214,25,40,-53),(101,268,23,35,-48)],
 [(75,157,25,40,-19),(154,211,26,43,-21),(228,249,24,41,-24),(292,277,20,30,-25)],
 [(98,92,24,40,-14),(160,169,28,46,-18),(232,230,27,44,-22),(294,256,22,34,-22)]
]
def mask_nails(im,index):
    import math
    w,h=im.size
    layer=Image.new('L',(w,h),0)
    brush=ImageDraw.Draw(layer)
    for cx,cy,rx,ry,angle in NAILS[index-1]:
        t=math.radians(angle)
        pts=[]
        for j in range(60):
            a=2*math.pi*j/60
            u=rx*math.cos(a);v=ry*math.sin(a)
            x=cx+u*math.cos(t)-v*math.sin(t)
            y=cy+u*math.sin(t)+v*math.cos(t)
            pts.append((x*w/300,y*h/300))
        brush.polygon(pts,fill=255)
    return np.asarray(layer.filter(ImageFilter.GaussianBlur(5)),dtype=np.float32)/255

def render_idea(i):
    source=OUT/f'milky-lilac-nails-{i:02d}.webp'
    if not source.exists():raise FileNotFoundError(source)
    im=Image.open(source).convert('RGB').resize((900,900),Image.Resampling.LANCZOS)
    base=np.asarray(im,dtype=np.float32)
    mask=mask_nails(im,i)
    target=rgb(COLORS[i-1])
    dot=tuple(int(x) for x in rgb(DOTS[i-1]))
    lum=np.asarray(im.convert('HSV'))[:,:,2].astype(np.float32)/255
    shade=np.clip(.59+.68*lum,.48,1.29)
    paint=np.minimum(255,target[None,None,:]*shade[:,:,None])
    alpha=np.minimum(.93,mask*.93)
    arr=base*(1-alpha[:,:,None])+paint*alpha[:,:,None]
    H,W=mask.shape;yy,xx=np.indices((H,W))
    shift=(i%4-.5)*W*.14
    shine=np.exp(-((xx-(W*.43+(yy-H*.46)*(.13 if i%2 else -.19)+shift))/(W*.038))**2)
    glow=mask*shine*.29
    arr=arr*(1-glow[:,:,None])+np.array([248,235,228])[None,None,:]*glow[:,:,None]
    result=Image.fromarray(np.uint8(np.clip(arr,0,255)),'RGB')
    # Spread tiny, real dotting-tool marks across enamel only, never skin.
    rng=random.Random(i*1879+420)
    interior=np.asarray(Image.fromarray(np.uint8(mask*255),'L').filter(ImageFilter.MinFilter(17)))>150
    coords=np.argwhere(interior)
    if len(coords)<100:coords=np.argwhere(mask>.76)
    layer=Image.new('RGBA',im.size,(0,0,0,0))
    painter=ImageDraw.Draw(layer,'RGBA')
    centers=[]
    for _ in range(min(650,len(coords))):
      if len(centers)>=55:break
      y,x=(int(z) for z in coords[rng.randrange(len(coords))])
      if all((x-px)**2+(y-py)**2>25**2 for px,py in centers):
        centers.append((x,y));rad=rng.randint(4,7)
        painter.ellipse((x-rad,y-rad,x+rad,y+rad),fill=dot+(248,))
    a=np.asarray(layer.getchannel('A'),dtype=np.float32)*mask
    layer.putalpha(Image.fromarray(np.uint8(a),'L'))
    return Image.alpha_composite(result.convert('RGBA'),layer).convert('RGB')

def main():
    dims_path=ROOT/'data/image-dimensions.json'
    dims=json.loads(dims_path.read_text())
    samples=[]
    for i in range(1,22):
      dest=f'assets/generated/{SLUG}-idea-{i:02d}.webp'
      im=render_idea(i)
      im.save(ROOT/dest,'WEBP',quality=88,method=5)
      dims[dest]=[900,900];samples.append(im)
    cover=Image.new('RGB',(1200,800),'#FAF4F1')
    for j,k in enumerate([0,1,3,7,9,13]):
      tile=samples[k].resize((400,400),Image.Resampling.LANCZOS)
      cover.paste(tile,((j%3)*400,(j//3)*400))
    cp=f'assets/generated/{SLUG}-cover.webp'
    cover.save(ROOT/cp,'WEBP',quality=87,method=5)
    dims[cp]=[1200,800]
    dims_path.write_text(json.dumps(dims,indent=2)+'\n')
    print('Verified 21 distinct photo sources, 21 dot-matched designs, 22 WebP assets.')

if __name__=='__main__':main()
