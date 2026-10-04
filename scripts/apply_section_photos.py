"""Keep the October guides in the established illustrated blog format."""
import json,hashlib,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def save(path,data): (ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main(records):
 posts=json.loads((ROOT/'data/posts.json').read_text());lookup={p['slug']:p for p in posts}
 dims=json.loads((ROOT/'data/image-dimensions.json').read_text())
 manifest_file=ROOT/'data/asset-batch-section-photos-2026-10-04.json'
 manifest=json.loads(manifest_file.read_text()) if manifest_file.exists() else dict(date='2026-10-04',imageCount=0,mode='built-in imagegen',images=[])
 images={r['path']:r for r in manifest['images']}
 for r in records:
  p=lookup[r['slug']];section=p['sections'][r['index']]
  path='assets/generated/'+r['slug']+'-section-'+str(r['index']+1).zfill(2)+'.webp';target=ROOT/path
  if path not in images:
   temporary=target.with_suffix('.tmp.webp')
   with Image.open(r['path']) as im: im.save(temporary,'WEBP',quality=82,method=6);dims[path]=list(im.size)
   temporary.replace(target)
   images[path]=dict(path=path,slug=p['slug'],section=r['index']+1,type='section',width=dims[path][0],height=dims[path][1],bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),prompt=r['prompt'])
  section.update(image=path,alt=r['scene'].split(', no ')[0],caption=section['heading'])
  p['dateModified']='2026-10-04'
  for field in ['sources','technicalReferences','trendEvidence']:p.pop(field,None)
 save('data/posts.json',posts);save('data/image-dimensions.json',dims)
 manifest['images']=list(images.values());manifest['imageCount']=len(images);save('data/asset-batch-section-photos-2026-10-04.json',manifest)
 # Keep the source batch consistent with the published guides for later rebuilds.
 drafts=json.loads((ROOT/'data/new-posts-october-expansion.json').read_text())
 for i,p in enumerate(drafts):drafts[i]=lookup[p['slug']]
 save('data/new-posts-october-expansion.json',drafts)
 print('Applied',len(records),'section photos;',len(images),'images in the saved batch.')
if __name__=='__main__':main(json.load(sys.stdin))
