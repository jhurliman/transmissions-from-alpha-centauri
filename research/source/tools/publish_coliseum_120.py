from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-120'
for name,path in [('before',R/'art/studies/coliseum-119/main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(path)
 im.crop((1400,350,2510,1140)).save(O/(name+'-detail.png'))
 im.crop((1800,420,2080,680)).save(O/(name+'-bay.png'))
 im.convert('L').resize((1440,1082)).save(O/(name+'-gray.png'))
 if name=='after':im.resize((1440,1082),Image.Resampling.LANCZOS).save(O/'main.png')
style='body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;max-width:1440px;margin:32px auto;padding:0 22px}a{color:#efbc91}img{width:100%;display:block}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:22px 0}figcaption{color:#c5bbc4}@media(max-width:800px){.pair{grid-template-columns:1fr}}'
p='/art/studies/coliseum-120/'
html=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>120 · Cornices, fracture detail and arch depth</title><style>{style}</style><h1>120 · Cornices, fracture detail and arch depth</h1>
<p>Taller tapered cornice blocks and two-tone arch interiors, with finer native fracture geometry tested on the central upper bay. Accepted framing and surrounding scene are preserved.</p>
<p><a href="#detail">Compare</a> · <a href="#geometry">Geometry</a> · <a href="#analysis">Flat-region review</a> · <a href="{p}main-4k.png">4K image</a> · <a href="{p}scene.blend">Editable scene</a></p><img src="{p}main.png">
<section id="detail"><h2>119 →120 · Same camera and crop</h2><div class="pair"><figure><img src="{p}before-detail.png"><figcaption>Before</figcaption></figure><figure><img src="{p}after-detail.png"><figcaption>Current</figcaption></figure></div><h2>Central damaged bay</h2><div class="pair"><img src="{p}before-bay.png"><img src="{p}after-bay.png"></div></section>
<section id="geometry"><h2>Native fracture geometry</h2><p>Matched neutral material studies. Broad break paths retained; shallow attached stone facets add relief. Finer edge remeshing was rejected because it introduced crossing faces, so the existing contours remain unchanged.</p><div class="pair"><img src="{p}fracture/before-clay.png"><img src="{p}fracture/after-clay.png"></div><h2>Undercornice reference</h2><img style="max-width:650px" src="/references/user-coliseum/cornice-supports.png"><p>UCL-03, user-supplied Roman Colosseum drawing crop; artist unspecified. Reference only.</p></section>
<section id="analysis"><h2>Where does the image lack detail?</h2><p>The geometry-masked analysis flags low local color variation. Approximately36% of the baseline landmark meets this threshold; almost none is exactly flat. These are review candidates, not an instruction to add noise. Large arch shadows can remain quiet; tower faces and upper wall panels deserve further architectural detail.</p><img src="{p}analysis/flat-region-map.png"><p><a href="{p}analysis/semantic-review.md">Visual interpretation</a> · <a href="{p}analysis/flat-regions.json">Measurements</a></p></section>
<details><summary>Grayscale</summary><div class="pair"><img src="{p}before-gray.png"><img src="{p}after-gray.png"></div></details><p>This remains a development revision, pending user acceptance. Fine fracture work is localized; broader panel refinement remains.</p></html>'''
(R/'prototype/review-120.html').write_text(html)
