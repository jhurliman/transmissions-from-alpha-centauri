"""World-space pigment study from approved relief plus explicit irregular brush stamps."""
from pathlib import Path
import sys,numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from ground_relief_089 import Relief
O=R/'art/studies/soil-092';O.mkdir(exist_ok=True)
W,H=1400,3600;xs=np.linspace(-8.2,8.2,W);ys=np.linspace(-10.5,35,H);X,Y=np.meshgrid(xs,ys);field=Relief();macro=field.macro(X,Y)
d=np.load(R/'art/studies/ground-089/relief.npz');sx=np.interp(xs,d['x'],np.arange(len(d['x'])));sy=np.interp(ys,d['y'],np.arange(len(d['y'])));YY,XX=np.meshgrid(sy,sx,indexing='ij');fine=map_coordinates(d['height'],[YY,XX],order=1)
sm=gaussian_filter(macro+fine,8);dy,dx=np.gradient(sm,ys,xs);guide=np.clip(-dx*.48-dy*.60,-.045,.045)/.045
medium=gaussian_filter(fine,3);dy2,dx2=np.gradient(medium,ys,xs);meso=np.clip(-dx2*.48-dy2*.60,-.025,.025)/.025
rng=np.random.default_rng(92015);canvas=Image.new('L',(W,H),128);draw=ImageDraw.Draw(canvas)
def stamp(cx,cy,rx,ry,t,value):
 pts=[]
 for i in range(16):
  a=i*np.pi/8;rr=rng.uniform(.72,1.14);u=np.cos(a)*rx*rr;v=np.sin(a)*ry*rr;xx=cx+u*np.cos(t)-v*np.sin(t);yy=cy+u*np.sin(t)+v*np.cos(t);pts.append(((xx+8.2)/16.4*W,(yy+10.5)/45.5*H))
 draw.polygon(pts,fill=int(value))
# Groups of dragged pigment follow road direction with broad quiet interstices.
for _ in range(240):
 cx=rng.uniform(-8.2,8.2);cy=rng.uniform(-10.5,35)
 for k in range(rng.integers(3,9)):
  stamp(cx+rng.normal(0,.22),cy+rng.normal(0,.5),rng.uniform(.025,.15),rng.uniform(.09,.65),rng.uniform(-.30,.30),rng.choice([95,110,143,155]))
# Scumbled grain belongs to local clusters, not uniformly covering the road.
for _ in range(280):
 cx=rng.uniform(-8,8);cy=rng.uniform(-10,34)
 for k in range(rng.integers(14,50)):
  stamp(cx+rng.normal(0,.22),cy+rng.normal(0,.30),rng.uniform(.005,.018),rng.uniform(.008,.045),rng.uniform(-1,1),rng.choice([89,111,148,171]))
brush=(np.array(canvas,dtype=np.float32)-128)/64
palette=np.array([[59,43,37],[67,48,40],[74,52,43],[80,58,46],[87,64,50],[96,73,57]],dtype=np.float32)
for label,weight,quant in [('A',.28,.32),('B',.53,1.0)]:
 v=np.clip(.50+guide*(.30 if label=='A' else .12)+meso*(.10 if label=='A' else .025)+brush*weight,0,1);q=np.round(v*7)/7;v=v*(1-quant)+q*quant;pos=v*5;lo=np.floor(pos).astype(int);hi=np.minimum(lo+1,5);t=pos-lo;rgb=palette[lo]*(1-t[:,:,None])+palette[hi]*t[:,:,None]
 if label=='B':rgb=palette[np.clip(np.round(pos).astype(int),0,5)]
 # Very low-amplitude paper tooth, subordinate to the painted patches.
 grain=rng.uniform(-1.2,1.2,(H,W,1));rgb=np.clip(rgb+grain,0,255).astype('uint8');Image.fromarray(rgb[::-1]).save(O/f'pigment-{label}.png')
Image.fromarray(np.clip((guide*.5+.5)*255,0,255).astype('uint8')[::-1]).save(O/'relief-guide.png');canvas.transpose(Image.Transpose.FLIP_TOP_BOTTOM).save(O/'brush-stamps.png')
print('Paint fields ready',flush=True)
