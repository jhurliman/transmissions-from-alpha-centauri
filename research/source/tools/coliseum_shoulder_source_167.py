import bpy,bmesh,sys,json,types
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_crown_continuation_154 import robust_crossings
O=R/'art/studies/coliseum-167/geometry';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-163/scene.blend'));dg=bpy.context.evaluated_depsgraph_get();names=['COL127 T2 continuous arcade wall','COL110 U7 sill wall']+[f'COL110 T2 band07 profile{i}'for i in range(4)]+[f'COL111 Tower7 tier2 stepped belt{i}'for i in range(5)]+['COL111 Tower7 tier2 rib shoulder1','COL111 Tower7 tier2 projecting shaft rib1'];rows=[]
for name in names:
 ob=bpy.data.objects.get(name)
 if not ob:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();M=ob.matrix_world;bb=[M@v.co for v in me.vertices];bm=bmesh.new();bm.from_mesh(me);r={'object':name,'faces':len(me.polygons),'bounds':[[min(v[k]for v in bb),max(v[k]for v in bb)]for k in range(3)],'nonmanifold':sum(not e.is_manifold for e in bm.edges),'zero_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'volume_local':bm.calc_volume(),'crossings':len(robust_crossings(types.SimpleNamespace(data=me,matrix_world=M)))};bm.free();ev.to_mesh_clear();rows.append(r);print(r,flush=True)
(O/'source-topology.json').write_text(json.dumps(rows,indent=2))
