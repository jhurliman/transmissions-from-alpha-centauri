import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=Path(__file__).parent;d=json.load(open(O/'package-B-map.json'));bpy.ops.wm.open_mainfile(filepath=str(R/d['source']));dg=bpy.context.evaluated_depsgraph_get()
def polygon_normal(points):
 no=Vector()
 for a,b in zip(points,points[1:]+points[:1]):no+=a.cross(b)
 return no.normalized()
for key,g in d['groups'].items():
 tower=g['tower_front_depth_anchor']['object'];base=Vector(g['tower_front_depth_anchor']['original_world']);bn=Vector(g['tower_front_depth_anchor']['normal_original'])
 for r in g['receiver_allowlist']:
  ob=bpy.data.objects[r['object']];me=ob.data;attr=me.attributes['115 Original world position'];selected=[];front=[]
  sample=r['original_visible_sample_bounds'];lo=Vector(sample[0])-Vector((.65,.65,.65));hi=Vector(sample[1])+Vector((.65,.65,.65))
  for p in me.polygons:
   ps=[attr.data[i].vector.copy()for i in p.vertices];no=polygon_normal(ps);mat=me.materials[p.material_index].name if me.materials else '';ok=False
   if ob.name==tower:
    depths=[(x-base).dot(bn)for x in ps];ok=no.dot(bn)>.96 and max(depths)>-.08 and min(depths)<.06
   elif ob.name=='COL127 T2 continuous arcade wall':ok=mat=='116 115 Painted masonry wall' and no.y<-.85 and abs(no.z)<.25
   elif 'sill wall'in ob.name:ok=no.y<-.85 and abs(no.z)<.25
   elif 'stepped belt'in ob.name or 'band'in ob.name:ok=no.y<-.6 and abs(no.z)<.55 and not any(token in mat.lower()for token in ['exposed','core'])
   elif 'projecting shaft rib'in ob.name:ok=no.y<-.75 and abs(no.z)<.2
   if not ok:continue
   front.append(p.index)
   if all(max(v[i]for v in ps)>=lo[i] and min(v[i]for v in ps)<=hi[i]for i in range(3)):selected.append(p.index)
  r['sampled_face_ids']=r.pop('evaluated_face_allowlist');r['exhaustive_front_class_face_ids']=front;r['exhaustive_finite_region_face_ids']=selected;r['finite_region_original_bbox']=[list(lo),list(hi)];r['mask_guidance']='Use exhaustive_front_class_face_ids with continuous finite original-coordinate field for seamless shading. exhaustive_finite_region_face_ids conservatively clips same front class to sampled object envelope +0.65m; never use sampled_face_ids as shader mask.'
  ev=ob.evaluated_get(dg);ee=ev.to_mesh();r['exhaustive_raw_eval_face_indices_match']=all(i<len(ee.polygons)and tuple(me.polygons[i].vertices)==tuple(ee.polygons[i].vertices)for i in front);ev.to_mesh_clear()
  print(key,ob.name,len(r['sampled_face_ids']),len(selected),len(front),flush=True)
 g['exhaustive_mask_rule']='Classify actual faces, not sampled pixels. Full front class + continuous finite original-coordinate material field is recommended; restrict all other objects. Depth gates remain required at tower niches. Finite face bbox is a conservative prefilter, not the final pigment boundary.'
(O/'package-B-map.json').write_text(json.dumps(d,indent=2));print('DONE',flush=True)
