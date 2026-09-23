import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-129'
bpy.ops.wm.open_mainfile(filepath=str(O/'pre-joint-correction/scene.blend'));saved={}
def coords(ob):return [(tuple(v.co))for v in ob.data.vertices]
for ob in bpy.data.collections['110 Coliseum detailed front ruin'].objects:
 if ob.type=='MESH' and 'niche' in ob.name.lower() and 'archivolt' in ob.name:
  saved[ob.name]={'coords':coords(ob),'slots':[(s.link,s.material.name if s.material else None)for s in ob.material_slots]}
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));restored=[]
missing=sorted({m for d in saved.values()for _,m in d['slots']if m and bpy.data.materials.get(m)is None})
if missing:
 with bpy.data.libraries.load(str(O/'pre-joint-correction/scene.blend'),link=False)as(src,dst):dst.materials=missing

for name,d in saved.items():
 ob=bpy.data.objects[name];assert coords(ob)==d['coords'];a=ob.data.attributes.get('129 Radial masonry joint end')
 if a:
  ob.data.attributes.remove(a)
  for s,(link,mname)in zip(ob.material_slots,d['slots']):s.link=link;s.material=bpy.data.materials[mname]if mname else None
  restored.append(name)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'kit.blend'),{bpy.data.collections['110 Coliseum detailed front ruin']},fake_user=True)
(O/'joint-scope-cleanup.json').write_text(json.dumps({'niche_materials_restored_and_added_attributes_removed':restored,'geometry_changed':False,'scope':'Only arcade stone end faces receive joint-shading correction; unrelated niche masonry retains128 material.'},indent=2));print('Restored:',len(restored))
