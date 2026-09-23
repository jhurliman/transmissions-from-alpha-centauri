from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];P=R/'art/studies/pixel-characters-217';a=np.array(Image.open(P/'native-composite.png').convert('RGBA'));b=np.array(Image.open(R/'art/studies/characters-spacesuit-214/pixel-double-scene.png').convert('RGBA'));rows=json.loads((P/'assets.json').read_text());out=[]
for row in rows:
 x=np.array(Image.open(R/row['placed_canvas']).convert('RGBA'));m=x[:,:,3]>0;diff=np.abs(a[:,:,:3][m].astype(int)-x[:,:,:3][m].astype(int));out.append({'name':row['name'],'visible_pixel_count':int(m.sum()),'changed_character_pixels':int(np.any(diff,axis=1).sum()),'max_channel_error':int(diff.max()),'actual_colors':len(np.unique(a[:,:,:3][m],axis=0))})
d=np.abs(a.astype(int)-b.astype(int));audit={'rows':out,'whole_composite_changed_pixels':int(np.any(d,axis=2).sum()),'whole_composite_max_channel_error':int(d.max()),'sprites_exact':all(r['changed_character_pixels']==0 for r in out),'selected214comparison':'pixel-double-scene.png','native_output':'native-composite.png','no_half_pixel_sampling':all(r['actual_colors']==24 for r in out)}
(P/'pixel-proof.json').write_text(json.dumps(audit,indent=2));Image.fromarray(a).crop((1450,1660,2360,2470)).save(P/'native-detail.png');print(json.dumps(audit,indent=2))
assert audit['sprites_exact'] and audit['no_half_pixel_sampling']
