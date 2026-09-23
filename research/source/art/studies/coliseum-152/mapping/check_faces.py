import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=Path(__file__).parent;d=json.load(open(O/'package-B-map.json'));bpy.ops.wm.open_mainfile(filepath=str(R/d['source']));dg=bpy.context.evaluated_depsgraph_get();out={}
for g in d['groups'].values():
 for r in g['receiver_allowlist']:
  ob=bpy.data.objects[r['object']];ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=r['evaluated_face_allowlist'];match=all(i<len(ob.data.polygons)and tuple(me.polygons[i].vertices)==tuple(ob.data.polygons[i].vertices)for i in ids)
  r['face_indices_match_raw_mesh']=match;r['raw_face_count']=len(ob.data.polygons);r['evaluated_face_count']=len(me.polygons);r['point_original_attribute_present']=bool(ob.data.attributes.get('115 Original world position'));out[ob.name]={'raw':len(ob.data.polygons),'evaluated':len(me.polygons),'selected_face_vertex_sequences_identical':match,'modifiers':[(m.name,m.type)for m in ob.modifiers]};ev.to_mesh_clear()
(O/'package-B-map.json').write_text(json.dumps(d,indent=2));(O/'face-index-validation.json').write_text(json.dumps(out,indent=2));print('match',all(q['selected_face_vertex_sequences_identical']for q in out.values()),len(out))
