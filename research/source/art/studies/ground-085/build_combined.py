import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));import ground_surface_085 as gs,ground_breaks_085 as gb
O=R/'art/studies/ground-085';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/cloud-084/scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;stats=gs.apply(s);stats.update(gb.apply(s));(O/'audit.json').write_text(json.dumps(stats,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
