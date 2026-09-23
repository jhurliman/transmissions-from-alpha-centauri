import bpy
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/rocks-090';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
# Neutral physical geometry check on a bank and adjacent road.
s.render.resolution_percentage=100;s.render.use_border=False;s.render.engine='BLENDER_EEVEE';s.render.use_freestyle=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.use_nodes=False
mat=bpy.data.materials.new('090 neutral placement clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.3,.3,.3,1);bs.inputs['Roughness'].default_value=.85
for ob in s.objects:
 if ob.type=='MESH':
  keep=ob.name=='Street foundation' or ob.get('rock_family');ob.hide_render=not keep
  if keep:ob.data.materials.clear();ob.data.materials.append(mat)
 if ob.type=='LIGHT' or ob.instance_type=='COLLECTION':ob.hide_render=True
world=bpy.data.worlds.new('090 neutral placement');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=world
bpy.ops.object.light_add(type='AREA',location=(-6,-6,7));bpy.context.object.data.energy=1400;bpy.context.object.data.size=3
s.camera.location=(-4.2,-7,3.3);s.camera.rotation_euler=(Vector((-7.5,-2.2,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=6;s.render.filepath=str(O/'placement-clay.png');bpy.ops.render.render(write_still=True)
