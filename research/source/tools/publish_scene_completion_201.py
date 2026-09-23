from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scene-completion-201';B=R/'art/studies/beam-rust-197'
frames={'left-beam':[140,821,673,1950],'colosseum':[1350,360,2500,1180],'street':[1350,830,2550,1320],'first-building':[0,810,760,1950],'sky':[1200,0,2600,470]}
for label,src in [('before',B/'main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(src).convert('RGB');im.resize((1800,round(im.height*1800/im.width)),Image.Resampling.LANCZOS).save(O/(label+'-display.png'))
 for name,box in frames.items():im.crop(box).save(O/(label+'-'+name+'.png'))
(O/'framing.json').write_text(json.dumps(frames,indent=2))
