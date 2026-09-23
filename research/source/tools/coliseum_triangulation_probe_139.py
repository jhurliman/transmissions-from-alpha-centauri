"""Read-only-in-effect repair probes on a private in-memory scene; never save changes."""
import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import coliseum_triangulation_134 as fix
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-details-138/scene.blend'))
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
names=['COL110 U9 aperture head','COL110 U9 fractured upper wall R','COL110 U10 aperture head']
out=[]
for name in names:
 ob=C.all_objects.get(name)
 if ob is None:out.append({'object':name,'error':'not found'});continue
 old=ob.data;fix.NAMES=(name,);t=time.time()
 try:result=fix.apply(C);out.append({'object':name,'result':result,'seconds':time.time()-t})
 except Exception as e:out.append({'object':name,'error':str(e),'seconds':time.time()-t})
 finally:
  ob.data=old
  if '134 safe prelayout triangulation' in ob:del ob['134 safe prelayout triangulation']
  bpy.context.view_layer.update()
O=R/'art/studies/coliseum-139';O.mkdir(parents=True,exist_ok=True);(O/'triangulation-probes.json').write_text(json.dumps({'source':'138','scene_saved':False,'probes':out},indent=2))
