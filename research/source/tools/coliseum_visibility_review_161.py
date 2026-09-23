"""Diagnostic crops of native161 render differences; never composited into art."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,find_objects,binary_dilation
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-161/visibility'
a=Image.open(R/'art/studies/coliseum-159/main-4k.png').convert('RGB');b=Image.open(O/'guarded.png').convert('RGB')
d=np.abs(np.array(a).astype('int16')-np.array(b).astype('int16')).max(2)
lab,n=label(binary_dilation(d>4,iterations=7));rows=[]
for k,sl in enumerate(find_objects(lab),1):
    if sl is None:continue
    yy,xx=sl;count=int(((d[sl]>4)&(lab[sl]==k)).sum())
    if count<4:continue
    box=[max(0,xx.start-8),max(0,yy.start-8),min(3840,xx.stop+8),min(2885,yy.stop+8)]
    row={'id':k,'pixels_over4':count,'box':box,'maxRGB':int(d[sl].max())};rows.append(row)
    ims=[im.crop(box)for im in [a,b]];w,h=ims[0].size;im=Image.new('RGB',(2*w,h+18),(28,28,32));draw=ImageDraw.Draw(im)
    for i,q in enumerate(ims):im.paste(q,(w*i,18));draw.text((w*i+2,2),'159'if i==0 else'161 guarded',fill='white')
    im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(O/f'guarded-change-{k}.png')
report={'baseline':'159 uncorrected main4K','new':'161 native guarded render','all_pixels_over4':int((d>4).sum()),'all_maxRGB':int(d.max()),'landmark_pixels_over4':int((d[300:1300,1250:2500]>4).sum()),'landmark_maxRGB':int(d[300:1300,1250:2500].max()),'regions':rows}
(O/'guarded-pixel-comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
