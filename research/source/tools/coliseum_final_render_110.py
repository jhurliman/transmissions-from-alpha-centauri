import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_materials_110 import apply_materials
O=R/'art/studies/coliseum-110';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
from coliseum_breakage_110 import add_breakage
C=bpy.data.collections['110 Coliseum detailed front ruin']
if not any(ob.get('localized_breakage') for ob in C.objects):(O/'breakage-audit.json').write_text(json.dumps(add_breakage(C),indent=2))
apply_materials(bpy.data.collections['110 Coliseum detailed front ruin'])
from coliseum_ink_occlusion_110 import clip_contacts
(O/'ink-occlusion.json').write_text(json.dumps(clip_contacts(s),indent=2))
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.line_thickness=3840/1440;s.render.filepath=str(O/'main-4k.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene-4k.blend'));t=time.time();bpy.ops.render.render(write_still=True);(O/'render-performance.json').write_text(json.dumps({'resolution':[3840,2885],'render_seconds':time.time()-t,'threads':s.render.threads,'linked_geometry':True},indent=2))
