from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-100'
a=Image.open(R/'art/studies/density-099/main.png');b=Image.open(O/'main.png')
for region,box in [('foundation',(880,470,1260,630)),('distance',(520,300,950,485))]:
 for label,im in [('before',a),('after',b)]:im.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3)).save(O/f'{region}-{label}.png')
b.convert('L').save(O/'grayscale.png')
s='''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>100 · A continuous distant street</title><style>body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;margin:32px auto;max-width:1450px;padding:0 22px}a{color:#efbc91}img{width:100%;display:block}figure{margin:0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}section{margin:35px 0}button{padding:12px;font:inherit;background:#45404a;color:white;border:1px solid #88776b;cursor:pointer}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>100 · A continuous distant street</h1><p>Inward-facing skyscrapers form two continuous sides of the street. The roadway stays clear as it recedes toward the landmark. The approved dark road, alley buildings and sky remain locked.</p><p><a href="#distance">Distant city</a> · <a href="/art/studies/city-100/scene.blend">Editable scene</a></p><button onclick="document.getElementById('main').src='/art/studies/density-099/main.png'">Before · 099</button> <button onclick="document.getElementById('main').src='/art/studies/city-100/main.png'">After · 100</button><img id="main" src="/art/studies/city-100/main.png">'''
for region,title in [('distance','Continuous street fronts')]:
 s+=f'<section id="{region}"><h2>{title}</h2><div class="grid">'
 for label in ['before','after']:s+=f'<figure><a href="/art/studies/city-100/{region}-{label}.png"><img src="/art/studies/city-100/{region}-{label}.png"></a><figcaption>{label.title()}</figcaption></figure>'
 s+='</div></section>'
s+='</html>';(R/'prototype/review-100.html').write_text(s);(R/'prototype/index.html').write_text(s)
