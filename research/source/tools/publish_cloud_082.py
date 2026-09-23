from pathlib import Path
import json,html
from PIL import Image
R=Path(__file__).resolve().parents[1]; O=R/'art/studies/cloud-082'; A='/art/studies/cloud-082/'
Image.open(O/'main.png').crop((445,0,998,177)).save(O/'camera-sky-closeup.png')
def fig(src,caption):
 return f'<figure><a href="{src}"><img src="{src}" alt="{html.escape(caption)}"></a><figcaption>{caption}</figcaption></figure>'
s='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>082 · Sculpted clouds, painted shapes</title><style>body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;margin:32px auto;max-width:1450px;padding:0 22px}a{color:#efbc91}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}figure{margin:0}img{width:100%;display:block}figcaption{padding:9px 0}section{margin:38px 0}table{border-collapse:collapse}td,th{text-align:left;padding:9px;border-bottom:1px solid #555}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>082 · Sculpted clouds, painted shapes</h1><p>Editable billowing cloud volumes supply the silhouette and lighting. Their rendered light is simplified into broad, contiguous color regions for the final sky. The reference remains a comparison only.</p><p><a href="#process">3D → 2D</a> · <a href="#reference">Reference</a> · <a href="#sky">Composition</a> · <a href="#scene">Alley camera</a> · <a href="/prototype/soil-study-083.html">Soil relief study</a></p>'''
s+='<section id="scene">'+fig(A+'main.png','082 · Native-derived cloud layers at the alley camera')+'</section>'
s+='<section id="process"><h2>From volume to broad color strokes</h2><div class="grid">'+fig(A+'native-component.png','Editable 3D cloud master · continuous light response')+fig(A+'flat-component.png','Same native silhouette · simplified contiguous palette regions')+'</div><p>Cloud outlines stay intact during flattening. Interior tone regions are simplified separately, allowing broader shading than the smaller contours.</p></section>'
s+='<section id="reference"><h2>Reference direction</h2>'+fig('/references/user-cloud-study/clouds-reference.png','UC-01 · supplied cloud color and shape reference')+fig('/references/user-cloud-study/cloud-detail-mask.png','UC-02 · supplied contour and negative-space mask')+'</section>'
s+='<section><h2>Clouds at the game camera</h2>'+fig(A+'camera-sky-closeup.png','Native camera pixels enlarged for inspection')+'</section>'
s+='<section id="sky"><h2>Composed cloud families</h2>'+fig(A+'composed-sky.png','Distinct billow, shoulder and wisp families, arranged around open sky')+'</section>'
s+='<section><h2>Editable sources</h2><p><a href="'+A+'scene.blend">Composed Blender scene</a> · <a href="'+A+'assets/arch-master.blend">Main billow master</a> · <a href="'+A+'assets/shoulder-master.blend">Shoulder master</a> · <a href="'+A+'assets/wisp-master.blend">Wisp master</a></p><p>This is an evolving candidate. The strict reference-fidelity target is 95/100; procedural correctness and improvement alone do not satisfy it.</p>'
if (O/'critic.json').exists():
 d=json.loads((O/'critic.json').read_text())
 s+='<p>Independent visual estimates, not objective measurements or user approval.</p><table><tr><th>Axis</th><th>Score / 100</th></tr>'+''.join('<tr><td>'+k.replace('_',' ').title()+'</td><td>'+str(v)+'</td></tr>' for k,v in d.get('final_main_scores',{}).items())+'</table><p>'+html.escape(' '.join(d.get('remaining_gaps',[])))+'</p><p><a href="'+A+'critic.json">Full critique ledger</a></p>'
s+='</section></html>'
(R/'prototype/review-082.html').write_text(s)
