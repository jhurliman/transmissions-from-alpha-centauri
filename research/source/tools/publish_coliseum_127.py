from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-127';p='/art/studies/coliseum-127/'
regions={'detail':(1350,320,2690,1230),'joins':(1590,620,2180,1080),'pipe':(1110,335,1640,1250)}
for label,path in [('before',R/'art/studies/coliseum-126/main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(path)
 for name,box in regions.items():im.crop(box).save(O/(label+'-'+name+'.png'))
 im.convert('L').resize((1440,1082)).save(O/(label+'-gray.png'))
 if label=='after':im.resize((1440,1082),Image.Resampling.LANCZOS).save(O/'main.png')
style='body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;max-width:1500px;margin:32px auto;padding:0 22px}a{color:#efbc91}img{width:100%;display:block}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:22px 0}figcaption{color:#c5bbc4}@media(max-width:800px){.pair{grid-template-columns:1fr}}'
h=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>127 · Consistent spacing and continuous walls</title><style>{style}</style><h1>127 · Consistent spacing and continuous walls</h1><p>The oversized margins beside the large pillars now match the small clearances beside the round columns. The three-arch groups remain, with the surplus width removed.</p><p>Arch walls and the flat masonry behind the columns now join into continuous surfaces, with consistent shading and regenerated contact ink. The selected left pipe receiver is 66% as deep; its width and the pipe diameter are unchanged, and the route is pulled toward the building.</p><p><a href="#detail">Spacing</a> · <a href="#joins">Wall joins</a> · <a href="#pipe">Recessed pipe</a> · <a href="{p}main-4k.png">4K image</a> · <a href="{p}scene.blend">Editable scene</a> · <a href="{p}kit.blend">Reusable kit</a></p><img src="{p}main.png">'''
for name,title in [('detail','Arch spacing'),('joins','Continuous wall joins'),('pipe','Recessed pipe assembly')]:
 h+=f'<section id="{name}"><h2>{title}</h2><div class="pair"><figure><img src="{p}before-{name}.png"><figcaption>126</figcaption></figure><figure><img src="{p}after-{name}.png"><figcaption>127</figcaption></figure></div></section>'
h+=f'<details><summary>Untextured geometry proof</summary><img src="{p}clay.png"></details><details><summary>Grayscale comparison</summary><div class="pair"><img src="{p}before-gray.png"><img src="{p}after-gray.png"></div></details><p>Painted masonry grain is more legible at 4K, with quieter deep arch interiors. Two detached crown specks are removed. Sky targets and cloud palette are preserved. Broader damage and connected weathering remain in development; the centerpiece is not locked.</p></html>'
(R/'prototype/review-127.html').write_text(h)
