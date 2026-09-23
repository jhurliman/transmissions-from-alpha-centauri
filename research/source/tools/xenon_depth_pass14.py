import bpy,json,re
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-014';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-013/scene.blend'));s=bpy.context.scene
pre=('Dome ','Fine secondary dome','Crown broken spar');obs=[o for o in s.objects if o.name.startswith(pre)]
def bounds(objects):
 pts=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
alley=bounds([o for o in s.objects if o.name.startswith(('Left deep wall core','Right shadow core'))]);length=alley[1][1]-alley[1][0];end=alley[1][1];front=end+3*length
old=bounds(obs);factor=.5
xf=Matrix.Translation(Vector((0,front-factor*old[1][0],-factor*old[2][0])))@Matrix.Scale(factor,4)
for o in obs:o.matrix_world=xf@o.matrix_world
# Each architectural group keeps its local proportions; only its placement changes.
# World-space mesh coordinates must be transformed about each group, not object origin.
col=bpy.data.collections['013 Long ruined city - depth layers']
old_layers=[39,57,83,120,168,224,288,353];new_layers=[40,53,67,83,100,117,134,145]
for o in col.objects:
 match=re.search(r'Layer (\d+)',o.name)
 if not match:continue
 layer=int(match[1]);a=old_layers[layer];b=new_layers[layer]
 # Reduce far structure size to ordinary ruined buildings along the shorter measured street.
 f=1 if layer<2 else .65
 # Compress lateral positions only for distant field so city stays present around sightline.
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  p.y=b+(p.y-a)*.55
  p.x*=max(.30, b/a)
  p.z*=f
  v.co=o.matrix_world.inverted()@p
for o in bpy.data.objects:
 if o.name.startswith('Distant dust volume'):
  o.location=(0,170,25);o.dimensions=(500,260,54)
  for n in o.data.materials[0].node_tree.nodes:
   if n.type=='VOLUME_SCATTER':n.inputs['Density'].default_value=.003
# Numeric inspection includes nearest shell edge, not dome center.
bpy.context.view_layer.update();new=bounds(obs)
audit={'alley_start':alley[1][0],'alley_end':end,'alley_length':length,'dome_nearest_edge':new[1][0],'gap':new[1][0]-end,'gap_in_alley_lengths':(new[1][0]-end)/length,'dome_lowest_z':new[2][0],'ruin_layers':new_layers,'image_textures':sum(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)}
assert abs(audit['gap_in_alley_lengths']-3)<.001
assert audit['image_textures']==0
(O/'depth-layout.json').write_text(json.dumps(audit,indent=2)+'\n')
s.use_nodes=False;s.cycles.samples=40;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
