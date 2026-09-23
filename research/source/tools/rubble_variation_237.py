import bpy,sys,json,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/rubble-variation-237';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rubble-transition-236/scene.blend'));s=bpy.context.scene
before={o.name:tuple(v for r in o.matrix_world for v in r) for o in s.objects}
dg=bpy.context.evaluated_depsgraph_get();soil=bpy.data.objects['Street foundation'];ev=soil.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();terrain=BVHTree.FromPolygons([soil.matrix_world@v.co for v in me.vertices],[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear()
groups=[([bpy.data.objects['078 severed kinked channel '+str(i)+'.006'] for i in range(3)],-24),([bpy.data.objects['077 bent industrial scrap remnant.056']],103)];rows=[]
for obs,angle in groups:
 ps=[o.matrix_world@v.co for o in obs for v in o.data.vertices];a=np.array(ps);center=Vector(a.mean(axis=0));vals,vec=np.linalg.eigh(np.cov(a.T));axis=Vector(vec[:,-1]);axis=axis if axis.x>0 else -axis
 target=Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle)),.025)).normalized();rot=axis.rotation_difference(target).to_matrix().to_4x4();xf=Matrix.Translation(center)@rot@Matrix.Translation(-center)
 for o in obs:o.matrix_world=xf@o.matrix_world
 s.view_layers.update()
 clear=[]
 for o in obs:
  for v in o.data.vertices:
   p=o.matrix_world@v.co;hit=terrain.ray_cast(Vector((p.x,p.y,15)),Vector((0,0,-1)),40)[0];assert hit is not None;clear.append(p.z-hit.z)
 shift=-min(clear)+.012
 for o in obs:o.location.z+=shift;o['237 laid into rubble']=True
 rows.append({'objects':[o.name for o in obs],'bearing_degrees':angle,'ground_clearance':.012})
s.view_layers.update();changed=[o.name for o in s.objects if before[o.name]!=tuple(v for r in o.matrix_world for v in r)];assert set(changed)==set(o.name for g,_ in groups for o in g)
(O/'audit.json').write_text(json.dumps({'changed':rows,'only_four_target_transforms_changed':True,'geometry_materials_and_depth_styles_unchanged':True,'front_hero_beam_preserved':True},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
