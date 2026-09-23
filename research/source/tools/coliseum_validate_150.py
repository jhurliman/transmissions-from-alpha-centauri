"""Check the full native material/visibility update against149."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-150'
a=np.array(Image.open(R/'art/studies/coliseum-149/main-4k.png').convert('RGB')).astype('int16');b=np.array(Image.open(O/'main-4k.png').convert('RGB')).astype('int16');assert a.shape==b.shape==(2885,3840,3)
d=np.abs(b-a).max(2);outside=np.ones(d.shape,bool);outside[300:1300,1250:2500]=False
expected_fix=np.zeros(d.shape,bool);expected_fix[820:885,225:295]=True
unexpected=outside&~expected_fix
r={'baseline':'149main-4k.png','native_size':[3840,2885],'landmark_region':[1250,300,2500,1300],'native_ink_fix_region':[225,820,295,885],'outside_region_pixels_over4':int(((d>4)&outside).sum()),'outside_landmark_and_ink_fix_pixels_over4':int(((d>4)&unexpected).sum()),'outside_landmark_and_ink_fix_max_channel_delta':int(d[unexpected].max()),'scope_note':'Full-frame raster check complements native geometry/material preservation; any unexpected region requires inspection.'}
for name,box in [('primary',(1680,525,1795,770)),('secondary',(2065,525,2165,785)),('ink',(225,820,295,885))]:
 x0,y0,x1,y1=box;delta=d[y0:y1,x0:x1];yy,xx=np.where(delta>4);r[name]={'crop':box,'pixels_over4':len(xx),'max_channel_delta':int(delta.max())}
(O/'pixel-comparison.json').write_text(json.dumps(r,indent=2));Image.fromarray(np.clip(np.abs(b-a)*6,0,255).astype('uint8')).resize((1440,1082)).save(O/'difference-6x.png');print(json.dumps(r,indent=2))
