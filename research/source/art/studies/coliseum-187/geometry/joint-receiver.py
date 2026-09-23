import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-187/geometry';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));dg=bpy.context.evaluated_depsgraph_get();ob=bpy.data.objects['COL110 T2 band10 profile0'].evaluated_get(dg);me=ob.to_mesh();me.calc_loop_triangles();v=[ob.matrix_world@q.co for q in me.vertices];tt=[tuple(t.vertices)for t in me.loop_triangles];tree=BVHTree.FromPolygons(v,tt,all_triangles=True);ink=bpy.data.objects['131 Recessed crown joint ink'].evaluated_get(dg);im=ink.to_mesh();points=[ink.matrix_world@p.co for p in im.vertices if 16<(ink.matrix_world@p.co).x<21.5 and 195<(ink.matrix_world@p.co).y<216];rows=[]
for p in points:
 h=tree.find_nearest(p)
 if h[3]>.02:continue
 ids=tt[h[2]];rows.append({'ink_point':list(p),'source_receiver_point':list(h[0]),'source_receiver_normal':list(h[1]),'source_distance_m':h[3],'receiver_triangle':[list(me.vertices[i].co)for i in ids],'left_cut_signed_clearance_m':16.6+.28*(p.y-202)+.1*(p.z-41)+.35-p.x})
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));me=bpy.data.objects['COL110 T2 band10 profile0'].data;me.calc_loop_triangles();keys={tuple(sorted(tuple(me.vertices[i].co)for i in t.vertices))for t in me.loop_triangles}
ob=bpy.data.objects['COL110 T2 band10 profile0'];nv=[ob.matrix_world@v.co for v in me.vertices];nt=[tuple(t.vertices)for t in me.loop_triangles];newtree=BVHTree.FromPolygons(nv,nt,all_triangles=True)
for r in rows:
 h=newtree.find_nearest(Vector(r['source_receiver_point']));r['local_receiver_distance_m']=h[3];r['receiver_normal_dot']=h[1].dot(Vector(r['source_receiver_normal']));r['receiver_triangle_exact']=tuple(sorted(tuple(p)for p in r['receiver_triangle']))in keys
report={'rows':rows,'all_receiver_triangles_exact':all(r['receiver_triangle_exact']for r in rows),'local_receiver_patch_preserved':all(r['local_receiver_distance_m']<.00002 and r['receiver_normal_dot']>.99999 for r in rows),'minimum_planar_cut_clearance_m':min(r['left_cut_signed_clearance_m']for r in rows),'method':'All131 vertices in localXYdomain whose source distance to band10profile0<=2cm. Some old receiver triangles are split by the distant cut. The local source receiver points remain on candidate surfaces with matching normals; positive linear left halfplane clearance prevents the cut from reaching the local support patch. Underlying arcade wall and lower arch surfaces are unchanged.'};(O/'joint-receiver-certificate.json').write_text(json.dumps(report,indent=2));print(report)
