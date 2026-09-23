"""One-pixel visible ownership ceiling for subtractive four-part work."""
import bpy,json,sys,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];sys.path[:0]=[str(R/'tools'),str(R/'art/studies/coliseum-174/native')];O=R/'art/studies/coliseum-176/feasibility';from repair_174 import apply;from coliseum_arch_ratio_125 import mapping
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];apply(C);_,_,unpack=mapping();names=set(json.load(open(R/'config/coliseum-broad-crown-176.json'))['targets'])
for ob in s.objects:
 if ob.type=='MESH'and(ob.hide_render or any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;rows=[];blockers={};t0=time.time()
for y in range(474,600):
 for x in range(1418,1590):
  q=iv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-origin).normalized();ok,p,n,fi,ob,_=s.ray_cast(dg,origin,di)
  if not ok:continue
  if ob.name not in names:
   if x<1440 or x>1548:blockers[ob.name]=blockers.get(ob.name,0)+1
   continue
  r,a,z=unpack(p)
  if z<67.8:continue
  protected=(r<=70 or (-2.3555<a<-2.321 and z<=71.15)or(-2.263<=a<=-2.243 and z>=71.6))
  rows.append({'pixel':[x,y],'object':ob.name,'face':fi,'authored':[r,a,z],'world':list(p),'protected':protected})
out={'source':'173 plus174 in memory','window':[1418,474,1590,600],'rays_cast':172*126,'eligible_target_hits':len(rows),'rows':rows,'outside_prior_bound_first_hit_blockers':blockers,'seconds':time.time()-t0};(O/'ownership-rays.json').write_text(json.dumps(out,indent=2));print('DONE',len(rows),time.time()-t0)
