from pathlib import Path
from PIL import Image
import json,shutil
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-052';P=R/'prototype'
for n,box in [('facade',(1050,30,1440,550)),('pipes',(280,120,560,670))]:
 Image.open(O/'render.png').crop(box).save(O/(n+'.png'))
 shutil.copyfile(R/'art/reviews/xenon-051'/(n+'.png'),O/('baseline-'+n+'.png'))
 shutil.copyfile(R/'art/reviews/xenon-051'/('reference-'+n+'.png'),O/('reference-'+n+'.png'))
s=(P/'review-051.html').read_text().replace('051','052').replace('050','051').replace('Grit, scars and shadow','Measured color and varied wear')
s=s.replace('C hybrid, with finer clustered surface wear. Facades gain pinprick chips, small scars and sparse pale fragments. Services use a separate, quieter enamel-wear treatment. Darker undersides group platform shadows; fine crease lines recede beneath stronger contours.','Darker blue and red-violet blue regions, with iron-brown warm patches. Color correction follows architectural material families and preserves the existing coating shapes. Small wear has a wider size range, plus a first set of irregular scars anchored below actual gallery fixings.')
s=s.replace('../art/reviews/xenon-051/hybrid.png','../art/reviews/xenon-051/render.png').replace('051 style study','051 detail study').replace('051 · approved hybrid direction','051 · previous palette').replace('052 · small wear and grouped shadows','052 · calibrated palette and varied wear').replace('051 · C hybrid','051 · previous palette').replace('052 · finer surface vocabulary','052 · darker blues and iron browns')
s=s.replace('Next refinement: make more of the small scars respond to seams and fasteners; the current placement follows broad weathering regions.','Selected gallery fixing scars now use measured world positions from the assembled scene. Most small wear remains region-based; this is the first localized test.')
colors=[('Reference blue','#53556b'),('Red-violet direction','#61586a'),('Reference iron brown','#805a50'),('051 blue','#63688b'),('051 warm','#95806e'),('052 rendered blue','#4f5065'),('052 rendered violet','#5f5a6c'),('052 rendered iron','#7c5952')]
chips='<section><h2>Color targets and previous palette</h2><div style="display:flex;gap:16px;flex-wrap:wrap">'+''.join(f'<div><div style="width:160px;height:75px;background:{c}"></div><p>{name}<br>{c}</p></div>' for name,c in colors)+'</div><p>Reference blue and iron brown come from clustered architectural pixels in the selected concept. The violet target is an art-directed intermediate within its redder blue-gray family. Correction is calibrated in linear light against 051 rendered colors. Lighting and atmosphere still create local variation; these are family targets, not a claim that every pixel matches.</p></section>'
s=s.replace('<section id="facade">',chips+'<section id="facade">')
(P/'index.html').write_text(s);(P/'review-052.html').write_text(s)
