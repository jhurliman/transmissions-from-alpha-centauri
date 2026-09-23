import bpy,json,math
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-054'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-053/C.blend'));s=bpy.context.scene

def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def op(nt,kind,a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation=kind
 for i,v in enumerate([a,b]):
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def mix(nt,a,b,f,kind='MIX'):
 n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type=kind
 for i,v in [(0,f),(1,a),(2,b)]:
  if isinstance(v,tuple):n.inputs[i].default_value=v
  elif isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
# Sky: physical direction only, no camera-projected painting.
nt=s.world.node_tree;bg=nt.nodes.get('Background.001');coord=nt.nodes.new('ShaderNodeTexCoord');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(coord.outputs['Normal'],xyz.inputs[0]);absolute=op(nt,'ABSOLUTE',xyz.outputs['Z'],0)
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.label='054 horizon amber to high-sky vermilion';ramp.color_ramp.elements[0].position=.04;ramp.color_ramp.elements[0].color=rgb('#ee8b35');ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=rgb('#c83c16');mid=ramp.color_ramp.elements.new(.3);mid.color=rgb('#ee5724');nt.links.new(absolute,ramp.inputs[0]);nt.links.new(mix(nt,ramp.outputs[0],(.96,.74,1.04,1),1,'MULTIPLY'),bg.inputs['Color'])
vol=bpy.data.materials['Actual distant dust volume']
for n in vol.node_tree.nodes:
 if n.type=='VOLUME_SCATTER':n.inputs['Color'].default_value=(.78,.40,.18,1)
records=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree;wear=next((n for n in nt.nodes if n.type=='GROUP' and n.node_tree.name.startswith('051 ')),None)
 em=next((n for n in nt.nodes if n.type=='EMISSION' and n.outputs[0].is_linked),None)
 if not wear or not em:continue
 source=em.inputs['Color'].links[0].from_socket
 sep=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(wear.inputs['Base'].links[0].from_socket,sep.inputs[0]);warm=op(nt,'GREATER_THAN',op(nt,'SUBTRACT',sep.outputs[0],sep.outputs[2]),.005)
 color=mix(nt,source,(1.17,1.0,.98,1),warm,'MULTIPLY')
 service='Services' in wear.node_tree.name and ('PIP' in m.name or 'DUCT' in m.name)
 if service:
  if ('PIP' in m.name and 'blue-gray enamel' in m.name):
   color=mix(nt,color,(.49,.65,.74,1),1,'MULTIPLY')
  geo=nt.nodes.new('ShaderNodeNewGeometry');noise=nt.nodes.new('ShaderNodeTexNoise');nt.links.new(geo.outputs['Position'],noise.inputs['Vector']);noise.inputs['Scale'].default_value=1.7;noise.inputs['Detail'].default_value=2
  active=op(nt,'GREATER_THAN',noise.outputs['Fac'],.53)
  scars=nt.nodes.new('ShaderNodeTexNoise');scars.inputs['Scale'].default_value=8.5;scars.inputs['Detail'].default_value=2.5;nt.links.new(geo.outputs['Position'],scars.inputs['Vector']);mask=op(nt,'MULTIPLY',active,op(nt,'GREATER_THAN',scars.outputs['Fac'],.66))
  color=mix(nt,color,(.37,.32,.32,1),op(nt,'MULTIPLY',mask,.82),'MULTIPLY')
  # Bands run along curved pipes because their surface normal is stable axially.
  normal=nt.nodes.new('ShaderNodeVectorMath');normal.operation='DOT_PRODUCT';nt.links.new(geo.outputs['Normal'],normal.inputs[0]);normal.inputs[1].default_value=(.68,-.65,.34)
  band=op(nt,'MULTIPLY',op(nt,'GREATER_THAN',normal.outputs['Value'],.55),op(nt,'LESS_THAN',normal.outputs['Value'],.77))
  slow=nt.nodes.new('ShaderNodeVectorMath');slow.operation='MULTIPLY';nt.links.new(geo.outputs['Position'],slow.inputs[0]);slow.inputs[1].default_value=(1.7,1.7,.35)
  breakup=nt.nodes.new('ShaderNodeTexNoise');breakup.inputs['Scale'].default_value=2;breakup.inputs['Detail'].default_value=1;nt.links.new(slow.outputs[0],breakup.inputs['Vector']);sections=op(nt,'GREATER_THAN',breakup.outputs['Fac'],.44)
  band=op(nt,'MULTIPLY',band,sections)
  # Off-white/cool pigment lift, not a physical specular lobe.
  color=mix(nt,color,rgb('#b8b5ae'),op(nt,'MULTIPLY',band,.22))
  records.append(m.name)
 nt.links.new(color,em.inputs['Color'])
s.render.filepath=str(O/'render.png');(O/'audit.json').write_text(json.dumps({'service_materials':records,'rust_red_linear_gain':1.17,'sky':['#ee8b35','#ee5724','#c83c16'],'dust_scatter':[.78,.40,.18],'highlight':'Normal-driven band with world-space axial breakup, 22% off-white mix','geometry_changed':False},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
