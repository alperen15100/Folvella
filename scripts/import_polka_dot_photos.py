"""Install 21 original, directly matched polka-dot cat-eye photos from one ZIP."""
import json,zipfile,io
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'assets/inspomint-polka-dot-photos.zip'
OUT=ROOT/'assets/generated'
SLUG='polka-dot-cat-eye-nail-ideas'

def main():
    dims_file=ROOT/'data/image-dimensions.json'
    dims=json.loads(dims_file.read_text())
    photos=[]
    with zipfile.ZipFile(ARCHIVE) as z:
        names=set(z.namelist())
        expected=[f'polka-dot-cat-eye-idea-{i:02d}.webp' for i in range(1,22)]
        missing=[x for x in expected if x not in names]
        if missing:raise ValueError(f'Archive missing manicure photos: {missing}')
        for i,name in enumerate(expected,1):
            img=Image.open(io.BytesIO(z.read(name))).convert('RGB')
            if min(img.size)<200:raise ValueError(f'Image too small: {name}')
            path=f'assets/generated/{SLUG}-idea-{i:02d}.webp'
            img.save(ROOT/path,'WEBP',quality=91,method=6)
            dims[path]=list(img.size)
            photos.append(img)
    # Six genuine photos on the hero collage, not a recolored stock nail.
    cover=Image.new('RGB',(1200,900),'#fcf8f5')
    for k,i in enumerate([0,1,3,7,9,13]):
        im=photos[i]
        target=im.resize((400,450),Image.Resampling.LANCZOS)
        cover.paste(target,((k%3)*400,(k//3)*450))
    cp=f'assets/generated/{SLUG}-cover.webp'
    cover.save(ROOT/cp,'WEBP',quality=90,method=6)
    dims[cp]=[1200,900]
    dims_file.write_text(json.dumps(dims,indent=2)+'\n',encoding='utf-8')
    print('INSTALLED 21 individually-matched original nail photos and collage cover')

if __name__=='__main__':main()
