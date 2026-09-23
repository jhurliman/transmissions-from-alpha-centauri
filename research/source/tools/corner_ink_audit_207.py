"""CPU preservation check:207 changes native visibility callbacks/text only."""
import bpy,sys,json,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/corner-ink-207';sys.path.insert(0,str(R/'tools'))
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")]);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-completion-205/scene.blend'));s=bpy.context.scene;before=fingerprint(s);m=material_snapshot();settings=[s.render.use_compositing,s.render.use_freestyle,s.render.line_thickness];texts=set(t.name for t in bpy.data.texts)
from architecture_ink_visibility_207 import apply
result=apply(s,embed=True);after=fingerprint(s);m2=material_snapshot();assert before==after;assert m==m2;assert settings==[s.render.use_compositing,s.render.use_freestyle,s.render.line_thickness]
(O/'preservation.json').write_text(json.dumps({'source':'205','recursive_native_objects':len(before),'original_material_graphs':len(m),'geometry_normals_transforms_instances_camera_lights_unchanged':True,'material_graphs_unchanged':True,'render_settings_unchanged':True,'added_texts':sorted(set(t.name for t in bpy.data.texts)-texts),'changed_behavior':'207 post-Freestyle segment visibility callback for proven source/receiver pairs only','pairs':result['pairs'],'user_approved':False},indent=2));print('207 PRESERVATION PASS',len(before),len(m),flush=True)
