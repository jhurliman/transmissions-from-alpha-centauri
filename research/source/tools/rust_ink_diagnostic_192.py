"""Temporary matched native crop experiment: film present vs absent; source scene never saved."""
import bpy,sys,time,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
O=R/'art/studies/plate-runoff-192/ink-diagnostic';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rust-189/scene.blend'))
s=bpy.context.scene
for g in(g149,g156,g161):g(s,embed=False)
box=(300,100,570,800);w,h=3840,2885
s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=box[0]/w;s.render.border_max_x=box[2]/w;s.render.border_min_y=1-box[3]/h;s.render.border_max_y=1-box[1]/h
s.render.use_compositing=False;s.render.use_freestyle=True
film=bpy.data.objects['189 Scene-wide fastener rust films'];rows=[]
for label,hidden in [('film-visible',False),('film-hidden',True)]:
 film.hide_render=hidden;bpy.context.view_layer.update();s.render.filepath=str(O/(label+'.png'));t=time.time();bpy.ops.render.render(write_still=True);rows.append(dict(label=label,seconds=time.time()-t,film_hide_render=hidden));(O/'render-audit.json').write_text(json.dumps(dict(source='art/studies/rust-189/scene.blend',region_native=box,original_resolution=[w,h],only_variable='189 film object hide_render',guards=[149,156,161],source_scene_saved=False,renders=rows),indent=2))
print('DIAGNOSTIC_COMPLETE',flush=True)
