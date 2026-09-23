"""Isolated editable two-tier bay proof, native geometry and material."""
import bpy,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-111';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
keep=set(C.all_objects)
bpy.data.batch_remove(ids=[ob for ob in list(s.objects) if ob not in keep and ob.type not in ['CAMERA','LIGHT']])
s.world=bpy.data.worlds.new('110 Neutral proof world');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.2,.2,.2,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.4
cam=s.camera;cam.location=(3.5,135,34);target=Vector((3.5,193,29));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=65
s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.threads_mode='FIXED';s.render.threads=4
s.render.filepath=str(O/'bay-painted.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'bay-proof.blend'));bpy.ops.render.render(write_still=True)

bpy.context.view_layer.update();bay_transform=cam.matrix_world.copy()
cam.location=(3.5,147,55);target=Vector((3.5,194,47));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60
bpy.context.view_layer.update();crown_transform=cam.matrix_world.copy();s.render.filepath=str(O/'crown-painted.png');bpy.ops.render.render(write_still=True)
cam.matrix_world=bay_transform;cam.data.lens=65

clay=bpy.data.materials.new('110 Bay clay proof');clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.34,.32,.30,1)
for ob in C.objects:
 if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(clay)
s.render.filepath=str(O/'bay-clay.png');bpy.ops.render.render(write_still=True)

cam.matrix_world=crown_transform;cam.data.lens=60;s.render.filepath=str(O/'crown-clay.png');bpy.ops.render.render(write_still=True)
