"""Refine the road surface while preserving actual crack openings and interiors."""
from pathlib import Path
import sys,json,numpy as np,shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from ground_heightfield_087 import Field
O=R/'art/studies/ground-087';d=json.loads((O/'base-ground.json').read_text());oldv=np.array(d['vertices']);region=box(-8.2,-10.5,8.2,35)
void=[];retained=[];out_top=[]
for f,mi in zip(d['faces'],d['materials']):
 v=oldv[f];p=Polygon(v[:,:2]);area=p.area
 if mi==1 and area>1e-9:void.append(p)
 top=mi==0 and np.max(np.abs(v[:,2]+.04))<.0002
 if not top:retained.append((f,mi))
 elif area>1e-9:
  outside=shapely.make_valid(p).difference(region)
  if not outside.is_empty:out_top.extend(shapely.get_parts(shapely.constrained_delaunay_triangles(outside)))
void=shapely.set_precision(shapely.make_valid(unary_union(void)),.000001);shapely.prepare(void)
verts=oldv.tolist();faces=[];mi=[];smooth=[];lookup={}
def vi(p):
 k=tuple(round(float(x),6) for x in p)
 if k not in lookup:lookup[k]=len(verts);verts.append(k)
 return lookup[k]
def tri(coords,material=0,sm=True):
 inds=[vi((p[0],p[1],-.04)) for p in coords[:3]]
 faces.append(inds);mi.append(material);smooth.append(sm)
for f,m in retained:
 for k in range(1,len(f)-1):faces.append([f[0],f[k],f[k+1]]);mi.append(m);smooth.append(False)
for p in out_top:
 if p.geom_type=='Polygon':tri(list(p.exterior.coords))
xs=np.linspace(-8.2,8.2,139);ys=np.linspace(-10.5,35,381);count=0
for j in range(len(ys)-1):
 for i in range(len(xs)-1):
  x0,x1=xs[i:i+2];y0,y1=ys[j:j+2];cell=box(x0,y0,x1,y1)
  if not shapely.intersects(void,cell):
   tri([(x0,y0),(x1,y0),(x1,y1)]);tri([(x0,y0),(x1,y1),(x0,y1)])
  else:
   clipped=shapely.make_valid(cell.difference(void))
   for p in shapely.get_parts(shapely.constrained_delaunay_triangles(clipped)):
    if p.geom_type=='Polygon' and p.area>1e-10:tri(list(p.exterior.coords))
  count+=1
 print('row',j,flush=True) if j%80==0 else None
verts=np.asarray(verts);faces=np.asarray(faces,np.int32);mi=np.asarray(mi,np.int16);smooth=np.asarray(smooth,bool)
for variant in 'ABC':
 field=Field(variant);v=verts.copy();v[:,2]+=field(v[:,0],v[:,1]);np.savez_compressed(O/f'{variant}-ground.npz',vertices=v,faces=faces,materials=mi,smooth=smooth)
 xx,yy=np.meshgrid(np.linspace(-7.35,7.35,160),np.linspace(-8.4,32.4,440));h=field(xx,yy)
 stats={'variant':variant,'lower_height_cap_m':field.cap,'flat_scale':field.flat_scale,'sampled_flat_fraction':float((h<.0005).mean()),'max_height_m':float(h.max()),'lower_radius_m':[3.2,5.2],'grid_cell_m':[float(xs[1]-xs[0]),float(ys[1]-ys[0])],'vertices':len(v),'triangles':len(faces),'continuous_native_surface':True,'preserved_crack_openings':True}
 (O/f'{variant}-audit.json').write_text(json.dumps(stats,indent=2));print(stats,flush=True)
