import bpy,sys,json,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/middle-rubble-204';sys.path.insert(0,str(R/'tools'))
source=(R/'tools/scene_integration_138.py').read_text();exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")])
s=bpy.context.scene;before=fingerprint(s);old=material_snapshot()
from middle_rubble_palette_204 import apply
a=apply(s);after=fingerprint(s);now=material_snapshot();changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};assert set(before)==set(after);assert all(v==['materials']for v in changes.values());assert len(changes)==a['total_objects'];assert all(now[k]==v for k,v in old.items())
assert not any(k.startswith('091 road ')for k in changes)
(O/'audit.json').write_text(json.dumps(a,indent=2));(O/'preservation.json').write_text(json.dumps({'source':'197','objects_audited':len(before),'material_only_changes':len(changes),'old_material_graphs_unchanged':len(old),'geometry_normals_transforms_camera_lights_unchanged':True,'changed':changes},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));print('204_PRESERVATION_PASS')
