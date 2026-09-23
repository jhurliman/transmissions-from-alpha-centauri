from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-097';A='/art/studies/soil-097/'
paths={'clean':R/'art/studies/lines-096/main.png','stray':R/'art/studies/lines-096/main-unfiltered.png','refined':O/'main.png'};ims={k:Image.open(p).convert('RGB') for k,p in paths.items()}
for region,box in [('road',(340,490,1160,780)),('edge',(975,570,1225,685))]:
 for k,im in ims.items():im.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2)).save(O/f'{region}-{k}.png')
box=(250,480,1230,865);base=np.asarray(ims['clean'].crop(box)).astype(int);counts={}
for k in ['stray','refined']:
 d=base-np.asarray(ims[k].crop(box)).astype(int);counts[k]=int((d.mean(2)>10).sum())
(O/'density.json').write_text(json.dumps({'road_crop_new_dark_pixels':counts,'retained_ratio':counts['refined']/max(1,counts['stray'])},indent=2))
ims['refined'].convert('L').save(O/'grayscale.png')
def fig(path,label):return f'<figure><a href="{path}"><img src="{path}" alt="{label}" loading="lazy"></a><figcaption>{label}</figcaption></figure>'
s='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>097 · Broken soil ink</title><style>body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;margin:32px auto;max-width:1450px;padding:0 22px}a{color:#efbc91}figure{margin:0}img{width:100%;display:block}figcaption{padding:9px 0}section{margin:38px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}button{padding:12px;font:inherit;color:#eee;background:#45404a;border:1px solid #88776b;cursor:pointer}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>097 · Broken soil ink</h1><p>The little dark soil marks return, with squared corners broken apart into shorter, irregular, tapered fragments. The approved soil surface and scene ink remain in place.</p><p><a href="#detail">Road detail</a> · <a href="#edge">Former angular marks</a> · <a href="#reference">Reference</a> · <a href="/art/studies/soil-097/scene.blend">Editable scene</a></p>'''
for k,label in [('clean','Clean 096'),('stray','Original stray lines'),('refined','Refined soil ink')]:
 path={'clean':'/art/studies/lines-096/main.png','stray':'/art/studies/lines-096/main-unfiltered.png','refined':A+'main.png'}[k]
 s+=f'<button onclick="document.getElementById(\'main\').src=\'{path}\';document.getElementById(\'label\').textContent=\'{label}\'">{label}</button>'
s+='<p id="label">Refined soil ink</p><img id="main" src="'+A+'main.png">'
for region,title in [('road','Road detail'),('edge','Breaking up the angular marks')]:
 s+=f'<section id="{"detail" if region=="road" else "edge"}"><h2>{title}</h2><div class="grid">'+fig(A+region+'-stray.png','Original stray lines')+fig(A+region+'-refined.png','Refined fragments')+'</div></section>'
s+='<section id="reference"><h2>Reference · broken soil marks</h2>'+fig('/references/user-soil-study/dark-soil-detail.png','User-provided soil reference: grain interrupts directional dark creases.')+'</section><p>The added ink is a separate editable layer. Existing terrain, road fractures, soil palette, rocks, buildings and sky are unchanged.</p></html>'
(R/'prototype/review-097.html').write_text(s);(R/'prototype/index.html').write_text(s)
