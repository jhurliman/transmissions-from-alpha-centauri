from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/arcade-tunnels-220'
a=np.array(Image.open(O/'main-4k.png').convert('RGB'));assert a.shape==(2885,3840,3)
report={'resolution':[3840,2885],'characters':{}}
for row in json.loads((R/'art/studies/pixel-characters-217/assets.json').read_text()):
 target=np.array(Image.open(R/row['placed_canvas']).convert('RGBA'));mask=target[:,:,3]==255;error=np.abs(a[mask].astype(int)-target[:,:,:3][mask].astype(int));assert not error.any(),row['name']
 report['characters'][row['name']]={'exact_selected_pixels':True,'colors':len(np.unique(a[mask],axis=0))}
b=np.array(Image.open(R/'art/studies/haze-texture-219/main-4k.png').convert('RGB'));delta=np.max(abs(a.astype(int)-b.astype(int)),axis=2);xy=np.argwhere(delta>16)
report['comparison_with_219']={'pixels_changed_over16':len(xy),'bounds_xyxy':[int(xy[:,1].min()),int(xy[:,0].min()),int(xy[:,1].max()+1),int(xy[:,0].max()+1)]if len(xy)else None}
(O/'root-pixel-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
