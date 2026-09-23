"""Preserve locked scene; permit only explicitly listed sky/cloud color edits."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
source=(R/'tools/validate_coliseum_116.py').read_text().split('x,xm=snapshot(')[0]
source=source.replace("d.append([m.name if m else None for m in o.data.materials])", "d.append([(slot.link,slot.material.name if slot.material else None) for slot in o.material_slots])")
source=source.replace('for m in o.data.materials:', 'for m in [slot.material for slot in o.material_slots]:')
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
 skipped={n.name for n in nt.nodes if n.label in ['075 Amber horizon to vermilion zenith','126 Strip top fifth, solid below roofline']}
 nodes=[]
 for n in nt.nodes:
  if n.name in skipped:continue
  row=[n.name,n.bl_idname,[(i.name,value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]]
  if hasattr(n,'color_ramp'):row.append([(e.position,tuple(e.color)) for e in n.color_ramp.elements])
  nodes.append(row)
 return digest((nodes,[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in nt.links if l.from_node.name not in skipped and l.to_node.name not in skipped]))
before,bm=snapshot(R/'art/studies/coliseum-125/scene.blend');bg=cloud_geometry();bw=protected_world()
after,am=snapshot(R/'art/studies/coliseum-126/scene.blend');ag=cloud_geometry();aw=protected_world()
audit=json.loads((R/'art/studies/coliseum-126/generation.json').read_text())['sky']
assignments=audit['cloud_assignments'];allowed={a['object'] for a in assignments}|{'__world_graph__'}
oldm={a['old_material'] for a in assignments};newm={a['new_material'] for a in assignments}
changes=[k for k,v in before.items() if after.get(k)!=v]
mat_changes=[k for k,v in bm.items() if am.get(k)!=v]
result={'baseline':'125','candidate':'126','nonlandmark_objects_compared':len(before),
 'authorized_sky_cloud_changes':sorted(set(changes)&allowed),
 'unexpected_object_changes':sorted(set(changes)-allowed),
 'unexpected_objects':sorted(set(after)-set(before)),
 'cloud_geometry_uv_transform_changes':[k for k,v in bg.items() if ag.get(k)!=v],
 'material_graphs_compared':len(bm),'unexpected_material_changes':[k for k in mat_changes if k not in oldm],
 'unexpected_added_materials':sorted(set(am)-set(bm)-newm),
 'protected_world_changed':bw!=aw,
 'cloud_assignment_mismatches':[a['object'] for a in assignments if not any(slot.material and slot.material.name==a['new_material'] for slot in bpy.data.objects[a['object']].material_slots)]}
(R/'art/studies/coliseum-126/preservation.json').write_text(json.dumps(result,indent=2))
assert not any(result[k] for k in ['protected_world_changed','unexpected_object_changes','unexpected_objects','cloud_geometry_uv_transform_changes','unexpected_material_changes','unexpected_added_materials','cloud_assignment_mismatches']),result
print(json.dumps(result))
C=bpy.data.collections['110 Coliseum detailed front ruin']
bpy.data.libraries.write(str(R/'art/studies/coliseum-126/kit.blend'),{C},fake_user=True,compress=True)
