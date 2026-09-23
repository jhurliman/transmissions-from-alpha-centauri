from pathlib import Path
import json
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-107';roi=(520,245,980,505);checks={};base=np.asarray(Image.open(R/'art/studies/city-106/A/main.png').convert('RGB'))
labels={'A':'A · 2× dark strokes','B':'B · 4× dark strokes','C':'C · 8× dark strokes'}
for v in labels:
 im=Image.open(O/v/'main.png').convert('RGB');im.crop(roi).resize((1380,780),Image.Resampling.LANCZOS).save(O/v/'city.png');im.crop(roi).convert('L').resize((1380,780),Image.Resampling.LANCZOS).save(O/v/'gray.png');diff=np.abs(np.asarray(im).astype(int)-base.astype(int));checks[v]={'road_max_difference':int(diff[560:880,420:1000].max())}
(O/'pixel-check.json').write_text(json.dumps(checks,indent=2))
s='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>107 · Dark city brushwork</title><style>body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;max-width:1440px;margin:32px auto;padding:0 22px}a{color:#efbc91}img{width:100%;display:block}figure{margin:24px 0}button{padding:12px;font:inherit;background:#36333d;color:white;border:1px solid #81716c;border-radius:5px;cursor:pointer}button.active{background:#89624c}figcaption{padding:8px 0;color:#c5bbc4}section{margin:40px 0}.ref{max-width:300px}</style><h1>107 · Dark city brushwork</h1><p>The accepted placement is preserved. Light strokes stay at the original 1× count and positions; only darker pigment increases. All three versions use the same stroke sizes and feathered edges.</p><p><a href="#detail">Closeups</a> · <a href="#reference">Facade reference</a> · <a href="/prototype/review-106.html">Previous review</a></p>'''
for v,label in labels.items():s+=f'<button id="{v}" onclick="show(\'{v}\')">{label}</button> '
s+='<p id="caption">A · 2× dark strokes / 1× light strokes</p><a id="full" href="/art/studies/city-107/A/main.png"><img id="main" src="/art/studies/city-107/A/main.png"></a><section id="detail"><h2>Matched city closeups</h2>'
for v,label in labels.items():
 a=json.loads((O/v/'marks.json').read_text());light=sum(x['light_strokes'] for x in a);dark=sum(x['dark_strokes'] for x in a)
 s+=f'<figure><img src="/art/studies/city-107/{v}/city.png"><figcaption>{label} · {light} light / {dark} dark marks · <a href="/art/studies/city-107/{v}/scene.blend">Editable scene</a></figcaption></figure>'
s+='</section><details><summary>Grayscale comparison</summary>'
for v,label in labels.items():s+=f'<figure><img src="/art/studies/city-107/{v}/gray.png"><figcaption>{label}</figcaption></figure>'
s+='</details><section id="reference"><h2>Supplied facade reference · UX-03</h2><img class="ref" src="/references/user-city-study/smooth-facade-detail.png"><p>Sparse warm marks over broad violet walls, with quieter dark painted detail.</p></section>'
s+='''<script>const labels={A:'A · 2× dark strokes',B:'B · 4× dark strokes',C:'C · 8× dark strokes'};function show(v){const p='/art/studies/city-107/'+v+'/main.png';document.getElementById('main').src=p;document.getElementById('full').href=p;document.getElementById('caption').textContent=labels[v]+' / 1× light strokes';for(const k of Object.keys(labels))document.getElementById(k).classList.toggle('active',k===v)}show('A');</script></html>'''
(R/'prototype/review-107.html').write_text(s);(R/'prototype/index.html').write_text(s)
