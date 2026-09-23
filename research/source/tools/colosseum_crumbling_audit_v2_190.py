import bpy,sys,json,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-190';sys.path.insert(0,str(R/'tools'))
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
build=json.loads((O/'build-audit-v2.json').read_text());allowed={r['object']for r in build['changed_walls']};changedfaceids={r['object']:{f['source_face']for f in r['affected_source_faces']}for r in build['changed_walls']}
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-188/scene.blend'));s=bpy.context.scene;before=fingerprint(s);materials=material_snapshot();old={}
for name in allowed:
 ob=bpy.data.objects[name];me=ob.data
 old[name]={'verts':[tuple(v.co)for v in me.vertices],'faces':[list(f.vertices)for f in me.polygons],'materials':[ob.material_slots[f.material_index].material.name if ob.material_slots[f.material_index].material else None for f in me.polygons],'corner_normals':[[tuple(me.corner_normals[i].vector)for i in f.loop_indices]for f in me.polygons]}
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate-v2.blend'));s=bpy.context.scene;after=fingerprint(s);after_mats=material_snapshot();changes={k:[f for f,v in before[k].items()if v!=after[k][f]]for k in before if before[k]!=after.get(k)}
assert set(changes)<=allowed,changes
assert all(v==after_mats.get(k)for k,v in materials.items()),'Old graph changed'
rows=[];total_materials=0;total_faces=0
for name in allowed:
 ob=bpy.data.objects[name];me=ob.data;previous=old[name];ids=me.attributes['190 Source face identity'];wrong=[];untouchedwrong=[];normaldelta=0.;children={}
 for f in me.polygons:
  original=ids.data[f.index].value;children.setdefault(original,[]).append(f.index);mat=ob.material_slots[f.material_index].material;matname=mat.name if mat else None
  if not(matname or '').startswith('190 '):
   total_materials+=1
   if matname!=previous['materials'][original]:wrong.append({'face':f.index,'source':original,'before':previous['materials'][original],'after':matname})
  if original not in changedfaceids[name]:
   total_faces+=1
   if list(f.vertices)!=previous['faces'][original]:untouchedwrong.append(original)
   for li,n in zip(f.loop_indices,previous['corner_normals'][original]):normaldelta=max(normaldelta,(me.corner_normals[li].vector-Vector(n)).length)
 vertex_errors=[i for i,p in enumerate(previous['verts'])if tuple(me.vertices[i].co)!=p]
 assert not wrong,wrong[:5];assert not untouchedwrong,untouchedwrong[:5];assert not vertex_errors,vertex_errors[:5]
 rows.append({'wall':name,'original_vertices_exact':len(previous['verts']),'untouched_faces_exact':sum(i not in changedfaceids[name]for i in children),'material_provenance_mismatches':wrong,'non_cut_face_material_bindings_exact':True,'maximum_untouched_corner_normal_storage_delta':normaldelta,'cut_face_count':sum((ob.material_slots[f.material_index].material.name if ob.material_slots[f.material_index].material else '').startswith('190 ')for f in me.polygons),'source_face_descendants':{str(i):js for i,js in children.items()if i in [95,126]}})
# The 65 failed v1 nearest-surface samples refer to horizontal cap faces. Compare those exact source face identities now.
held=json.loads((O/'held-v1/native-audit.json').read_text());cases=[]
for wr in held['wall_cut_faces']:
 name=wr['wall']
 for case in wr.get('nearest_face_material_mismatches',[]):
  fi=case['face']
  if name not in allowed:cases.append({'wall':name,'source_face':fi,'result':'Entire object unchanged in v2'});continue
  ob=bpy.data.objects[name];me=ob.data;faces=[f for f in me.polygons if me.attributes['190 Source face identity'].data[f.index].value==fi];exact=len(faces)==1 and list(faces[0].vertices)==old[name]['faces'][fi] and ob.material_slots[faces[0].material_index].material.name==old[name]['materials'][fi]
  cases.append({'wall':name,'source_face':fi,'exact_original_face_and_material_retained':exact})
assert all(c.get('exact_original_face_and_material_retained',True)for c in cases),cases
out={'version':2,'source':'188','changes':changes,'non_target_entries_preserved':len(before)-len(changes),'all_existing_material_graphs_unchanged':True,'source_identity_material_checks':total_materials,'untouched_face_geometry_checks':total_faces,'walls':rows,'v1_65_case_resolution':cases,'diagnosis':'V1 whole-wall Boolean regularized nearly coplanar wall/pier horizontal cap interfaces despite those faces lying outside weathering. V2 does not Boolean the wall: exact source face identity shows all 65 previously flagged samples lie on faces retained with original geometry and material. No nearest-surface approximation is used to establish this.','limits':'Native study; global inherited topology not re-certified. Custom normal storage quantization reported per wall. Visual proof pending.'}
(O/'native-audit-v2.json').write_text(json.dumps(out,indent=2));print('AUDIT V2 PASS',total_materials,total_faces,'resolvedcases',len(cases))
