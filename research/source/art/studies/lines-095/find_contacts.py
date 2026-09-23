import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-094/scene-C.blend'));d=bpy.context.evaluated_depsgraph_get();items=[]
for ins in d.object_instances:
 o=ins.object
 if o.type=='MESH' and ('foot' in o.name.lower() or 'bearing' in o.name.lower()):
  vs=[ins.matrix_world@Vector(v) for v in o.bound_box];mn=[min(v[i] for v in vs) for i in range(3)];mx=[max(v[i] for v in vs) for i in range(3)]
  if mn[2]<.3 and mx[2]>-.1 and abs(mn[0])<15:items.append({'name':o.name,'instance':ins.is_instance,'matrix':[list(row) for row in ins.matrix_world],'min':mn,'max':mx})
(R/'art/studies/lines-095/contacts.json').write_text(json.dumps(items,indent=2));print('CONTACTS',len(items),[(i['name'],i['min']) for i in items])
