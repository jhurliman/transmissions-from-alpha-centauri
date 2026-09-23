from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scene-direction-218';report={'characters':{},'native_resolution':[3840,2885]}
frames={k:np.array(Image.open(O/k/'main-4k.png').convert('RGB'))for k in('current-sun','right-sun')}
assets=json.loads((R/'art/studies/pixel-characters-217/assets.json').read_text())
for name,a in frames.items():
 assert a.shape==(2885,3840,3)
 report['characters'][name]={}
 for row in assets:
  target=np.array(Image.open(R/row['placed_canvas']).convert('RGBA'));mask=target[:,:,3]==255
  err=np.abs(a[mask].astype(int)-target[:,:,:3][mask].astype(int));colors=len(np.unique(a[mask],axis=0))
  report['characters'][name][row['name']]={'max_channel_error':int(err.max()),'changed_pixels':int(np.count_nonzero(np.any(err,axis=1))),'colors':colors,'pixel_count':int(mask.sum())}
  assert not err.any(),report['characters'][name][row['name']]
a,b=frames.values();diff=np.max(np.abs(a.astype(int)-b.astype(int)),axis=2);coords=np.argwhere(diff>0)
report['sun_comparison']={'changed_pixels':len(coords),'bounds_xyxy':[int(coords[:,1].min()),int(coords[:,0].min()),int(coords[:,1].max()+1),int(coords[:,0].max()+1)]if len(coords)else None}
outside=diff.copy();outside[100:330,2160:2440]=0
report['sun_comparison']['outside_sun_changed_pixels']=int(np.count_nonzero(outside))
report['sun_comparison']['outside_sun_max_channel_error']=int(outside.max())
report['sun_comparison']['outside_sun_mean_max_channel_error']=float(outside.mean())
(O/'pixel-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
