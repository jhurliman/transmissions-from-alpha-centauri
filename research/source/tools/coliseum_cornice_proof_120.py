import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-120/cornice'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry-proof.blend'));bpy.context.view_layer.update();camera_pose=bpy.context.scene.camera.matrix_world.copy();camera_scale=bpy.context.scene.camera.data.ortho_scale
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];s.render.use_freestyle=False;s.render.resolution_x=2880;s.render.resolution_y=2164;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.37;s.render.border_max_x=.65;s.render.border_min_y=.59;s.render.border_max_y=.90
for ob in bpy.data.objects:
 if 'Landmark contact ink'in ob.name:ob.hide_render=True
s.render.filepath=str(O/'main-crop.png');bpy.ops.render.render(write_still=True)
keep={o for o in C.objects if o.get('bay')==8}
for ob in list(keep):
 while ob.parent:ob=ob.parent;keep.add(ob)
keep.update(o for o in s.objects if o.type in ['LIGHT','CAMERA']);bpy.data.batch_remove(ids=[o for o in list(s.objects)if o not in keep]);s.camera.matrix_world=camera_pose;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=camera_scale;s.render.use_border=False;s.render.resolution_x=1300;s.render.resolution_y=1300;s.world=bpy.data.worlds.new('120 Neutral proof');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.2,.2,.23,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.65
bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'));s.render.filepath=str(O/'painted.png');bpy.ops.render.render(write_still=True)
m=bpy.data.materials.new('120 Neutral clay');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.45,.45,.45,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.7
for ob in C.objects:
 if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(m)
s.render.filepath=str(O/'clay.png');bpy.ops.render.render(write_still=True)
