"""Install only the validated U4-head two-face diagonal change; no source append/bake."""
import bpy
from types import SimpleNamespace
from coliseum_crown_continuation_154 import robust_crossings

def apply(C):
 ob=C.objects.get('COL110 U4 aperture head')
 if ob is None:raise RuntimeError('174 missing exact target')
 old=ob.data
 if old.has_custom_normals:raise RuntimeError('174 expected automatic-normal source; new source needs review')
 oldfaces={711:(304,82,83),4612:(1263,304,83)};newfaces={711:(1263,82,83),4612:(1263,304,82)}
 dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);src=ev.to_mesh();src.calc_loop_triangles();M=ev.matrix_world.copy()
 for i,v in oldfaces.items():
  if tuple(old.polygons[i].vertices)!=v or tuple(src.polygons[i].vertices)!=v:raise RuntimeError('174 raw/evaluated correspondence failed')
 before_cross=robust_crossings(SimpleNamespace(data=src,matrix_world=M));coords=[tuple(v.co)for v in src.vertices];tris=[tuple(t.vertices)for t in src.loop_triangles];normals=[tuple(n.vector)for n in src.corner_normals];ev.to_mesh_clear()
 if len(before_cross)!=1:raise RuntimeError('174 unexpected baseline crossings')
 me=old.copy();eid=next(e.index for e in me.edges if set(e.vertices)=={304,83});me.edges[eid].vertices=(1263,82)
 for fid,vs in newfaces.items():
  for li,vi in zip(me.polygons[fid].loop_indices,vs):me.loops[li].vertex_index=vi
 edges={tuple(sorted(e.vertices)):e.index for e in me.edges}
 for fid,vs in newfaces.items():
  for j,li in enumerate(me.polygons[fid].loop_indices):me.loops[li].edge_index=edges[tuple(sorted((vs[j],vs[(j+1)%3])))]
 me.update();ob.data=me;bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());result=ev.to_mesh();result.calc_loop_triangles();after_cross=robust_crossings(SimpleNamespace(data=result,matrix_world=M))
 protected=[i for i in range(len(result.polygons))if i not in newfaces];ok=not after_cross and coords==[tuple(v.co)for v in result.vertices]and all(tris[i]==tuple(result.loop_triangles[i].vertices)for i in protected)and all(normals[li]==tuple(result.corner_normals[li].vector)for i in protected for li in result.polygons[i].loop_indices)
 ev.to_mesh_clear()
 if not ok:ob.data=old;raise RuntimeError('174 protected evaluated geometry/normal gate failed')
 return {'targets':[{'object':ob.name,'faces':[711,4612],'removed_diagonal':[304,83],'new_diagonal':[1263,82],'crossings_before':len(before_cross),'crossings_after':len(after_cross),'vertices_exact':True,'protected_triangles_and_corner_normals_exact':True,'modifiers_preserved':True,'material_slots_preserved':True}],'scope':'Hidden rear-cap diagonal only; no crown carving','proof':'art/studies/coliseum-174/native/audit.json'}
