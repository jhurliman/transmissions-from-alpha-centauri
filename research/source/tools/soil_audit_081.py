import bpy,json
from mathutils.bvhtree import BVHTree
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-081';out={}
for file in ['discrete-scene.blend','selected-scene.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(O/file));g=bpy.data.objects['Street foundation'];tree=BVHTree.FromObject(g,bpy.context.evaluated_depsgraph_get());count=0;bad=0;empty=0;badpts=[]
 for ob in bpy.context.scene.objects:
  if not ob.name.startswith('077 broken earth lip'):continue
  if not len(ob.data.vertices):empty+=1
  ob.data.calc_loop_triangles()
  for p in ob.data.loop_triangles:
   c=ob.matrix_world@(sum((ob.data.vertices[i].co for i in p.vertices),Vector())/3)
   if c.z<-.04:continue
   hit=tree.ray_cast(Vector((c.x,c.y,.2)),Vector((0,0,-1)),1)
   if hit[0] is not None:
    count+=1
    if hit[0].z<-.043:bad+=1;badpts.append({'object':ob.name,'point':list(c),'ground':list(hit[0]),'ground_material':g.data.polygons[hit[2]].material_index if hit[2]<len(g.data.polygons) else -1})
 out[file]={'surface_face_samples':count,'samples_projecting_over_recess':bad,'empty_lips':empty,'bad_points':badpts}
(O/'junction-audit.json').write_text(json.dumps(out,indent=2));print(out)
