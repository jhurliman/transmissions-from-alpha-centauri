"""Portable approved-scene renderer. Run with Blender --disable-autoexec --python-exit-code 1."""
import bpy, sys, json, time, argparse, platform, hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True,help='New output directory; existing files are never overwritten')
parser.add_argument('--check-only',action='store_true')
parser.add_argument('--allow-different-build',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if bpy.app.build_hash.decode()!='9e2066aef7ef' and not args.allow_different_build:
    raise RuntimeError('Use Blender 5.2.1 LTS build 9e2066aef7ef, or explicitly allow an unverified build')
D=Path(args.output).expanduser().resolve()
if D.exists(): raise RuntimeError('Output already exists: '+str(D))
D.mkdir(parents=True)
sys.path.insert(0,str(R/'runtime'))
bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'))
assert not bpy.data.libraries, 'External linked library'
for im in bpy.data.images:
    if im.source=='FILE': assert im.packed_file or im.packed_files, 'Unpacked image: '+im.name
    else: assert im.source in {'VIEWER','GENERATED'}, 'External image type: '+im.source
s=bpy.context.scene
start=time.time()
for vl in s.view_layers:
 vl.use=True
 if vl.use_freestyle:vl.freestyle_settings.use_culling=True
s.eevee.taa_render_samples=64
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
from footing_ground_guard_244 import apply as footguard
footguard(s,embed=False)
s.eevee.shadow_pool_size='1024'
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.use_compositing=True;s.render.dither_intensity=0
s.render.filepath=str(D/'main-4k.png')

report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'platform':platform.platform(),'scene_sha256':hashlib.sha256((R/'scene.blend').read_bytes()).hexdigest(),'resolution':[s.render.resolution_x,s.render.resolution_y],'packed_file_images':sum(i.source=='FILE' for i in bpy.data.images),'check_only':args.check_only}
(D/'run.json').write_text(json.dumps(report,indent=2))
if not args.check_only:
    bpy.ops.render.render(write_still=True)
    report.update(seconds=time.time()-start,image_sha256=hashlib.sha256((D/'main-4k.png').read_bytes()).hexdigest())
    (D/'run.json').write_text(json.dumps(report,indent=2))
print('V1_RELEASE_COMPLETE',json.dumps(report))
