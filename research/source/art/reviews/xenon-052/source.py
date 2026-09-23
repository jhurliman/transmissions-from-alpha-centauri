import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-052'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-051/scene.blend'));s=bpy.context.scene

def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)
def ratio(a,b):return tuple(x/y for x,y in zip(rgb(a),rgb(b)))+(1,)
# Observed rendered families -> reference family centers. Lighting structure retained.
cool=ratio('#53556b','#63688b');violet=ratio('#61586a','#63688b');warm=ratio('#805a50','#95806e')
def mathn(nt,kind,a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation=kind
 for i,v in enumerate([a,b]):
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def mix(nt,a,b,fac,kind='MIX'):
 n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type=kind
 for i,v in [(0,fac),(1,a),(2,b)]:
  if isinstance(v,tuple):n.inputs[i].default_value=v
  elif isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
# Actual fixing locations from the evaluated assembled scene, not invented floating scars.
anchors=[]
for ins in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=ins.object
 if ob.name.startswith('047 ') and any(t in ob.name.lower() for t in ['fix','bolt','washer']):
  p=ins.matrix_world.translation
  if 8<p.x<12 and 7<p.y<20 and .1<p.z<3:anchors.append(tuple(p))
anchors=list(dict.fromkeys(anchors))[:8]
records=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree;em=next((n for n in nt.nodes if n.type=='EMISSION' and n.outputs[0].is_linked),None)
 wear=next((n for n in nt.nodes if n.type=='GROUP' and n.node_tree.name.startswith('051 ')),None)
 if not em or not wear:continue
 base=wear.inputs['Base'].links[0].from_socket
 sep=nt.nodes.new('ShaderNodeSeparateColor');sep.mode='RGB';nt.links.new(base,sep.inputs[0])
 warmmask=mathn(nt,'GREATER_THAN',mathn(nt,'SUBTRACT',sep.outputs[0],sep.outputs[2]),.005)
 geom=nt.nodes.new('ShaderNodeNewGeometry');noise=nt.nodes.new('ShaderNodeTexNoise');nt.links.new(geom.outputs['Position'],noise.inputs['Vector']);noise.inputs['Scale'].default_value=.17;noise.inputs['Detail'].default_value=1
 variation=nt.nodes.new('ShaderNodeMapRange');nt.links.new(noise.outputs['Fac'],variation.inputs['Value']);variation.inputs['From Min'].default_value=.43;variation.inputs['From Max'].default_value=.61
 blue=mix(nt,cool,violet,variation.outputs[0]);mult=mix(nt,blue,warm,warmmask)
 old=em.inputs['Color'].links[0].from_socket;corrected=mix(nt,old,mult,1,'MULTIPLY');nt.links.new(corrected,em.inputs['Color'])
 # Sparse irregular stains immediately below known gallery fixings.
 if 'Seam loss' in m.name or 'lighter panel' in m.name:
  mask=None
  for p in anchors:
   vec=nt.nodes.new('ShaderNodeVectorMath');vec.operation='SUBTRACT';nt.links.new(geom.outputs['Position'],vec.inputs[0]);vec.inputs[1].default_value=(p[0],p[1],p[2]-.045)
   scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';nt.links.new(vec.outputs[0],scale.inputs[0]);scale.inputs[1].default_value=(7,22,10)
   length=nt.nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';nt.links.new(scale.outputs[0],length.inputs[0]);splotch=mathn(nt,'LESS_THAN',length.outputs['Value'],1)
   mask=splotch if mask is None else mathn(nt,'MAXIMUM',mask,splotch)
  if mask is not None:
   fine=nt.nodes.new('ShaderNodeTexNoise');nt.links.new(geom.outputs['Position'],fine.inputs['Vector']);fine.inputs['Scale'].default_value=32;ragged=mathn(nt,'GREATER_THAN',fine.outputs['Fac'],.48);mask=mathn(nt,'MULTIPLY',mask,ragged)
   nt.links.new(mix(nt,corrected,(.34,.24,.24,1),mathn(nt,'MULTIPLY',mask,.62),'MULTIPLY'),em.inputs['Color'])
 records.append(m.name)
# Broaden the size range without increasing fine-dot density.
for g in bpy.data.node_groups:
 if not g.name.startswith('051 '):continue
 for n in g.nodes:
  if n.type=='TEX_NOISE' and abs(n.inputs['Scale'].default_value-3.5)<.01:n.inputs['Scale'].default_value=2.2
  if n.type=='VECT_MATH' and n.operation=='MULTIPLY' and abs(n.inputs[1].default_value[2]-.12)<.001:n.inputs[1].default_value[2]=.085
(O/'audit.json').write_text(json.dumps({'colors':{'cool_target':'#53556b','violet_target':'#61586a','warm_target':'#805a50','cool_multiplier':cool,'warm_multiplier':warm},'materials':records,'actual_fixing_anchors':anchors,'geometry_changed':False},indent=2))
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
