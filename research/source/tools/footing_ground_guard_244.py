"""Clip footing outline where actual soil geometry is in front of the stroke."""
import bpy
from mathutils.bvhtree import BVHTree

def install(scene):
 from freestyle.types import StrokeShader
 import parameter_editor
 ground=bpy.data.objects['Street foundation'];dg=bpy.context.evaluated_depsgraph_get();e=ground.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True);e.to_mesh_clear()
 M=scene.camera.matrix_world.copy();origin=M.translation.copy()
 class GroundVisible(StrokeShader):
  def shade(self,stroke):
   stroke.resample(1.0)
   pts=list(stroke)
   for a,b in zip(pts,pts[1:]):
    p=M@((a.point_3d+b.point_3d)/2);v=p-origin;hit=tree.ray_cast(origin,v.normalized(),v.length)
    if hit[0]is not None and hit[3]<v.length-.003:a.attribute.visible=False
 def callback(scene,layer,ls):return [GroundVisible()]if ls.name=='242 Service footing visible contour'else[]
 callback._guard244foot=True
 parameter_editor.callbacks_modifiers_post[:]=[f for f in parameter_editor.callbacks_modifiers_post if not getattr(f,'_guard244foot',False)];parameter_editor.callbacks_modifiers_post.append(callback)
def apply(scene,embed=True):
 def pre(scene,*args):install(scene)
 pre._guard244foot=True;bpy.app.handlers.render_pre[:]=[f for f in bpy.app.handlers.render_pre if not getattr(f,'_guard244foot',False)];bpy.app.handlers.render_pre.append(pre)
 if embed:
  from pathlib import Path
  t=bpy.data.texts.get('244 Footing soil visibility.py')or bpy.data.texts.new('244 Footing soil visibility.py');t.clear();t.write(Path(__file__).read_text()+'\napply(bpy.context.scene,embed=False)\n');t.use_module=True
 return {'method':'Native soil BVH occludes actual 3D footing contours','sampling_pixels':1,'ground':'Street foundation','scope':'242 Service footing visible contour only'}
