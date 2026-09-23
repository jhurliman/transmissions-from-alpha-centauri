from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-panel-257'
a=np.asarray(Image.open(R/'art/studies/gallery-sills-256/main-4k.png').convert('RGB')).astype(np.int16);b=np.asarray(Image.open(O/'main-4k.png').convert('RGB')).astype(np.int16)
d=np.max(np.abs(a-b),axis=2);outside=np.ones(d.shape,dtype=bool)
outside[1120:1445,2580:2760]=False;outside[1400:2050,2350:3700]=False
rows=[]
for label,mask in [('outside_edit_areas',outside),('frame_border',np.indices(d.shape)[1]<30)]:
 vals=d[mask];rows.append({'region':label,'pixels':int(mask.sum()),'difference_over_32':int((vals>32).sum()),'mean_max_channel_difference':float(vals.mean())})
(O/'image-difference.json').write_text(json.dumps(rows,indent=2))
# Bright false-color image locates contour differences for manual review.
q=np.zeros((*d.shape,3),dtype=np.uint8);q[d>32]=[255,70,120];q[~outside]=[30,60,100];Image.fromarray(q).resize((960,721)).save(O/'difference-overview.png')
for name in ['panel','soil']:
 before=Image.open(O/f'comparison/before-{name}.png').convert('L');after=Image.open(O/f'comparison/after-{name}.png').convert('L');im=Image.new('L',(before.width*2,before.height));im.paste(before,(0,0));im.paste(after,(before.width,0));im.save(O/f'{name}-grayscale.png')
print(json.dumps(rows))
