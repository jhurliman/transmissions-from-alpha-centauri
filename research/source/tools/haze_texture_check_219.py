from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/haze-texture-219';base=R/'art/studies/scene-direction-218/current-sun/main-4k.png';candidate=O/'main-4k.png'
A=Image.open(base).convert('RGB');B=Image.open(candidate).convert('RGB');a=np.asarray(A);b=np.asarray(B);assert a.shape==b.shape==(2885,3840,3)
report={'baseline':str(base.relative_to(R)),'candidate':str(candidate.relative_to(R)),'characters':{},'regions':{}}
for row in json.loads((R/'art/studies/pixel-characters-217/assets.json').read_text()):
 target=np.asarray(Image.open(R/row['placed_canvas']).convert('RGBA'));mask=target[:,:,3]==255;err=np.abs(b[mask].astype(int)-target[:,:,:3][mask].astype(int));report['characters'][row['name']]={'max_channel_error':int(err.max()),'changed_pixels':int(np.count_nonzero(np.any(err,axis=1))),'pixel_count':int(mask.sum())};assert not err.any()
for name,box in {'street':(1180,700,2690,1600),'warm_bank':(1500,950,2370,1200),'near_left':(150,500,1000,1750),'sky':(1400,0,2600,130)}.items():
 x1,y1,x2,y2=box;x=a[y1:y2,x1:x2].astype(float);y=b[y1:y2,x1:x2].astype(float);diff=y-x;report['regions'][name]={'bounds':box,'baseline_mean_rgb':x.mean(axis=(0,1)).tolist(),'candidate_mean_rgb':y.mean(axis=(0,1)).tolist(),'mean_rgb_delta':diff.mean(axis=(0,1)).tolist(),'mean_abs_channel_delta':float(np.abs(diff).mean()),'max_channel_delta':float(np.abs(diff).max()),'changed_pixels':int(np.count_nonzero(np.any(diff,axis=2)))}
for name,im in [('before',A),('after',B)]:
 im.crop((1180,700,2690,1600)).save(O/(name+'-street.png'));im.resize((1920,1442),Image.Resampling.LANCZOS).save(O/(name+'-display.jpg'),quality=95);ImageOps.grayscale(im).resize((1440,1082)).save(O/(name+'-gray.png'))
(O/'pixel-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
