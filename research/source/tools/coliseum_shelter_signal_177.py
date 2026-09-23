"""Native AO-distance comparison. Diagnostic data only; never save the scene."""
import bpy
import json
import time
import sys
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parents[1]
O = R / 'art/studies/coliseum-177/diagnosis'
O.mkdir(parents=True, exist_ok=True)
cfg = json.loads((R / 'config/coliseum-shelter-signal-177.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R / cfg['source']))
s = bpy.context.scene
C = bpy.data.collections['110 Coliseum detailed front ruin']
copies = {}
assignments = []
for ob in C.all_objects:
    if ob.type != 'MESH':
        continue
    for i, slot in enumerate(ob.material_slots):
        old = slot.material
        if not old or not old.use_nodes or not any(n.type == 'AMBIENT_OCCLUSION' for n in old.node_tree.nodes):
            continue
        if old not in copies:
            m = old.copy()
            m.name = '177 Shelter distances ' + old.name
            nodes, links = m.node_tree.nodes, m.node_tree.links
            signal = nodes.new('ShaderNodeCombineXYZ')
            for channel, distance in enumerate((0.7, 6.0, 18.0)):
                ao = nodes.new('ShaderNodeAmbientOcclusion')
                ao.label = f'177 Native shelter at {distance} m'
                ao.inputs['Distance'].default_value = distance
                links.new(ao.outputs['AO'], signal.inputs[channel])
            emission = nodes.new('ShaderNodeEmission')
            links.new(signal.outputs[0], emission.inputs['Color'])
            output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
            links.new(emission.outputs[0], output.inputs['Surface'])
            copies[old] = m
        slot.link = 'OBJECT'
        slot.material = copies[old]
        assignments.append({'object': ob.name, 'slot': i, 'source': old.name})
x0, y0, x1, y1 = cfg['crop']
s.render.resolution_x = 3840
s.render.resolution_y = 2885
s.render.resolution_percentage = 100
s.render.use_compositing = False
s.render.use_freestyle = False
s.render.use_border = s.render.use_crop_to_border = True
s.render.border_min_x, s.render.border_max_x = x0 / 3840, x1 / 3840
s.render.border_min_y, s.render.border_max_y = 1 - y1 / 2885, 1 - y0 / 2885
s.render.image_settings.file_format = 'OPEN_EXR'
s.render.image_settings.color_depth = '32'
s.render.filepath = str(O / 'signals.exr')
t = time.time()
if '--scalar' in sys.argv:
    # Keep every probe achromatic so colored atmosphere cannot masquerade
    # as a difference between the three AO distances.
    times = {}
    for channel, distance in enumerate((0.7, 6.0, 18.0)):
        for m in copies.values():
            nodes, links = m.node_tree.nodes, m.node_tree.links
            output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
            emission = output.inputs['Surface'].links[0].from_node
            ao = next(n for n in nodes if n.label == f'177 Native shelter at {distance} m')
            links.new(ao.outputs['AO'], emission.inputs['Color'])
        s.render.filepath = str(O / f'scalar-{channel}.exr')
        start = time.time()
        bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load(s.render.filepath, check_existing=False)
        w, h = im.size
        pixels = np.empty(w * h * 4, dtype=np.float32)
        im.pixels.foreach_get(pixels)
        np.save(O / f'scalar-{channel}.npy', pixels.reshape(h, w, 4)[::-1])
        times[str(distance)] = time.time() - start
    (O / 'scalar-audit.json').write_text(json.dumps({
        'source': cfg['source'], 'distances': [0.7, 6.0, 18.0],
        'method': 'Three matched achromatic AO probes; same output channel comparisons avoid chromatic-volume cross-channel confound.',
        'render_seconds': times, 'art_scene_saved': False
    }, indent=2) + '\n')
    raise SystemExit(0)
bpy.ops.render.render(write_still=True)
im = bpy.data.images.load(str(O / 'signals.exr'), check_existing=False)
w, h = im.size
a = np.empty(w * h * 4, dtype=np.float32)
im.pixels.foreach_get(a)
a = a.reshape(h, w, 4)[::-1]
np.save(O / 'signals.npy', a)
(O / 'audit.json').write_text(json.dumps({
    'source': cfg['source'], 'crop': cfg['crop'], 'assignments': assignments,
    'channels': 'R AO0.7m, G AO6m, B AO18m, all after retained scene transport',
    'seconds': time.time() - t, 'saved_art_scene': False,
    'limits': ['Signals include volume transport and silhouette antialiasing.', 'Distance differences are diagnostic and provide no automatic aesthetic credit.']
}, indent=2) + '\n')
