import numpy as np,json
from scipy import ndimage as ndi
from PIL import Image,ImageDraw
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-129/flat-analysis';im=Image.open(R/'art/studies/coliseum-128/main-4k.png').convert('RGB');a=np.array(im,dtype=np.float32);m=np.array(Image.open(O/'surface-role-mask.png').convert('RGB'));roi=np.zeros(m.shape[:2],bool);roi[320:1240,1320:2480]=1;uniform=(m.max(2)-m.min(2))<2;core=(m.min(2)>245)&uniform&roi;land=(m.min(2)>120)&uniform&roi
mean=ndi.uniform_filter(a,size=(5,5,1));std=np.sqrt(np.maximum(ndi.uniform_filter(a*a,size=(5,5,1))-mean*mean,0)).max(2);span=ndi.maximum_filter(a,size=(3,3,1))-ndi.minimum_filter(a,size=(3,3,1));exact=span.max(2)==0
rows=[]
for typ,mask in [('tagged_exposed_core',core),('other_landmark',land&~core)]:
 mask=ndi.binary_erosion(mask,iterations=1);quiet=mask&(std<1.25);lab,num=ndi.label(quiet);sizes=np.bincount(lab.ravel());sizes[0]=0
 reg=[]
 for val in np.argsort(sizes)[::-1]:
  if sizes[val]<3 or len(reg)>=12:break
  yy,xx=np.where(lab==val);box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];pix=a[yy,xx];r={'rank':len(reg)+1,'pixels':int(len(xx)),'xyxy':box,'mean_rgb':pix.mean(0).round(2).tolist(),'region_rgb_std':pix.std(0).round(3).tolist(),'mean_maxchannel_local5x5_std':round(float(std[yy,xx].mean()),3)};reg.append(r)
 rows.append({'class':typ,'visible_eroded_pixels':int(mask.sum()),'quiet_pixels':int(quiet.sum()),'quiet_fraction':float(quiet.sum()/max(1,mask.sum())),'exact_constant3x3_pixels':int((exact&mask).sum()),'regions':reg})
for r in rows[0]['regions']:
 b=r['xyxy'];pad=18;box=[b[0]-pad,b[1]-pad,b[2]+pad,b[3]+pad];im.crop(box).resize(((box[2]-box[0])*4,(box[3]-box[1])*4)).save(O/f"core-flat-{r['rank']:02d}.png")
over=im.copy();d=ImageDraw.Draw(over)
for r in rows[0]['regions']:
 b=r['xyxy'];d.rectangle(b,outline='cyan',width=2);d.text((b[0],b[1]-12),str(r['rank']),fill='cyan')
over.crop((1320,320,2480,1240)).save(O/'core-flat-map.png')
(O/'statistics.json').write_text(json.dumps({'source':'128/main-4k.png','size':list(im.size),'threshold':'Maximum RGB channel5x5local standard deviation<1.25 on0–255 values; strict constant3x3 means per-channel range0.','mask':'Native visible-surface render; white=117Exposedcore FACE tag or core/fracture material family; gray=other landmark. Eroded1px.','semantic_limitation':'Inherited fracture faces lacking tags/material classification are not counted as core. Other-landmark low variation includes intentional recesses and intact walls and is not a defect count.','classes':rows},indent=2));print(json.dumps(rows[0],indent=2))
