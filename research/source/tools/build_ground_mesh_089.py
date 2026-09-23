"""Dense continuous dirt surface with preserved native fracture voids."""
from pathlib import Path
import sys,json,numpy as np,shapely,time
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from ground_relief_089 import Relief
O=R/'art/studies/ground-089';O.mkdir(exist_ok=True);d=json.loads((R/'art/studies/ground-087/base-ground.json').read_text());oldv=np.array(d['vertices']);region=box(-8.2,-10.5,8.2,35);void=[];retained=[];outside=[]
for f,m in zip(d['faces'],d['materials']):
 v=oldv[f];p=Polygon(v[:,:2]);area=p.area;top=m==0 and np.max(np.abs(v[:,2]+.04))<.0002
 if m==1 and area>1e-9:void.append(shapely.make_valid(p))
 if not top:
  for k in range(1,len(f)-1):retained.append(([f[0],f[k],f[k+1]],m))
 elif area>1e-9:
  q=shapely.make_valid(p).difference(region)
  outside.extend(p for p in shapely.get_parts(shapely.constrained_delaunay_triangles(q)) if p.geom_type=='Polygon')
void=shapely.set_precision(shapely.make_valid(unary_union(void)),1e-6);shapely.prepare(void)
xs=np.linspace(-8.2,8.2,1173);ys=np.concatenate([np.linspace(-10.5,2,894),np.linspace(2,15,435)[1:],np.linspace(15,35,251)[1:]])
X,Y=np.meshgrid(xs,ys);field=Relief();print('Relief start',X.shape,flush=True);H=field.generate(xs,ys);print('Relief ready',flush=True)
# Fade intrinsic grains beside native crack openings to meet unchanged fracture walls exactly.
buffer=shapely.buffer(void,.06);shapely.prepare(buffer);flatx=X.ravel();flaty=Y.ravel();fade=np.ones(flatx.shape)
for start in range(0,len(flatx),100000):
 end=min(start+100000,len(flatx));px=flatx[start:end];py=flaty[start:end];sel=shapely.contains_xy(buffer,px,py);dist=shapely.distance(shapely.points(px[sel],py[sel]),void);t=np.clip(dist/.045,0,1);fade[start:end][sel]=t*t*(3-2*t)
H*=fade.reshape(H.shape);edge=field.edge(X,Y);weights=np.gradient(ys)[:,None]*np.gradient(xs)[None,:];correction=np.sum(H*weights)/np.sum(edge*fade.reshape(H.shape)*weights);H-=correction*edge*fade.reshape(H.shape)
macro=field.macro(X,Y);grid=np.column_stack([flatx,flaty,(-.04+macro+H).ravel()]);offset=len(oldv);verts=[oldv,grid];extras=[];extra_lookup={};fs=[];mats=[];smooth=[]
for f,m in retained:fs.append(f);mats.append(m);smooth.append(False)
def addtri(coords):
 ids=[]
 for p in coords[:3]:
  key=(round(float(p[0]),6),round(float(p[1]),6))
  if key not in extra_lookup:
   extra_lookup[key]=offset+len(grid)+len(extras);extras.append((key[0],key[1],-.04))
  ids.append(extra_lookup[key])
 fs.append(ids);mats.append(0);smooth.append(True)
for p in outside:addtri(list(p.exterior.coords))
blocks=[]
for j in range(len(ys)-1):
 cells=shapely.box(xs[:-1],ys[j],xs[1:],ys[j+1]);hit=shapely.intersects(cells,void);i=np.flatnonzero(~hit);v0=offset+j*len(xs)+i;v1=v0+1;v2=v1+len(xs);v3=v0+len(xs);blocks.append(np.concatenate([np.column_stack([v0,v1,v2]),np.column_stack([v0,v2,v3])]).astype(np.int32))
 for cell in cells[hit]:
  q=cell.difference(void)
  for p in shapely.get_parts(shapely.constrained_delaunay_triangles(q)):
   if p.geom_type=='Polygon' and p.area>1e-11:addtri(list(p.exterior.coords))
 if j%150==0:print('mesh row',j,flush=True)
# Top clipping vertices are on either grid cell boundaries or crack boundaries. Interpolate same fine field, then fade.
e=np.asarray(extras);oldv[:,2]+=field.macro(oldv[:,0],oldv[:,1])
if len(e):
 ix=np.clip(np.searchsorted(xs,e[:,0])-1,0,len(xs)-2);iy=np.clip(np.searchsorted(ys,e[:,1])-1,0,len(ys)-2);u=np.clip((e[:,0]-xs[ix])/(xs[ix+1]-xs[ix]),0,1);v=np.clip((e[:,1]-ys[iy])/(ys[iy+1]-ys[iy]),0,1);hh=H[iy,ix]*(1-u)*(1-v)+H[iy,ix+1]*u*(1-v)+H[iy+1,ix]*v*(1-u)+H[iy+1,ix+1]*u*v
 dist=shapely.distance(shapely.points(e[:,:2]),void);hh=np.where(dist<1e-5,0,hh);inside=(e[:,0]>=xs[0])&(e[:,0]<=xs[-1])&(e[:,1]>=ys[0])&(e[:,1]<=ys[-1]);hh*=inside;e[:,2]+=field.macro(e[:,0],e[:,1])+hh
vertices=np.concatenate([oldv,grid,e]);faces=np.concatenate([np.asarray(fs,np.int32)]+blocks);materials=np.concatenate([np.asarray(mats,np.int16),np.zeros(sum(len(b) for b in blocks),np.int16)]);sm=np.concatenate([np.asarray(smooth,bool),np.ones(sum(len(b) for b in blocks),bool)])
# Compact away unused original and crack-interior grid vertices.
used=np.unique(faces);remap=np.empty(len(vertices),np.int32);remap[used]=np.arange(len(used));vertices=vertices[used];faces=remap[faces]
# Weld coincident clipped/grid endpoints for continuous smooth surface normals.
keys=np.round(vertices,6);_,first,inverse=np.unique(keys,axis=0,return_index=True,return_inverse=True);vertices=vertices[first];faces=inverse[faces].astype(np.int32)
np.savez_compressed(O/'ground.npz',vertices=vertices.astype(np.float32),faces=faces,materials=materials,smooth=sm)
np.savez_compressed(O/'relief.npz',x=xs,y=ys,height=H.astype(np.float32))
audit={'vertices':len(vertices),'triangles':len(faces),'road_extent_m':[-8.2,-10.5,8.2,35],'grid_x_m':float(xs[1]-xs[0]),'grid_y_m':[.014,.03,.08],'macro_datum_lowering_m':field.delta,'fine_area_weighted_mean_m':float(np.sum(H*weights)/np.sum(weights)),'fine_minmax_m':[float(H.min()),float(H.max())],'fine_rms_m':float(np.sqrt(np.sum(H*H*weights)/np.sum(weights))),'macro_area_weighted_mean_m':float(np.sum(macro*weights)/np.sum(weights)),'total_area_weighted_mean_m':float(np.sum((macro+H)*weights)/np.sum(weights)),'native_crack_openings_preserved':True,'fine_fades_at_crack_edges_m':.045,'method':'Unique world-space deposition/compaction-inspired native relief, approved088 scales. No tiled samples or shader bump.'}
(O/'audit.json').write_text(json.dumps(audit,indent=2));print(audit,flush=True)
