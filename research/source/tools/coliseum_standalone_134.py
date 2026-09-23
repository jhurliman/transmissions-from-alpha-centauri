"""Remove superseded linked ink scenes; preserve all current primary native content."""
import bpy,json,hashlib,array,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-134/standalone';O.mkdir(parents=True,exist_ok=True)
source=(R/'tools/scene_detail_integration_133.py').read_text();helper=source[source.index('def fingerprint(scene):'):source.index("if '--render' not in sys.argv:")];exec(helper)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-details-133/scene.blend'));s=bpy.context.scene;before=fingerprint(s);libs=[x.filepath for x in bpy.data.libraries];removed=[]
assert s.compositing_node_group is None and not s.render.use_compositing
for other in list(bpy.data.scenes):
 if other!=s:removed.append(other.name);bpy.data.scenes.remove(other,do_unlink=True)
bpy.data.orphans_purge(do_local_ids=False,do_linked_ids=True,do_recursive=True)
after=fingerprint(s);assert before==after,'Primary contents changed'
audit={'source':'scene-details-133','removed_superseded_scenes':removed,'prior_libraries':libs,'remaining_libraries':[x.filepath for x in bpy.data.libraries],'primary_fingerprint_unchanged':before==after,'primary_objects':len(before),'purpose':'Standalone final-scene preparation; primary now renders all current ink natively, archived128 secondary scene no longer used.'}
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));(O/'audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit),flush=True)
