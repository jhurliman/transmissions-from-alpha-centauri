import bpy,random,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-019';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-018/scene.blend'));s=bpy.context.scene;random.seed(1919)
for ob in s.objects:
 if ob.name.startswith('Torn cladding sheet'):
  vs=ob.data.vertices;ys=[v.co.y for v in vs];zs=[v.co.z for v in vs];w=max(ys)-min(ys);h=max(zs)-min(zs)
  for i in [1,2,3,4,5]:
   vs[i].co.y+=random.uniform(-.12,.12)*w;vs[i].co.z+=random.uniform(-.12,.12)*h
  if random.random()<.45:
   for v in vs:v.co.y=min(ys)+max(ys)-v.co.y
# Restore a legible contour hierarchy from real surface boundaries.
s.render.use_freestyle=True;s.render.line_thickness=1.15
for vl in s.view_layers:
 for ls in vl.freestyle_settings.linesets:
  if ls.linestyle:
   ls.linestyle.thickness=1.25;ls.linestyle.color=(.055,.046,.061);ls.linestyle.alpha=.9
# Remove high-frequency speckling from architectural cladding; use sparse broad worn islands.
for name in ['Painted lavender steel','Sun-worn warm cladding','Exposed weathered steel']:
 m=bpy.data.materials.get(name)
 if not m or not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='TEX_NOISE':
   if n.inputs['Scale'].default_value>25:n.inputs['Scale'].default_value=5.5
  if n.type=='MATH' and n.operation=='GREATER_THAN':n.inputs[1].default_value=.43
s.use_nodes=False;s.cycles.samples=48;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
