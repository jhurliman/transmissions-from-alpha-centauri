"""Suppress only proven hidden native foreground strokes using actual3D receivers."""
import bpy
PAIRS={
 'Long platform girder back flange.009':('Folded fascia.004',),
 'Deck cross joist back flange.031':('Folded fascia.004',),
 'Deck cross joist web.031':('Folded fascia.004',),
}

def install(scene):
 from mathutils.bvhtree import BVHTree
 from freestyle.types import StrokeShader
 import parameter_editor
 dg=bpy.context.evaluated_depsgraph_get();targets={n for ns in PAIRS.values()for n in ns};data={n:([],[])for n in targets}
 for instance in dg.object_instances:
  name=instance.object.name
  if name not in targets:continue
  me=instance.object.to_mesh();me.calc_loop_triangles();vv,tt=data[name];offset=len(vv);vv.extend(instance.matrix_world@v.co for v in me.vertices);tt.extend(tuple(offset+i for i in t.vertices)for t in me.loop_triangles);instance.object.to_mesh_clear()
 trees={n:BVHTree.FromPolygons(vv,tt,all_triangles=True)for n,(vv,tt)in data.items()};M=scene.camera.matrix_world.copy();origin=M.translation.copy();audit={'threshold_m':.02,'pairs':PAIRS,'sampled_segments':0,'hidden_segments':0,'by_shape':{},'examples':[]}
 class VisibleNativeOnly(StrokeShader):
  def shade(self,stroke):
   points=list(stroke)
   for a,b in zip(points,points[1:]):
    fe=a.fedge;shape=fe.viewedge.viewshape if fe and fe.viewedge else None
    if not shape or shape.name not in PAIRS:continue
    source=shape.name;wa=M@a.point_3d;wb=M@b.point_3d;samples=[wa,(wa+wb)/2,wb];hide=False;winner=None;gaps=[]
    for target in PAIRS[source]:
     values=[]
     for p in samples:
      delta=p-origin;hit=trees[target].ray_cast(origin,delta.normalized(),delta.length);values.append(delta.length-hit[3]if hit[0]is not None else-1)
     if min(values)>.02:hide=True;winner=target;gaps=values;break
    audit['sampled_segments']+=1
    if hide:
     a.attribute.visible=False;audit['hidden_segments']+=1;audit['by_shape'][source]=audit['by_shape'].get(source,0)+1
     if len(audit['examples'])<60:audit['examples'].append({'source':source,'occluder':winner,'gaps_m':gaps,'world_segment':[list(wa),list(wb)]})
 def callback(scene,layer,ls):return [VisibleNativeOnly()]if ls.name in ['Selective geometry contours','050 Fine structural creases']else[]
 callback._guard161=True;callback._guard161_audit=audit
 parameter_editor.callbacks_modifiers_post[:]=[f for f in parameter_editor.callbacks_modifiers_post if not getattr(f,'_guard161',False)];parameter_editor.callbacks_modifiers_post.append(callback);return audit
def apply(scene,embed=True):
 def render_pre(scene,*args):install(scene)
 render_pre._guard161=True;bpy.app.handlers.render_pre[:]=[f for f in bpy.app.handlers.render_pre if not getattr(f,'_guard161',False)];bpy.app.handlers.render_pre.append(render_pre);audit=install(scene)
 if embed:
  from pathlib import Path
  name='161 Proven fascia occlusion guard.py';t=bpy.data.texts.get(name)or bpy.data.texts.new(name);t.clear();t.write(Path(__file__).read_text()+'\napply(bpy.context.scene,embed=False)\n');t.use_module=True
 return audit
