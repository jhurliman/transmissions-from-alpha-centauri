from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-163';a=Image.open(R/'art/studies/coliseum-159/main-4k.png').convert('RGB');b=Image.open(O/'main-4k.png').convert('RGB');aa=np.array(a).astype('int16');bb=np.array(b).astype('int16');assert aa.shape==bb.shape==(2885,3840,3)
d=np.abs(bb-aa).max(2);outside=np.ones(d.shape,bool);outside[300:1300,1250:2500]=False;lab,n=label((d>4)&outside);rows=[]
for k,sl in enumerate(find_objects(lab),1):
 if sl is None:continue
 size=int((lab[sl]==k).sum());yy,xx=sl;box=[xx.start,yy.start,xx.stop,yy.stop];rows.append({'id':k,'pixels':size,'box':box})
 if size>=4:
  box=(max(0,xx.start-20),max(0,yy.start-20),min(3840,xx.stop+20),min(2885,yy.stop+20));x=a.crop(box);y=b.crop(box);im=Image.new('RGB',(x.width*2,x.height));im.paste(x,(0,0));im.paste(y,(x.width,0));im.resize((im.width*5,im.height*5)).save(O/f'outside-{k}.png')
r={'baseline':'159main-4k.png','native_size':[3840,2885],'landmark_region':[1250,300,2500,1300],'outside_landmark_pixels_over4':int(((d>4)&outside).sum()),'outside_landmark_max_channel_delta':int(d[outside].max()),'outside_regions':rows,'note':'Inspect all meaningful outside regions; geometry/data preservation does not imply identical Freestyle raster.'}
for name,box in [('crown',(1930,435,2085,605)),('primary',(1665,520,1940,785)),('secondary',(2065,540,2300,790))]:
 x0,y0,x1,y1=box;delta=d[y0:y1,x0:x1];r[name]={'crop':box,'pixels_over4':int((delta>4).sum()),'max_channel_delta':int(delta.max())}
(O/'pixel-comparison.json').write_text(json.dumps(r,indent=2));Image.fromarray(np.clip(np.abs(bb-aa)*6,0,255).astype('uint8')).resize((1440,1082)).save(O/'difference-6x.png');print(json.dumps(r,indent=2))
