"""Second subtly warmer/lighter rust pigment,5percent biased-overlap surface coverage."""
import bpy

def apply(scene):
 C=scene.objects['Architecture | gangway_single_Y_8m'].instance_collection;cache={};rows=[]
 for ob in C.all_objects:
  if not ob.name.startswith(('Y arm','Y stem')):continue
  for slot in ob.material_slots:
   old=slot.material
   if old not in cache:
    m=old.copy();m.name='143 Warm oxide flecks '+old.name;n=m.node_tree.nodes;l=m.node_tree.links
    first=next(q for q in n if q.label=='140 Single-color coverage mask');base=next(q for q in n if q.label=='140 One oxide pigment, no nested rust colors');dest=[x.to_socket for x in base.outputs[0].links]
    geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.label='143 Independent second-layer patch field';noise.noise_dimensions='4D';noise.inputs['W'].default_value=8.31;noise.inputs['Scale'].default_value=7.1;noise.inputs['Detail'].default_value=2.5;noise.inputs['Roughness'].default_value=.7;noise.inputs['Distortion'].default_value=.28;l.new(geo.outputs['Position'],noise.inputs['Vector'])
    bias=n.new('ShaderNodeMath');bias.operation='MULTIPLY';bias.inputs[1].default_value=.02;l.new(first.outputs[0],bias.inputs[0]);score=n.new('ShaderNodeMath');score.operation='ADD';l.new(noise.outputs['Fac'],score.inputs[0]);l.new(bias.outputs[0],score.inputs[1]);mask=n.new('ShaderNodeMath');mask.label='143 Five percent weighted coverage';mask.operation='GREATER_THAN';mask.inputs[1].default_value=.620;l.new(score.outputs[0],mask.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.label='143 Slightly lighter warmer oxide';l.new(mask.outputs[0],mix.inputs[0]);l.new(base.outputs[0],mix.inputs[1]);mix.inputs[2].default_value=(.205,.073,.036,1)
    for sock in dest:l.new(mix.outputs[0],sock)
    cache[old]=m
   slot.link='OBJECT';slot.material=cache[old];rows.append(ob.name)
 return {'changed_slots':rows,'threshold':.620,'overlap_bias':.02,'second_pigment_linear':[.205,.073,.036],'sampled_coverage':.04931640625,'geometry_and_lighting_unchanged':True}
