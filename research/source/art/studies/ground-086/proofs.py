import bpy
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/ground-086';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=False
s.render.resolution_x=2880;s.render.resolution_y=2164;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=210/1440;s.render.border_max_x=1190/1440;s.render.border_min_y=1-910/1082;s.render.border_max_y=1-600/1082;s.render.filepath=str(O/'road-detail.png');bpy.ops.render.render(write_still=True)
mat=bpy.data.materials.new('086 untextured deposit proof');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.35,.35,.35,1);bs.inputs['Roughness'].default_value=.82
for ob in s.objects:
 keep=ob.name=='Street foundation' or ob.name.startswith(('086 finite deposits','085 clustered low','085 trapped and bank'))
 if ob.type not in ['CAMERA','LIGHT']:ob.hide_render=not keep
 if keep:ob.data.materials.clear();ob.data.materials.append(mat)
s.camera.location=(-7.2,-9,.7);s.camera.rotation_euler=(Vector((-3,-3.5,.03))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=36;s.render.use_border=False;s.render.resolution_x=1440;s.render.resolution_y=810;s.render.filepath=str(O/'clay-low-angle.png');bpy.ops.render.render(write_still=True)
