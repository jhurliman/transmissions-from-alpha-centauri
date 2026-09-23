"""Continuous metre-scale relief: preserved high deposits, broader low rises, 20% flat cores."""
import numpy as np
M=[(-5.4,-5.8,1.55,2.05,.14,.4),(-4.65,-5.05,.82,1.15,.055,-.4),(3.35,-6.2,2.05,1.6,.12,-.65),(4.6,-5.8,.85,1.05,.045,.2),(-1.2,5.3,1.7,2.1,.105,.75),(-.35,6.35,.9,1.15,.05,-.3),(5.5,6.7,1.6,2.4,.18,-.2),(-5.65,13.1,1.75,2.15,.15,.4),(2.75,15.9,2.0,2.35,.11,-.4),(-2.6,22.5,1.7,2.5,.12,.3),(5.3,25.3,1.9,2.2,.14,-.6),(-5.25,29,1.8,2.5,.17,.5)]
FLAT=[(-.1,-.8,1.5,2.0,.2),(-4.0,2.6,1.5,2.0,-.4),(3,10.7,1.8,2.0,.5),(-1,18.8,2,2.2,-.4),(3.4,29.7,1.8,2.0,.2),(-5,22,1.7,2.2,.3)]
def smooth(t):
 t=np.clip(t,0,1);return t*t*t*(10+t*(-15+6*t))
def old(x,y):
 z=np.zeros_like(np.asarray(x)+np.asarray(y),dtype=float)
 for j,(cx,cy,rx,ry,h,a) in enumerate(M):
  dx=x-cx;dy=y-cy;u=(dx*np.cos(a)+dy*np.sin(a))/rx;v=(-dx*np.sin(a)+dy*np.cos(a))/ry;phi=np.arctan2(v,u);r2=(u*u+v*v)/(1+.10*np.sin(3*phi+j*.7)+.055*np.cos(5*phi+j))**2;z+=h*np.maximum(0,1-r2)**2.2
 return z
class Field:
 def __init__(self,variant):
  self.variant=variant;self.cap={'A':.06,'B':.075,'C':.09}[variant];self.flat_scale=1.;rng=np.random.default_rng(87031);self.broad=[]
  for y in np.arange(-10,39,5.5):
   for x in [-5.8,0,5.8]:self.broad.append((x+rng.uniform(-.9,.9),y+rng.uniform(-1.2,1.2),rng.uniform(3.2,4.5),rng.uniform(3.6,5.2),rng.uniform(-.7,.7),rng.uniform(.8,1.2)))
  xx,yy=np.meshgrid(np.linspace(-7.35,7.35,120),np.linspace(-8.4,32.4,320));lo,hi=.3,2.7
  for _ in range(24):
   self.flat_scale=(lo+hi)/2;frac=float(np.mean(self(xx,yy)<.0005))
   if frac<.20:lo=self.flat_scale
   else:hi=self.flat_scale
  self.flat_scale=(lo+hi)/2
 def __call__(self,x,y):
  x=np.asarray(x);y=np.asarray(y);hi=old(x,y);w=np.zeros_like(x+y,dtype=float)
  for j,(cx,cy,rx,ry,a,weight) in enumerate(self.broad):
   dx=x-cx;dy=y-cy;u=(dx*np.cos(a)+dy*np.sin(a))/rx;v=(-dx*np.sin(a)+dy*np.cos(a))/ry;r2=u*u+v*v;w+=weight*np.maximum(0,1-r2)**3
  low=self.cap*(1-np.exp(-2.2*w));mask=np.ones_like(w)
  for cx,cy,rx,ry,a in FLAT:
   u=((x-cx)*np.cos(a)+(y-cy)*np.sin(a))/(rx*self.flat_scale);v=(-(x-cx)*np.sin(a)+(y-cy)*np.cos(a))/(ry*self.flat_scale);r=np.sqrt(u*u+v*v);mask*=smooth((r-1)/.65)
  low*=mask
  # Smooth maximum preserves established tall peaks without stacking lower hills onto them.
  k=.008;h=np.maximum(hi,low)+.25*k*np.maximum(0,1-np.abs(hi-low)/k)**2
  # Exact flat cores: do not add the smooth-max rounding at zero.
  h=np.where((hi<1e-7)&(low<1e-7),0,h)
  edge=smooth((8.2-np.abs(x))/.85)*smooth((y+10.5)/1.4)*smooth((35-y)/2.0)
  return h*edge
