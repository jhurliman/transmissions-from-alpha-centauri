import bpy,sys,json,hashlib,math,array
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-190';sys.path.insert(0,str(R/'tools'))
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-188/scene.blend'));s=bpy.context.scene;before=fingerprint(s);materials=material_snapshot()
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene;after=fingerprint(s);after_mats=material_snapshot();build=json.loads((O/'build-audit.json').read_text());allowed={r['object']for r in build['changed_walls']}
changes={k:[f for f,v in before[k].items()if v!=after[k][f]]for k in before if before[k]!=after.get(k)}
assert set(changes)<=allowed,changes
changedgraphs=[k for k,v in materials.items()if after_mats.get(k)!=v];assert not changedgraphs,changedgraphs
C=bpy.data.collections['110 Coliseum detailed front ruin'];dg=bpy.context.evaluated_depsgraph_get();vs=[];tris=[];rows=[];bounds=[]
for ob in C.all_objects:
 if ob.type!='MESH' or ob.name.startswith('190 ') or ob.hide_render:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();base=len(vs);vs.extend(ob.matrix_world@v.co for v in me.vertices);tris.extend(tuple(base+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,tris,all_triangles=True);camera=s.camera.matrix_world.translation
for p in build['patches']:
 point=Vector(p['center']);direction=(point-camera).normalized();hit=tree.ray_cast(camera,direction,(point-camera).length+1)
 visible=hit[0] is not None and (hit[0]-point).length<.5
 p['unoccluded_by_colosseum']=visible
 if p['role']=='primary':
  tier=p['tier'];arches=[o for o in C.all_objects if o.type=='MESH' and o.get('tier')==tier and 'archivolt'in o.name]
  if arches:
   near=min(arches,key=lambda o:((o.matrix_world@(sum((Vector(b)for b in o.bound_box),Vector())/8))-point).length)
   p['nearest_arch_bay']=int(near.get('bay',-1))
for name in allowed:
 ob=bpy.data.objects[name];counts={}
 for f in ob.data.polygons:
  mat=ob.data.materials[f.material_index]if f.material_index<len(ob.data.materials)else None
  if mat and mat.name.startswith('190 '):counts[mat.name]=counts.get(mat.name,0)+1
 source=bpy.data.meshes.get(ob['190 original mesh']);current=ob.data
 localtree=BVHTree.FromPolygons([v.co for v in current.vertices],[tuple(f.vertices)for f in current.polygons],all_triangles=False)
 sourcetree=BVHTree.FromPolygons([v.co for v in source.vertices],[tuple(f.vertices)for f in source.polygons],all_triangles=False)
 checked=0;wrong=[];ambiguous=[]
 source.calc_loop_triangles()
 for triangle in source.loop_triangles:
  f=source.polygons[triangle.polygon_index]
  center=sum((source.vertices[i].co for i in triangle.vertices),Vector())/3
  hit=localtree.find_nearest(center)
  if hit[0] is None or hit[3]>2e-5 or hit[1].dot(f.normal)<.99:continue
  beforemat=source.materials[f.material_index]if f.material_index<len(source.materials)else None
  afterface=current.polygons[hit[2]];aftermat=current.materials[afterface.material_index]if afterface.material_index<len(current.materials)else None
  checked+=1
  if beforemat!=aftermat:
   names={source.materials[source.polygons[h[2]].material_index].name for h in sourcetree.find_nearest_range(center,2e-5)if h[1].dot(f.normal)>.99 and source.materials[source.polygons[h[2]].material_index]}
   entry={'face':f.index,'before':beforemat.name if beforemat else None,'after':aftermat.name if aftermat else None}
   (ambiguous if aftermat and aftermat.name in names else wrong).append(entry)
 rows.append({'wall':name,'new_cut_material_faces':counts,'unchanged_face_material_samples':checked,'nearest_face_material_mismatches':wrong,'overlapping_source_material_ambiguities':ambiguous,'face_provenance_binding_exact':all(f.material_index==current.attributes['190 Material provenance'].data[f.index].value-1 for f in current.polygons),'all_slots_data_linked':all(sl.link=='DATA'for sl in ob.material_slots),'attributes':[a.name for a in ob.data.attributes]})
summary={str(t):{'total_primary':sum(p['role']=='primary'and p['tier']==t for p in build['patches']),'colosseum_unoccluded_primary':sum(p['role']=='primary'and p['tier']==t and p['unoccluded_by_colosseum']for p in build['patches']),'bay_ids':sorted({p.get('nearest_arch_bay',p['bay'])for p in build['patches']if p['role']=='primary'and p['tier']==t})}for t in range(4)}
out={'source':'188','non_target_entries_preserved':len(before)-len(changes),'changes':changes,'new_entries':sorted(set(after)-set(before)),'existing_material_graph_changes':changedgraphs,'wall_cut_faces':rows,'distribution':summary,'patches':build['patches'],'visibility_note':'Ray casting against colosseum meshes only; foreground alley/city occlusion excluded from this count. Full-camera crop remains the visual authority.','old_architecture_preserved':True,'limits':'Scoped shallow subtraction; not a globally manifold topology certificate. Existing wall topology inherited.'}
(O/'native-audit.json').write_text(json.dumps(out,indent=2));print('AUDIT190',summary,'PRESERVED',out['non_target_entries_preserved'])
