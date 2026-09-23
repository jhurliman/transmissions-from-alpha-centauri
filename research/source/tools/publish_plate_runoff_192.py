from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/plate-runoff-192';B=R/'art/studies/rust-189'
a=Image.open(O/'main-4k.png').convert('RGB');b=Image.open(B/'main-4k.png').convert('RGB')
regions={'ink':(300,100,570,800),'left-splice':(367,1355,667,1655),'right-splice':(3287,1355,3587,1655),'ordinary-mounts':(530,190,750,750),'middle-anchor':(765,956,995,1186),'deeper-anchor':(979,916,1209,1146)}
for name,im in [('before',b),('after',a)]:
 im.resize((1800,round(im.height*1800/im.width)),Image.Resampling.LANCZOS).save(O/(name+'-display.png'))
 im.convert('L').resize((1200,round(im.height*1200/im.width)),Image.Resampling.LANCZOS).save(O/(name+'-gray.png'))
 for label,box in regions.items():im.crop(box).save(O/(name+'-'+label+'.png'))
sections=''
for label,title in [('ink','Building corner ink'),('left-splice','Left support plate'),('right-splice','Right support plate'),('ordinary-mounts','Ordinary pipe mounts'),('middle-anchor','Middle anchor'),('deeper-anchor','Deeper anchor')]:
 sections+=f'<section id="{label}"><h2>{title}</h2><div class="pair"><figure><img src="/art/studies/plate-runoff-192/before-{label}.png"><figcaption>189</figcaption></figure><figure><img src="/art/studies/plate-runoff-192/after-{label}.png"><figcaption>192</figcaption></figure></div></section>'
html='''<!doctype html><meta charset="utf-8"><title>192 · Bolt runoff and ink repair</title><style>body{margin:24px auto;max-width:1600px;background:#211f26;color:#ece6e0;font:16px system-ui}a{color:#f3b383}h1{font-size:28px}img{max-width:100%}#main{display:block;width:100%}.pair{display:flex;align-items:flex-start;gap:24px}.pair figure{margin:0;flex:1}.pair img{width:100%;object-fit:contain;max-height:850px}section{padding:26px 0;border-top:1px solid #514750}button{padding:9px 16px;margin:8px;cursor:pointer}figcaption{padding:8px}nav{padding:16px 0}</style><h1>192 · Bolt runoff and building-edge ink</h1><p>Short layered rust-water trails across the anchor-plate family, with fading tails and lower trails ending at the plate rim. Architectural ink is calculated without the translucent rust surfaces.</p><nav><a href="#ink">Corner ink</a> · <a href="#left-splice">Support plates</a> · <a href="#ordinary-mounts">Pipe mounts</a></nav><button onclick="pick('after')">192 updated</button><button onclick="pick('before')">189 before</button><img id="main" src="/art/studies/plate-runoff-192/after-display.png"><p><a href="/art/studies/plate-runoff-192/main-4k.png">Full render</a> · <a href="/art/studies/plate-runoff-192/scene.blend">Editable scene</a></p>'''+sections+'''<script>function pick(v){document.getElementById('main').src='/art/studies/plate-runoff-192/'+v+'-display.png'}</script>'''
(R/'prototype/review-192.html').write_text(html)
(O/'crop-regions.json').write_text(json.dumps(regions,indent=2))
