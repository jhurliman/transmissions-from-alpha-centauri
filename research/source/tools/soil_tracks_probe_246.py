import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/soil-tracks-246';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-finish-245/scene.blend'));s=bpy.context.scene
from soil_tracks_246 import apply
orig=bpy.data.objects['Street foundation'].material_slots[0].material
s.render.use_freestyle=False;s.render.use_compositing=False
for vl in s.view_layers:vl.use=vl.name=='ViewLayer'
s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=2700/3840;s.render.border_max_x=3500/3840;s.render.border_min_y=1-1910/2885;s.render.border_max_y=1-1500/2885
s.eevee.taa_render_samples=24;s.eevee.shadow_pool_size='1024'
for name,amount in [('continuous',1.5)]:
 bpy.data.objects['Street foundation'].material_slots[0].material=orig;a=apply(s,amount);s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
print('245 PROBES DONE')
