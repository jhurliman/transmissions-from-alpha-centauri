from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/ground-088';A='/art/studies/ground-088/'
def fig(name,label):return f'<figure><a href="{A}{name}"><img src="{A}{name}" alt="{label}"></a><figcaption>{label}</figcaption></figure>'
s='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>088 · Packed soil geometry</title><style>body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;margin:32px auto;max-width:1450px;padding:0 22px}a{color:#efbc91}figure{margin:0}img{width:100%;display:block}figcaption{padding:9px 0}section{margin:38px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>088 · Packed soil geometry first</h1><p>C’s broad relief is retained, lowered about 1 cm to match A’s mean road height. The separate road rock and grain objects are hidden. The detailed soil below is a separate editable geometry study, not yet applied across the alley.</p><p><a href="#detail">Packed soil proof</a> · <a href="#macro">Macro terrain</a> · <a href="#scene">Scene placement</a></p>'''
s+='<section id="detail"><h2>Actual surface geometry · neutral clay</h2>'
for filename,label in [('detail-baseline.png','Baseline · broad terrain only'),('detail-candidate.png','Candidate · modeled packed soil relief'),('detail-close.png','Close view · embedded surface relief')]:
 if (O/filename).exists():s+=fig(filename,label)
s+='<p>The new detail is mean-centered: it adds surface relief without adding average road height.</p><p>One continuous mesh. No color texture, shader bump, or separate loose stones. This is procedural geometric modeling inspired by compaction and deposition, not a calibrated physical simulation.</p></section>'
s+='<section id="macro"><h2>Recentered C macro terrain, without rocks</h2>'+fig('macro-clay.png','Original low-angle proof camera · no height exaggeration')+'</section>'
s+='<section id="scene"><h2>Placement check only</h2>'+fig('main.png','C relative relief, A mean elevation; road scatter hidden')+'<p>The fine soil study is intentionally kept separate while its geometry is being developed.</p></section>'
s+='<p>Reference benchmark: <a href="https://polyhaven.com/a/gravel_road">Gravel Road by Amal Kumar / Poly Haven</a>, plus the project’s US-01, US-02 and DP-08 references. The scan is a structural reference, not a copied terrain asset.</p><p><a href="'+A+'scene.blend">Editable alley scene</a>'
for name in ['detail-scene.blend','detail-candidate.blend']:
 if (O/name).exists():s+=' · <a href="'+A+name+'">Editable soil study</a>'
s+='</p></html>'
(R/'prototype/review-088.html').write_text(s);(R/'prototype/index.html').write_text(s)
