import bpy,json
from pathlib import Path
from collections import Counter
R=Path('/PATH/TO/transmissions-from-alpha-centauri');bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-094/scene-C.blend'))
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH' and (o.get('rock_family') or any(t in o.name.lower() for t in ['crack','weather','spall','chip','substrate'])):
  rows.append({'name':o.name,'hidden':o.hide_render,'location':list(o.location),'family':o.get('rock_family'),'zone':o.get('rock_zone'),'props':{k:str(v) for k,v in o.items()},'materials':[m.name for m in o.data.materials if m]})
(R/'art/studies/lines-095/details-inventory.json').write_text(json.dumps(rows,indent=2));print('TOTAL',len(rows));print('ROCKS',rows[:4]);print('WEATHER',[x['name'] for x in rows if not x['family']][:100])
