import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-016';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-015/scene.blend'));s=bpy.context.scene
# Double the clear ground distance without enlarging the dome again.
for o in s.objects:
 if o.name.startswith(('Dome ','Fine secondary dome','Crown broken spar')):o.location.y+=120
# Stretch placement of all ruin geometry beyond the alley end across the longer span.
for o in bpy.data.collections['013 Long ruined city - depth layers'].objects:
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co;p.y=32+2*(p.y-32);v.co=inv@p
for o in s.objects:
 if o.name.startswith('Distant dust volume'):
  o.location=(0,235,25);o.dimensions=(600,390,54)
  for n in o.data.materials[0].node_tree.nodes:
   if n.type=='VOLUME_SCATTER':n.inputs['Density'].default_value=.0025
bpy.context.view_layer.update()
def bounds(prefix):
 pts=[o.matrix_world@Vector(v) for o in s.objects if o.name.startswith(prefix) for v in o.bound_box]
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
a=bounds(('Left deep wall core','Right shadow core'));d=bounds(('Dome ','Fine secondary dome','Crown broken spar'));length=a[1][1]-a[1][0];gap=d[1][0]-a[1][1]
audit={'alley_length':length,'alley_end':a[1][1],'dome_nearest_edge':d[1][0],'gap':gap,'gap_in_alley_lengths':gap/length,'dome_rescaled':False,'image_textures':sum(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)}
assert abs(gap/length-6)<.001;assert audit['image_textures']==0
(O/'depth-layout.json').write_text(json.dumps(audit,indent=2)+'\n')
s.use_nodes=False;s.cycles.samples=40;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
