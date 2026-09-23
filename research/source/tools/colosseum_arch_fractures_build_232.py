import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/colosseum-fractures-232';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/midground-arches-231/scene.blend'))
from colosseum_arch_fractures_232 import apply
start=time.time();a=apply(bpy.context.scene);a['seconds']=time.time()-start;(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'fractures-only.blend'));print('232 READY',a['changed_objects'],a['seconds'],flush=True)
