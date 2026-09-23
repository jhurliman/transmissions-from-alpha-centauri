from pathlib import Path
import json
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'art/studies/cloud-080'
def fig(url,label):return f'<figure><a href="{url}"><img src="{url}" alt="{label}"></a><figcaption>{label}</figcaption></figure>'
for name in ('mask','detail'):
 if (O/f'{name}.png').exists():Image.open(O/f'{name}.png').crop((140,35,890,375)).save(O/f'{name}-selected.png')
style='body{background:#19191e;color:#eee7df;font:17px/1.6 system-ui;margin:30px}a{color:#efbc91}img{width:100%;display:block}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}figure{margin:0}section{margin:36px 0}figcaption{padding:8px 0}table{border-collapse:collapse}td,th{padding:8px;text-align:left;border-bottom:1px solid #555}@media(max-width:800px){.grid{grid-template-columns:1fr}}'
s=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>080 · Procedural cloud shapes</title><style>{style}</style><h1>080 · Procedural cloud shapes</h1><p>Individual cloud contours, smoother dark insets, and restrained palette variation. Compared against the supplied cloud image and silhouette mask.</p><p><a href="#masks">Silhouette comparison</a> · <a href="#color">Color and layering</a> · <a href="#scene">Scene comparison</a> · <a href="/art/studies/cloud-080/scene.blend">Editable Blender scene</a></p>'
a='/art/studies/cloud-080/'
if (O/'main.png').exists():s+=fig(a+'main.png','080 · native scene candidate')
s+='<section id="masks"><h2>Contour rhythm</h2><div class="grid">'+fig('/references/user-cloud-study/cloud-detail-mask.png','UC-02 · user silhouette reference')+fig(a+'mask-selected.png','Enlarged native bank group · contour and joining detail')+'</div></section>'
s+='<section id="color"><h2>Cloud bodies and smoother dark insets</h2><div class="grid">'+fig('/references/user-cloud-study/clouds-reference.png','UC-01 · color and layering reference')+fig(a+'detail.png','Native cloud color proof')+'</div></section>'
s+='<section id="scene"><h2>Main camera</h2><div class="grid">'+fig('/art/reviews/xenon-079/render.png','079 · previous sky')+fig(a+'main.png','080 · cloud system')+'</div></section>'
s+='<section><h2>Contour frequency range</h2><div class="grid">'+fig('/art/studies/cloud-080/low.png','Frequency 10 · broader contours')+fig('/art/studies/cloud-080/high.png','Frequency 30 · finer contours')+'</div><p>The selected scene uses frequency 20, with per-cloud variation and smaller bumps at higher frequencies.</p></section>'
cfg=json.loads((R/'config/cloud-system-080.json').read_text())
s+='<section id="controls"><h2>Reproducible controls</h2><p>Each cloud varies around a shared edge rhythm. Larger clouds receive a smoother dark inset. Rare small-cloud colors use a seeded choice, so rebuilding keeps the same composition.</p><table><tr><th>Control</th><th>Current value</th></tr>'
for label,key in [('Contour frequency','contour_frequency'),('Per-cloud frequency variation','per_cloud_frequency_jitter'),('Inset frequency relative to outer edge','inset_frequency_ratio'),('Small-cloud alternate-color chance','rare_color_chance'),('Seed','seed')]:
 s+=f'<tr><td>{label}</td><td>{cfg.get(key,"—")}</td></tr>'
s+='</table></section>'
review=O/'review.json'
if review.exists():
 data=json.loads(review.read_text())
 s+='<section><h2>Review status</h2><p>'+data.get('summary','Candidate pending user review.')+'</p></section>'
s+='<p>References guide shape and palette; they are not projected onto the scene. Native scene and procedural parameters are saved in the project. This is a candidate, pending your review.</p></html>'
(R/'prototype/review-080.html').write_text(s)
(R/'prototype/index.html').write_text(s)
