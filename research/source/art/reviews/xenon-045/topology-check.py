import bpy,bmesh,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-045');results=[]
for label in ['clean','low','medium','high']:
 O=R if label=='medium' else R/label;bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));host=bpy.data.objects['Architecture | buttress_45'];beam=next(o for o in host.instance_collection.objects if o.name.startswith('Solid concrete'))
 dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(beam.evaluated_get(dg));bm=bmesh.new();bm.from_mesh(mesh)
 adj={v.index:set() for v in bm.verts}
 for e in bm.edges:
  a,b=e.verts;adj[a.index].add(b.index);adj[b.index].add(a.index)
 unseen=set(adj);cc=0
 while unseen:
  todo=[unseen.pop()];cc+=1
  while todo:
   for j in adj[todo.pop()]:
    if j in unseen:unseen.remove(j);todo.append(j)
 mesh.calc_loop_triangles();info={'variant':label,'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'connected_components':cc,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume()};results.append(info);bm.free()
 col=bpy.data.collections.new('BAKED | '+label);obj=bpy.data.objects.new('Baked concrete beam | '+label,mesh);col.objects.link(obj);bpy.data.libraries.write(str(O/'baked-beam.blend'),{col},fake_user=True)
(R/'topology-audit.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
