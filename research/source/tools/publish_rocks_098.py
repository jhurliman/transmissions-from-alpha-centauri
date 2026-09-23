from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'art/studies/rocks-098'
a=Image.open(R/'art/studies/soil-097/main.png');b=Image.open(O/'main.png')
for region,box in [('left',(0,480,550,780)),('right',(890,470,1440,790))]:
 for label,im in [('before',a),('after',b)]:im.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2)).save(O/f'{region}-{label}.png')
b.convert('L').save(O/'grayscale.png')
s='''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>098 · Foundation rock placement</title><style>body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;margin:32px auto;max-width:1450px;padding:0 22px}a{color:#efbc91}img{width:100%;display:block}figure{margin:0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}section{margin:35px 0}button{padding:12px;font:inherit;background:#45404a;color:white;border:1px solid #88776b;cursor:pointer}</style><h1>098 · Rocks gathered at the foundations</h1><p>Larger fragments gather against the building faces, with smaller pieces spread across the light soil. The approved dark road and its small stones are locked.</p><p><a href="#detail">Foundation details</a> · <a href="/art/studies/rocks-098/scene.blend">Editable scene</a></p><button onclick="document.getElementById('main').src='/art/studies/soil-097/main.png'">Before · 097</button> <button onclick="document.getElementById('main').src='/art/studies/rocks-098/main.png'">After · 098</button><img id="main" src="/art/studies/rocks-098/main.png">'''
for region in ['left','right']:
 s+=f'<section id="{"detail" if region=="left" else "right"}"><h2>{region.title()} foundations</h2><div class="grid">'
 for label in ['before','after']:s+=f'<figure><a href="/art/studies/rocks-098/{region}-{label}.png"><img src="/art/studies/rocks-098/{region}-{label}.png"></a><figcaption>{label.title()}</figcaption></figure>'
 s+='</div></section>'
s+='<section><h2>Reference · accumulation around buildings</h2><img src="/art/reviews/xenon-075/reference-ground.png"></section></html>'
(R/'prototype/review-098.html').write_text(s);(R/'prototype/index.html').write_text(s)
