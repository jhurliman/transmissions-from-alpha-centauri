"""Bound the240 blue balance at bright architectural edges; preserve its pigment shift.

The affected vent slats/condensers/straps share blue-balanced cladding. Avoid
unbounded luminance division, and construct the corrected RGB channels explicitly.
"""
import bpy

def apply(scene):
 rows=[]
 for m in bpy.data.materials:
  if not m.use_nodes or not m.get('240 left blue balance') or m.get('241 bounded blue balance'):continue
  nt=m.node_tree;n=nt.nodes;l=nt.links
  final=next(q for q in n if '240 left facade blue restoration' in q.label)
  source=final.inputs[1].links[0].from_socket
  # Keep240's existing world-space side and cool-pigment eligibility weight.
  def math(op,a,b,label):
   q=n.new('ShaderNodeMath');q.operation=op;q.label='241 '+label
   for s,x in zip(q.inputs,(a,b)):
    if hasattr(x,'node'):l.new(x,s)
    else:s.default_value=x
   return q.outputs[0]
  sep=n.new('ShaderNodeSeparateColor');sep.mode='RGB';sep.label='241 unchanged source channels';l.new(source,sep.inputs['Color'])
  rgb=[math('MAXIMUM',sep.outputs[i],0,'nonnegative radiance') for i in range(3)]
  toned=[math('MULTIPLY',a,b,'same240blue channel multiplier') for a,b in zip(rgb,(.82,1.035,1.39))]
  def lum(ch):
   vals=[math('MULTIPLY',a,w,'scene luminance coefficient')for a,w in zip(ch,(.2126,.7152,.0722))]
   return math('ADD',math('ADD',vals[0],vals[1],'luminance sum'),vals[2],'luminance sum')
  gain=math('DIVIDE',lum(rgb),math('MAXIMUM',lum(toned),.00001,'safe positive luminance denominator'),'luminance preservation')
  gain=math('MINIMUM',math('MAXIMUM',gain,.70,'bounded luminance correction'),1.23,'bounded luminance correction')
  combine=n.new('ShaderNodeCombineColor');combine.mode='RGB';combine.label='241 bounded explicit blue-balanced RGB'
  for i,t in enumerate(toned):l.new(math('MULTIPLY',t,gain,'bounded corrected channel'),combine.inputs[i])
  l.new(combine.outputs['Color'],final.inputs[2])
  m['241 bounded blue balance']=True
  rows.append({'material':m.name,'unchanged_multiplier':[.82,1.035,1.39],'gain_bounds':[.70,1.23],'negative_radiance_clamp':0,'source_preserved':True,'original_side_and_cool_pigment_weight_preserved':True})
 return {'materials':rows,'diagnosis':'Camera-ray sampled green-yellow pixels hit240blue-balanced facade, vent-slat, condenser and strap materials.239contains zero matching yellow-green pixels in left crop;240contains1508. Replaces unbounded RGBToBW normalization with nonnegative bounded explicit channel normalization.','new_sun_direction_preserved':True,'geometry_and_other_materials_unchanged':True,'requires_actual_render_verification':True}
