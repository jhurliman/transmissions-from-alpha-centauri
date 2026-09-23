"""Promote the reviewed native157/158 pairing, with optional160 return repair."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
O=R/'art/studies/coliseum-159';O.mkdir(parents=True,exist_ok=True)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
from coliseum_ink_regression_149 import apply as visibility
from coliseum_foreground_visibility_156 import apply as foreground_visibility
from coliseum_foreground_visibility_161 import apply as fascia_visibility
if 'render' in sys.argv:
    bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
    visibility(s,embed=False);foreground_visibility(s,embed=False);fascia_visibility(s,embed=False)
    s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True)
    (O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]}))
    import parameter_editor
    (O/'native-ink-visibility.json').write_text(json.dumps([f._guard_149_audit for f in parameter_editor.callbacks_modifiers_post if getattr(f,'_guard_149',False)],indent=2))
    (O/'foreground-ink-visibility.json').write_text(json.dumps([f._guard156_audit for f in parameter_editor.callbacks_modifiers_post if getattr(f,'_guard156',False)],indent=2))
    (O/'fascia-ink-visibility161.json').write_text(json.dumps([f._guard161_audit for f in parameter_editor.callbacks_modifiers_post if getattr(f,'_guard161',False)],indent=2))
    raise SystemExit
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'))
before=fingerprint(bpy.context.scene);mats=material_snapshot()
bpy.ops.wm.open_mainfile(filepath=str(O/'pairing/scene.blend'))
s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
geo_audit=json.loads((R/'art/studies/coliseum-157/geometry/audit.json').read_text())
age_audit=json.loads((O/'pairing/audit.json').read_text())
geo={r['object']for r in geo_audit['targets']};mat={r['object']for r in age_audit['assignments']}
result={'source':'156 via reviewed157 V3 native geometry and158 paired material proof','geometry':geo_audit,'age':age_audit}
if '--include-return' in sys.argv:
    from coliseum_return_apply_160 import apply as repair_return
    repair=repair_return(C)
    result['return_repair']=repair;geo.add('COL110 U10 fractured upper wall L')
result['native_visibility']=visibility(s,embed=True)
result['foreground_visibility']=foreground_visibility(s,embed=True)
result['fascia_visibility161']=fascia_visibility(s,embed=True)
after=fingerprint(s);ma=material_snapshot()
changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]}
assert set(before)==set(after)
for name,fields in changes.items():
    for field in fields:assert (field in ['geometry','normals']and name in geo)or(field=='materials'and name in geo|mat),(name,field)
missing_materials={name:sorted(k for k,v in before.items()if name in v['materials'])for name in set(mats)-set(ma)}
# Saving the paired proof discards unused superseded material datablocks.
# Their former users must be confined to the authorized replacement scope.
assert all(set(owners)<=geo|mat for owners in missing_materials.values()),missing_materials
assert all(v==ma[k] for k,v in mats.items()if k in ma)
(O/'preservation.json').write_text(json.dumps({'changes':changes,'retained_existing_material_graphs_unchanged':True,'unused_superseded_materials_discarded_on_reload':missing_materials,'unrelated_geometry_normals_camera_lights_transforms_unchanged':True,'geometry_targets':sorted(geo),'compared_objects':len(before)},indent=2))
(O/'generation.json').write_text(json.dumps(result,indent=2))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
s.render.line_thickness=3840/1440;s.render.use_freestyle=True;s.render.use_compositing=False
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath='//main-4k.png'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'kit.blend'),{C},fake_user=True)
