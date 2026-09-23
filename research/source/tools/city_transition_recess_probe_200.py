import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-transition-200';a=json.loads((O/'audit.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.hide_render or(ob.type=='MESH'and any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();origin=s.camera.matrix_world.translation;rows=[]
for row in a['rows']:
 for f in row['features']:
  if f['label'] != 'descending connected fracture':continue
  c=Vector(f['center']);di=(c-origin).normalized();hit=s.ray_cast(dg,origin,di)
  if not hit[0]:rows.append(dict(target=row['object'],result='no hit'));continue
  ob=hit[4];ev=ob.evaluated_get(dg);me=ev.to_mesh();face=me.polygons[hit[3]];m=ob.material_slots[face.material_index].material;ev.to_mesh_clear()
  rows.append(dict(target=row['object'],first_hit=ob.name,material=m.name,slot=face.material_index if False else None,center=list(c),hit=list(hit[1]),distance_beyond_original=(hit[1]-origin).length-(c-origin).length,depth=f['depth']))
(O/'recess-probe.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=1),flush=True)
