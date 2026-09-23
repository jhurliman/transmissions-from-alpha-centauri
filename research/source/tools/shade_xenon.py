import bpy,math,json,random
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-003'
bpy.ops.wm.open_mainfile(filepath=str(O/'xenon-refinement.blend'));s=bpy.context.scene;random.seed(69)
# Graphic three-value form shading with contact occlusion; all reference pixels remain separate.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nodes=m.node_tree.nodes;em=next((n for n in nodes if n.type=='EMISSION'),None)
 if not em:continue
 base=tuple(em.inputs[0].default_value);nodes.clear();links=m.node_tree.links
 out=nodes.new('ShaderNodeOutputMaterial');emit=nodes.new('ShaderNodeEmission');links.new(emit.outputs[0],out.inputs[0])
 geo=nodes.new('ShaderNodeNewGeometry');dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.5,-.35,.79);links.new(geo.outputs['Normal'],dot.inputs[0])
 ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
 ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1]);el=ramp.color_ramp.elements[0];el.position=0;el.color=(*(c*.50 for c in base[:3]),1)
 el=ramp.color_ramp.elements.new(.22);el.color=(*(c*.78 for c in base[:3]),1)
 el=ramp.color_ramp.elements.new(.66);el.color=(*base[:3],1);links.new(dot.outputs['Value'],ramp.inputs[0])
 ao=nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=1.4;ao.samples=8
 mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.45;links.new(ramp.outputs[0],mix.inputs[1]);links.new(ao.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],emit.inputs[0])
# Road should remain its own quiet color plane, avoiding exaggerated normal shading.
# Break a few large pieces rather than applying noise to every vertex.
for o in bpy.data.objects:
 if o.type!='MESH':continue
 if o.name.startswith('Right diagonal buttress'):
  o.scale.y=random.uniform(.8,1.12);o.rotation_euler.y+=random.uniform(-.06,.05)
 if o.name.startswith('Left vertical structure'):
  o.scale.z=random.uniform(.8,1);o.location.y+=random.uniform(-.12,.12)
 if o.name.startswith('Remaining wall panel') and random.random()<.28:
  o.rotation_euler.y=random.uniform(-.08,.08)
# Line renderer supplies sparse silhouette/crease strokes from actual geometry.
s.render.use_freestyle=True;s.render.line_thickness=.65
ls=bpy.context.view_layer.freestyle_settings.linesets[0];ls.linestyle.color=(.025,.020,.033);ls.linestyle.thickness=.65
ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True;bpy.context.view_layer.freestyle_settings.crease_angle=math.radians(110)
s.cycles.samples=24
# Scene opens to camera; reference is packed and available in Image Editor.
s.render.filepath=str(O/'refinement-shaded.png');s['stage']='003 geometry and graphic shading study; user review pending'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'xenon-refinement-shaded.blend'));bpy.ops.render.render(write_still=True)
