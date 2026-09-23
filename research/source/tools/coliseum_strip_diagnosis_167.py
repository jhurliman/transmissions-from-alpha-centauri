"""Read-only ray correspondence of inherited B07 crown strip."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-167/geometry';allrows={};objects={}
for label,path in [('166',R/'art/studies/coliseum-166/scene.blend'),('167v2',O/'scene.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 for o in s.objects:
  if o.type=='MESH'and(o.hide_render or any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in o.material_slots)):o.hide_set(True)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();org=cam.matrix_world.translation;rows=[]
 for y in [605,612,620,630,640,650,660,666]:
  for x in [1778,1783,1786,1789,1792,1795,1800]:
   q=iv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-org).normalized();ok,p,n,fi,o,_=s.ray_cast(dg,org,di)
   if not ok:continue
   ev=o.evaluated_get(dg);me=ev.to_mesh();idx=me.polygons[fi].material_index if 0<=fi<len(me.polygons)else None;mat=o.material_slots[idx].material if idx is not None and idx<len(o.material_slots)else None;ev.to_mesh_clear();rows.append({'pixel':[x,y],'object':o.name,'face':fi,'material':mat.name if mat else None,'world':list(p),'normal':list(n),'distance':(p-org).length})
   if o.name not in objects:
    objects[o.name]={'type':o.type,'modifiers':[{'name':m.name,'type':m.type}for m in o.modifiers],'properties':{k:str(v)for k,v in o.items()},'bounds_world':[list(o.matrix_world@Vector(v))for v in o.bound_box]}
 allrows[label]=rows
 allrows[label+'_renderable_temporary_objects']=[o.name for o in s.objects if not o.hide_render and any(t in o.name.lower()for t in ['167 cutter','167 temporary','connected facing cutter'])]
(O/'strip-rays.json').write_text(json.dumps({'rays':allrows,'objects':objects},indent=2));from collections import Counter
for k,v in allrows.items():
 if isinstance(v,list)and v and isinstance(v[0],dict):print(k,Counter(r['object']for r in v),flush=True)
