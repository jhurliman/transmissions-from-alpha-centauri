"""Review composites from indexed alpha sprites and the native-rendered clean scene plate."""
from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-spacesuit-214';A=O/'anime'
placement=json.loads((A/'placement.json').read_text());base=Image.open(R/'art/studies/characters-206/anime/clean-background-4k.png').convert('RGBA');reports=[]
for mult,tag in [(1,'pixel-native'),(2,'pixel-double')]:
 canvas=base.copy()
 for row in placement:
  n=row['name'];h=(49 if n=='traveler-a' else 47)*mult
  im=Image.open(O/'pixel'/f'{n}-{h}h-24c.png').convert('RGBA');im=im.crop(im.getchannel('A').getbbox())
  im=im.resize((im.width*(10//mult),im.height*(12//mult)),Image.Resampling.NEAREST)
  fx,fy=row['foot_pixel_4k'];xy=(round(fx-im.width/2),round(fy-im.height));canvas.alpha_composite(im,xy)
  reports.append({'variant':tag,'character':n,'bbox':[xy[0],xy[1],xy[0]+im.width,xy[1]+im.height],'scaling':[10//mult,12//mult],'palette_budget':24,'method':'Only nearest-neighbor integer enlargement and alpha-over onto native clean plate; no generated background or painted shadow.'})
 canvas.convert('RGB').save(O/f'{tag}-scene.png')
 canvas.crop((1450,1660,2360,2470)).save(O/f'{tag}-scene-detail.png')
(O/'composite-audit.json').write_text(json.dumps(reports,indent=2)+'\n')

# Native RGBA card pass over the existing verified proxy-free native209 plate.
import numpy as np
fg=Image.open(A/'native-lit-characters-4k.png').convert('RGBA')
canvas=Image.alpha_composite(base,fg);canvas.save(A/'scene-composite.png');canvas.crop((1450,1660,2360,2470)).save(A/'scene-detail.png')
a=np.array(fg);b=np.array(Image.open(A/'native-lowlight-characters-4k.png').convert('RGBA'));mask=(a[:,:,3]>240)&(b[:,:,3]>240);diff=np.abs(a[:,:,:3].astype(float)-b[:,:,:3].astype(float))[mask]
(A/'lighting-response-audit.json').write_text(json.dumps({'opaque_pixels':int(mask.sum()),'normal_energy':1,'lowlight_energy':.15,'mean_abs_rgb_change':diff.mean(0).tolist(),'max_abs_rgb_change':diff.max(0).tolist(),'method':'Actual native renders of same flat cards, only light energies change; no image relighting filter.'},indent=2))
