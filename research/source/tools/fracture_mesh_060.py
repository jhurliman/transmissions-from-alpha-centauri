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
verts=[];faces=[];mats=[]
for poly in polys:
 poly=orient(poly.simplify(.0015,preserve_topology=True),sign=1);rings=[list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in poly.interiors]
 def inset(ring,amount):
  out=[]
  for j,b in enumerate(ring):
   a=np.array(ring[j-1]);b=np.array(b);c=np.array(ring[(j+1)%len(ring)]);p=b-a;q=c-b;l1=np.linalg.norm(p);l2=np.linalg.norm(q);p/=l1;q/=l2;n1=np.array([-p[1],p[0]]);n2=np.array([-q[1],q[0]]);v=n1+n2;v/=max(np.linalg.norm(v),1e-9);distance=min(amount,.22*l1,.22*l2)/max(.4,np.dot(v,n1));out.append(tuple(b+v*distance))
  return out
 amount=.006
 for attempt in range(10):
  inners=[inset(r,amount) for r in rings];inner=Polygon(inners[0],inners[1:])
  if inner.is_valid and poly.covers(inner):break
  amount*=.5
 else:raise RuntimeError('Cannot create a valid chamfer inset')
 ids=[]
 for ring,inside in zip(rings,inners):
  layers=[]
  for coords,z in [(ring,.018),(ring,0),(inside,-.022)]:
   layer=[]
   for x,y in coords:layer.append(len(verts));verts.append((x,y,z))
   layers.append(layer)
  ids.append(layers)
  for k in range(2):
   for j in range(len(ring)):
    h=(j+1)%len(ring);faces.append((layers[k][j],layers[k][h],layers[k+1][h],layers[k+1][j]));mats.append(0)
 for shape,layer,material in [(poly,0,0),(inner,2,1)]:
  coords=rings if layer==0 else inners;lookup={tuple(p):ids[k][layer][j] for k,ring in enumerate(coords) for j,p in enumerate(ring)}
  for tri in constrained_delaunay_triangles(shape).geoms:
   faces.append(tuple(lookup[tuple(p)] for p in list(tri.exterior.coords)[:3]));mats.append(material)
json.dump({'vertices':verts,'faces':faces,'materials':mats,'polygons':len(polys)},open(sys.argv[2],'w'))
