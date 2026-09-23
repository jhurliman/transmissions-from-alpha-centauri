"""Integrate user-selected landmark, alley continuation and exact pixel characters."""
import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/scene-direction-218'
args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
s.render.use_border=False;s.render.use_crop_to_border=False
from pixel_characters_217 import apply as characters
from sun_position_216 import apply as sun
report={'source':str(source.relative_to(R)),'characters':characters(s),'variants':{}}
for label,moved in [('current-sun',False),('right-sun',True)]:
 dest=O/label;dest.mkdir(parents=True,exist_ok=True)
 report['variants'][label]=sun(s,moved)
 s.render.filepath=str(dest/'main-4k.png')
 bpy.ops.wm.save_as_mainfile(filepath=str(dest/'scene.blend'))
(O/'integration-audit.json').write_text(json.dumps(report,indent=2));print('218 BUILD COMPLETE',flush=True)
