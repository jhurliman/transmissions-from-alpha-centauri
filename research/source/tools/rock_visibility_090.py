import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/rocks-090';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
sun=next(o for o in s.objects if o.type=='LIGHT' and o.data.type=='SUN');direction=sun.matrix_world.to_quaternion()@Vector((0,0,1))
for m in bpy.data.materials:
 if not m.name.startswith(('090 earth stone','090 bank fragment')):continue
 n=m.node_tree.nodes;l=m.node_tree.links;r=next(q for q in n if q.type=='VALTORGB');base=tuple(r.color_ramp.elements[-1].color);n.clear();geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=direction;mx=n.new('ShaderNodeMath');mx.operation='MAXIMUM';mx.inputs[1].default_value=0;mp=n.new('ShaderNodeMapRange');mp.inputs['To Min'].default_value=.25;mp.inputs['To Max'].default_value=1.;mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=base;em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(geo.outputs['Normal'],dot.inputs[0]);l.new(dot.outputs['Value'],mx.inputs[0]);l.new(mx.outputs[0],mp.inputs[0]);l.new(mp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs[0])
s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.use_freestyle=False;s.render.resolution_percentage=200;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.03;s.render.border_max_x=.42;s.render.border_min_y=.14;s.render.border_max_y=.52;s.render.filepath=str(O/'road-detail.png');bpy.ops.render.render(write_still=True)
# Neutral physical geometry check on a bank and adjacent road.
s.render.resolution_percentage=100;s.render.use_border=False;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1400;s.render.resolution_y=1000;s.use_nodes=False
mat=bpy.data.materials.new('090 neutral placement clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.3,.3,.3,1);bs.inputs['Roughness'].default_value=.85
for ob in s.objects:
 if ob.type=='MESH':
  keep=ob.name=='Street foundation' or ob.get('rock_family');ob.hide_render=not keep
  if keep:ob.data.materials.clear();ob.data.materials.append(mat)
 if ob.type=='LIGHT':ob.hide_render=True
world=bpy.data.worlds.new('090 neutral placement');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=world
bpy.ops.object.light_add(type='AREA',location=(-6,-6,7));bpy.context.object.data.energy=1400;bpy.context.object.data.size=3
s.camera.location=(-4.2,-7,3.3);s.camera.rotation_euler=(Vector((-7.5,-2.2,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=6;s.render.filepath=str(O/'placement-clay.png');bpy.ops.render.render(write_still=True)
