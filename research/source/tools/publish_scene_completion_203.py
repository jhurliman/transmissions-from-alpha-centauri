from pathlib import Path
from PIL import Image
import json,html
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scene-completion-203';B=R/'art/studies/beam-rust-197'
frames={
 'first-building':[0,810,760,1950],
 'alley-left':[0,0,1150,1950],
 'alley-right':[2730,0,3840,2100],
 'colosseum':[1350,360,2500,1180],
 'left-beam':[140,821,673,1950],
 'clouds':[1180,0,2740,560],
 'transition':[1080,880,2720,1530],
 'haze':[1350,830,2550,1320],
 'corner-ink':[300,100,570,800],
 'right-beam':[3269,821,3836,1950],
 'rear-post':[610,960,800,1760],
 'palette-source':[40,2430,1700,2885]}
for label,path in [('before',B/'main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(path).convert('RGB');im.resize((1800,round(im.height*1800/im.width)),Image.Resampling.LANCZOS).save(O/(label+'-display.png'))
 for key,box in frames.items():im.crop(box).save(O/(label+'-'+key+'.png'))
(O/'framing.json').write_text(json.dumps(frames,indent=2))
sections=[('first-building','First building','Connected surface wear and native recessed damage across the facade, including the lower-left panels.'),('alley-left','Broader alley damage · left','Reusable recesses, impacts, edge losses and cracks placed on visible facade panels.'),('alley-right','Broader alley damage · right','Unequal wear on both sides of the street; original service assemblies retained.'),('colosseum','Colosseum crumbling','The separate native wall-crumbling pass is now integrated across the arcade tiers and upper walls.'),('left-beam','Left beam','Unequal middle patches and a visible interrupted warm rust connection along the near edge.'),('clouds','Clouds','Quieter internal color layering and varied contour detail; saturated sky retained.'),('transition','Ruined street transition','Jagged losses on the partial buildings that bridge the alley and city, with a 50% blend of the foreground steel-blue/rust palette across the middle rubble and walls.'),('haze','Distant street haze','A broader low transition from the nearest skyscrapers toward the Colosseum, retaining cool silhouettes.')]
parts=[]
for key,title,desc in sections:
 extra=''
 if key=='colosseum':extra='<details><summary>Original artwork reference</summary><img src="/art/studies/coliseum-190/reference/UCL01-landmark.png"><p>Original artwork by the project creator, made with ChatGPT Images 2.5.</p></details>'
 if key=='transition':extra='<details><summary>Palette source · unchanged foreground junk pile</summary><img src="/art/studies/scene-completion-203/after-palette-source.png"><p>The middle area retains half its original color and receives half of this lighting-driven blue/rust palette.</p></details>'
 if key=='haze':extra='<details><summary>Atmosphere reference</summary><img src="/art/studies/coliseum-136/haze/reference-street.png"><p>Detail of the project creator’s original artwork.</p></details>'
 parts.append(f'<section id="{key}"><h2>{title}</h2><p>{desc}</p><div class="pair"><figure><img loading="lazy" src="/art/studies/scene-completion-203/before-{key}.png"><figcaption>Before · 197</figcaption></figure><figure><img loading="lazy" src="/art/studies/scene-completion-203/after-{key}.png"><figcaption>Combined update · 203</figcaption></figure></div>{extra}</section>')
nav=' · '.join(f'<a href="#{k}">{t}</a>'for k,t,_ in sections)
p='''<!doctype html><html><meta charset="utf-8"><title>203 · Combined scene weathering</title><style>body{max-width:1800px;margin:24px auto;padding:0 20px;background:#211f26;color:#eee6de;font:16px/1.5 system-ui}a{color:#efb38f}img{max-width:100%;display:block}nav{position:sticky;top:0;background:#211f26ed;padding:12px;z-index:1}section{border-top:1px solid #554b50;padding:25px 0;scroll-margin-top:100px}.pair{display:flex;gap:22px;align-items:flex-start}.pair figure{flex:1;min-width:0;margin:0}.pair img{width:100%;max-height:1200px;object-fit:contain;object-position:top}figcaption{padding:8px}button{background:#5c4945;color:#fff;border:1px solid #ad8274;padding:10px 18px;margin:10px 10px 10px 0;border-radius:4px;cursor:pointer}details{margin:20px 0}details img{max-height:900px}#main{width:100%}</style><h1>203 · Combined scene weathering</h1><p>All seven work areas brought into one current scene. Before/after views below use the same camera. Final artistic approval remains with you.</p><nav>'''+nav+'''</nav><button onclick="pick('after')">Combined update</button><button onclick="pick('before')">Before</button><img id="main" src="/art/studies/scene-completion-203/after-display.png"><p><a href="/art/studies/scene-completion-203/main-4k.png">Full-resolution render</a> · <a href="/art/studies/scene-completion-203/scene.blend">Editable scene</a></p>'''+''.join(parts)+'''<script>function pick(v){document.getElementById('main').src='/art/studies/scene-completion-203/'+v+'-display.png'}</script></html>'''
(R/'prototype/review-203.html').write_text(p)
