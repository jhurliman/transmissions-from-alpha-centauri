import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-085/scene.blend'));g=bpy.data.objects['Street foundation'];d={'vertices':[list(v.co) for v in g.data.vertices],'faces':[list(f.vertices) for f in g.data.polygons],'materials':[f.material_index for f in g.data.polygons]};(R/'art/studies/ground-087/base-ground.json').write_text(json.dumps(d));print(len(d['vertices']),len(d['faces']))
