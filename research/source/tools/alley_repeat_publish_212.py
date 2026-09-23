from pathlib import Path
from PIL import Image
import json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-repeat-212'
im=Image.open(O/'main-4k.png').convert('RGB')
im.resize((1920,round(im.height*.5)),Image.Resampling.LANCZOS).save(O/'after-display.png')
boxes={'after-street.png':(650,400,3260,2380),'after-first-building.png':(0,810,760,1950),'after-floor-detail.png':(0,1230,450,1950)}
for name,box in boxes.items():im.crop(box).save(O/name)
(O/'publication.json').write_text(json.dumps({'source':'main-4k.png','native_size':im.size,'crops':boxes},indent=2))

base=Image.open(R/'art/studies/scene-completion-209/main-4k.png').convert('RGB')
for name,box in boxes.items():base.crop(box).save(O/name.replace('after-','before-'))

im.convert('L').resize((1920,round(im.height*.5)),Image.Resampling.LANCZOS).save(O/'after-grayscale.png')
base.convert('L').resize((1920,round(base.height*.5)),Image.Resampling.LANCZOS).save(O/'before-grayscale.png')
