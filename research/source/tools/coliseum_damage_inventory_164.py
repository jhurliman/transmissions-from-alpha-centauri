"""Read-only native receiver/material graph inventory, no render or scene save."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from collections import Counter
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-164/diagnosis';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-163/scene.blend'));s=bpy.context.scene
for o in s.objects:
 if o.type=='MESH'and(o.hide_render or any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in o.material_slots)):o.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();org=cam.matrix_world.translation
boxes={'tower7_right_shoulder':[1725,570,1845,770],'tower10_left_lower_shoulder':[2025,730,2130,900]};rows=[];mats={}
for label,(x0,y0,x1,y1) in boxes.items():
 for y in range(y0,y1,15):
  for x in range(x0,x1,15):
   q=iv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-org).normalized();ok,p,n,fi,ob,_=s.ray_cast(dg,org,di)
   if not ok:continue
   ev=ob.evaluated_get(dg);me=ev.to_mesh();idx=me.polygons[fi].material_index if 0<=fi<len(me.polygons)else None;mat=ob.material_slots[idx].material if idx is not None and idx<len(ob.material_slots)else None;ev.to_mesh_clear()
   rows.append({'region':label,'pixel':[x,y],'object':ob.name,'face':fi,'material':mat.name if mat else None,'world':list(p),'normal':list(n)})
   if mat:mats[mat.name]=mat

(O/'damage-receivers.json').write_text(json.dumps(rows,indent=2));print(sorted(set(r['object']for r in rows)),flush=True)
