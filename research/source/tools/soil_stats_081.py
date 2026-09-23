from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-081'
im=Image.open(R/'references/user-soil-study/dark-soil-detail.png').convert('RGB');roi=(900,450,1160,570);crop=im.crop(roi);crop.save(O/'reference-clean.png')
a=np.asarray(crop);colors,counts=np.unique(a.reshape(-1,3),axis=0,return_counts=True);order=np.argsort(-counts)
(O/'reference-full-palette.json').write_text(json.dumps([{'rgb':c.tolist(),'count':int(n)} for c,n in zip(colors[order],counts[order])]))
def stats(im):
 a=np.asarray(im).astype(float);y=a@np.array([.2126,.7152,.0722]);out={'size':im.size,'mean_rgb':a.mean((0,1)).tolist(),'std_rgb':a.std((0,1)).tolist(),'percentiles_rgb':np.percentile(a.reshape(-1,3),[1,5,25,50,75,95,99],axis=0).tolist(),'luma_std':float(y.std()),'gradient_xy':[float(np.abs(np.diff(y,axis=i)).mean()) for i in (1,0)]}
 out['blur_residual_std']={str(s):float((a-np.asarray(im.filter(ImageFilter.GaussianBlur(s)))).std()) for s in (1,2,4,8,16)};return out
(O/'reference-statistics.json').write_text(json.dumps({'roi':roi,**stats(crop)},indent=2));print(json.dumps(stats(crop),indent=2))
