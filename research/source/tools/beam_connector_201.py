"""A camera-readable, irregular edge run on the selected near left flange."""
import bpy
from beam_rust_connections_196 import Field

def apply(scene):
 ob=bpy.data.objects['Y arm front flange.010'];old=ob.material_slots[0].material;m=old.copy();m.name='201 Visible interrupted near edge oxide'
 node=next(n for n in m.node_tree.nodes if n.type=='GROUP' and n.node_tree and n.node_tree.name.startswith('197 Selected'))
 prior=node.node_tree;seed=node.inputs[2].default_value
 g=bpy.data.node_groups.new('201 Near edge readable oxide connector','ShaderNodeTree')
 for name in ('Along in half widths','Across in half widths','Seed'):g.interface.new_socket(name=name,in_out='INPUT',socket_type='NodeSocketFloat')
 g.interface.new_socket(name='Coverage',in_out='OUTPUT',socket_type='NodeSocketFloat')
 i=g.nodes.new('NodeGroupInput');o=g.nodes.new('NodeGroupOutput');p=g.nodes.new('ShaderNodeGroup');p.node_tree=prior
 for k in range(3):g.links.new(i.outputs[k],p.inputs[k])
 f=Field(g);s,u=i.outputs[0],i.outputs[1]
 def gap(c,w):return f.smooth(f.op('DIVIDE',f.sub(w,f.op('ABSOLUTE',f.sub(s,c))),w*.34))
 # The 197 run was under the ink footprint. Carry pigment farther inward while
 # retaining narrow, unequal broken runs rather than a continuous solid border.
 width=f.add(.36,f.add(f.mul(.055,f.op('SINE',f.mul(s,1.77))),f.mul(.025,f.op('SINE',f.mul(s,7.1)))))
 opened=f.sub(1,f.op('MAXIMUM',gap(-9.6,.80),gap(2.5,.40)))
 rail=f.mul(.95,f.mul(opened,f.smooth(f.op('DIVIDE',f.sub(width,f.add(1,u)),.09))))
 near=f.smooth(f.op('DIVIDE',f.sub(f.mul(-1,u),.10),.30));result=f.op('MAXIMUM',p.outputs[0],f.mul(near,rail));g.links.new(result,o.inputs[0])
 node.node_tree=g;node.inputs[2].default_value=seed;node.label='201 Broken oxide edge wide enough to emerge inside ink'
 ob.material_slots[0].link='OBJECT';ob.material_slots[0].material=m
 return {'object':ob.name,'old_material':old.name,'new_material':m.name,'middle_pair_preserved':True,'half_width_relative_connector':.36,'other_materials_unchanged':True}
