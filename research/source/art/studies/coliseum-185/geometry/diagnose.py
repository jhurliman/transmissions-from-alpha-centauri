import bpy,sys,json,types
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'tools'))
from coliseum_crown_continuation_154 import robust_crossings,freeze_render_triangles
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'))
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();out=[]
for name in json.load(open(R/'config/coliseum-course-simplification-185.json'))['targets']:
 ob=bpy.data.objects[name];me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg);M=ob.matrix_world.copy();row={'object':name,'stages':{}}
 for stage in ['evaluated_source','frozen_triangles']:
  if stage=='frozen_triangles':me=freeze_render_triangles(me)
  me.calc_loop_triangles();p=robust_crossings(types.SimpleNamespace(data=me,matrix_world=M),True)
  for q in p:
   q['faces']=[me.loop_triangles[i].polygon_index for i in q['pair']]
   px=[]
   for tri in q['triangles_world']:
    for v in tri:
     from mathutils import Vector
     co=world_to_camera_view(s,s.camera,Vector(v));px.append([co.x*3840,(1-co.y)*2885])
   q['pixel_bounds']=[min(x for x,y in px),min(y for x,y in px),max(x for x,y in px),max(y for x,y in px)]
  row['stages'][stage]={'count':len(p),'crossings':p}
 out.append(row)
(R/'art/studies/coliseum-185/geometry/source-crossings.json').write_text(json.dumps(out,indent=2))
print([(r['object'],{k:v['count']for k,v in r['stages'].items()})for r in out])
