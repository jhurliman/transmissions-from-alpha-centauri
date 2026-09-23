import bpy,json
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-164/diagnosis';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-163/scene.blend'));names=['COL110 U4 fractured upper wall R','COL110 U5 fractured upper wall L','COL110 U9 fractured upper wall L','COL110 U9 aperture head','COL110 U9 fractured upper wall R'];rows=[]
for name in names:
 o=bpy.data.objects[name];rows.append({'object':name,'slots':[{'index':i,'material':s.material.name if s.material else None,'link':s.link,'raw_faces':sum(p.material_index==i for p in o.data.polygons)}for i,s in enumerate(o.material_slots)],'face_masks':[a.name for a in o.data.attributes if a.domain=='FACE']})
(O/'core-slots.json').write_text(json.dumps(rows,indent=2));print(rows,flush=True)
