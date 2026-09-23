"""Native full-resolution proof with established architecture visibility guards."""
import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/haze-texture-221'
label='221';D=O
bpy.ops.wm.open_mainfile(filepath=str(D/'scene.blend'));s=bpy.context.scene
from alley_repeat_212 import repeat_guard_pairs
repeat_guard_pairs(s)
from coliseum_ink_regression_149 import apply as a149
from coliseum_foreground_visibility_156 import apply as a156
from coliseum_foreground_visibility_161 import apply as a161
from architecture_ink_visibility_192 import apply as a192
from architecture_ink_visibility_205 import apply as a205
for fn in(a149,a156,a161,a192,a205):fn(s,embed=False)
def guards(scene,*args):
 from architecture_ink_visibility_207 import install
 install(scene,str(D/'207-guard-proof.json'))
 import parameter_editor
 from types import SimpleNamespace
 original=list(parameter_editor.callbacks_modifiers_post)
 source=[f for f in original if any(getattr(f,'_guard'+str(n),False)for n in(192,205,207))]
 def callback(scene,layer,ls):
  if ls.name!='215 Distant component architecture':return []
  return [shader for f in source for shader in f(scene,layer,SimpleNamespace(name='Selective geometry contours'))]
 callback._guard218=True
 parameter_editor.callbacks_modifiers_post[:]=[f for f in original if not getattr(f,'_guard218',False)]
 parameter_editor.callbacks_modifiers_post.append(callback)
 from alley_roof_seating_215 import install_line_counter
 install_line_counter(scene,str(D/'far-line-count.json'))
 (D/'far-guard-audit.json').write_text(json.dumps({'source_callback_count':len(source),'styles':'215 Distant component architecture','rules':[192,205,207]}))
bpy.app.handlers.render_pre.append(guards)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.use_compositing=True;s.render.dither_intensity=0
s.render.filepath=str(D/'main-4k.png')
t=time.time();bpy.ops.render.render(write_still=True)
(D/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'width':3840,'height':2885,'guards':[149,156,161,192,205,207,218]}));print('221 PROOF DONE',label,flush=True)

original_media=s.render.image_settings.media_type;original_format=s.render.image_settings.file_format
try:
 s.render.image_settings.media_type='MULTI_LAYER_IMAGE';s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';bpy.data.images['Render Result'].save_render(str(D/'native-render.exr'),scene=s)
finally:
 s.render.image_settings.media_type=original_media;s.render.image_settings.file_format=original_format
