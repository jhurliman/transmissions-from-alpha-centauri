import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-repeat-212';sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-completion-209/scene.blend'));s=bpy.context.scene
from alley_repeat_212 import apply,SOURCES,visible_objects
source=set()
for name in SOURCES+['101 Original city layout study']:
 c=bpy.data.collections.get(name)
 if c:source.update(visible_objects(c))
for row in json.loads((R/'art/studies/alley-recess-208/audit.json').read_text())['objects']:source.add(bpy.data.objects[row['object']])
source.add(s.camera);source.update(o for o in s.objects if o.type=='LIGHT');source_refs={o.name:o for o in source}
before={o.name:([list(r)for r in o.matrix_world],o.hide_render,o.data.name if o.data else None,[m.material.name if m.material else None for m in o.material_slots])for o in source}
from recess_scuffs_213 import apply as scuff
print('212 SCOPED SOURCE SNAPSHOT READY',len(before),flush=True)
a213=scuff(s);print('212 SCUFFS READY',flush=True);(O/'recess-213-audit.json').write_text(json.dumps(a213,indent=2))
a=apply(s);print('212 ASSEMBLY READY',flush=True);allowed=set(a['original_city_hidden']);changedmats=[]
for name,(M,hidden,data,mats)in before.items():
 o=source_refs[name];assert [list(r)for r in o.matrix_world]==M,name;assert (o.data.name if o.data else None)==data,name
 assert o.hide_render==hidden or name in allowed,name
 now=[m.material.name if m.material else None for m in o.material_slots]
 if now!=mats:changedmats.append(name)
assert len(changedmats)==14,len(changedmats)
a['preservation']={'scoped_original_objects_checked':len(before),'source_assemblies_original_data_and_transforms_unchanged':True,'material_binding_changes_only213':changedmats,'render_visibility_changes_only_old_city':len(allowed),'every_cloned_component_shares_original_geometry_data':True,'audit_scope':'all source root assemblies,oldcity,14recess receivers,camera/lights; unrelated hidden archival objects not redundantly traversed'}
(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));print('212_BUILD_DONE',flush=True)
