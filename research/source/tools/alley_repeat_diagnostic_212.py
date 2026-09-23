import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-repeat-212';sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene
rows=[]
for vl in s.view_layers:
 for ls in vl.freestyle_settings.linesets:
  rows.append({'layer':vl.name,'layer_ink':vl.use_freestyle,'name':ls.name,'show':ls.show_render,'visibility':ls.visibility,'select_by_visibility':ls.select_by_visibility,'qi_start':ls.qi_start,'qi_end':ls.qi_end,'collection':ls.collection.name if ls.collection else None,'negation':ls.collection_negation,'objects':len(ls.collection.all_objects)if ls.collection else 0})
(O/'ink-linesets-diagnostic.json').write_text(json.dumps(rows,indent=2));print('212 DIAGNOSTIC STYLES',json.dumps(rows),flush=True)
from alley_repeat_212 import repeat_guard_pairs
repeat_guard_pairs(s)
from coliseum_ink_regression_149 import apply as a149
from coliseum_foreground_visibility_156 import apply as a156
from coliseum_foreground_visibility_161 import apply as a161
from architecture_ink_visibility_192 import apply as a192
from architecture_ink_visibility_205 import apply as a205
for fn in(a149,a156,a161,a192,a205):fn(s,embed=False)
def pre(scene,*args):
 from architecture_ink_visibility_207 import install
 install(scene)
 import architecture_ink_capture_192 as cap
 cap.REGION=(1320,480,2420,1100);cap.install(scene,O/'native-far-stroke-owners.json')
bpy.app.handlers.render_pre.append(pre)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1320/3840;s.render.border_max_x=2420/3840;s.render.border_min_y=1-1100/2885;s.render.border_max_y=1-480/2885;s.render.use_freestyle=True;s.render.use_compositing=True;s.render.filepath=str(O/'diagnostic-native.png')
t=time.time();bpy.ops.render.render(write_still=True);print('212_DIAGNOSTIC_DONE',time.time()-t,flush=True)
