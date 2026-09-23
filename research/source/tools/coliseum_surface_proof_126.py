import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_surface_126 import apply
args=sys.argv[sys.argv.index('--')+1:];label=args[0];O=R/'art/studies/coliseum-126/surface';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-125/scene.blend'))
if label!='before':(O/(label+'-audit.json')).write_text(json.dumps(apply(bpy.data.collections['110 Coliseum detailed front ruin'],float(args[1])),indent=2))
s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.37;s.render.border_max_x=.66;s.render.border_min_y=.60;s.render.border_max_y=.89;s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True)
