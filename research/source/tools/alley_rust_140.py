"""Consistent Y steel and single-pigment scattered corrosion, user correction140."""
import bpy

def apply(scene):
 rows=[];cache={}
 for host_name in ['Architecture | gangway_single_Y_8m','Architecture | gangway_single_Y_8m.001']:
  host=scene.objects[host_name];left=not host_name.endswith('.001');C=host.instance_collection
  for ob in C.all_objects:
   if not ob.name.startswith(('Y arm','Y stem')):continue
   for slot in ob.material_slots:
    old=slot.material
    if not old:continue
    key=(old.name,left,'arm' if ob.name.startswith('Y arm') else 'stem')
    if key not in cache:
     m=old.copy();m.name='140 Consistent steel '+old.name;n=m.node_tree.nodes;l=m.node_tree.links
     dark=n.get('Mix (Legacy).002');assert dark and dark.blend_type=='MULTIPLY'
     for link in list(dark.inputs[0].links):l.remove(link)
     dark.inputs[0].default_value=0;dark.label='140 Artificial underside multiplier disabled; actual light and AO retained'
     if left:
      em=next(q for q in n if q.type=='EMISSION');cor=next(q for q in n if q.label=='137 Finite fastener corrosion over retained steel')
      base=cor.inputs[1].links[0].from_socket if ob.name.startswith('Y arm') else em.inputs['Color'].links[0].from_socket
      geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.label='140 Irregular dispersed coating loss';noise.inputs['Scale'].default_value=5.2;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.72;noise.inputs['Distortion'].default_value=.22;l.new(geo.outputs['Position'],noise.inputs['Vector'])
      mask=n.new('ShaderNodeMath');mask.operation='GREATER_THAN';mask.label='140 Single-color coverage mask';mask.inputs[1].default_value=.546;l.new(noise.outputs['Fac'],mask.inputs[0])
      mix=n.new('ShaderNodeMixRGB');mix.label='140 One oxide pigment, no nested rust colors';l.new(mask.outputs[0],mix.inputs[0]);l.new(base,mix.inputs[1]);mix.inputs[2].default_value=(.17,.063,.033,1);l.new(mix.outputs[0],em.inputs['Color'])
      # Retain bolt-fed runoff above the new plain rust on the stem.
      if ob.name.startswith('Y stem'):
       l.new(cor.inputs[1].links[0].from_socket,mix.inputs[1]);l.new(mix.outputs[0],cor.inputs[1]);l.new(cor.outputs[0],em.inputs['Color'])
     cache[key]=m
    slot.link='OBJECT';slot.material=cache[key];rows.append({'host':host_name,'object':ob.name,'material':cache[key].name})
 return {'changed_slots':rows,'materials':[m.name for m in cache.values()],'orientation_darkener_disabled':True,'left_repeated_seam_fields_bypassed':True,'left_rust_threshold':.546,'pigment_linear':[.17,.063,.033],'coverage_target':'approximately25percent by4096area-weighted native shader samples','geometry_normals_lights_unchanged':True}
