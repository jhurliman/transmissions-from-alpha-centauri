from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/entry-surround-229';C=O/'comparison';C.mkdir(exist_ok=True)
ims=[]
for label,path in [('before',R/'art/studies/ground-weathering-steps-228/main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(path).convert('RGB');ims.append(np.asarray(im));im.crop((2860,1160,3180,1570)).save(C/(label+'-entry.png'));im.resize((1920,1442),Image.Resampling.LANCZOS).save(C/(label+'-full.jpg'),quality=96)
a,b=ims;garage=(2440,1160,2720,1410);x,y,X,Y=garage;assert np.array_equal(a[y:Y,x:X],b[y:Y,x:X]),'garage changed'
characters={}
for row in json.loads((R/'art/studies/pixel-characters-217/assets.json').read_text()):
 target=np.asarray(Image.open(R/row['placed_canvas']).convert('RGBA'));mask=target[:,:,3]==255;assert np.array_equal(b[mask],target[:,:,:3][mask]);characters[row['name']]='exact'
diff=np.any(a!=b,axis=2);yy,xx=np.where(diff)
(O/'pixel-check.json').write_text(json.dumps({'garage_crop_exact':True,'characters':characters,'changed_pixels':int(diff.sum()),'change_bounds':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]},indent=2))
(R/'prototype/review-229.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>229 · Warm entryway surround</title><style>body{margin:0;background:#191820;color:#e4ded7;font:16px system-ui}main{max-width:1400px;margin:auto;padding:24px}h1{font-size:24px}p{line-height:1.5;color:#c3bab4}button{background:#33303e;color:inherit;border:1px solid #777080;padding:12px 18px;border-radius:6px;cursor:pointer;margin:4px}button.active{background:#775347}img{display:block;max-width:100%;height:auto;margin:20px auto}#entry{width:640px;image-rendering:auto}#full{width:100%}a{color:#e8c8a4}</style><main><h1>229 · Warm entryway surround</h1><p>Continuous warm plaster around the recessed gate, retaining chips and scuffs. Garage and gate weathering are unchanged.</p><button onclick="choose('before',this)">Before · 228</button><button class="active" onclick="choose('after',this)">Warm surround · 229</button><img id="entry" src="../art/studies/entry-surround-229/comparison/after-entry.png" alt="Entryway surround close-up"><p><a href="../art/studies/entry-surround-229/main-4k.png">Full-resolution scene</a> · <a href="../art/studies/entry-surround-229/scene.blend">Editable scene</a></p><img id="full" src="../art/studies/entry-surround-229/comparison/after-full.jpg" alt="Whole scene"></main><script>function choose(v,b){document.querySelectorAll('button').forEach(x=>x.classList.remove('active'));b.classList.add('active');for(let id of ['entry','full'])document.getElementById(id).src='../art/studies/entry-surround-229/comparison/'+v+'-'+id+(id==='full'?'.jpg':'.png');location.hash=v}</script></html>''')
print('229 published and pixel preservation verified')
