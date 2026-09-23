import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-040';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-039/scene.blend'));s=bpy.context.scene
for m in bpy.data.materials:
 if not m.name.startswith('039 Layered coating'):continue
 nt=m.node_tree;n=nt.nodes;l=nt.links
 # Find the existing shared field from the actual base color connection.
 bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');ramp=bs.inputs['Base Color'].links[0].from_node;add=ramp.inputs[0].links[0].from_node
 broad=add.inputs[0].links[0].from_node;fine_mul=add.inputs[1].links[0].from_node
 tex=next(x for x in n if x.type=='TEX_COORD' and x.object and x.object.name=='039 Building coating coordinates')
 # Quiet the uniformly fine fuzz. Most of the original broad field survives.
 fine_mul.inputs[1].default_value=.028;fine_mul.inputs[2].default_value=-.014
 vor=n.new('ShaderNodeTexVoronoi');vor.distance='MANHATTAN';vor.inputs['Scale'].default_value=2.5;l.new(tex.outputs['Object'],vor.inputs['Vector'])
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.9;noise.inputs['Detail'].default_value=1;l.new(tex.outputs['Object'],noise.inputs['Vector'])
 gate=n.new('ShaderNodeMath');gate.operation='GREATER_THAN';gate.inputs[1].default_value=.54;l.new(noise.outputs['Fac'],gate.inputs[0])
 angular=n.new('ShaderNodeMath');angular.operation='MULTIPLY_ADD';angular.inputs[1].default_value=.09;angular.inputs[2].default_value=-.045;l.new(vor.outputs['Distance'],angular.inputs[0])
 mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(angular.outputs[0],mul.inputs[0]);l.new(gate.outputs[0],mul.inputs[1])
 combined=n.new('ShaderNodeMath');combined.operation='ADD';l.new(add.outputs[0],combined.inputs[0]);l.new(mul.outputs[0],combined.inputs[1]);l.new(combined.outputs[0],ramp.inputs[0])
 # Sparse detached chips only within the neighborhood of a large coating boundary.
 near=n.new('ShaderNodeMath');near.operation='SUBTRACT';near.inputs[1].default_value=.515;l.new(combined.outputs[0],near.inputs[0])
 ab=n.new('ShaderNodeMath');ab.operation='ABSOLUTE';l.new(near.outputs[0],ab.inputs[0])
 band=n.new('ShaderNodeMath');band.operation='LESS_THAN';band.inputs[1].default_value=.07;l.new(ab.outputs[0],band.inputs[0])
 chips=n.new('ShaderNodeTexVoronoi');chips.distance='MANHATTAN';chips.inputs['Scale'].default_value=6;l.new(tex.outputs['Object'],chips.inputs['Vector'])
 dot=n.new('ShaderNodeMath');dot.operation='LESS_THAN';dot.inputs[1].default_value=.11;l.new(chips.outputs['Distance'],dot.inputs[0])
 mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';l.new(dot.outputs[0],mask.inputs[0]);l.new(band.outputs[0],mask.inputs[1])
 mix=n.new('ShaderNodeMixRGB');l.new(mask.outputs[0],mix.inputs[0]);l.new(ramp.outputs['Color'],mix.inputs[1]);mix.inputs[2].default_value=ramp.color_ramp.elements[-1].color;l.new(mix.outputs[0],bs.inputs['Base Color'])
 # Narrower intermediate coating exposure; retain the established two dominant colors.
 for e in ramp.color_ramp.elements:
  if abs(e.position-.495)<.001:e.position=.507
 m['coating_revision']='040: quieter fine edge, localized coarse angular loss, sparse boundary chips'
s.render.use_freestyle=False;s.render.filepath=str(O/'color-only.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)

exec(compile((R/"art/reviews/xenon-040/line-pass.py").read_text(),"line-pass.py","exec"))
