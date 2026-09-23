from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-124';url='/art/studies/coliseum-124/'
for k in ['baseline','A','B','C']:
 p=R/'art/studies/coliseum-123/main-4k.png' if k=='baseline' else O/k/'main-4k.png'
 out=O/k;out.mkdir(exist_ok=True);im=Image.open(p)
 im.resize((1440,1082),Image.Resampling.LANCZOS).save(out/'main.png');im.crop((1400,350,2510,1140)).save(out/'detail.png');im.crop((1700,690,2150,1140)).save(out/'columns.png');im.crop((2000,340,2280,670)).save(out/'framing.png');im.convert('L').resize((1440,1082)).save(out/'gray.png')
style='body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;max-width:1600px;margin:32px auto;padding:0 22px}a{color:#efbc91}img{width:100%;display:block}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}figure{margin:22px 0}figcaption{color:#c5bbc4}nav{position:sticky;top:0;background:#19191eee;padding:12px}@media(max-width:850px){.grid{grid-template-columns:1fr}}'
labels={'A':'A — 5% smaller','B':'B — 10% smaller','C':'C — 20% smaller'}
h=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>124 · Round columns and arch proportions</title><style>{style}</style><h1>124 · Round columns and arch proportions</h1><p>Three studies of smaller clear arch openings. Percentages reduce both width and height; floor bands and the overall structure stay fixed. The same heavily damaged bay remains unchanged in all options; the other 53 openings receive the measured reduction. Every option includes round columns with bases and capitals, extended exposed framing, and cornice blocks using their supporting wall material without an extra darkening tint.</p><nav><a href="#detail">Compare arches</a> · <a href="#columns">Columns</a> · <a href="#framing">Framing</a> · <a href="#full">Full scenes</a></nav>'
for section,title,img in [('detail','Matched detail views','detail.png'),('columns','Round shafts, bases and capitals','columns.png'),('framing','Framing tied into surviving masonry','framing.png'),('full','Full scenes','main.png')]:
 h+=f'<section id="{section}"><h2>{title}</h2><div class="grid">'
 for k,l in labels.items():h+=f'<figure><a href="{url}{k}/main-4k.png"><img src="{url}{k}/{img}"></a><figcaption>{l} · <a href="{url}{k}/scene.blend">Editable scene</a></figcaption></figure>'
 h+='</div></section>'
h+=f'<details><summary>Previous scene123</summary><img src="{url}baseline/detail.png"></details><details><summary>Grayscale comparison</summary><div class="grid">'+''.join(f'<figure><img src="{url}{k}/gray.png"><figcaption>{l}</figcaption></figure>' for k,l in labels.items())+'</div></details><h2>Column reference</h2><img style="width:300px" src="/references/user-coliseum/round-column-reference.png"><p>UCL-11, user-supplied reference, original artwork by the project creator using ChatGPT Images 2.5. Reference artwork is not used in the rendered scene. These are editable geometry studies, pending your choice.</p></html>'
(R/'prototype/review-124.html').write_text(h)
