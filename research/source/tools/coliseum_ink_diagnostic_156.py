"""Read-only full native Freestyle stroke evidence for three foreground regions."""
import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-156/regression'
from coliseum_ink_regression_149 import apply as guard
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));s=bpy.context.scene;guard(s,embed=False)
import parameter_editor
from freestyle.types import StrokeShader
rows=[];camera=s.camera.matrix_world.copy();regions={'left':[100,860,205,930],'right':[3510,865,3610,935],'crack':[120,1795,250,1880]}
class Capture(StrokeShader):
 def __init__(self,label):super().__init__();self.label=label
 def shade(self,stroke):
  points=list(stroke);hit=set()
  for v in points:
   x,y=v.point; y=2885-y
   for key,(x0,y0,x1,y1)in regions.items():
    if x0<=x<=x1 and y0<=y<=y1:hit.add(key)
  if not hit:return
  out=[]
  for v in points:
   fe=v.fedge;shape=fe.viewedge.viewshape if fe and fe.viewedge else None
   out.append({'pixel':[float(v.point.x),2885-float(v.point.y)],'world':list(camera@v.point_3d),'shape':shape.name if shape else None,'nature':int(fe.nature)if fe else None,'visible':v.attribute.visible})
  rows.append({'lineset':self.label,'regions':sorted(hit),'points':out});(O/'native-strokes.json').write_text(json.dumps(rows,indent=2))
def callback(scene,layer,ls):return [Capture(ls.name)]if ls.name in ['Selective geometry contours','050 Fine structural creases']else[]
parameter_editor.callbacks_modifiers_post.append(callback);s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'diagnostic.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'diagnostic-timing.json').write_text(json.dumps({'seconds':time.time()-t,'strokes':len(rows)}));print('DONE',len(rows),flush=True)
