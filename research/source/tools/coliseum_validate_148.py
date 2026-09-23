"""Final native render comparisons; pixel checks complement, not replace, scene preservation."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-148'
a=np.array(Image.open(R/'art/studies/alley-weathering-147/actual/main-4k.png').convert('RGB')).astype('int16')
b=np.array(Image.open(O/'main-4k.png').convert('RGB')).astype('int16')
assert a.shape==b.shape==(2885,3840,3)
d=np.abs(b-a).max(2);outside=np.ones(d.shape,bool);outside[300:1300,1250:2500]=False
r={'baseline':'147 actual/main-4k.png','native_size':[3840,2885],'landmark_region':[1250,300,2500,1300],'outside_region_pixels_over_4':int(((d>4)&outside).sum()),'outside_region_pixels_over_12':int(((d>12)&outside).sum()),'outside_region_max_channel_delta':int(d[outside].max()),'note':'Region includes whole visible landmark. Geometry preservation is separately recorded; raster differences outside it require inspection.'}
for name,box in [('age',(1720,480,2120,850)),('cornice',(1680,710,1835,840))]:
 x0,y0,x1,y1=box;delta=d[y0:y1,x0:x1];yy,xx=np.where(delta>4);r[name]={'crop':box,'pixels_over_4':len(xx),'max_channel_delta':int(delta.max())}
(O/'pixel-comparison.json').write_text(json.dumps(r,indent=2)+'\n')
Image.fromarray(np.clip(np.abs(b-a)*6,0,255).astype('uint8')).resize((1440,1082)).save(O/'difference-6x.png')
print(json.dumps(r,indent=2))
