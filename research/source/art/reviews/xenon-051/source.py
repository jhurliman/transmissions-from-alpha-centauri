import bpy,json,math
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-051'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-050/hybrid.blend'));s=bpy.context.scene

def build_group(name,service=False):
 g=bpy.data.node_groups.new(name,'ShaderNodeTree');g.interface.new_socket(name='Base',in_out='INPUT',socket_type='NodeSocketColor');g.interface.new_socket(name='Color',in_out='OUTPUT',socket_type='NodeSocketColor');nt=g
 inp=nt.nodes.new('NodeGroupInput');out=nt.nodes.new('NodeGroupOutput');geo=nt.nodes.new('ShaderNodeNewGeometry')
 def mathn(kind,a,b):
  n=nt.nodes.new('ShaderNodeMath');n.operation=kind
  for i,v in enumerate([a,b]):
   if isinstance(v,(float,int)):n.inputs[i].default_value=v
   else:nt.links.new(v,n.inputs[i])
  return n.outputs[0]
 def noise(scale,vec=None):
  n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=2;n.inputs['Roughness'].default_value=.72;nt.links.new(vec or geo.outputs['Position'],n.inputs['Vector']);return n.outputs['Fac']
 def mix(base,col,fac,kind='MIX'):
  n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type=kind;nt.links.new(base,n.inputs[1]);nt.links.new(fac,n.inputs[0]) if not isinstance(fac,(int,float)) else setattr(n.inputs[0],'default_value',fac)
  if isinstance(col,tuple):n.inputs[2].default_value=col
  else:nt.links.new(col,n.inputs[2])
  return n.outputs[0]
 # Hierarchy: quiet/active regions -> small scars -> tiny chips. Stable world coordinates.
 gate=mathn('SMOOTHSTEP' if False else 'GREATER_THAN',noise(1.1),.54 if service else .50)
 fine=mathn('MULTIPLY',gate,mathn('GREATER_THAN',noise(24),.67 if service else .645))
 scar=mathn('MULTIPLY',gate,mathn('GREATER_THAN',noise(3.5),.715 if service else .70))
 marks=mathn('MAXIMUM',fine,scar)
 # Short thin vertical wear, significantly sparser on industrial enamel.
 v=nt.nodes.new('ShaderNodeVectorMath');v.operation='MULTIPLY';nt.links.new(geo.outputs['Position'],v.inputs[0]);v.inputs[1].default_value=(1,1,.12)
 scratch=mathn('MULTIPLY',mathn('GREATER_THAN',noise(23,v.outputs[0]),.70),gate)
 marks=mathn('MAXIMUM',marks,scratch)
 dark=mix(inp.outputs['Base'],(.26,.27,.33,1) if service else (.34,.29,.28,1),1,'MULTIPLY')
 color=mix(inp.outputs['Base'],dark,mathn('MULTIPLY',marks,.9))
 # Sparse pale fragments, offset from dark scarring; no embossed bump/glints.
 off=nt.nodes.new('ShaderNodeVectorMath');off.operation='ADD';nt.links.new(geo.outputs['Position'],off.inputs[0]);off.inputs[1].default_value=(.026,.018,.035)
 pale=mathn('MULTIPLY',gate,mathn('GREATER_THAN',noise(24,off.outputs[0]),.68))
 pale=mathn('MULTIPLY',pale,mathn('SUBTRACT',1,marks))
 light=mix(inp.outputs['Base'],(1.38,1.32,1.23,1),1,'MULTIPLY');color=mix(color,light,mathn('MULTIPLY',pale,.55))
 nt.links.new(color,out.inputs[0]);return g
fac=build_group('051 Facade | clustered chips and short scars');svc=build_group('051 Services | sparse enamel abrasions',True)
records=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree;ramp=next((n for n in nt.nodes if n.label=='050 hybrid painted light'),None)
 if not ramp:continue
 # Find base color input at the lighting multiplication, preserving existing weather graphs.
 lighting=next((l.to_node for l in ramp.outputs[0].links if l.to_node.type=='MIX_RGB'),None)
 if not lighting:continue
 is_service=m.name.startswith(('PIP','DUCT','Service','Pipe')) or any(t in m.name.lower() for t in ['enamel','galvan','steel','metal'])
 if 'Cladding' in m.name or 'coating' in m.name:is_service=False
 is_facade=any(t in m.name for t in ['coating','Cladding','Structure','concrete','mineral','Seam loss','panel'])
 if is_service or is_facade:
  base=lighting.inputs[1].links[0].from_socket
  detail=nt.nodes.new('ShaderNodeGroup');detail.node_tree=svc if is_service else fac;nt.links.new(base,detail.inputs['Base']);nt.links.new(detail.outputs[0],lighting.inputs[1]);records.append((m.name,'service' if is_service else 'facade'))
 # Group contact shading, retaining flatter broad surfaces.
 for n in nt.nodes:
  if n.type=='AMBIENT_OCCLUSION':n.inputs['Distance'].default_value=1.1
  if n.label=='050 Local recess shadow':
   n.color_ramp.elements[0].position=.35;n.color_ramp.elements[0].color=(.17,.18,.25,1)
   n.color_ramp.elements[1].position=.82
 # Under-surfaces become one deliberate dark family, no specular contribution.
 em=next((n for n in nt.nodes if n.type=='EMISSION' and n.outputs[0].is_linked),None)
 if em:
  geom=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Normal'],sep.inputs[0]);test=nt.nodes.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=-.35;nt.links.new(sep.outputs['Z'],test.inputs[0]);mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[2].default_value=(.42,.44,.54,1);nt.links.new(test.outputs[0],mul.inputs[0]);nt.links.new(em.inputs['Color'].links[0].from_socket,mul.inputs[1]);nt.links.new(mul.outputs[0],em.inputs['Color'])
for ls in s.view_layers[0].freestyle_settings.linesets:
 style=ls.linestyle
 if 'Fine structural' in ls.name:style.thickness=.42;style.alpha=.46
 else:style.thickness=1.10;style.alpha=.9
 # Subtle longitudinal variation; avoid perfect mechanical stroke weight.
 mod=style.thickness_modifiers.new('051 restrained stroke variation','NOISE');mod.amplitude=.12;mod.period=32
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
(O/'audit.json').write_text(json.dumps({'material_families':records,'geometry_changed':False,'camera':list(s.camera.location),'lens':s.camera.data.lens,'marks':'World-space noise, region-gated pinholes, scars, short scratches and offset pale flecks; services use independent lower density thresholds.'},indent=2))
bpy.ops.render.render(write_still=True)
