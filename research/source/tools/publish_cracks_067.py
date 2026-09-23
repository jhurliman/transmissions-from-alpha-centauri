from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');P=R/'prototype';a='/art/reviews/xenon-067/'
css='body{margin:0;background:#19191e;color:#eee7df;font:16px/1.6 system-ui}header,section{padding:24px 3vw}p{max-width:1000px;color:#c9c1c9}a{color:#efbc91}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}figure{margin:0;background:#24212b;padding:8px}img{display:block;width:100%}figcaption{padding:8px 0}@media(max-width:800px){.grid{grid-template-columns:1fr}}'
page=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>067 · Crack depth darkening</title><style>{css}</style><header><h1>067 · Crack depth darkening</h1><p>All three retain the projected weathered finish and reach 100% darkening at maximum depth. The opening starts at 20%, 40%, or 60% darkening. Geometry, lighting, and narrow lip reflection are unchanged.</p><p><a href="#panel">Column</a> · <a href="#support">Support</a> · <a href="#alley">Alley camera</a> · <a href="review-066.html#panel">066 previous comparison</a></p></header>'
for part,title in [('panel','Column face'),('support','Concrete support'),('render','Alley camera')]:
 page+=f'<section id="{"alley" if part=="render" else part}"><h2>{title}</h2><div class="grid">'
 for label,description in [('A','20% → 100%'),('B','40% → 100%'),('C','60% → 100%')]:
  src=a+label+'-'+part+'.png';page+=f'<figure><a href="{src}"><img src="{src}" alt="{label} {description}"></a><figcaption>{label} · {description} darkening · <a href="{a}{label}.blend">Blender scene</a></figcaption></figure>'
 page+='</div></section>'
page+='<section><p>Darkening multiplies the rendered matte material in linear color space; display brightness changes also depend on color management. Each specimen reaches its maximum at its deepest point. Click any image for full resolution. Native Blender renders; user selection pending.</p></section></html>'
(P/'review-067.html').write_text(page);(P/'index.html').write_text(page)
