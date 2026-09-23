import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-composition-215';sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/colosseum-scale-210/70/scene.blend'));s=bpy.context.scene
from alley_repeat_212 import verts,SOURCES,visible_objects
rows=[]
for name in SOURCES:
 c=bpy.data.collections.get(name)
 if not c:continue
 for o in list(visible_objects(c)):
  if o.hide_render or not(o.type in('MESH','CURVE')or o.instance_type=='COLLECTION'):continue
  p=list(verts(o))
  if not p:continue
  rows.append({'name':o.name,'type':o.type,'collection':o.instance_collection.name if o.instance_collection else None,'source_group':name,'location':list(o.matrix_world.translation),'bounds':[[min(v[k]for v in p)for k in range(3)],[max(v[k]for v in p)for k in range(3)]],'count':len(o.instance_collection.all_objects)if o.instance_collection else 1})
(O/'component-inventory.json').write_text(json.dumps(rows,indent=2));print('215INVENTORY',len(rows),flush=True)
