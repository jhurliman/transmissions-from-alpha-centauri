"""Read-only dense support comparison for the proposed crown cut."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'tools'))
from coliseum_contact_clip_169 import snapshot, digest
O = R / 'art/studies/coliseum-179/contact-source'
inventory = json.loads((O / 'audit.json').read_text())
names = set(inventory['targets'])

def mesh_tree(objects, bounds=None):
    verts, tris, owners = [], [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in objects:
        if ob.type != 'MESH' or ob.hide_render or 'ink' in ob.name.lower():
            continue
        ev = ob.evaluated_get(dg)
        bb = [ev.matrix_world @ Vector(v) for v in ev.bound_box]
        if bounds and any(max(p[k] for p in bb) < bounds[k][0] - .05 or
                          min(p[k] for p in bb) > bounds[k][1] + .05 for k in range(3)):
            continue
        me = ev.to_mesh()
        me.calc_loop_triangles()
        offset = len(verts)
        verts += [ev.matrix_world @ v.co for v in me.vertices]
        tris += [tuple(offset + i for i in t.vertices) for t in me.loop_triangles]
        owners.append(ob.name)
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, tris, all_triangles=True), verts, owners

bpy.ops.wm.open_mainfile(filepath=str(R / inventory['source']))
gp = bpy.data.objects['110 Landmark contact ink']
snap = snapshot(gp)
assert digest(snap) == inventory['source_drawing_digest']
matrix = gp.matrix_world.copy()
old, verts, _ = mesh_tree([bpy.data.objects[n] for n in names])
bounds = [(min(v[k] for v in verts) - .05, max(v[k] for v in verts) + .05) for k in range(3)]
bpy.ops.wm.open_mainfile(filepath=str(R / 'art/studies/coliseum-179/geometry/candidate.blend'))
assert digest(snapshot(bpy.data.objects['110 Landmark contact ink'])) == inventory['source_drawing_digest']
current, _, owners = mesh_tree(bpy.data.collections['110 Coliseum detailed front ruin'].all_objects, bounds)
rows, total = [], 0
for record in snap:
    for index, stroke in enumerate(record['strokes']):
        points = [matrix @ Vector(p) for p in stroke['point']['position']]
        tested, lost, preserved = 0, [], []
        for segment, (a, b) in enumerate(zip(points, points[1:])):
            if any(max(a[k], b[k]) < bounds[k][0] or min(a[k], b[k]) > bounds[k][1] for k in range(3)):
                continue
            count = max(1, math.ceil((b - a).length / .01))
            for j in range(count + 1):
                p = a.lerp(b, j / count)
                before = old.find_nearest(p)[3]
                if before > .02:
                    continue
                after = current.find_nearest(p)[3]
                tested += 1
                if after > .025:
                    lost.append({'t': segment + j / count, 'world': list(p), 'source_target_distance': before, 'current_solid_distance': after})
                else:
                    preserved.append(after)
        if tested:
            rows.append({'layer': record['layer'], 'frame': record['frame'], 'stroke': index,
                         'tested_samples': tested, 'lost_samples': lost,
                         'maximum_other_supported_sample_distance': max(preserved, default=None)})
            total += tested
result = {'source_digest': inventory['source_drawing_digest'], 'candidate': '179/geometry/candidate.blend',
          'sample_step_max_m': .01, 'source_supported_threshold_m': .02, 'lost_screen_threshold_m': .025,
          'support_meshes': owners, 'sample_count': total, 'strokes': rows,
          'strokes_with_potential_removed_support': [r['stroke'] for r in rows if r['lost_samples']],
          'limits': 'Dense screen only, not a continuous removal certificate. No strokes modified; preserve supported spans and refine any potential losses before clipping.'}
(O / 'candidate-support-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print('Source-supported samples:', total, 'Potentially affected strokes:', result['strokes_with_potential_removed_support'])
