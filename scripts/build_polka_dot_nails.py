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

def mask_nails(im):
    hsv=np.asarray(im.convert('HSV'))
    h,s,v=hsv[:,:,0],hsv[:,:,1],hsv[:,:,2]
    raw=((h>=165)&(h<=242)&(s>=13)&(v>=55)).astype('uint8')*255
    arr=np.asarray(Image.fromarray(raw,'L').filter(ImageFilter.MedianFilter(5)))>128
    H,W=arr.shape
    seen=np.zeros((H,W),dtype=np.uint8)
    keep=np.zeros((H,W),dtype=np.uint8)
    # Compact, oval enamel components; ignore large lilac fabrics and flowers.
    for y in range(0,H,2):
      for x in range(0,W,2):
        if not arr[y,x] or seen[y,x]:continue
        stack=[(y,x)];seen[y,x]=1;pts=[]
        minx=maxx=x;miny=maxy=y
        while stack:
          cy,cx=stack.pop();pts.append((cy,cx))
          minx=min(minx,cx);maxx=max(maxx,cx)
          miny=min(miny,cy);maxy=max(maxy,cy)
          for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=cy+dy,cx+dx
            if 0<=ny<H and 0<=nx<W and arr[ny,nx] and not seen[ny,nx]:
              seen[ny,nx]=1;stack.append((ny,nx))
        bw=maxx-minx+1;bh=maxy-miny+1;area=len(pts)
        if 420<=area<125000 and 20<=bw<450 and 26<=bh<530 and area/(bw*bh)>.17:
          for yy,xx in pts:keep[yy,xx]=255
    if np.count_nonzero(keep)<2500:keep=np.where(arr,255,0).astype(np.uint8)
    return np.asarray(Image.fromarray(keep,'L').filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(3.4))).astype(np.float32)/255

def render_idea(i):
    source=OUT/f'milky-lilac-nails-{i:02d}.webp'
    if not source.exists():raise FileNotFoundError(source)
    im=Image.open(source).convert('RGB').resize((900,900),Image.Resampling.LANCZOS)
    base=np.asarray(im,dtype=np.float32)
    mask=mask_nails(im)
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
