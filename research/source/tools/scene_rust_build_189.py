"""Integrate scene-wide native fastener rust and the replacement Y-beam finish."""
import array
import hashlib
import json
from pathlib import Path
import sys
import time
import bpy

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'tools'))
O = R / 'art/studies/rust-189'
O.mkdir(parents=True, exist_ok=True)
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from coliseum_contact_clip_169 import snapshot, digest


def write(name, data):
    (O / name).write_text(json.dumps(data, indent=2, default=str) + '\n')


def guards(scene, embed):
    return [g(scene, embed=embed) for g in (g149, g156, g161)]


if 'render' in sys.argv:
    bpy.ops.wm.open_mainfile(filepath=str(O / 'scene.blend'))
    s = bpy.context.scene
    guards(s, False)
    s.render.filepath = str(O / 'main-4k.png')
    t = time.time()
    bpy.ops.render.render(write_still=True)
    write('performance.json', {'seconds': time.time() - t, 'resolution': [3840, 2885]})
else:
    bpy.ops.wm.open_mainfile(filepath=str(R / 'art/studies/coliseum-188/scene.blend'))
    s = bpy.context.scene
    source = (R / 'tools/scene_integration_138.py').read_text()
    exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")])
    before = fingerprint(s)
    old_materials = material_snapshot()
    gp_before = digest(snapshot(bpy.data.objects['110 Landmark contact ink']))
    from beam_rust_189 import apply as beam
    from bolt_rust_189 import append_payload as fasteners
    t = time.time()
    result = {'beam': beam(s), 'fasteners': fasteners(s)}
    bpy.context.view_layer.update()
    after = fingerprint(s)
    missing = sorted(set(before) - set(after))
    changed = {k: [f for f in v if v[f] != after[k][f]] for k, v in before.items() if k in after and v != after[k]}
    assert not missing, missing
    assert all(set(fields) <= {'materials'} for fields in changed.values()), changed
    ma = material_snapshot()
    graph_changes = [k for k, v in old_materials.items() if ma.get(k) != v]
    assert not graph_changes, graph_changes
    assert digest(snapshot(bpy.data.objects['110 Landmark contact ink'])) == gp_before
    assert not any(k.startswith(('COL110', 'COL120')) for k in changed), 'Unexpected landmark change'
    write('preservation.json', {
        'source': 'coliseum-188', 'source_recursive_entries': len(before),
        'original_changes': changed, 'missing_originals': missing,
        'new_objects': sorted(set(after) - set(before)),
        'original_geometry_normals_transforms_camera_lights_unchanged': True,
        'old_material_graphs_unchanged': True, 'landmark_contact_ink_unchanged': True,
        'limits': 'Weathering uses new private materials and attached native marks. Render differences are reviewed separately; no pixel-identity claim.',
    })
    result['build_seconds'] = time.time() - t
    result['source'] = 'art/studies/coliseum-188/scene.blend'
    result['references'] = ['RS-01', 'RS-02', 'RS-03', 'UP-03']
    result['guards'] = guards(s, True)
    write('generation.json', result)
    s.render.resolution_x = 3840
    s.render.resolution_y = 2885
    s.render.resolution_percentage = 100
    s.render.line_thickness = 3840 / 1440
    s.render.use_freestyle = True
    s.render.use_compositing = False
    s.render.use_border = False
    s.render.use_crop_to_border = False
    s.render.filepath = '//main-4k.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(O / 'scene.blend'))
    write('dependency-check.json', {
        'unpacked_file_images': [im.name for im in bpy.data.images if im.source == 'FILE' and im.users and not im.packed_file],
        'linked_objects': [o.name for o in bpy.data.objects if o.library],
        'photo_references_used_as_textures': False,
    })
