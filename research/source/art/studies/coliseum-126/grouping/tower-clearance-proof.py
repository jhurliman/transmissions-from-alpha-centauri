import bpy,math,json,sys,os
from mathutils.bvhtree import BVHTree
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'tools'));from coliseum_arch_depth_120 import _authored
bpy.ops.wm.open_mainfile(filepath=str(R/os.environ.get('GROUP_RAY_SOURCE','art/studies/coliseum-126/grouping/scene.blend')));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();origin=s.camera.matrix_world.translation;records=[]
vs=[];fs=[];owners=[]
for ob in C.objects:
 if ob.type!='MESH'or 'tower'not in ob.name.lower():continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();off=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices);fs.extend(tuple(off+i for i in p.vertices)for p in me.polygons);owners.extend([ob.name]*len(me.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(vs,fs)

for ob in C.objects:
 if ob.type!='MESH'or 'archivolt1 stone'not in ob.name or ob.get('tier')not in [0,1,2] or ob.get('bay')not in range(4,13):continue
 p=_authored(ob);rr=[math.hypot(v.x,v.y)/(1-.055*v.z/78)for v in p];hi=max(rr);ids=[i for i,r in enumerate(rr)if r>hi-.03];ev=ob.evaluated_get(dg);me=ev.to_mesh()
 for i in ids[::2]:
  target=ev.matrix_world@me.vertices[i].co;d=target-origin;hit=bvh.ray_cast(origin,d.normalized(),d.length+.001)
  records.append({'object':ob.name,'bay':ob.get('bay'),'vertex':i,'tier':ob.get('tier'),'hit':owners[hit[2]] if hit[0] is not None else None,'tower_occludes':bool(hit[0] is not None and (target-hit[0]).length>.05),'distance_to_target':(target-hit[0]).length if hit[0] is not None else None})
 ev.to_mesh_clear()
O=R/'art/studies/coliseum-126/grouping';(O/os.environ.get('GROUP_RAY_OUTPUT','tower-only-rays.json')).write_text(json.dumps(records,indent=2));print('RAYS',len(records),'TOWER',sum(r['tower_occludes']for r in records));print([(j,sum(r['tower_occludes']for r in records if r['bay']==j))for j in range(4,13)])
