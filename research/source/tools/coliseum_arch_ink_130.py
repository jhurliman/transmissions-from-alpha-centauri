"""Native curved-edge ink from current evaluated masonry, no radial joint strokes."""
import bpy,math,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping
from coliseum_arch_thickness_129 import params,closest
NAME='130 Actual curved arch rim ink'
def paths(edges):
 adj={};remaining=set(tuple(sorted(e))for e in edges)
 for a,b in remaining:adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 runs=[]
 while remaining:
  endpoints=[v for e in remaining for v in e if len(adj[v])!=2];start=min(endpoints)if endpoints else min(min(e)for e in remaining);run=[start];v=start
  while True:
   candidates=sorted(w for w in adj[v]if tuple(sorted((v,w)))in remaining)
   if not candidates:break
   w=candidates[0];remaining.remove(tuple(sorted((v,w))));run.append(w);v=w
   if v==start or len(adj[v])!=2:break
  if len(run)>1:runs.append(run)
 return runs

def apply(C,radius=.035):
 if bpy.data.objects.get(NAME):raise RuntimeError('Arch rim ink exists; regenerate from source')
 _,_,unpack=mapping();dg=bpy.context.evaluated_depsgraph_get();curve=bpy.data.curves.new(NAME,'CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=radius;curve.bevel_resolution=1;curve.use_fill_caps=True;ink=bpy.data.objects.new(NAME,curve);C.objects.link(ink)
 m=bpy.data.materials.new('130 Dark plum physical rim line');m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(.018,.012,.022,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],out.inputs['Surface']);curve.materials.append(m);rows=[]
 for ob in list(C.objects):
  stone=ob.type=='MESH'and'archivolt'in ob.name and 'niche'not in ob.name.lower();wall=ob.type=='MESH'and ob.name.startswith('COL127 T')and'continuous arcade wall'in ob.name
  if not(stone or wall):continue
  t=int(ob['tier']);coords=[]
  for v in ob.data.vertices:
   rr,a,z=unpack(ob.matrix_world@v.co);b=int(ob['bay'])if stone else min(17,max(0,int((a+math.pi)/(math.tau/36))));rx,rz,sp=params(t,b);ac=-math.pi+(b+.5)*math.tau/36;d,nx,ny=closest((a-ac)*75,z-sp,rx,rz);th=math.atan2(ny*rz,nx*rx);coords.append((rr,d,th,z,sp,b))
  selected=[];rear=set();rlo=min(co[0]for co in coords);rhi=max(co[0]for co in coords)
  for e in ob.data.edges:
   i,j=e.vertices;a,b=coords[i],coords[j]
   if a[5]!=b[5]or abs(a[2]-b[2])<.00005:continue
   if abs(a[0]-b[0])>.003:continue
   if stone:
    # Both vertices on one inner/outer offset contour and one front/back face.
    if abs(a[1]-b[1])>.004 or min(abs(a[0]-rlo),abs(a[0]-rhi))>.003:continue
   else:
    if min(a[3]-a[4],b[3]-b[4])<-.005:continue
    if max(abs(a[1]+.645),abs(b[1]+.645))>.035 or min(abs(a[0]-67),abs(a[0]-75))>.003:continue
   selected.append((i,j))
   if abs(a[0]-(rlo if stone else 67))<.004:rear.add(i);rear.add(j)
  if not selected:continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh()
  if len(me.vertices)!=len(ob.data.vertices):raise RuntimeError('Topology-changing modifier '+ob.name)
  runs=paths(selected);count=0
  for run in runs:
   sp=curve.splines.new('POLY');sp.points.add(len(run)-1)
   for dst,i in zip(sp.points,run):p=ev.matrix_world@me.vertices[i].co;dst.co=(*p,1);dst.radius=1.4 if wall and i in rear else .82 if i in rear else 1.
   count+=len(run)-1
  ev.to_mesh_clear();rows.append({'source':ob.name,'curved_edges':count,'runs':len(runs),'kind':'stone perimeter'if stone else'tunnel opening'})
 ink['130 source']='Actual evaluated129 curved mesh edges; regenerate if layout/geometry changes';ink['130 no radial end edges']=True
 return {'radius_world':radius,'rear_opening_radius_world':radius*1.4,'color_linear':[.018,.012,.022],'sources':rows,'total_runs':sum(x['runs']for x in rows),'total_edges':sum(x['curved_edges']for x in rows),'geometry_source_unchanged':True,'occlusion':'Native depth-tested curve geometry, no always-on-top overlay','gaps':'Separate existing mesh edges; no connection across stones or damaged missing sections'}
if __name__=='__main__':
 O=R/'art/studies/coliseum-130/arch-ink';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-129/ink-preservation/fresh-scene.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print('INK130',a['total_runs'],a['total_edges'])
