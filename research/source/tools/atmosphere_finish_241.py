"""Small accepted-fog adjustment: 90% optical strength and a new spatial realization."""
import bpy

def apply(scene):
 ob=scene.objects['Distant dust volume - real lighting'];old=ob.active_material
 m=old.copy();m.name='241 Ten percent lighter rerolled atmosphere';ob.active_material=m
 n=m.node_tree.nodes;l=m.node_tree.links;changes=[]
 for name,offset in [('219 Broad billow stable seed',(51.3,-8.7,22.6)),('219 Fine variation stable seed',(-38.4,16.8,43.7))]:
  q=n[name];changes.append({'node':name,'before':list(q.inputs[1].default_value),'after':list(offset)});q.inputs[1].default_value=offset
 for name,socket in [('Volume Scatter','Density'),('136 Orange atmospheric radiance','Strength')]:
  target=n[name].inputs[socket];source=target.links[0].from_socket
  q=n.new('ShaderNodeMath');q.name='241 Ninety percent '+socket;q.operation='MULTIPLY';q.inputs[1].default_value=.9
  l.new(source,q.inputs[0]);l.new(q.outputs[0],target)
 return {'material':m.name,'optical_density_and_radiance_multiplier':.9,'noise_offsets':changes,'noise_scales_and_variance_unchanged':True,'palette_unchanged':True}
