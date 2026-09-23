"""Unique world-space deposition and compaction stamps matching the approved 088 grain scale."""
import numpy as np
from ground_heightfield_087 import Field,smooth
class Relief:
 def __init__(self):
  self.c=Field('C');a=Field('A');x,y=np.meshgrid(np.linspace(-7.35,7.35,160),np.linspace(-8.4,32.4,440));self.delta=float((self.c(x,y).mean()-a(x,y).mean())/self.edge(x,y).mean())
 def edge(self,x,y):return smooth((8.2-np.abs(x))/.85)*smooth((y+10.5)/1.4)*smooth((35-y)/2)
 def macro(self,x,y):return self.c(x,y)-self.delta*self.edge(x,y)
 def generate(self,xs,ys):
  H=np.zeros((len(ys),len(xs)));comp=np.ones_like(H);rng=np.random.default_rng(89031);area=(xs[-1]-xs[0])*(ys[-1]-ys[0]);scale=area/36
  def stamp(target,cx,cy,rx,ry,a,amp,power=2,grain=False,phase=0):
   rr=max(rx,ry)*1.25;i0,i1=np.searchsorted(xs,[cx-rr,cx+rr]);j0,j1=np.searchsorted(ys,[cy-rr,cy+rr]);i1=min(i1+1,len(xs));j1=min(j1+1,len(ys));
   if i0>=i1 or j0>=j1:return
   dx=xs[None,i0:i1]-cx;dy=ys[j0:j1,None]-cy;u=(dx*np.cos(a)+dy*np.sin(a))/rx;v=(-dx*np.sin(a)+dy*np.cos(a))/ry;t=np.arctan2(v,u);rad=np.sqrt(u*u+v*v)/(1+.10*np.sin(3*t+phase)+.06*np.sin(5*t-phase))
   if grain:
    n=4+int(phase)%3;ang=(t+phase+np.pi/n)%(2*np.pi/n)-np.pi/n;rad/=np.cos(np.pi/n)/np.cos(ang);q=np.clip((1-rad)/.38,0,1);q=q*q*(3-2*q)*np.clip(.86+.11*u-.08*v,.55,1)
   else:q=np.maximum(0,1-rad*rad)**power
   target[j0:j1,i0:i1]+=amp*q
  def pos():return rng.uniform(xs[0],xs[-1]),rng.uniform(ys[0],ys[-1])
  for j in range(int(38*scale)):
   cx,cy=pos();stamp(H,cx,cy,rng.uniform(.15,.48),rng.uniform(.35,.9),rng.uniform(-.3,.3),rng.uniform(-.014,-.004),2.8,phase=j)
  for j in range(int(9*scale)):
   cx,cy=pos()
   for k in range(8):
    if rng.random()<.5:continue
    stamp(H,cx+.1*np.sin(k*.7+j),cy+(k-3.5)*.15,.15+.025*np.sin(k),.26,.2,rng.uniform(.0005,.0017),.9,phase=j+k)
  for j in range(int(220*scale)):
   cx,cy=pos()
   if rng.random()>.35+.65*(.5+.5*np.sin(cx*1.5+cy*.8)):continue
   stamp(H,cx,cy,rng.uniform(.025,.07),rng.uniform(.08,.23),rng.uniform(-3.14,3.14),rng.uniform(.001,.004),1.4,phase=j)
  for j in range(int(6*scale)):
   cx,cy=pos();stamp(comp,cx,cy,rng.uniform(.55,.8),rng.uniform(.7,1.5),rng.uniform(-.4,.4),-.55,2,phase=j)
  comp=np.clip(comp,.2,1);before=H.copy()
  for j in range(int(27000*scale)):
   cx,cy=pos();ix=min(np.searchsorted(xs,cx),len(xs)-1);iy=min(np.searchsorted(ys,cy),len(ys)-1);loose=comp[iy,ix];pocket=np.clip(-before[iy,ix]/.012,0,1)
   if rng.random()>np.clip(.15+.65*loose+.2*pocket,.2,.95):continue
   r=rng.uniform(.012,.030);stamp(H,cx,cy,r,r*rng.uniform(.45,2.3),rng.uniform(-3.14,3.14),rng.uniform(.001,.004)*min(1,r/.018),.75,True,j)
  H=before+(H-before)*comp
  for j in range(int(2900*scale)):
   cx,cy=pos();stamp(H,cx,cy,rng.uniform(.009,.03),rng.uniform(.01,.035),rng.uniform(-3,3),rng.uniform(-.0035,-.0008),1.5,phase=j)
  X,Y=np.meshgrid(xs,ys);edge=self.edge(X,Y);weights=np.gradient(ys)[:,None]*np.gradient(xs)[None,:];H-=np.sum(H*edge*weights)/np.sum(edge*weights);return H*edge

def sample_detail(x,y,path=None):
 """Bilinear native fine-relief sampler for later anchored details; zero outside road."""
 from pathlib import Path
 if path is None:path=Path(__file__).resolve().parents[1]/'art/studies/ground-089/relief.npz'
 d=np.load(path);xs,ys,H=d['x'],d['y'],d['height'];x=np.asarray(x);y=np.asarray(y);ix=np.clip(np.searchsorted(xs,x)-1,0,len(xs)-2);iy=np.clip(np.searchsorted(ys,y)-1,0,len(ys)-2);u=np.clip((x-xs[ix])/(xs[ix+1]-xs[ix]),0,1);v=np.clip((y-ys[iy])/(ys[iy+1]-ys[iy]),0,1)
 h=H[iy,ix]*(1-u)*(1-v)+H[iy,ix+1]*u*(1-v)+H[iy+1,ix]*v*(1-u)+H[iy+1,ix+1]*u*v
 return np.where((x>=xs[0])&(x<=xs[-1])&(y>=ys[0])&(y<=ys[-1]),h,0)
