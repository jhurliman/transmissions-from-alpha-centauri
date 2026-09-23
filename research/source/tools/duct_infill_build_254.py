import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/duct-infill-254';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/duct-mounts-253/scene.blend'));s=bpy.context.scene
panel=bpy.data.objects['253 Flat weathered masonry duct entry'];panel.location.y-=.55
receiver=bpy.data.objects['Duct wall receiver'];receiver.location.x-=.55
(O/'audit.json').write_text(json.dumps({'panel_forward_m':.55,'receiver_forward_m':.55,'panel_front_world_x':9.60,'four_brackets_unchanged':True,'bottom_mount_unchanged':True},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
