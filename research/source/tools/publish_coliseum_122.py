from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-122';p='/art/studies/coliseum-122/'
for name,path in [('before',R/'art/studies/coliseum-120/main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(path);im.crop((1400,350,2510,1140)).save(O/(name+'-detail.png'));im.crop((1750,420,2400,700)).save(O/(name+'-upper.png'));im.convert('L').resize((1440,1082)).save(O/(name+'-gray.png'))
 if name=='after':im.resize((1440,1082),Image.Resampling.LANCZOS).save(O/'main.png')
style='body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;max-width:1440px;margin:32px auto;padding:0 22px}a{color:#efbc91}img{width:100%;display:block}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:22px 0}figcaption{color:#c5bbc4}@media(max-width:800px){.pair{grid-template-columns:1fr}}'
html=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>122 · Repeated upper-ring architecture</title><style>{style}</style><h1>122 · Repeated upper-ring architecture</h1>
<p>Small drainage mouths follow the lower attic shelf. Repeated vertical supports project farther in their lower third. Shallow panel floors stay closer to the surrounding masonry color, while narrow returns and deep niches retain shade.</p>
<p>The preceding pass adds tower channels and repeated panel fields. Cornice blocks use the intermediate masonry tone with the requested additional35% brightness; the light portion of arch interiors occupies only the front quarter.</p><p><a href="#detail">Compare</a> · <a href="#reference">Reference</a> · <a href="{p}main-4k.png">4K image</a> · <a href="{p}scene.blend">Editable scene</a> · <a href="{p}kit.blend">Appendable kit</a></p><img src="{p}main.png">
<section id="detail"><h2>120 →122 · Matched 4K crops</h2><div class="pair"><figure><img src="{p}before-detail.png"><figcaption>120 before your latest notes</figcaption></figure><figure><img src="{p}after-detail.png"><figcaption>122 current</figcaption></figure></div><h2>Upper-ring rhythm</h2><div class="pair"><img src="{p}before-upper.png"><img src="{p}after-upper.png"></div></section>
<section id="reference"><h2>Reference: drains and stepped supports</h2><img style="max-width:650px" src="/references/user-coliseum/drains-stepped-supports.png"><p>UCL-08, user-supplied reference crop; original artwork by the project creator using ChatGPT Images 2.5. Geometry is native and editable, with no projected artwork.</p></section>
<details><summary>Grayscale</summary><div class="pair"><img src="{p}before-gray.png"><img src="{p}after-gray.png"></div></details>
<p>Fine fracture-boundary work remains open. A separate repair study addresses inherited folded faces before adding smaller chips. The coliseum remains in development and is not locked.</p></html>'''
(R/'prototype/review-122.html').write_text(html)
