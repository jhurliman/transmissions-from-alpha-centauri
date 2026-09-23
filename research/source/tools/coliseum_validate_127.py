"""Preserve locked scene, including instance geometry; permit only selected pipe and attached ink edits."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
source=(R/'tools/validate_coliseum_116.py').read_text().split('x,xm=snapshot(')[0]
source=source.replace("d.append([m.name if m else None for m in o.data.materials])", "d.append([(slot.link,slot.material.name if slot.material else None) for slot in o.material_slots])")
source=source.replace('for m in o.data.materials:', 'for m in [slot.material for slot in o.material_slots]:')
source=source.replace("  data[o.name]=digest(d)", "  if o.instance_type=='COLLECTION' and o.instance_collection:d.append(instance_payload(o.instance_collection))\n  data[o.name]=digest(d)")
payload_cache={}
def instance_payload(collection):
 key=(bpy.data.filepath,collection.name)
 if key in payload_cache:return payload_cache[key]
 rows=[]
 for ob in collection.all_objects:
  row=[ob.name,ob.type,ob.hide_render,[tuple(r)for r in ob.matrix_local]]
  if ob.type=='MESH':row.extend([[tuple(v.co)for v in ob.data.vertices],[(tuple(p.vertices),p.material_index)for p in ob.data.polygons]])
  if hasattr(ob.data,'materials'):
   row.append([(slot.link,slot.material.name if slot.material else None)for slot in ob.material_slots])
   graphs=[]
   for slot in ob.material_slots:
    m=slot.material
    if not m or not m.use_nodes:continue
    nodes=[]
    for n in m.node_tree.nodes:
     nd=[n.name,n.bl_idname,[(i.name,value(i.default_value))for i in n.inputs if hasattr(i,'default_value')]]
     if hasattr(n,'color_ramp'):nd.append([(e.position,tuple(e.color))for e in n.color_ramp.elements])
     nodes.append(nd)
    graphs.append([m.name,nodes,[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)for l in m.node_tree.links]])
   row.append(graphs)
  rows.append(row)
 result=digest(rows);payload_cache[key]=result;return result
exec(source)
def cloud_geometry():
 out={}
 for ob in bpy.data.collections['082 Derived flat clouds'].all_objects:
  d=[ob.type,[tuple(r) for r in ob.matrix_world],ob.hide_render]
  if ob.type=='MESH':
   d += [[tuple(v.co) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],[[tuple(v.uv) for v in layer.data] for layer in ob.data.uv_layers]]
  out[ob.name]=digest(d)
 return out
def protected_world():
 nt=bpy.context.scene.world.node_tree
 skipped=set()
 nodes=[]
 for n in nt.nodes:
  if n.name in skipped:continue
  row=[n.name,n.bl_idname,[(i.name,value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]]
  if hasattr(n,'color_ramp'):row.append([(e.position,tuple(e.color)) for e in n.color_ramp.elements])
  nodes.append(row)
 return digest((nodes,[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in nt.links if l.from_node.name not in skipped and l.to_node.name not in skipped]))
def selected_pipe_dimensions():
 receiver=bpy.data.objects['XL | primary_building_receiver'];body=next(o for o in receiver.instance_collection.objects if o.name.startswith('Projecting receiver'))
 dims=[max(v.co[i]for v in body.data.vertices)-min(v.co[i]for v in body.data.vertices)for i in range(3)]
 trunk=bpy.data.objects['XL | trunk_1350_L3'];tube=next(o for o in trunk.instance_collection.objects if o.name.startswith('Hollow straight section'))
 return {'box_local_dimensions':dims,'tube_diameter':max(v.co.x for v in tube.data.vertices)-min(v.co.x for v in tube.data.vertices),'pipe_axis_x':trunk.location.x}
before,bm=snapshot(R/'art/studies/coliseum-126/scene.blend');bg=cloud_geometry();bw=protected_world();bp=selected_pipe_dimensions()
after,am=snapshot(R/'art/studies/coliseum-127/scene.blend');ag=cloud_geometry();aw=protected_world();ap=selected_pipe_dimensions()
audit=json.loads((R/'art/studies/coliseum-127/generation.json').read_text())
assignments=[];allowed={x['object']for x in audit['pipe']['moved_instances']}|{'XL | primary_building_receiver'}|set(audit['pipe']['shortened_wall_mounts'])|set(audit['pipe_ink']['changed_objects']);oldm=set();newm=set()
changes=[k for k,v in before.items() if after.get(k)!=v]
mat_changes=[k for k,v in bm.items() if am.get(k)!=v]
result={'baseline':'126','candidate':'127','nonlandmark_objects_compared':len(before),
 'authorized_pipe_geometry_and_ink_changes':sorted(set(changes)&allowed),
 'unexpected_object_changes':sorted(set(changes)-allowed),
 'unexpected_objects':sorted(set(after)-set(before)),
 'cloud_geometry_uv_transform_changes':[k for k,v in bg.items() if ag.get(k)!=v],
 'material_graphs_compared':len(bm),'unexpected_material_changes':[k for k in mat_changes if k not in oldm],
 'unexpected_added_materials':sorted(set(am)-set(bm)-newm),
 'protected_world_changed':bw!=aw,
 'selected_pipe_before':bp,'selected_pipe_after':ap,
 'pipe_dimensions_invalid':abs(ap['box_local_dimensions'][1]/bp['box_local_dimensions'][1]-.66)>.00001 or abs(ap['box_local_dimensions'][0]-bp['box_local_dimensions'][0])>.00001 or abs(ap['tube_diameter']-bp['tube_diameter'])>.00001,
 'cloud_assignment_mismatches':[a['object'] for a in assignments if not any(slot.material and slot.material.name==a['new_material'] for slot in bpy.data.objects[a['object']].material_slots)]}
(R/'art/studies/coliseum-127/preservation.json').write_text(json.dumps(result,indent=2))
assert not any(result[k] for k in ['pipe_dimensions_invalid','protected_world_changed','unexpected_object_changes','unexpected_objects','cloud_geometry_uv_transform_changes','unexpected_material_changes','unexpected_added_materials','cloud_assignment_mismatches']),result
print(json.dumps(result))
C=bpy.data.collections['110 Coliseum detailed front ruin']
bpy.data.libraries.write(str(R/'art/studies/coliseum-127/kit.blend'),{C},fake_user=True,compress=True)
