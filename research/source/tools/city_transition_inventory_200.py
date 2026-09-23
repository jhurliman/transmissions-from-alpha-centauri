import bpy,json,sys,collections,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-transition-200';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/beam-rust-197/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.hide_render or (ob.type=='MESH' and any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;C=bpy.data.collections['133 Ruined transition structures'];names=set(o.name for o in C.objects);rows=[];hits=collections.defaultdict(list)
for ob in C.objects:
 ps=[world_to_camera_view(s,cam,ob.matrix_world@Vector(v))for v in ob.bound_box];rows.append(dict(object=ob.name,vertices=len(ob.data.vertices),faces=len(ob.data.polygons),bounds=[min(p.x for p in ps)*3840,(1-max(p.y for p in ps))*2885,max(p.x for p in ps)*3840,(1-min(p.y for p in ps))*2885],materials=[sl.material.name if sl.material else None for sl in ob.material_slots]))
for y in range(880,1530,4):
 for x in range(1080,2720,4):
  
  if not any(r['bounds'][0]-2<=x<=r['bounds'][2]+2 and r['bounds'][1]-2<=y<=r['bounds'][3]+2 for r in rows):continue
  q=iv@Vector((2*(x+.5)/3840-1,1-2*(y+.5)/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-origin).normalized();ok,p,n,fi,ob,_=s.ray_cast(dg,origin,di)
  if ok and ob.name in names:hits[ob.name].append(dict(pixel=[x,y],point=list(p),normal=list(n),face=fi))
report=dict(source='beam-rust-197',objects=rows,visible_samples=dict(hits),summary={n:len(v)for n,v in sorted(hits.items(),key=lambda kv:-len(kv[1]))});(O/'inventory.json').write_text(json.dumps(report,indent=2));print('VISIBLE',report['summary'],flush=True)
