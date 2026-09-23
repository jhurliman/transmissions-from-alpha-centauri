import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/haze-ground-202';O.mkdir(parents=True,exist_ok=True)
if 'render' in sys.argv:
 for kind in ('before','after'):
  path=R/'art/studies/scene-completion-201/scene.blend' if kind=='before' else O/'candidate.blend'
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.resolution_percentage=50;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=False
  for vl in s.view_layers:
   vl.use_freestyle=False
   if vl.name.startswith('192 Architecture'):vl.use=False
  s.render.filepath=str(O/(kind+'.png'));t=time.time();bpy.ops.render.render(write_still=True);(O/(kind+'-performance.json')).write_text(json.dumps({'seconds':time.time()-t,'native_no_ink_matched_pair':True}))
else:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-completion-201/scene.blend'));from haze_ground_transition_202 import apply
 a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'))
