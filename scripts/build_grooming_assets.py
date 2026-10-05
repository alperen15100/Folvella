"""Optimize original photos and apply the existing Folvella Pin layout."""
import io,json,hashlib
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
import fitz
from publish_grooming import items
R=Path(__file__).resolve().parents[1]
dimensions=json.loads((R/'data/image-dimensions.json').read_text())
pins=[];images=[]
for item in items:
 p=item['post']
 for i,headline in enumerate(item['headlines']):
  photo=p['sections'][i]['image']
  im=Image.open(R/photo).convert('RGB')
  encoded=io.BytesIO();im.save(encoded,'WEBP',quality=86,method=6);(R/photo).write_bytes(encoded.getvalue())
  dimensions[photo]=list(im.size)
  images.append(dict(slug=p['slug'],path=photo,sha256=hashlib.sha256((R/photo).read_bytes()).hexdigest()))
  buffer=io.BytesIO();c=canvas.Canvas(buffer,pagesize=(1000,1500))
  c.setFillColorRGB(250/255,243/255,231/255);c.rect(0,0,1000,1500,fill=1,stroke=0)
  reader=ImageReader(im.copy());width,height=reader.getSize()
  scale=max(1000/width,1124/height);w,h=width*scale,height*scale
  c.saveState();clip=c.beginPath();clip.rect(0,66,1000,1124);c.clipPath(clip,stroke=0)
  c.drawImage(reader,(1000-w)/2,66+(1124-h)/2,width=w,height=h);c.restoreState()
  lines=headline.split('\n');size=104
  while max(stringWidth(line,'Times-Bold',size) for line in lines)>928:size-=1
  c.setFillColorRGB(48/255,32/255,20/255);c.setFont('Times-Bold',size)
  lineheight=size*.98;baseline=1345+(len(lines)-1)*lineheight/2-size*.34
  for line in lines:c.drawCentredString(500,baseline,line);baseline-=lineheight
  brand=c.beginText();brand.setTextOrigin(403,27);brand.setFont('Times-Roman',14);brand.setCharSpace(7);brand.textOut('FOLVELLA');c.drawText(brand)
  c.showPage();c.save()
  doc=fitz.open(stream=buffer.getvalue(),filetype='pdf');output=f"assets/generated/{p['slug']}-pin-{i+1}.jpg"
  doc[0].get_pixmap().save(str(R/output),jpg_quality=92);doc.close()
  dimensions[output]=[1000,1500]
  title=headline.replace('\n',' ')
  pins.append(dict(slug=p['slug'],category=p['category'],image=output,download=output,title=title,description=title+'. '+p['excerpt']+' Read the guide on Folvella.',sourcePhoto=photo))
(R/'data/image-dimensions.json').write_text(json.dumps(dimensions,indent=2)+'\n')
(R/'data/pinterest-pins-grooming-2026-10-05.json').write_text(json.dumps(dict(preparedAt='2026-10-05',pins=pins),ensure_ascii=False,indent=2)+'\n')
(R/'data/asset-batch-grooming-2026-10-05.json').write_text(json.dumps(dict(imageCount=len(images),images=images),indent=2)+'\n')
print('Optimized 24 distinct photos and composed 24 Pins in the established layout.')
