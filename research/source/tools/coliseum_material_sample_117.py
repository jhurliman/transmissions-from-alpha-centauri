"""Render sample geometry with localized damage deposits; preserve source proof."""
import bpy, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'art/studies/coliseum-117'
sys.path.insert(0, str(ROOT / 'tools'))
from coliseum_weathering_117 import apply, exposed_core

bpy.ops.wm.open_mainfile(filepath=str(OUT / 'geometry-proof.blend'))
audit = json.loads((OUT / 'geometry-audit.json').read_text())
objects = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.get('bay') == 4 and o.get('tier') == 3]
records = apply(objects, audit['weathering_regions_original_world'], strength=1)
core = exposed_core()
core_faces = 0
for ob in objects:
    attr = ob.data.attributes.get('117 Exposed core')
    if not attr:
        continue
    slot = len(ob.data.materials)
    ob.data.materials.append(core)
    for face in ob.data.polygons:
        if attr.data[face.index].value > .5:
            face.material_index = slot
            core_faces += 1
records.append({'exposed_core_faces': core_faces, 'material': core.name})
(OUT / 'weathering-audit.json').write_text(json.dumps(records, indent=2))
bpy.context.scene.render.filepath = str(OUT / 'sample-weathered.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'sample-weathered.blend'))
start = time.time()
bpy.ops.render.render(write_still=True)
(OUT / 'weathering-performance.json').write_text(json.dumps({'render_seconds': time.time() - start}, indent=2))
