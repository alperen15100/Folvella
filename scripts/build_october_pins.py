"""Compose the October photo Pins with the established cream/serif layout."""
import io,json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
import fitz

root=Path(__file__).resolve().parents[1]
posts=json.loads((root/'data/posts.json').read_text())
headlines=json.loads((root/'data/october-pin-headlines.json').read_text())
pins=[]
for post in posts:
 if post['slug'] not in headlines: continue
 for i,headline in enumerate(headlines[post['slug']]):
  source=post['sections'][i]['image']
  buffer=io.BytesIO();c=canvas.Canvas(buffer,pagesize=(1000,1500))
  c.setFillColorRGB(250/255,243/255,231/255);c.rect(0,0,1000,1500,fill=1,stroke=0)
  reader=ImageReader(str(root/source));width,height=reader.getSize()
  scale=max(1000/width,1124/height);w,h=width*scale,height*scale
  c.saveState();clip=c.beginPath();clip.rect(0,66,1000,1124);c.clipPath(clip,stroke=0)
  c.drawImage(reader,(1000-w)/2,66+(1124-h)/2,width=w,height=h);c.restoreState()
  lines=headline.split('\n');size=104
  while max(stringWidth(line,'Times-Bold',size) for line in lines)>928: size-=1
  c.setFillColorRGB(48/255,32/255,20/255);c.setFont('Times-Bold',size)
  lineheight=size*.98;baseline=1345+(len(lines)-1)*lineheight/2-size*.34
  for line in lines: c.drawCentredString(500,baseline,line);baseline-=lineheight
  brand=c.beginText();brand.setTextOrigin(403,27);brand.setFont('Times-Roman',14);brand.setCharSpace(7);brand.textOut('FOLVELLA');c.drawText(brand)
  c.showPage();c.save()
  doc=fitz.open(stream=buffer.getvalue(),filetype='pdf')
  output=f"assets/generated/{post['slug']}-pin-{i+1}.jpg"
  doc[0].get_pixmap().save(str(root/output),jpg_quality=94);doc.close()
  title=headline.replace('\n',' ')
  pins.append(dict(slug=post['slug'],category=post['category'],image=output,download=output,title=title,description=title+'. '+post['excerpt']+' Read the full guide on Folvella.',sourcePhoto=source))
(root/'data/pinterest-pins-october-2026-10-05.json').write_text(json.dumps(dict(preparedAt='2026-10-05',pins=pins),ensure_ascii=False,indent=2)+'\n')
print(f'Rendered {len(pins)} distinct photo Pins for {len(headlines)} guides.')
