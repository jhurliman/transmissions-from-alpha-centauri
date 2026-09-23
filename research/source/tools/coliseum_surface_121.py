"""Local weathering cleanup tied to new architecture; original palette retained."""
from coliseum_materials_115 import rgba
from coliseum_weathering_117 import apply as deposits

def apply(objects,regions):
 cache={};changed=[];target=rgba('242039')
 for ob in objects:
  if ob.type!='MESH':continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes:continue
   if old in cache:slot.material=cache[old];continue
   m=old.copy();m.name='121 Connected weather '+old.name;cache[old]=m;slot.material=m
   nodes,links=m.node_tree.nodes,m.node_tree.links;count=0
   for n in list(nodes):
    if n.type!='MIX_RGB' or n.inputs[2].is_linked:continue
    color=n.inputs[2].default_value
    if max(abs(color[k]-target[k])for k in range(3))>.00001:continue
    if not n.inputs[0].is_linked:continue
    src=n.inputs[0].links[0].from_socket
    gate=nodes.new('ShaderNodeMath');gate.operation='MULTIPLY';gate.label='121 Reduce disconnected pigment islands';gate.inputs[1].default_value=.40
    links.new(src,gate.inputs[0]);links.new(gate.outputs[0],n.inputs[0]);count+=1
   changed.append({'material':m.name,'isolated_pigment_masks_attenuated':count})
 # Explicit regions are anchored to the actual lintels/sills, not distributed at random.
 weather=deposits(objects,regions,strength=.65) if regions else []
 return {'materials':changed,'attached_deposit_materials':len(weather),'regions':regions,'island_factor':.40,'deposit_strength':.65}
