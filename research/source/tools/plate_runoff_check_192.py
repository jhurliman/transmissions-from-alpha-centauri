import bpy,json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'art/studies/plate-runoff-192'
def film_hash():
 o=bpy.data.objects['189 Scene-wide fastener rust films'];m=o.data
 return hashlib.sha256(json.dumps(dict(v=[list(v.co)for v in m.vertices],f=[list(p.vertices)for p in m.polygons],c=[list(c.color)for c in m.color_attributes['Oxide'].data],mat=[s.material.name for s in o.material_slots])).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rust-189/scene.blend'));before=film_hash()
bpy.ops.wm.open_mainfile(filepath=str(OUT/'candidate.blend'));after=film_hash();ob=bpy.data.objects['192 Plate bolt rusty-water overlays'];rows=[]
for vl in bpy.context.scene.view_layers:
 for ls in vl.freestyle_settings.linesets:
  assert ls.select_by_collection and ls.collection
  objects=set(ls.collection.all_objects);excluded=ob not in objects if ls.collection_negation=='INCLUSIVE'else ob in objects
  assert excluded
  rows.append(dict(line_set=ls.name,filter=ls.collection.name,mode=ls.collection_negation,new_film_excluded=excluded,filter_count=len(objects),fake_user=ls.collection.use_fake_user))
a=dict(fresh_reopened=True,passed=before==after,original189_film_hash_before=before,original189_film_hash_after=after,filters=rows,render_ink_occlusion='Not validated by collection filters; root must verify native line visibility in actual render')
assert a['passed'];(OUT/'fresh-check.json').write_text(json.dumps(a,indent=2));print(json.dumps(a,indent=2))
