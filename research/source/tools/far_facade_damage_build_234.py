import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/far-facade-damage-234';O.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/facade-finish-233/scene.blend'))
from far_facade_damage_234 import apply
start=time.time();a=apply(bpy.context.scene);a['seconds']=time.time()-start;(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'damage-only.blend'));print('234 DAMAGE READY',a['event_count'],a['visible_buildings'],a['seconds'],flush=True)
