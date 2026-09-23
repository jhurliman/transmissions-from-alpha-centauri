"""Presentation-only native render derivatives; never alters the Blender source."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'art/studies/colosseum-scale-210';source=R/'art/studies/scene-completion-209/main-4k.png'
im=Image.open(source).convert('RGB');baseline=im.resize((1920,1442),Image.Resampling.LANCZOS);baseline.save(O/'baseline/preview.png')
(O/'baseline/preview-source.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_dimensions':list(im.size),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'preview_dimensions':list(baseline.size),'operation':'Lanczos downsample of actual native209 render only'},indent=2))
frames=[]
for key in ['baseline','10','20','70']:
 p=O/key/'preview.png'
 if not p.exists():continue
 frame=Image.open(p).convert('RGB');ImageOps.grayscale(frame).save(O/key/'grayscale.png');frame.crop((590,0,1360,675)).save(O/key/'landmark-sun.png');frame.crop((325,30,490,550)).save(O/key/'foreground-ink.png');frames.append((key,frame))
if len(frames)==4:
 sheet=Image.new('RGB',(1600,1262),'#1b1920');draw=ImageDraw.Draw(sheet)
 for i,(key,frame)in enumerate(frames):
  x=(i%2)*800;y=(i//2)*631;sheet.paste(frame.resize((800,601),Image.Resampling.LANCZOS),(x,y+30));draw.text((x+12,y+8),'Current'if key=='baseline'else key+'% of sky gap filled',fill='#eeddda')
 sheet.save(O/'comparison.png')
print('210 presentation images:',len(frames))
held=O/'held-thin-ink-10/preview.png'
if held.exists() and (O/'10/preview.png').exists():
 proof=Image.new('RGB',(495,545),'#1b1920');d=ImageDraw.Draw(proof)
 for i,(label,path)in enumerate([('209 baseline',O/'baseline/preview.png'),('Held thin ink',held),('Corrected native10%',O/'10/preview.png')]):
  crop=Image.open(path).convert('RGB').crop((325,30,490,550));proof.paste(crop,(165*i,25));d.text((165*i+7,6),label,fill='#eeddda')
 proof.save(O/'ink-width-check.png')
# Fixed sun-window pixel coverage is supplemental evidence, not a lighting/material edit.
import numpy as np
sun={}
for key,frame in frames:
 arr=np.asarray(frame.crop((1090,65,1165,145)))
 mask=(arr[:,:,0]>215)&(arr[:,:,1]>155)&(arr[:,:,2]<175)
 sun[key]={'yellow_disk_pixels':int(mask.sum()),'preview_bounds':[1090,65,1165,145]}
for key,row in sun.items():row['area_relative_to_baseline']=row['yellow_disk_pixels']/sun['baseline']['yellow_disk_pixels']
(O/'sun-coverage.json').write_text(json.dumps(sun,indent=2))
