import bpy,json,re,collections
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-094/scene-C.blend'));dep=bpy.context.evaluated_depsgraph_get();rows={}
for ins in dep.object_instances:
 o=ins.object
 if o.type!='MESH' or o.hide_render:continue
 v=[ins.matrix_world@Vector(p) for p in o.bound_box];lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
 if lo[2]>.2 or hi[2]>.6:continue
 if o.get('rock_family'):continue
 name=re.sub(r'\.\d+$','',o.name)
 if name not in rows:rows[name]={'name':name,'count':0,'min':lo,'max':hi,'materials':[m.name for m in o.data.materials if m],'polygons':len(o.data.polygons)}
 rows[name]['count']+=1
O=R/'art/studies/lines-096';(O/'ground-helper-candidates.json').write_text(json.dumps(list(rows.values()),indent=2));print([(r['name'],r['count'],r['materials']) for r in rows.values()])
