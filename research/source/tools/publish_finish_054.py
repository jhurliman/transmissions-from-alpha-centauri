from pathlib import Path
from PIL import Image
import json,numpy as np
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-054';P=R/'prototype'
for k,path in [('baseline',R/'art/reviews/xenon-053/C.png'),('new',O/'render.png')]:
 im=Image.open(path)
 for n,b in [('pipes',(280,120,560,670)),('facade',(1050,30,1440,550))]:im.crop(b).save(O/(k+'-'+n+'.png'))
measure={}
for k,path in [('reference',R/'art/reviews/xenon-001/selected-third.png'),('053 C',R/'art/reviews/xenon-053/C.png'),('054',O/'render.png')]:
 im=Image.open(path).convert('RGB');measure[k]={}
 for label,y in [('Upper sky',15),('Middle exposed sky',60),('Lower exposed sky',100)]:
  a=np.array(im.crop((690,y-6,750,y+6)));v=np.median(a.reshape(-1,3),axis=0).astype(int);measure[k][label]='#'+''.join(f'{n:02x}' for n in v)
(O/'sky-measurements.json').write_text(json.dumps(measure,indent=2))
css='''*{box-sizing:border-box}body{margin:0;background:#19181e;color:#eee7df;font:16px system-ui}header,section{padding:24px 3vw}p{max-width:1000px;line-height:1.6;color:#c9c1c9}a{color:#efbc91}button{padding:10px 16px;background:#38313e;color:#eee;border:1px solid #79637a;border-radius:6px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.trio{grid-template-columns:1fr 1fr 1fr}figure{margin:0;background:#24212b;padding:10px}img{display:block;width:100%}figcaption{padding:10px 0}.gray img{filter:grayscale(1)}td,th{padding:12px;text-align:left}table{border-collapse:collapse}@media(max-width:800px){.grid{grid-template-columns:1fr}}'''
def fig(path,cap):return f'<figure><a href="{path}" target="_blank"><img src="{path}" alt="{cap}"></a><figcaption>{cap}</figcaption></figure>'
page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fire sky and painted metal · 054</title><style>{css}</style><header><h1>Fire sky and painted metal · 054</h1><p>053 C continues with redder rust, a directional orange-red sky, warmer dust scattering, and a separate pipe treatment: larger scars, an independent dark steel blue-gray palette for round bodies, and broken strips of pale reflected color.</p><p><a href="#alley">Full comparison</a> · <a href="#pipes">Pipe detail</a> · <a href="#sky">Sky samples</a> · <a href="../art/reviews/xenon-054/scene.blend">Blender scene</a> · <a href="review-053.html">Previous review</a></p><button onclick="document.body.classList.toggle('gray')">Toggle grayscale</button></header><section id="alley"><div class="grid">'''+fig('../art/reviews/xenon-053/C.png','053 C · approved direction')+fig('../art/reviews/xenon-054/render.png','054 · sky, rust and painted metal')+'</div></section>'
for region in ['pipes','facade']:
 page+=f'<section id="{region}"><h2>{region.title()} · reference / before / after</h2><div class="grid trio">'+fig('../art/reviews/xenon-051/reference-'+region+'.png','Selected concept')+fig('../art/reviews/xenon-054/baseline-'+region+'.png','053 C')+fig('../art/reviews/xenon-054/new-'+region+'.png','054')+'</div></section>'
page+='<section id="sky"><h2>Why the sky was pink</h2><p>The previous world background was flat orange, but rays also passed through a large dust volume with a pink-violet scattering color. That volume washed the visible background toward salmon. This pass adds an angular sky gradient and warms the scattering color; the distant structures therefore receive a warmer haze as well.</p><table><tr><th>Exposed sky sample</th><th>Selected concept</th><th>053 C</th><th>054</th></tr>'
for label in measure['reference']:
 page+='<tr><th>'+label+'</th>'+''.join(f'<td><span style="display:inline-block;width:26px;height:26px;background:{measure[k][label]};vertical-align:middle"></span> {measure[k][label]}</td>' for k in ['reference','053 C','054'])+'</tr>'
page+='</table><p>Median pixels from three small, exposed sky regions. These compare the visible upper sky, not a complete horizon profile; reference cloud shapes also affect the samples.</p><h2>Painted highlights</h2><p>Round-pipe midtone samples in the reference include #42475A–#434A5E. This pass moves pipe bodies toward that darker steel blue-gray independently of the walls. The pale strips follow surface normals and break into world-space sections. They are native color bands, not glossy PBR reflections. Service scars remain separate from the facade coating. Camera and architectural geometry are preserved.</p></section></html>'
(P/'index.html').write_text(page);(P/'review-054.html').write_text(page)
print(json.dumps(measure,indent=2))
