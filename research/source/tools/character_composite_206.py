"""Review composites from indexed alpha sprites and the native-rendered clean scene plate."""
from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-206';A=O/'anime'
placement=json.loads((A/'placement.json').read_text());base=Image.open(A/'clean-background-4k.png').convert('RGBA');reports=[]
for mult,tag in [(1,'pixel-native'),(2,'pixel-double')]:
 canvas=base.copy()
 for row in placement:
  n=row['name'];h=(49 if n=='airam' else 47)*mult
  im=Image.open(O/'pixel'/f'{n}-{h}h-24c.png').convert('RGBA');im=im.crop(im.getchannel('A').getbbox())
  im=im.resize((im.width*(10//mult),im.height*(12//mult)),Image.Resampling.NEAREST)
  fx,fy=row['foot_pixel_4k'];xy=(round(fx-im.width/2),round(fy-im.height));canvas.alpha_composite(im,xy)
  reports.append({'variant':tag,'character':n,'bbox':[xy[0],xy[1],xy[0]+im.width,xy[1]+im.height],'scaling':[10//mult,12//mult],'palette_colors':24,'method':'Only nearest-neighbor integer enlargement and alpha-over onto native clean plate; no generated background or painted shadow.'})
 canvas.convert('RGB').save(O/f'{tag}-scene.png')
 canvas.crop((1450,1660,2360,2470)).save(O/f'{tag}-scene-detail.png')
(O/'composite-audit.json').write_text(json.dumps(reports,indent=2)+'\n')
