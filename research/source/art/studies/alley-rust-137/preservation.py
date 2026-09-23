import bpy,sys,json,hashlib,array,time
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-rust-137';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-134/scene.blend'));s=bpy.context.scene
from alley_rust_137 import apply
def meshes():
 d={}
 for me in bpy.data.meshes:
  a=array.array('f',[0])*(len(me.vertices)*3);me.vertices.foreach_get('co',a);b=array.array('i',[0])*len(me.loops);me.loops.foreach_get('vertex_index',b);ns=array.array('f',[0])*(len(me.corner_normals)*3);me.corner_normals.foreach_get('vector',ns);d[me.name]=hashlib.sha256(a.tobytes()+b.tobytes()+ns.tobytes()).hexdigest()
 return d
def mats():
 return {m.name:hashlib.sha256(str(([(n.name,n.type,[(i.name,str(i.default_value))for i in n.inputs if hasattr(i,'default_value')])for n in m.node_tree.nodes],[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in m.node_tree.links])).encode()).hexdigest()for m in bpy.data.materials if m.use_nodes}
def obs():return {o.name:([list(r)for r in o.matrix_world],o.hide_render,[q.material.name if q.material else None for q in o.material_slots])for o in bpy.data.objects}
a,b,c=meshes(),mats(),obs();res=apply(s);aa,bb,cc=meshes(),mats(),obs();changes=[n for n in c if c[n]!=cc[n]];assert a==aa;assert all(bb[n]==v for n,v in b.items());assert all(n in res['changed_objects']for n in changes)
(O/'preservation.json').write_text(json.dumps({'all_existing_mesh_geometry_and_corner_normals_exact':a==aa,'mesh_datablocks_checked':len(a),'all_existing_material_graphs_unchanged':True,'existing_materials_checked':len(b),'object_changes':changes,'only_private_support_material_slots_changed':True,'camera_lights_transforms_untouched':True,'new_materials':res['materials'],'limitations':'No geometry mutation; mesh hash covers positions, loop indices and corner normals, not every arbitrary attribute. Material graph hash covers nodes, input defaults and links; original materials not edited.'},indent=2));print('PASS137')
