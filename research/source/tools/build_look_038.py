import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-038';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-037/scene.blend'));s=bpy.context.scene
# Calibrate display sky against prior rendered sample; atmosphere lifts its blue channel.
def rgb(h):
 vals=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)+(1,)
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND' and n.name!='Background':n.inputs['Color'].default_value=rgb('#d23c08')
# Add a broad, bounded normal-based tonal grouping to painted surfaces, while retaining physical lighting.
# Bands follow actual surface orientation; no camera coordinates or image textures.
for m in bpy.data.materials:
 if not m.use_nodes or not (m.name.startswith('Cladding') or 'blue-gray enamel' in m.name or m.name.startswith('DUCT')):continue
 nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');base=tuple(bs.inputs['Base Color'].default_value)
 g=nt.nodes.new('ShaderNodeNewGeometry');v=nt.nodes.new('ShaderNodeVectorMath');v.operation='DOT_PRODUCT';v.inputs[1].default_value=(.65,-.45,.61);nt.links.new(g.outputs['Normal'],v.inputs[0])
 ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
 e=ramp.color_ramp.elements;e[0].position=.0;e[0].color=tuple(c*.76 for c in base[:3])+(1,);e[1].position=.55;e[1].color=tuple(min(c*1.18,1) for c in base[:3])+(1,)
 mid=e.new(.18);mid.color=base
 nt.links.new(v.outputs['Value'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.9
s.render.use_freestyle=False
s.render.filepath=str(O/'color-only.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)

exec(compile((R/"art/reviews/xenon-038/line-pass.py").read_text(),"line-pass.py","exec"))
