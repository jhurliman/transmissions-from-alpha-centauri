from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/beam-rust-196';B=R/'art/studies/scene-weathering-195'
boxes=json.loads((B/'framing.json').read_text())
for label,path in [('before',B/'main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(path).convert('RGB');im.resize((1800,round(im.height*1800/im.width)),Image.Resampling.LANCZOS).save(O/(label+'-display.png'))
 for key in ['left-beam','right-beam']:im.crop(boxes[key]).save(O/(label+'-'+key+'.png'))
parts=''
for key,title in [('left-beam','Left support'),('right-beam','Right support · half strength')]:parts+=f'<section id="{key}"><h2>{title}</h2><div class="pair"><figure><img src="/art/studies/beam-rust-196/before-{key}.png"><figcaption>195</figcaption></figure><figure><img src="/art/studies/beam-rust-196/after-{key}.png"><figcaption>196</figcaption></figure></div></section>'
html='''<!doctype html><meta charset="utf-8"><title>196 · Connected edge rust</title><style>body{max-width:1600px;margin:24px auto;background:#211f26;color:#ece6e0;font:16px system-ui}a{color:#f3b383}img{max-width:100%}#main{width:100%}.pair{display:flex;gap:24px;align-items:flex-start}.pair figure{flex:1;margin:0}.pair img{width:100%;max-height:1100px;object-fit:contain}section{border-top:1px solid #514750;padding:28px 0}button{padding:10px 18px;margin:8px;cursor:pointer}figcaption{padding:8px}</style><h1>196 · Connected edge rust</h1><p>More irregular feathered patch spacing, with narrow interrupted rust runs along the beam edges. The right support remains at half strength.</p><p><a href="#left-beam">Left support</a> · <a href="#right-beam">Right support</a> · <a href="/prototype/review-195.html">195 comparison</a></p><button onclick="pick('after')">196 updated</button><button onclick="pick('before')">195 before</button><img id="main" src="/art/studies/beam-rust-196/after-display.png"><p><a href="/art/studies/beam-rust-196/main-4k.png">Full render</a> · <a href="/art/studies/beam-rust-196/scene.blend">Editable scene</a></p>'''+parts+'''<script>function pick(v){document.getElementById('main').src='/art/studies/beam-rust-196/'+v+'-display.png'}</script>'''
(R/'prototype/review-196.html').write_text(html)
