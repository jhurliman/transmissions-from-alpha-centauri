from pathlib import Path
import json
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-070';a='/art/reviews/xenon-070/';n=len(json.loads((O/'spalls.json').read_text()))
css='body{margin:0;background:#19191e;color:#eee7df;font:16px/1.6 system-ui}header,section{padding:24px 3vw}p{max-width:1000px}a{color:#efbc91}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img{width:100%;display:block}figcaption{padding:8px 0}@media(max-width:800px){.grid{grid-template-columns:1fr}}'
def fig(src,title):return f'<figure><a href="{src}"><img src="{src}" alt="{title}"></a><figcaption>{title}</figcaption></figure>'
p=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>070 · Fractured edge losses</title><style>{css}</style><header><h1>070 · Fractured edge losses</h1><p>{n} selective spalls open up existing crack endpoints into irregular missing edge fragments. These are real geometry cuts. The 55% → 100% projected interior finish, approved crack routes, and services remain intact.</p><p><a href="#left">Left comparison</a> · <a href="#right">Right comparison</a> · <a href="{a}scene.blend">Editable scene</a></p></header><section>'+fig(a+'render.png','070 · full alley')+'</section>'
for side in ['left','right']:
 p+=f'<section id="{side}"><h2>{side.title()} architecture</h2><div class="grid">'+fig('/art/reviews/xenon-069/'+side+'.png','069 · connected cracks')+fig(a+side+'.png','070 · selected edge losses')+'</div></section>'
p+='<section><p>Each cutter is tied to a crack boundary endpoint, with variable size and depth bounded by the component thickness. All accepted outputs are closed meshes. Further review should judge whether these losses need more irregular perimeter detail or a small number of larger hero breaks.</p></section></html>'
(R/'prototype/review-070.html').write_text(p);(R/'prototype/index.html').write_text(p)
