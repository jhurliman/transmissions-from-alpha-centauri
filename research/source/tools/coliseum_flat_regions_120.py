"""Rank contiguous low-variation regions at native4K; candidates require visual review."""
from pathlib import Path
import json,csv
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-120/analysis'
im=Image.open(R/'art/studies/coliseum-119/main-4k.png').convert('RGB')
a=np.asarray(im).astype(np.float32)
mask=np.asarray(Image.open(O/'landmark-mask.png').convert('RGB'))[:,:,0]>240
mask=ndi.binary_erosion(mask,iterations=2)
mean=ndi.uniform_filter(a,size=(5,5,1))
var=np.maximum(ndi.uniform_filter(a*a,size=(5,5,1))-mean*mean,0)
std=np.sqrt(var).max(axis=2)
flat=mask&(std<1.25)
labels,count=ndi.label(flat)
sizes=np.bincount(labels.ravel());sizes[0]=0
ranked=np.argsort(sizes)[::-1]
regions=[]
for label in ranked:
    if sizes[label]<40 or len(regions)>=24:break
    yy,xx=np.where(labels==label)
    x0,x1,y0,y1=int(xx.min()),int(xx.max()+1),int(yy.min()),int(yy.max()+1)
    pixels=a[yy,xx]
    region={'rank':len(regions)+1,'pixels':int(sizes[label]),'bounds_xyxy':[x0,y0,x1,y1],
            'mean_rgb':np.round(pixels.mean(axis=0),2).tolist(),
            'mean_local_std_0_255':round(float(std[yy,xx].mean()),3),
            'fill_fraction':round(len(xx)/((x1-x0)*(y1-y0)),3),
            'review_status':'Candidate only; intentional painted shadow regions may be retained.'}
    regions.append(region)
    pad=14
    crop=im.crop((max(0,x0-pad),max(0,y0-pad),min(im.width,x1+pad),min(im.height,y1+pad)))
    crop.save(O/f'region-{len(regions):02d}.png')
exact_range=ndi.maximum_filter(a,size=(3,3,1))-ndi.minimum_filter(a,size=(3,3,1))
exact=mask&(exact_range.max(axis=2)==0)
stats={'source':'119/main-4k.png','mask':'Geometry-rendered visible landmark, eroded2px',
       'resolution':list(im.size),'masked_pixels':int(mask.sum()),
       'low_variation_5x5_pixels':int(flat.sum()),'low_variation_fraction':round(float(flat.sum()/mask.sum()),4),
       'exact_constant_3x3_pixels':int(exact.sum()),
       'threshold':'Maximum per-channel local5x5 standard deviation <1.25 on0–255 RGB; components >=40pixels.',
       'interpretation':'Detection ranks candidates, not defects. Review surface role, reference relief, and repeated straight forms. Do not fill every region with noise.',
       'regions':regions}
(O/'flat-regions.json').write_text(json.dumps(stats,indent=2))
with (O/'flat-regions.csv').open('w')as f:
    w=csv.writer(f);w.writerow(['rank','pixels','x0','y0','x1','y1','mean_local_std'])
    for r in regions:w.writerow([r['rank'],r['pixels'],*r['bounds_xyxy'],r['mean_local_std_0_255']])
# A diagnostic overlay, never an artwork replacement.
overlay=im.copy();draw=ImageDraw.Draw(overlay)
for r in regions:
    x0,y0,x1,y1=r['bounds_xyxy'];draw.rectangle((x0,y0,x1,y1),outline='#28ffff',width=2)
    draw.rectangle((x0,y0-15,x0+25,y0),fill='#10252a');draw.text((x0+3,y0-13),str(r['rank']),fill='white')
ys,xs=np.where(mask)
bounds=(max(0,int(xs.min())-20),max(0,int(ys.min())-20),min(im.width,int(xs.max())+20),min(im.height,int(ys.max())+20))
overlay.crop(bounds).save(O/'flat-region-map.png')
print(json.dumps({k:v for k,v in stats.items()if k!='regions'}))
