"""Read-only native stroke owner capture for user-reported corner overrun."""
import bpy,json
from pathlib import Path
REGION=(370,275,430,330)
def install(scene,output):
 from freestyle.types import StrokeShader
 import parameter_editor
 rows=[];camera=scene.camera.matrix_world.copy();output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 class Capture(StrokeShader):
  def __init__(self,label,layer):super().__init__();self.label=label;self.layer=layer
  def shade(self,stroke):
   points=list(stroke)
   if not any(REGION[0]<=p.point.x<=REGION[2] and REGION[1]<=2885-p.point.y<=REGION[3]for p in points):return
   out=[]
   for p in points:
    fe=p.fedge;shape=fe.viewedge.viewshape if fe and fe.viewedge else None
    out.append(dict(pixel=[float(p.point.x),2885-float(p.point.y)],world=list(camera@p.point_3d),shape=shape.name if shape else None,nature=int(fe.nature)if fe else None,visible=p.attribute.visible))
   rows.append(dict(lineset=self.label,layer=self.layer,points=out));output.write_text(json.dumps(dict(region=REGION,strokes=rows),indent=2))
 def callback(scene,layer,ls):return[Capture(ls.name,layer.name)]
 callback._capture192=True
 parameter_editor.callbacks_modifiers_post[:]=[f for f in parameter_editor.callbacks_modifiers_post if not getattr(f,'_capture192',False)]
 parameter_editor.callbacks_modifiers_post.append(callback)
 return rows
