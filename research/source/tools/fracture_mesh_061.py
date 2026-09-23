import json,sys,math
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union,orient
from shapely import constrained_delaunay_triangles
# Pure 2D union then matched-ring loft; caller supplies physical planar points.
d=json.load(open(sys.argv[1]));shapes=[]
for path in d['paths']:
 p=path['points'];ws=path['widths']
 for j in range(len(p)-1):
  a=np.array(p[j]);b=np.array(p[j+1]);v=b-a;side=np.array([-v[1],v[0]])/np.linalg.norm(v)
  shapes.append(Polygon([a+side*ws[j],b+side*ws[j+1],b-side*ws[j+1],a-side*ws[j]]))
 for a,w in zip(p,ws):
  shapes.append(Polygon([(a[0]+math.cos(k*math.pi/4)*w,a[1]+math.sin(k*math.pi/4)*w) for k in range(8)]))
union=unary_union(shapes).buffer(0);polys=list(union.geoms) if union.geom_type=='MultiPolygon' else [union]
# Adaptive-looking V recess: depth is bounded by distance to the nearest mouth edge.
# Piecewise-linear sampling of the distance field makes the walls meet along a varying valley.
from shapely import points,distance
verts=[];faces=[];mats=[];stats=[]
for poly in polys:
 poly=orient(poly.simplify(.0015,preserve_topology=True),sign=1)
 triangles=[list(t.exterior.coords)[:3] for t in constrained_delaunay_triangles(poly).geoms]
 for level in range(2):
  refined=[]
  for a,b,c in triangles:
   a=np.array(a);b=np.array(b);c=np.array(c);ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2;refined.extend([(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)])
  triangles=refined
 xy=[];lookup={};tris=[]
 for tri in triangles:
  ids=[]
  for p in tri:
   key=tuple(round(float(v),10) for v in p)
   if key not in lookup:lookup[key]=len(xy);xy.append(key)
   ids.append(lookup[key])
  tris.append(ids)
 xy=np.array(xy);dist=distance(points(xy),poly.boundary);dist[dist<1e-8]=0
 modulation=.82+.18*np.sin(xy[:,0]*8.1+np.sin(xy[:,1]*5.3))
 depth=dist*math.tan(math.radians(55))*modulation
 start=len(verts);N=len(xy)
 for z in [np.full(N,.018),-depth]:
  verts.extend([(float(p[0]),float(p[1]),float(h)) for p,h in zip(xy,z)])
 edgecounts={}
 for tri in tris:
  faces.append(tuple(start+i for i in tri));mats.append(0)
  faces.append(tuple(start+N+i for i in tri[::-1]));mats.append(0)
  for a,b in zip(tri,tri[1:]+tri[:1]):
   key=tuple(sorted((a,b)));edgecounts[key]=edgecounts.get(key,0)+1
 for (a,b),count in edgecounts.items():
  if count==1:faces.append((start+a,start+b,start+N+b,start+N+a));mats.append(0)
 stats.append({'max_depth_m':float(depth.max()),'max_wall_angle_degrees':55,'minimum_depth_m':float(depth.min()),'vertices':N})
json.dump({'vertices':verts,'faces':faces,'materials':mats,'polygons':len(polys),'depth_stats':stats},open(sys.argv[2],'w'))
