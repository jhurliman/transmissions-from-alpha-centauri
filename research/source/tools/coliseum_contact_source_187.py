"""Read-only inventory of native contact strokes attached to the left course-end solids and conditional dentil."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'tools'))
from coliseum_contact_clip_169 import snapshot, digest
from bpy_extras.object_utils import world_to_camera_view

O = R / 'art/studies/coliseum-187/contact-source'
O.mkdir(parents=True, exist_ok=True)
source = R / 'art/studies/coliseum-173/scene.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
targets = ['COL110 T2 band10 profile'+str(i) for i in range(5)] + ['COL110 U10 sill wall', 'COL120 bay10 arcade2 dentil03']
dg = bpy.context.evaluated_depsgraph_get()
trees = {}
for name in targets:
    ob = bpy.data.objects[name].evaluated_get(dg)
    me = ob.to_mesh()
    me.calc_loop_triangles()
    trees[name] = BVHTree.FromPolygons(
        [ob.matrix_world @ v.co for v in me.vertices],
        [tuple(t.vertices) for t in me.loop_triangles], all_triangles=True)
    ob.to_mesh_clear()
gp = bpy.data.objects['110 Landmark contact ink']
snap = snapshot(gp)
selected = []
for record in snap:
    for index, stroke in enumerate(record['strokes']):
        points = [gp.matrix_world @ Vector(p) for p in stroke['point']['position']]
        owners = {}
        near = []
        samples = [(float(i), p) for i, p in enumerate(points)]
        samples += [(i + 0.5, (a + b) * 0.5) for i, (a, b) in enumerate(zip(points, points[1:]))]
        for t, p in samples:
            nearest = min(((tree.find_nearest(p)[3], name) for name, tree in trees.items()))
            if nearest[0] <= 0.02:
                owners[nearest[1]] = owners.get(nearest[1], 0) + 1
                near.append({'t': t, 'world': list(p), 'owner': nearest[1], 'distance_m': nearest[0]})
        if near:
            screen = [world_to_camera_view(bpy.context.scene, bpy.context.scene.camera, p) for p in points]
            selected.append({'layer': record['layer'], 'frame': record['frame'], 'stroke': index,
                             'point_count': len(points), 'owners': owners, 'samples': near,
                             'world_z_range': [min(p.z for p in points), max(p.z for p in points)],
                             'native_pixel_bounds': [min(p.x * 3840 for p in screen), min((1 - p.y) * 2885 for p in screen),
                                                     max(p.x * 3840 for p in screen), max((1 - p.y) * 2885 for p in screen)],
                             'attributes': stroke})
audit = {
    'source': str(source.relative_to(R)), 'source_drawing_digest': digest(snap),
    'matrix_world': [list(row) for row in gp.matrix_world],
    'targets': targets, 'total_strokes': sum(len(r['strokes']) for r in snap),
    'candidate_strokes': len(selected),
    'method': 'Native point and segment midpoint samples within20mm of actual evaluated target solids. Read-only broad candidate inventory, not a continuous support certificate.',
    'limitations': ['Some unsampled segment interiors may also touch the targets.',
                   'No stroke is authorized for removal by this inventory. Compare to the actual187 retained solids, preserve supported runs, then certify any removed intervals.'],
    'retained_scene_changed': False
}
(O / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n')
(O / 'candidate-strokes.json').write_text(json.dumps(selected, indent=2) + '\n')
print(json.dumps({k: v for k, v in audit.items() if k not in ('matrix_world', 'targets')}, indent=2))
