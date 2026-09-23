"""103: final user-directed distant street placement cleanup."""
import bpy,json,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-103';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/city-102/scene.blend'));s=bpy.context.scene
low_ids={o.get('reference_mass') for o in s.objects if 'low single-story block' in o.name and o.get('reference_mass')}
hidden=[];moved=[];delta=Vector((9.5-(-1.6989911794662476),0,0))
for o in s.objects:
 mid=o.get('reference_mass')
 if mid in low_ids:o.hide_render=True;hidden.append(o.name)
 elif mid=='L06':o.location+=delta;moved.append(o.name)
(O/'changes.json').write_text(json.dumps({'removed_single_story_ids':sorted(low_ids),'hidden_parts':hidden,'moved_mass':'L06','old_position':[-1.6989911794662476,156.43258666992188,0],'new_position':[9.5,156.43258666992188,0],'moved_parts':moved,'fixed':['all other geometry and placement','all materials','camera','soil','rocks','sky','landmark'],'reason':'User asks to remove complete single-story row and move the rear brown left tower onto the pale soil to the right of the road.'},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=True;s.render.resolution_percentage=100;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
if os.environ.get('CITY_PREVIEW')=='1':
 s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=540/1440;s.render.border_max_x=960/1440;s.render.border_min_y=1-490/1082;s.render.border_max_y=1-260/1082;s.render.filepath=str(O/'preview-city.png')
bpy.ops.render.render(write_still=True)
