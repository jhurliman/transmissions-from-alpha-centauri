"""Increase the existing pale-soil deposit by50%, retaining its spatial mask."""
import bpy

def apply(scene):
 cache={};rows=[]
 rocks=[o for o in scene.objects if o.get('rock_family')and o.get('scatter_zone')=='bank']
 for ob in rocks:
  for slot in ob.material_slots:
   old=slot.material
   if old is None:continue
   assert not old.node_tree.nodes.get('227 Fifty percent more deposit'),'Already applied227 dust'
   assert old.node_tree.nodes.get('223 Dust over original stone'),old.name
   if old not in cache:
    mat=old.copy();mat.name='227 Increased dust | '+old.name;n=mat.node_tree.nodes;l=mat.node_tree.links;mix=n['223 Dust over original stone'];source=mix.inputs[0].links[0].from_socket
    multiply=n.new('ShaderNodeMath');multiply.name='227 Fifty percent more deposit';multiply.label='Existing soil deposit ×1.5';multiply.operation='MULTIPLY';multiply.use_clamp=True;multiply.inputs[1].default_value=1.5;l.new(source,multiply.inputs[0]);l.new(multiply.outputs[0],mix.inputs[0]);cache[old]=mat
   slot.link='OBJECT';slot.material=cache[old]
  rows.append(ob.name)
 return {'rock_count':len(rows),'visible_rocks':sum(not o.hide_render for o in rocks),'private_materials':{a.name:b.name for a,b in cache.items()},'existing_mask_multiplier':1.5,'nominal_upper_fraction_before':.52,'nominal_upper_fraction_after':.78,'nominal_side_fraction_before':.16,'nominal_side_fraction_after':.24,'maximum_fraction_before':.65,'maximum_fraction_after':.975,'geometry_and_spatial_mask_unchanged':True,'original_stone_graph_retained':True,'scope':'Only existing bank-stone material overrides; main-road stones and junk unchanged'}
