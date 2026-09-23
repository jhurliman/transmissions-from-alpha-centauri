import bpy,sys,json,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-transition-200';source=(R/'tools/scene_integration_138.py').read_text();exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")])
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/beam-rust-197/scene.blend'));before=fingerprint(bpy.context.scene);mats=material_snapshot();allowed={o.name for o in bpy.data.collections['133 Ruined transition structures'].all_objects}
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));after=fingerprint(bpy.context.scene);ma=material_snapshot();changes={k:[f for f in v if v[f]!=after.get(k,{}).get(f)]for k,v in before.items()if v!=after.get(k)};material_changes=[k for k,v in mats.items()if v!=ma.get(k)]
assert set(before)==set(after);assert all(n in allowed and set(fields)<={'geometry','normals','materials'}for n,fields in changes.items()),changes;assert not material_changes,material_changes
report=dict(source='beam-rust-197',recursive_object_entries=len(before),changed_objects=changes,old_material_graph_changes=material_changes,only133bridge_changed=True,all_transforms_camera_lights_other_geometry_unchanged=True)
(O/'preservation.json').write_text(json.dumps(report,indent=2));print('200_PRESERVATION_PASS',len(changes),flush=True)
