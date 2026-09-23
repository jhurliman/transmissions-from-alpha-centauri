import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/reviews/xenon-077';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-077/scene.blend'));s=bpy.context.scene
from ground_lips_077 import apply as lips
from scrap_palette_077 import apply as scrap
from far_refine_077 import apply as far
from sky_refine_077 import apply as sky
from highlight_refine_077 import apply as highlights
from end_rubble_077 import apply as end
results={}
for name,fn in [('lips',lips),('scrap',scrap),('far',far),('sky',sky),('highlights',highlights),('end_rubble',end)]:results[name]=fn(s)
(O/'integration.json').write_text(json.dumps(results,indent=2,default=str))
s.render.filepath=str(O/'render.png');s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.use_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
