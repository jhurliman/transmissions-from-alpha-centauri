import bpy,sys,json,hashlib,array,numpy as np,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[4];sys.path[:0]=[str(R/'tools'),str(R/'art/studies/coliseum-174/native')];O=R/'art/studies/coliseum-179/geometry'
from repair_174 import apply
from coliseum_crown_continuation_154 import freeze_render_triangles
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
names=json.load(open(R/'config/coliseum-broad-crown-179.json'))['targets'];bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];apply(C);before=fingerprint(bpy.context.scene);mats=material_snapshot();sources={};dg=bpy.context.evaluated_depsgraph_get()
for n in names:
 ob=C.objects[n];me=freeze_render_triangles(bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg));v=np.array([tuple(q.co)for q in me.vertices]);tri=np.array([tuple(p.vertices)for p in me.polygons]);sources[n]={'v':v,'tri':tri,'M':[list(q)for q in ob.matrix_world]}
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene;after=fingerprint(s);ma=material_snapshot();changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};assert set(before)==set(after);assert set(changes)<=set(names);assert all(v==ma[k]for k,v in mats.items());rows=[]
for n,d in sources.items():
 ob=bpy.data.objects[n];me=ob.data;me.calc_loop_triangles();v=d['v'];tri=d['tri'];coords={tuple(q)for q in v};keys={tuple(sorted(tuple(v[i])for i in t))for t in tri};tree=BVHTree.FromPolygons([Vector(q)for q in v],tri.tolist(),all_triangles=True);a=v[tri];samples=[(q.co.copy(),'new_vertex')for q in me.vertices if tuple(q.co)not in coords]+[(sum((me.vertices[i].co for i in t.vertices),Vector())/3,'changed_triangle_center')for t in me.loop_triangles if tuple(sorted(tuple(me.vertices[i].co)for i in t.vertices))not in keys];checks=[];outside=[]
 for p,kind in samples:
  hit=tree.find_nearest(p)
  if hit[3]<=1e-4:continue
  abc=a-np.array(tuple(p));ll=np.linalg.norm(abc,axis=2);num=np.einsum('ij,ij->i',abc[:,0],np.cross(abc[:,1],abc[:,2]));den=ll.prod(axis=1)+np.einsum('ij,ij->i',abc[:,0],abc[:,1])*ll[:,2]+np.einsum('ij,ij->i',abc[:,1],abc[:,2])*ll[:,0]+np.einsum('ij,ij->i',abc[:,2],abc[:,0])*ll[:,1];w=float(np.sum(2*np.arctan2(num,den))/(4*np.pi));rr={'point_local':list(p),'kind':kind,'winding':w,'inside':abs(w)>.5,'nearest_world_m':(ob.matrix_world@p-ob.matrix_world@hit[0]).length};checks.append(rr)
  if not rr['inside']:outside.append(rr)
 rows.append({'object':n,'changed_samples':len(samples),'off_original_surface_checks':len(checks),'outside':outside,'checks':checks})
(O/'full-containment-and-preservation.json').write_text(json.dumps({'source':'173+174','unchanged_other_entries':len(before)-len(changes),'changed':changes,'existing_material_graphs_exact':True,'object_inventory_exact':True,'containment':'Float64 winding of every changed vertex/triangle-center farther than1e-4local from source; exact inherited triangles/vertices certify by correspondence. Finite sampling does not mathematically certify every continuous face point.','rows':rows,'passed':not any(r['outside']for r in rows)},indent=2));print('CERT',[(r['object'],r['off_original_surface_checks'],len(r['outside']))for r in rows],flush=True)
