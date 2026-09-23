"""Additional painted marks over accepted092B; no relief or broad-pigment changes."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-093';base=np.array(Image.open(R/'art/studies/soil-092/pigment-B.png').convert('RGB'));H,W=base.shape[:2];rng=np.random.default_rng(93011)
# Shared, irregular regions of pigment loading create quiet interstices.
centers=[(rng.uniform(0,W),rng.uniform(0,H),rng.uniform(18,80),rng.uniform(25,105)) for _ in range(570)]
audit={}
for label,nflecks,nsponges in [('A',85000,0),('B',0,2300),('C',42000,1400)]:
 rng=np.random.default_rng(93011);masks=[Image.new('L',(W,H),0) for _ in range(3)];draw=[ImageDraw.Draw(m) for m in masks]
 def dab(x,y,r,aspect,index,opacity):
  theta=rng.uniform(0,np.pi);pts=[]
  for k in range(5):
   a=k*np.pi*2/5;rr=rng.uniform(.65,1.2);u=np.cos(a)*r*rr;v=np.sin(a)*r*aspect*rr;pts.append((x+u*np.cos(theta)-v*np.sin(theta),y+u*np.sin(theta)+v*np.cos(theta)))
  draw[index].polygon(pts,fill=int(opacity))
 for i in range(nflecks):
  if rng.random()<.80:
   cx,cy,rx,ry=centers[rng.integers(len(centers))];x=rng.normal(cx,rx);y=rng.normal(cy,ry)
  else:x=rng.uniform(0,W);y=rng.uniform(0,H)
  r=rng.uniform(.7,2.2) if rng.random()<.92 else rng.uniform(2.2,3.8)
  dab(x,y,r,rng.uniform(.4,1.7),rng.choice(3,p=[.48,.40,.12]),rng.uniform(105,205))
 for i in range(nsponges):
  cx,cy,rx,ry=centers[rng.integers(len(centers))];x=rng.normal(cx,rx);y=rng.normal(cy,ry);size=rng.uniform(7,27);index=rng.choice(3,p=[.46,.42,.12])
  for j in range(rng.integers(22,70)):
   u,v=rng.uniform(-1,1,2)
   if u*u+v*v>1 or rng.random()<.26:continue
   dab(x+u*size,y+v*size*rng.uniform(.7,1.4),rng.uniform(.6,2.5),rng.uniform(.55,1.6),index,rng.uniform(95,190)*(1-.35*(u*u+v*v)))
 out=base.astype(float);coverage=np.zeros((H,W),bool)
 # Pigment colors relative to the existing local wash: ochre, umber, cooler dusty brown.
 for mask,delta in zip(masks,[(23,18,11),(-18,-14,-10),(-2,4,7)]):
  a=np.array(mask,dtype=float)/255;coverage|=a>.12;out+=a[:,:,None]*np.array(delta)
 Image.fromarray(np.clip(out,0,255).astype('uint8')).save(O/f'pigment-{label}.png')
 audit[label]={'marked_texel_fraction':float(coverage.mean()),'flecks':nflecks,'sponge_dabs':nsponges,'mean_rgb_delta':(out-base).mean(axis=(0,1)).tolist()}
(O/'pigment-audit.json').write_text(json.dumps(audit,indent=2));print(audit)
