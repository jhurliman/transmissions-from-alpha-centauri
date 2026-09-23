import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-122/rhythm'
def isolate():
 s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];keep={o for o in C.objects if o.get('bay')==9}
 for ob in list(keep):
  while ob.parent:ob=ob.parent;keep.add(ob)
 keep.update(o for o in s.objects if o.type in ['LIGHT','CAMERA']);bpy.data.batch_remove(ids=[o for o in list(s.objects)if o not in keep]);return s,C
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-121/scene.blend'));s,C=isolate();dep=bpy.context.evaluated_depsgraph_get();points=[]
for ob in C.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(dep);me=ev.to_mesh();points.extend(ob.matrix_world@v.co for v in me.vertices if(ob.matrix_world@v.co).z>36);ev.to_mesh_clear()
lo=Vector(tuple(min(p[k]for p in points)for k in range(3)));hi=Vector(tuple(max(p[k]for p in points)for k in range(3)));center=(lo+hi)/2;pose=(center+Vector((0,-1,.04)).normalized()*100,(center-(center+Vector((0,-1,.04)).normalized()*100)).to_track_quat('-Z','Y').to_euler());scale=max(hi.z-lo.z,(hi.x-lo.x)*1.1)*1.15
for label,path in [('baseline',R/'art/studies/coliseum-121/scene.blend'),('candidate',O/'scene.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];s.render.use_freestyle=False
 for ob in bpy.data.objects:
  if 'Landmark contact ink'in ob.name:ob.hide_render=True
 if label=='candidate':
  s.render.resolution_x=2880;s.render.resolution_y=2164;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.37;s.render.border_max_x=.65;s.render.border_min_y=.59;s.render.border_max_y=.90;s.render.filepath=str(O/'main-crop.png');bpy.ops.render.render(write_still=True)
 s,C=isolate();s.camera.location=pose[0];s.camera.rotation_euler=pose[1];s.camera.data.type='ORTHO';s.camera.data.ortho_scale=scale;s.render.use_border=False;s.render.resolution_x=1300;s.render.resolution_y=1300;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('121 Neutral proof');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.2,.2,.23,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.65
 if label=='candidate':
  bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'));s.render.filepath=str(O/'painted.png');bpy.ops.render.render(write_still=True)
 m=bpy.data.materials.new('121 Neutral clay');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.45,.45,.45,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.7
 for ob in C.objects:
  if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(m)
 s.render.filepath=str(O/(label+'-clay.png'));bpy.ops.render.render(write_still=True)
