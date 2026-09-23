import bpy,sys,json,types
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_crown_continuation_154 import robust_crossings
O=R/'art/studies/coliseum-160/right-repair/v3';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));s=bpy.context.scene;ob=bpy.data.objects['COL110 U15 fractured upper wall R'];dg=bpy.context.evaluated_depsgraph_get();old=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg);M=ob.matrix_world.copy()
with bpy.data.libraries.load(str(O/'candidate.blend'),link=False)as(src,dst):dst.meshes=['160 right ruled return candidate']
new=dst.meshes[0]
for m in [old,new]:m.calc_loop_triangles()
def key(m,t):return tuple(sorted(tuple(m.vertices[i].co)for i in t.vertices))
a={key(old,t)for t in old.loop_triangles};pairs=robust_crossings(types.SimpleNamespace(data=new,matrix_world=M),True);rows=[]
for p in pairs:
 tags=['preserved'if key(new,new.loop_triangles[i])in a else'reconstructed'for i in p['pair']];points=[Vector(v)for tri in p['triangles_world']for v in tri];uv=[world_to_camera_view(s,s.camera,v)for v in points];rows.append({'pair':p['pair'],'roles':tags,'projected_box':[min(v.x for v in uv)*3840,min(1-v.y for v in uv)*2885,max(v.x for v in uv)*3840,max(1-v.y for v in uv)*2885],'world_triangles':p['triangles_world']})
verts=[M@v.co for v in old.vertices];tree=BVHTree.FromPolygons(verts,[tuple(t.vertices)for t in old.loop_triangles],all_triangles=True);deltas=[tree.find_nearest(M@v.co)[3]for v in new.vertices];from collections import Counter
D={'held':True,'crossings':len(rows),'role_pairs':dict(Counter('/'.join(r['roles'])for r in rows)),'crossing_details':rows,'max_candidate_vertex_distance_to_source_surface_m':max(deltas),'mean_candidate_vertex_distance_to_source_surface_m':sum(deltas)/len(deltas),'note':'Surface-distance figure measures new return construction, not movement of retained source vertices. Exact protected triangle loss is zero. No primary writes or render.'};(O/'shape-audit.json').write_text(json.dumps(D,indent=2));print({k:v for k,v in D.items()if k!='crossing_details'},flush=True)
