"""Actual source-solid intervals and protected counterfactual first hits; no mesh mutation except authorized174 in memory."""
import bpy,json,sys,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[4];sys.path[:0]=[str(R/'tools'),str(R/'art/studies/coliseum-174/native')];O=R/'art/studies/coliseum-176/feasibility';cfg=json.load(open(R/'config/coliseum-broad-crown-176.json'));from repair_174 import apply;from coliseum_arch_ratio_125 import mapping
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];repair=apply(C);_,_,unpack=mapping();names=cfg['targets']
for ob in s.objects:
 if ob.type=='MESH'and(ob.hide_render or any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;trees={};triowners=[]
for name in names:
 ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();trees[name]=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[t.vertices[:]for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear()
def intervals(tree,direction):
 hits=[];offset=0.
 for _ in range(32):
  hit=tree.ray_cast(origin+direction*offset,direction)
  if hit[0]is None:break
  t=(hit[0]-origin).dot(direction)
  if not hits or t-hits[-1]>.0001:hits.append(t)
  offset=t+.0002
 return list(zip(hits[::2],hits[1::2])),len(hits)%2
rays=[];t0=time.time();odd=0
for y in range(440,635,2):
 for x in range(1440,1650,2):
  q=iv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-origin).normalized();ok,p,n,fi,ob,_=s.ray_cast(dg,origin,di)
  if not ok or ob.name not in names:continue
  au=unpack(p)
  if au[2]<67.8:continue
  parts=[]
  for name,tr in trees.items():
   vv,bad=intervals(tr,di);odd+=bad;parts.extend((a,b,name)for a,b in vv)
  if not parts:continue
  parts.sort();merged=[]
  for a,b,name in parts:
   if merged and a<=merged[-1][1]+.0005:merged[-1][1]=max(b,merged[-1][1]);merged[-1][2].append(name)
   else:merged.append([a,b,[name]])
  rays.append({'pixel':[x,y],'direction':list(di),'first_object':ob.name,'first_face':fi,'first_world':list(p),'first_authored':list(au),'solid_intervals':merged})
 print('ROW',y,'rays',len(rays),flush=True)if y%20==0 else None
# Retain every non-target geometry occluder during the virtual source-skin removal test.
for name in names:bpy.data.objects[name].hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for row in rays:
 di=Vector(row['direction']);ok,p,n,fi,ob,_=s.ray_cast(dg,origin,di);row['other_distance']=(p-origin).length if ok else 1e9;row['other_object']=ob.name if ok else None
 def cut(t,rear):
  r,a,z=unpack(origin+di*t)
  if not(-2.425<a<-2.191)or z<=67.8 or r<=rear:return False
  if -2.3555<a<-2.321 and z<=71.15:return False
  if -2.263<=a<=-2.243 and z>=71.6:return False
  return True
 for label,rear in [('conservative',72.2),('upper_bound',70.25)]:
  result=None
  for a,b,owners in row['solid_intervals']:
   if a>=row['other_distance']:break
   a+=.0003;b-=.0003
   if a>=b:continue
   if not cut(a,rear):result={'distance':a,'kind':'retained_source','owners':owners};break
   steps=math.ceil((b-a)/.025);prev=a
   for j in range(1,steps+1):
    t=min(b,a+j*(b-a)/steps)
    if not cut(t,rear):
     lo,hi=prev,t
     for _ in range(18):
      mid=(lo+hi)/2
      if cut(mid,rear):lo=mid
      else:hi=mid
     result={'distance':(lo+hi)/2,'kind':'prospective_cut_surface','owners':owners};break
    prev=t
   if result:break
  if result and result['distance']<row['other_distance']:
   p=origin+di*result['distance'];result['world']=list(p);result['authored']=list(unpack(p));result['camera_depth_from_original_first_m']=result['distance']-(Vector(row['first_world'])-origin).length
  else:result={'kind':'other_geometry_or_open_background','other':row['other_object']}
  row[label]=result
out={'source':'173 plus174 in memory','174':repair,'config':cfg,'rays':rays,'odd_source_interval_rays':odd,'seconds':time.time()-t0,'scope':'Read-only implicit removal visibility bounds, not an actual geometry candidate or rendered art. Protected rear radius, high peak strip and niche-head bearing remain.'};(O/'depth-rays.json').write_text(json.dumps(out,indent=2));print('DONE',len(rays),odd,time.time()-t0,flush=True)
