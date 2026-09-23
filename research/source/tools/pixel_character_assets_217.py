"""Lossless integer-grid placement of the user-selected214sprites; no generated edits."""
from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parents[1];src=R/'art/studies/characters-spacesuit-214';O=R/'art/studies/pixel-characters-217';O.mkdir(exist_ok=True);rows=[]
audit=json.loads((src/'composite-audit.json').read_text())
for name,h in [('airam',98),('miranda',94)]:
 p=src/'pixel'/f'{name}-{h}h-24c.png';im=Image.open(p).convert('RGBA');box=im.getchannel('A').getbbox();body=im.crop(box);body=body.resize((body.width*5,body.height*6),Image.Resampling.NEAREST)
 row=next(q for q in audit if q['variant']=='pixel-double' and q['character']==name);x,y,xx,yy=row['bbox'];assert body.size==(xx-x,yy-y)
 canvas=Image.new('RGBA',(3840,2885),(0,0,0,0));canvas.alpha_composite(body,(x,y));dest=O/f'{name}-placed-4k.png';canvas.save(dest)
 rows.append({'name':name,'source_sprite':str(p.relative_to(R)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'placed_canvas':str(dest.relative_to(R)),'canvas_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'body_bbox':row['bbox'],'grid_body_height':h,'integer_scale':[5,6],'dos_pixel_aspect':1.2,'palette_colors':24,'alpha':[0,255],'world_foot_assumption':[-.30 if name=='airam' else .55,-6.5,.005],'height_assumption_m':1.72 if name=='airam' else 1.65})
(O/'assets.json').write_text(json.dumps(rows,indent=2))
