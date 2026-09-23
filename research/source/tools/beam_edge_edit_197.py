"""Art-directed correction to the near edge of the left forward Y arm only."""
import bpy
from beam_rust_connections_196 import Field

def apply(scene):
 ob=bpy.data.objects['Y arm front flange.010'];old=ob.material_slots[0].material;m=old.copy();m.name='197 Left near arm irregular middle pair'
 node=next(n for n in m.node_tree.nodes if n.type=='GROUP' and n.node_tree and n.node_tree.name.startswith('196 Irregular'))
 prior=node.node_tree;seed=node.inputs[2].default_value
 g=bpy.data.node_groups.new('197 Selected edge middle patches and visible runoff','ShaderNodeTree')
 for name in ('Along in half widths','Across in half widths','Seed'):g.interface.new_socket(name=name,in_out='INPUT',socket_type='NodeSocketFloat')
 g.interface.new_socket(name='Edge rooted coverage',in_out='OUTPUT',socket_type='NodeSocketFloat')
 i=g.nodes.new('NodeGroupInput');o=g.nodes.new('NodeGroupOutput');p=g.nodes.new('ShaderNodeGroup');p.node_tree=prior
 for k in range(3):g.links.new(i.outputs[k],p.inputs[k])
 f=Field(g);s,u,seed_socket=i.outputs[0],i.outputs[1],i.outputs[2]
 def swath(center,span):return f.smooth(f.op('DIVIDE',f.sub(span,f.op('ABSOLUTE',f.sub(s,center))),span*.38))
 # Replace the two middle repeats with one long shallow feather and one small offset tuft.
 a=swath(6.0,3.1);b=swath(-5.3,1.05);reach=f.op('MAXIMUM',f.mul(a,.39),f.mul(b,.76));tip=f.mul(reach,.22)
 for k,spacing in enumerate((.065,.113,.197)):
  phase=f.add(seed_socket,119.7+k*23.1);pos=f.add(s,f.mul(phase,.031));cell=f.op('FLOOR',f.op('DIVIDE',pos,spacing));h=f.hash(f.add(cell,phase));h2=f.hash(f.add(cell,f.add(phase,31.9)))
  center=f.mul(spacing,f.add(cell,f.add(.2,f.mul(.6,h))));w=f.mul(spacing,f.add(.2,f.mul(.3,h2)));strand=f.smooth(f.op('DIVIDE',f.sub(w,f.op('ABSOLUTE',f.sub(pos,center))),f.mul(w,.7)))
  tip=f.op('MAXIMUM',tip,f.mul(reach,f.mul(strand,f.add(.3,f.mul(.7,h2)))))
 d=f.add(1,u);new=f.mul(.9,f.smooth(f.op('DIVIDE',f.sub(tip,d),.05)))
 window=f.mul(f.smooth(f.op('DIVIDE',f.add(s,8),.6)),f.smooth(f.op('DIVIDE',f.sub(10.2,s),.6)))
 near=f.smooth(f.op('DIVIDE',f.sub(f.mul(-1,u),.03),.30));blend=f.mul(window,near)
 result=f.add(f.mul(p.outputs[0],f.sub(1,blend)),f.mul(new,blend))
 # Wider than the old subpixel line, with irregular edges and two unequal breaks.
 width=f.add(.155,f.add(f.mul(.018,f.op('SINE',f.mul(s,2.3))),f.mul(.010,f.op('SINE',f.mul(s,7.1)))))
 gap1=swath(-9.6,.65);gap2=swath(2.5,.27);open_run=f.sub(1,f.op('MAXIMUM',gap1,gap2))
 rail=f.mul(.85,f.mul(open_run,f.smooth(f.op('DIVIDE',f.sub(width,d),.045))))
 result=f.op('MAXIMUM',result,f.mul(near,rail));g.links.new(result,o.inputs[0])
 node.node_tree=g;node.inputs[2].default_value=seed;node.label='197 Long shallow feather plus smaller offset tuft; visible broken edge runoff'
 ob.material_slots[0].link='OBJECT';ob.material_slots[0].material=m
 return {'object':ob.name,'old_material':old.name,'new_material':m.name,'near_edge':'Across coordinate -1','middle_patch_centers_half_width_units':[6.0,-5.3],'middle_patch_half_spans':[3.1,1.05],'connector_width_half_width_units':.155,'other_beams_and_opposite_edge_preserved':True,'geometry_palette_and_lighting_unchanged':True,'references':['RS-01','RS-02','UP-03']}
