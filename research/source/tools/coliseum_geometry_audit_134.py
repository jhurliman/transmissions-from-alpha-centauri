"""Broad native mesh-health inventory; diagnoses, does not imply all contacts valid."""
import bpy,bmesh,json,time,sys
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-134';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-details-133/scene.blend'));s=bpy.context.scene;C=next(c for c in s.collection.children_recursive if c.name=='110 Coliseum detailed front ruin' and c.library is None)
t=time.time();cache={};rows=[]
for ob in C.all_objects:
 if ob.type!='MESH':continue
 me=ob.data
 if me not in cache:
  bm=bmesh.new();bm.from_mesh(me)
  zero=[f.index for f in bm.faces if f.calc_area()<1e-10];boundary=sum(e.is_boundary for e in bm.edges);wire=sum(e.is_wire for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);noncontig=sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
  same=Counter(tuple(sorted(v.index for v in f.verts)) for f in bm.faces);duplicate=sum(v-1 for v in same.values() if v>1)
  components=0;pending=set(bm.verts)
  while pending:
   components+=1;stack=[pending.pop()]
   while stack:
    v=stack.pop()
    for e in v.link_edges:
     q=e.other_vert(v)
     if q in pending:pending.remove(q);stack.append(q)
  cache[me]={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':boundary,'wire_edges':wire,'nonmanifold_edges':nonmanifold,'noncontiguous_manifold_edges':noncontig,'zero_area_faces':len(zero),'duplicate_vertex_set_faces':duplicate,'signed_volume':bm.calc_volume(signed=True),'connected_components':components};bm.free()
 row={'object':ob.name,'mesh':me.name,'role':ob.get('coliseum_role'),'feature':ob.get('feature'),'bay':ob.get('bay'),'tier':ob.get('tier'),'render_hidden':ob.hide_render,'world_det':ob.matrix_world.to_3x3().determinant(),**cache[me]};rows.append(row)
issues=[r for r in rows if r['nonmanifold_edges'] or r['zero_area_faces'] or r['noncontiguous_manifold_edges'] or r['duplicate_vertex_set_faces'] or r['signed_volume']<-.000001]
report={'source':'scene-details-133','seconds':time.time()-t,'mesh_objects':len(rows),'unique_meshes':len(cache),'issue_objects':len(issues),'issues':issues,'all':rows,'limitations':['Raw native meshes before modifiers; evaluated geometry must be checked on revised specimens.','Open flat detail meshes may be intentional; issue list is diagnostic, not automatic failure.','Does not establish all inter-object contact or absence of floating fragments.','No triangle self-crossing test in this broad inventory; current continuous walls already have dedicated zero-crossing evidence from131.']}
(O/'geometry-health-baseline.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['seconds','mesh_objects','unique_meshes','issue_objects']}),flush=True)
