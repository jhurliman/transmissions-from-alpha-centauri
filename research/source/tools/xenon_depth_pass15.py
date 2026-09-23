import bpy,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-015';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-014/scene.blend'));s=bpy.context.scene
mats=[]
for i in range(8):
 m=bpy.data.materials.new('Ruin depth mineral tone '+str(i));m.diffuse_color=(.20+i*.018,.18+i*.014,.22+i*.018,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.95;mats.append(m)
for o in bpy.data.collections['013 Long ruined city - depth layers'].objects:
 match=re.search(r'Layer (\d+)',o.name)
 if not match:continue
 i=int(match[1]);factor=[.45,.40,.65,.8,1,1,1,1][i]
 for v in o.data.vertices:
  p=o.matrix_world@v.co;p.z*=factor;v.co=o.matrix_world.inverted()@p
 o.data.materials.clear();o.data.materials.append(mats[i])
s.use_nodes=False;s.cycles.samples=40;s.render.filepath=str(O/'render.png')
(O/'depth-layout.json').write_text((R/'art/reviews/xenon-014/depth-layout.json').read_text())
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
