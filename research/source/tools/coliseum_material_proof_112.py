import bpy,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-112/material-study';O.mkdir(parents=True,exist_ok=True)
from coliseum_materials_112 import apply_materials
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-111/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];apply_materials(C)
keep=set(C.all_objects);bpy.data.batch_remove(ids=[o for o in list(s.objects) if o not in keep and o.type not in ['CAMERA','LIGHT']]);s.world=bpy.data.worlds.new('112 Neutral proof');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.2,.2,.2,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.4
cam=s.camera;cam.location=(3.5,147,55);target=Vector((3.5,194,47));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.filepath=str(O/'crown-painted.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'));bpy.ops.render.render(write_still=True)
