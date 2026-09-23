"""Measure native fine-noise samples and solve for3x weighted coverage at identical feature scale."""
import bpy,sys,json
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-weathering-147';bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
from alley_panel_material_147 import make_panel_material
panels=json.loads((R/'art/studies/alley-weathering-145/geometry/audit.json').read_text())['panels'];m=make_panel_material(panel_regions=panels);nt=m.node_tree;pattern=next(n for n in nt.nodes if n.label=='147 Fine splatter noise field');bottom=next(n for n in nt.nodes if n.label=='147 Panel base weight');rgb=nt.nodes.new('ShaderNodeCombineColor');nt.links.new(pattern.outputs[0],rgb.inputs[0]);nt.links.new(bottom.outputs[0],rgb.inputs[1]);em=next(n for n in nt.nodes if n.type=='EMISSION');nt.links.new(rgb.outputs[0],em.inputs[0])
W,H=4.546,1.42;me=bpy.data.meshes.new('Coverage plane');me.from_pydata([(0,0,0),(W,0,0),(W,0,H),(0,0,H)],[],[(0,1,2,3)]);o=bpy.data.objects.new('Coverage plane',me);s.collection.objects.link(o);me.materials.append(m)
c=bpy.data.cameras.new('Coverage camera');co=bpy.data.objects.new('Coverage camera',c);s.collection.objects.link(co);co.location=(W/2,-4,H/2);co.rotation_euler=(1.57079632679,0,0);c.type='ORTHO';c.ortho_scale=W;s.camera=co;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1536;s.render.resolution_y=480;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.filepath=str(O/'native-splatter-field.exr');bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(s.render.filepath,check_existing=False);a=np.array(im.pixels[:],dtype=np.float64).reshape(-1,4);ok=a[:,3]>.999;x=a[ok,0];w=a[ok,1];assert w.max()>.95 and x.std()>.02,(w.max(),x.std())
def smooth(x,a,b):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def coverage(a,b,inverse=False):
 z=smooth(x,a,b);z=1-z if inverse else z;return float(np.sum(z*w)/np.sum(w))
results={}
for name,a,b,inv in [('islands',.552,.603,False),('holes',.365,.455,True)]:
 old=coverage(a,b,inv);target=old*3;assert target<1
 lo,hi=-.25,.25
 for _ in range(50):
  mid=(lo+hi)/2;val=coverage(a+mid,b+mid,inv)
  if (val<target)==inv:lo=mid
  else:hi=mid
 shift=(lo+hi)/2;new=coverage(a+shift,b+shift,inv);results[name]={'old_thresholds':[a,b],'new_thresholds':[a+shift,b+shift],'old_weighted_coverage':old,'new_weighted_coverage':new,'ratio':new/old}
(O/'coverage-calibration.json').write_text(json.dumps({'sample_count':len(x),'method':'Native Blender fine-noise field, weighted by actual panel-base falloff; solve smooth-mask threshold shift at unchanged spatial scales','coverage':results},indent=2));print(json.dumps(results))
