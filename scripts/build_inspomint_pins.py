"""Generate one branded 3-photo Pinterest Pin for every published InspoMint guide."""
import json, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'pins'/'inspomint'
OUT.mkdir(parents=True,exist_ok=True)

posts=[p for p in json.loads((ROOT/'data/posts.json').read_text(encoding='utf-8')) if p.get('status')=='published']

W,H=1000,1500
BG=(253,251,246)
INK=(15,43,37)
SAGE=(111,145,120)
LINE=(171,188,176)
WHITE=(255,255,255)

def font(path,size):
    return ImageFont.truetype(path,size)

SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SERIF_REG='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SANS_BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def fit_crop(img,size):
    img=ImageOps.exif_transpose(img).convert('RGB')
    return ImageOps.fit(img,size,method=Image.Resampling.LANCZOS,centering=(0.5,0.45))

def rounded_paste(canvas,img,box,radius=28):
    x,y,w,h=box
    img=fit_crop(img,(w,h))
    mask=Image.new('L',(w,h),0)
    md=ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,w,h),radius=radius,fill=255)
    canvas.paste(img,(x,y),mask)

def text_width(draw,text,f):
    b=draw.textbbox((0,0),text,font=f)
    return b[2]-b[0]

def wrap_for(draw,text,f,max_w):
    words=text.split()
    lines=[]
    cur=''
    for word in words:
        trial=word if not cur else cur+' '+word
        if text_width(draw,trial,f)<=max_w:
            cur=trial
        else:
            if cur: lines.append(cur)
            cur=word
    if cur: lines.append(cur)
    return lines

def title_layout(draw,title,max_w=860,max_lines=3):
    for size in range(86,51,-2):
        f=font(SERIF,size)
        lines=wrap_for(draw,title,f,max_w)
        if len(lines)<=max_lines:
            return f,lines
    f=font(SERIF,52)
    lines=wrap_for(draw,title,f,max_w)
    if len(lines)>max_lines:
        lines=lines[:max_lines]
        last=lines[-1]
        while text_width(draw,last+'…',f)>max_w and len(last)>4:
            last=last[:-1]
        lines[-1]=last.rstrip()+ '…'
    return f,lines

def draw_leaf(draw,cx,cy,scale=1.0):
    # minimal leaf mark inspired by the approved InspoMint identity
    draw.line((cx,cy+18*scale,cx,cy-4*scale),fill=INK,width=max(1,int(2*scale)))
    draw.ellipse((cx-19*scale,cy-22*scale,cx+2*scale,cy+4*scale),fill=SAGE)
    draw.ellipse((cx-2*scale,cy-26*scale,cx+19*scale,cy),fill=SAGE)

def available_images(p):
    candidates=[]
    for src in [p.get('cover'),p.get('pinCover')]+[s.get('image') for s in p.get('sections',[]) if s.get('image')]:
        if src and src not in candidates and (ROOT/src).is_file():
            candidates.append(src)
    if not candidates:
        raise FileNotFoundError(p['slug'])
    while len(candidates)<3:
        candidates.append(candidates[len(candidates)%len(candidates)])
    return candidates[:3]

def brand(draw):
    f1=font(SERIF,68); f2=font(SERIF,68)
    a='Inspo'; b='Mint'
    wa=text_width(draw,a,f1); wb=text_width(draw,b,f2)
    total=wa+wb
    x=(W-total)//2
    draw.text((x,1305),a,font=f1,fill=INK)
    draw.text((x+wa,1305),b,font=f2,fill=SAGE)
    # small sparkle
    sx=x+24; sy=1294
    draw.polygon([(sx,sy-11),(sx+4,sy-3),(sx+12,sy),(sx+4,sy+3),(sx,sy+11),(sx-4,sy+3),(sx-12,sy),(sx-4,sy-3)],fill=INK)
    tagline='Fresh ideas worth saving.'
    tf=font(SERIF_REG,21)
    tw=text_width(draw,tagline,tf)
    draw.text(((W-tw)//2,1384),tagline,font=tf,fill=INK)

def build(p):
    canvas=Image.new('RGB',(W,H),BG)
    d=ImageDraw.Draw(canvas)

    # soft decorative shapes
    d.ellipse((-100,980,170,1390),fill=(232,240,233))
    d.ellipse((850,-100,1090,260),fill=(236,242,235))

    cat=p['category'].upper()
    cf=font(SANS,22)
    cw=text_width(d,cat,cf)
    cy=46
    d.line((140,59,(W-cw)//2-28,59),fill=LINE,width=2)
    d.line(((W+cw)//2+28,59,860,59),fill=LINE,width=2)
    d.text(((W-cw)//2,44),cat,font=cf,fill=(88,113,96))

    title=p['title']
    tf,lines=title_layout(d,title)
    line_h=int(tf.size*1.02)
    block_h=line_h*len(lines)
    y=100+(250-block_h)//2
    for i,line in enumerate(lines):
        w=text_width(d,line,tf)
        fill=INK if i==0 else (99,126,105)
        d.text(((W-w)//2,y+i*line_h),line,font=tf,fill=fill)

    d.line((340,348,463,348),fill=LINE,width=2)
    d.line((537,348,660,348),fill=LINE,width=2)
    draw_leaf(d,500,348,0.85)

    imgs=[Image.open(ROOT/src) for src in available_images(p)]
    rounded_paste(canvas,imgs[0],(58,392,480,770),28)
    rounded_paste(canvas,imgs[1],(558,392,384,376),28)
    rounded_paste(canvas,imgs[2],(558,786,384,376),28)
    for im in imgs:
        im.close()

    d.line((70,1352,292,1352),fill=LINE,width=2)
    d.line((708,1352,930,1352),fill=LINE,width=2)
    brand(d)

    out=OUT/(p['slug']+'.jpg')
    canvas.save(out,'JPEG',quality=84,optimize=True,progressive=True)
    return out

for p in posts:
    build(p)

print(f'Generated {len(posts)} InspoMint 3-photo Pinterest Pins in {OUT.relative_to(ROOT)}.')
