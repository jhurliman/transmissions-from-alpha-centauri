import bpy,math
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/ground-087';bpy.ops.wm.open_mainfile(filepath=str(O/'B-scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=False;s.render.use_border=False
mat=bpy.data.materials.new('086 neutral clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.26,.26,.26,1);bs.inputs['Roughness'].default_value=.9
for ob in s.objects:
 keep=ob.name=='Street foundation' or ob.name.startswith(('086 finite deposits','085 clustered low'))
 if ob.type not in ['CAMERA','LIGHT']:ob.hide_render=not keep
 if ob.type=='LIGHT':ob.hide_render=True
 if keep:ob.data.materials.clear();ob.data.materials.append(mat)
w=bpy.data.worlds.new('086 neutral geometry proof');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.09,.09,.09,1);w.node_tree.nodes['Background'].inputs[1].default_value=.3;s.world=w
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.data.energy=2.5;sun.rotation_euler=(math.radians(74),0,math.radians(-75));sun.data.angle=.06
s.camera.location=(-1.6,-9.4,2.5);s.camera.rotation_euler=(Vector((-5.15,-5.5,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=6.3;s.render.resolution_x=1440;s.render.resolution_y=810
# Proof uses neutral display, independent from final illustrated compositing.
s.use_nodes=False;s.render.filepath=str(O/'B-clay.png');bpy.ops.render.render(write_still=True)
