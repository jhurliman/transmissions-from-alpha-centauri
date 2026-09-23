from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/duct-infill-254';C=O/'comparison';C.mkdir(exist_ok=True)
for label,path in [('before',R/'art/studies/duct-mounts-253/main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(path).convert('RGB');im.resize((1920,1442),Image.Resampling.LANCZOS).save(C/(label+'-full.jpg'),quality=96)
 for name,box in [('arcade',(2690,70,2980,1390))]:im.crop(box).save(C/(label+'-'+name+'.png'))
assert (C/'before-full.jpg').read_bytes()!=(C/'after-full.jpg').read_bytes()
b=np.asarray(Image.open(O/'main-4k.png').convert('RGB'));checks={}
for row in json.loads((R/'art/studies/pixel-characters-217/assets.json').read_text()):
 target=np.asarray(Image.open(R/row['placed_canvas']).convert('RGBA'));mask=target[:,:,3]==255;assert np.array_equal(b[mask],target[:,:,:3][mask]);checks[row['name']]='exact'
(O/'pixel-check.json').write_text(json.dumps(checks,indent=2))
(R/'prototype/review-254.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>254 · Forward-set duct entry panel</title><style>body{margin:0;background:#191820;color:#e4ded7;font:16px system-ui}main{max-width:1500px;margin:auto;padding:24px}h1{font-size:25px}p{line-height:1.5;color:#c3bab4}button{background:#33303e;color:inherit;border:1px solid #777080;padding:12px 18px;border-radius:6px;cursor:pointer;margin:4px}button.active{background:#775347}img{display:block;width:100%;height:auto;margin:18px auto}#arcade{max-width:580px}#soil{max-width:1100px}a{color:#e8c8a4}</style><main><h1>254 · Forward-set duct entry panel</h1><p>The solid entry panel is brought forward by 55 cm, with its duct collar seated on the new face.</p><button onclick="choose('before')">Before · 253</button><button onclick="choose('after')">After · 254</button><h2>Duct entry and four side-wall returns</h2><img id="arcade" alt="Duct bracket and entry architecture"><h2>Whole scene</h2><img id="full" alt="Whole scene"><p><a href="../art/studies/duct-infill-254/main-4k.png">Full-resolution scene</a> · <a href="../art/studies/duct-infill-254/scene.blend">Editable scene</a></p></main><script>function choose(v){document.querySelectorAll('button').forEach((b,i)=>b.classList.toggle('active',i===(v==='before'?0:1)));for(let id of ['arcade','full'])document.getElementById(id).src='../art/studies/duct-infill-254/comparison/'+v+'-'+id+(id==='full'?'.jpg':'.png')+'?v=254';location.hash=v}function sync(){choose(location.hash==='#before'?'before':'after')}addEventListener('hashchange',sync);sync()</script></html>''')
print('254 published; exact characters verified')
