import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/rust-189';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'))
ob=bpy.data.objects.get('189 Scene-wide fastener rust films');assert ob and ob.type=='MESH';attr=ob.data.color_attributes.get('Oxide');assert attr and len(attr.data)==len(ob.data.vertices)
linked=[]
for coll in [bpy.data.objects,bpy.data.materials,bpy.data.meshes,bpy.data.images,bpy.data.collections]:linked.extend(x.name for x in coll if x.library)
audit={'source':'art/studies/rust-189/scene.blend','film_vertices':len(ob.data.vertices),'film_faces':len(ob.data.polygons),'vertex_oxide_attribute':bool(attr),'linked_runtime_ids':linked,'unpacked_used_images':[x.name for x in bpy.data.images if x.source=='FILE' and x.users and not x.packed_file],'native_visibility_guards':[x.name for x in bpy.data.texts if 'visibility guard' in x.name or 'occlusion guard' in x.name]}
filters=[]
for vl in bpy.context.scene.view_layers:
 for ls in vl.freestyle_settings.linesets:
  if not ls.show_render:continue
  included=bool(ls.collection and ob.name in ls.collection.all_objects)
  assert ls.select_by_collection and ((ls.collection_negation=='EXCLUSIVE' and included) or (ls.collection_negation=='INCLUSIVE' and not included)), ls.name
  filters.append({'name':ls.name,'collection':ls.collection.name if ls.collection else None,'mode':ls.collection_negation,'film_member':included})
audit['fresh_film_line_exclusion']=filters
assert not audit['linked_runtime_ids'] and not audit['unpacked_used_images'];(O/'fresh-native-check.json').write_text(json.dumps(audit,indent=2));print(audit)
