"""Isolated156 control: restore five source meshes, retain new materials/crown."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_degenerate_cleanup_156 import TARGETS
from coliseum_ink_regression_149 import apply as guard
O=R/'art/studies/coliseum-156/regression';O.mkdir(exist_ok=True,parents=True)
if 'render'in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'without-cleanup.blend'));s=bpy.context.scene;guard(s,embed=False);s.render.filepath=str(O/'without-cleanup.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'timing.json').write_text(json.dumps({'seconds':time.time()-t}));raise SystemExit
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));s=bpy.context.scene;targets={name:bpy.data.objects[name]for name in TARGETS};slots={name:[(sl.link,sl.material)for sl in ob.material_slots]for name,ob in targets.items()}
with bpy.data.libraries.load(str(R/'art/studies/coliseum-152/scene.blend'),link=False)as(src,dst):dst.objects=list(TARGETS)
rows=[]
for name,loaded in zip(TARGETS,dst.objects):
 ob=targets[name];old=ob.data;data=loaded.data.copy();data.name='156 Control original152 '+name;ob.data=data
 for sl,(kind,mat)in zip(ob.material_slots,slots[name]):sl.link=kind;sl.material=mat
 rows.append({'object':name,'source_faces':len(data.polygons),'cleanup_faces':len(old.polygons),'materials_preserved':[(sl.link,sl.material.name if sl.material else None)for sl in ob.material_slots]});bpy.data.objects.remove(loaded,do_unlink=True)
guard(s,embed=True);s.render.threads_mode='FIXED';s.render.threads=4
settings=[]
for vl in s.view_layers:
 for ls in vl.freestyle_settings.linesets:
  st=ls.linestyle;settings.append({'layer':vl.name,'lineset':ls.name,'enabled':ls.show_render,'style':st.name,'chaining':st.chaining,'use_chaining':st.use_chaining,'geometry_modifiers':[(m.name,m.type)for m in st.geometry_modifiers],'thickness':st.thickness})
(O/'without-cleanup-audit.json').write_text(json.dumps({'restored':rows,'other_changes':'None to153/154/155, geometry transforms or line styles','freestyle':settings},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'without-cleanup.blend'));print('READY',flush=True)
