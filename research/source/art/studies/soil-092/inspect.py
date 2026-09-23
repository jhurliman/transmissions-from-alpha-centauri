import bpy,json
bpy.ops.wm.open_mainfile(filepath='/PATH/TO/transmissions-from-alpha-centauri/art/studies/rocks-091/scene.blend')
g=bpy.data.objects['Street foundation'];print('MATERIALS',[(i,m.name) for i,m in enumerate(g.data.materials)])
m=g.data.materials[0]
print('NODES',[(n.name,n.type,[(i.name,i.default_value if isinstance(i.default_value,(str,int,float)) else str(i.default_value)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked]) for n in m.node_tree.nodes])
print('LINKS',[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
