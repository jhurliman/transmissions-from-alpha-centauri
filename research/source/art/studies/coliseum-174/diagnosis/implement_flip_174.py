"""Isolated two-face native diagonal flip; no carving or source scene mutation."""
import bpy,json,sys,types,hashlib,array,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-174/native';O.mkdir(parents=True,exist_ok=True)
from coliseum_crown_continuation_154 import robust_crossings
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-168/scene.blend'));ob=bpy.data.objects['COL110 U4 aperture head'];dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);evaluated=ev.to_mesh();M=ev.matrix_world.copy();old=ob.data
expected={711:(304,82,83),4612:(1263,304,83)};newfaces={711:(1263,82,83),4612:(1263,304,82)}
for i,v in expected.items():
 if tuple(old.polygons[i].vertices)!=v or tuple(evaluated.polygons[i].vertices)!=v:raise RuntimeError('Raw/evaluated face correspondence failed')
if len(old.vertices)!=len(evaluated.vertices)or any(tuple(a.vertices)!=tuple(b.vertices)for a,b in zip(old.polygons,evaluated.polygons)):raise RuntimeError('Raw/evaluated topology mismatch')
before_cross=robust_crossings(types.SimpleNamespace(data=evaluated,matrix_world=M),True);before_coords=[list(v.co)for v in evaluated.vertices];before_tris=[list(t.vertices)for t in evaluated.loop_triangles];before_normals=[q.vector.copy()for q in evaluated.corner_normals];before_raw_normals=[q.vector.copy()for q in old.corner_normals];before_materials=[p.material_index for p in old.polygons];before_transform=[list(r)for r in ob.matrix_world];mods=[{'name':m.name,'type':m.type,'group':m.node_group.name if m.type=='NODES'else None}for m in ob.modifiers]
def attrs_snapshot(me):
 d={}
 for a in me.attributes:
  if a.name.startswith('.')or a.name=='position':continue
  prop=next((k for k in ['value','vector','color']if len(a.data)and hasattr(a.data[0],k)),None)
  if not prop:continue
  vals=[]
  for x in a.data:
   v=getattr(x,prop);vals.append(tuple(v)if hasattr(v,'__len__')else v)
  d[a.name]={'domain':a.domain,'type':a.data_type,'values':vals}
 return d
before_attributes=attrs_snapshot(old);ev.to_mesh_clear();me=old.copy();eid=next(e.index for e in me.edges if set(e.vertices)=={304,83});print('FLIPEDGE',eid,flush=True)
me.edges[eid].vertices=(1263,82)
for fid,vs in newfaces.items():
 p=me.polygons[fid]
 for li,vi in zip(p.loop_indices,vs):me.loops[li].vertex_index=vi
edges={tuple(sorted(e.vertices)):e.index for e in me.edges}
for fid,vs in newfaces.items():
 for j,li in enumerate(me.polygons[fid].loop_indices):me.loops[li].edge_index=edges[tuple(sorted((vs[j],vs[(j+1)%3])))]
me.update()
norms=[v.copy()for v in before_raw_normals]
for fid in newfaces:
 for li in me.polygons[fid].loop_indices:norms[li]=me.polygons[fid].normal.copy()

if old.has_custom_normals:me.normals_split_custom_set(norms)
ob.data=me;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);after=ev.to_mesh();after.calc_loop_triangles();cross=robust_crossings(types.SimpleNamespace(data=after,matrix_world=M),True)
from collections import Counter
counts=Counter(tuple(sorted((t.vertices[i],t.vertices[(i+1)%3])))for t in after.loop_triangles for i in range(3));protected=[i for i in range(len(after.polygons))if i not in newfaces];deltas=[(after.corner_normals[li].vector-before_normals[li]).length for i in protected for li in after.polygons[i].loop_indices]
checks={'raw_evaluated_topology_correspondence_before':True,'source_has_custom_normals':old.has_custom_normals,'before_crossings':len(before_cross),'after_crossings':len(cross),'non2_edge_incidence':sum(n!=2 for n in counts.values()),'all_vertex_coordinates_exact':before_coords==[list(v.co)for v in after.vertices],'all_protected_evaluated_triangles_exact':all(before_tris[i]==list(after.loop_triangles[i].vertices)for i in protected),'all_material_assignments_exact':before_materials==[p.material_index for p in me.polygons],'all_named_attributes_exact':before_attributes==attrs_snapshot(me),'protected_corner_normal_max_delta':max(deltas,default=0),'transform_exact':before_transform==[list(r)for r in ob.matrix_world],'modifiers':mods,'native_modifier_count':len(ob.modifiers),'changed_faces':list(newfaces),'new_faces':newfaces,'before_pairs':before_cross,'after_pairs':cross}
after_attributes=attrs_snapshot(me);checks['attribute_differences']={k:{'before_domain':v['domain'],'after_domain':after_attributes.get(k,{}).get('domain'),'changed_indices':[i for i,(a,b)in enumerate(zip(v['values'],after_attributes.get(k,{}).get('values',[])))if a!=b][:30]}for k,v in before_attributes.items()if v!=after_attributes.get(k)};checks['new_attributes']=[k for k in after_attributes if k not in before_attributes]
checks['accepted_cpu']=len(before_cross)==1 and not cross and not checks['non2_edge_incidence'] and all(checks[k]for k in ['all_vertex_coordinates_exact','all_protected_evaluated_triangles_exact','all_material_assignments_exact','all_named_attributes_exact','transform_exact']) and checks['protected_corner_normal_max_delta']<1e-5
(O/'audit.json').write_text(json.dumps(checks,indent=2));print({k:v for k,v in checks.items()if k not in ['before_pairs','after_pairs']},flush=True)
if not checks['accepted_cpu']:raise RuntimeError('174 held native gate')
ev.to_mesh_clear();bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'))
