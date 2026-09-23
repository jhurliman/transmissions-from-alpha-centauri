import bpy,sys,json,time,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-111'
from coliseum_structure_111 import upgrade_structure
from coliseum_materials_111 import apply_materials
from coliseum_ink_occlusion_110 import clip_contacts
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-110/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
t=time.time();audit=upgrade_structure(C);audit['generation_seconds']=time.time()-t;(O/'structure-audit.json').write_text(json.dumps(audit,indent=2));apply_materials(C)
(O/'ink-occlusion.json').write_text(json.dumps(clip_contacts(s),indent=2))
for vl in s.view_layers:
 for ls in vl.freestyle_settings.linesets:
  if ls.name=='110 Landmark contours':ls.linestyle.thickness=2.5
  elif ls.name=='110 Landmark fine creases':ls.linestyle.thickness=1.25
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.line_thickness=1;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));t=time.time()
if os.environ.get("COL111_BUILD_ONLY")!="1":bpy.ops.render.render(write_still=True)
(O/'performance.json').write_text(json.dumps({'render_seconds':time.time()-t},indent=2))
