"""Matched117 sample: ink alone versus ink plus geometry-responsive shade."""
import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_depth_118 import refine
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
O=R/'art/studies/coliseum-118/depth-trials';O.mkdir(parents=True,exist_ok=True)
for name,shade in [('ink',False),('shade-ink',True)]:
    bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-117/sample-weathered.blend'))
    s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
    changes=refine(C.objects) if shade else []
    ink=add_intersection_ink(C,'118 Sample visible contact ink',radius=.025)
    start=time.time();count=bake_intersection_ink(ink)
    s.render.use_freestyle=True;s.render.line_thickness=.65
    s.render.filepath=str(O/(name+'.png'))
    bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
    bpy.ops.render.render(write_still=True)
    (O/(name+'.json')).write_text(json.dumps({'source':'117/sample-weathered.blend','shade':changes,'contact_strokes':count,'seconds':time.time()-start},indent=2))
