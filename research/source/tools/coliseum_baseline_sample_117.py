"""116 sample from the exact117 proof camera, for valid before/after comparison."""
import bpy
from pathlib import Path
R = Path(__file__).resolve().parents[1]
O = R / 'art/studies/coliseum-117'
bpy.ops.wm.open_mainfile(filepath=str(O / 'geometry-proof.blend'))
s = bpy.context.scene
camera_matrix = s.camera.matrix_world.copy()
scale = s.camera.data.ortho_scale
resolution = (s.render.resolution_x, s.render.resolution_y)
bpy.ops.wm.open_mainfile(filepath=str(R / 'art/studies/coliseum-116/scene.blend'))
s = bpy.context.scene
C = bpy.data.collections['110 Coliseum detailed front ruin']
keep = {o for o in C.objects if o.get('bay') == 4}
for ob in list(keep):
    while ob.parent:
        ob = ob.parent
        keep.add(ob)
keep.update(o for o in s.objects if o.type in ['LIGHT', 'CAMERA'])
bpy.data.batch_remove(ids=[o for o in list(s.objects) if o not in keep])
s.camera.matrix_world = camera_matrix
s.camera.data.type = 'ORTHO'
s.camera.data.ortho_scale = scale
s.world = bpy.data.worlds.new('117 Matched baseline world')
s.world.use_nodes = True
s.world.node_tree.nodes.get('Background').inputs[0].default_value = (.2, .2, .23, 1)
s.world.node_tree.nodes.get('Background').inputs[1].default_value = .65
s.render.resolution_x, s.render.resolution_y = resolution
s.render.resolution_percentage = 100
s.render.use_border = False
s.render.use_crop_to_border = False
s.render.use_freestyle = False
s.render.filepath = str(O / 'baseline-painted.png')
bpy.ops.render.render(write_still=True)
m = bpy.data.materials.new('117 Baseline clay')
m.use_nodes = True
p = m.node_tree.nodes.get('Principled BSDF')
p.inputs['Base Color'].default_value = (.45, .45, .45, 1)
p.inputs['Roughness'].default_value = .7
for ob in s.objects:
    if ob.type == 'MESH':
        ob.data.materials.clear()
        ob.data.materials.append(m)
s.render.filepath = str(O / 'baseline-clay.png')
bpy.ops.render.render(write_still=True)
