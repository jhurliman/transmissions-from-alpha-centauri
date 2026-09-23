from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/cloud-084'
for rev in ['082','084']:
 p=R/f'art/studies/cloud-{rev}';Image.open(p/'main.png').crop((445,0,998,210)).save(p/'layout-closeup.png')
def fig(src,label):return f'<figure><a href="{src}"><img src="{src}" alt="{label}"></a><figcaption>{label}</figcaption></figure>'
a='/art/studies/cloud-084/'
s='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>084 · Denser cloud banks</title><style>body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;margin:32px auto;max-width:1450px;padding:0 22px}a{color:#efbc91}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}figure{margin:0}img{width:100%;display:block}figcaption{padding:9px 0}section{margin:38px 0}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>084 · Denser cloud banks</h1><p>The same cloud shapes and calibrated colors, arranged into larger overlapping groups with smaller, uneven gaps.</p><p><a href="#compare">Before / after</a> · <a href="#reference">Reference</a> · <a href="/art/studies/cloud-084/scene.blend">Editable scene</a></p>'''
s+=fig(a+'main.png','084 · denser cloud layout')
s+='<section id="compare"><h2>Sky at the game camera</h2><div class="grid">'+fig('/art/studies/cloud-082/layout-closeup.png','082 · previous sparse layout')+fig(a+'layout-closeup.png','084 · layered cloud banks')+'</div></section>'
s+='<section id="reference"><h2>Reference direction</h2>'+fig('/references/user-cloud-study/clouds-reference.png','UC-01 · cloud grouping and negative spaces')+'</section></html>'
(R/'prototype/review-084.html').write_text(s);(R/'prototype/index.html').write_text(s)
