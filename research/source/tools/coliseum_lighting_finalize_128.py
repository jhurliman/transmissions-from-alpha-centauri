"""Apply only the selected landmark illumination study to127; preserve native editability."""
import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_lighting_128 import apply
label=sys.argv[-1];O=R/'art/studies/coliseum-128';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-127/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];t=time.time();audit=apply(C,label);audit['generation_seconds']=time.time()-t
s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.line_thickness=1;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'kit.blend'),{C},fake_user=True)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.line_thickness=3840/1440;s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);audit['render_seconds']=time.time()-t;audit['source_scene']='127';audit['integration_scope']='Native landmark lighting and masonry palette only. Other128 geometry studies remain separate.';(O/'generation.json').write_text(json.dumps(audit,indent=2))
