import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-120/scene.blend'));rows=[]
for o in bpy.data.objects:
 if o.type=='MESH'and ('Tower'in o.name or o.get('coliseum_role')=='tower'):
  vv=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'bay':o.get('bay'),'tier':o.get('tier'),'v':len(vv),'bounds':[[min(v[k]for v in vv)for k in range(3)],[max(v[k]for v in vv)for k in range(3)]]})
(R/'art/studies/coliseum-121/towers/inventory.json').write_text(json.dumps(rows,indent=2))
