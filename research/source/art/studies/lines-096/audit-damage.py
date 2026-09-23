import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-094/scene-C.blend'));s=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get()
placements=json.loads((R/'art/reviews/xenon-069/placements.json').read_text());known={p['part'] for p in placements}
for o in bpy.data.objects:
 if o.type=='MESH' and any(m and ('crack' in m.name.lower() or 'fracture' in m.name.lower()) for m in o.data.materials) and o.name!='Street foundation':known.add(o.name)
rows={}
for ins in dep.object_instances:
 o=ins.object
 if o.type!='MESH' or o.hide_render or o.name in known:continue
 mats=[m.name for m in o.data.materials if m];mods=[m.name for m in o.modifiers if m.type=='BOOLEAN'];tags=['projected surface','exposed mineral','depth dark','crack','fracture']
 if any(any(t in mat.lower() for t in tags) for mat in mats) or any(m.startswith(('059','069')) for m in mods):
  rows[o.name]={'name':o.name,'materials':mats,'boolean_modifiers':mods,'is_instance':ins.is_instance,'matrix':[list(r) for r in ins.matrix_world]}
O=R/'art/studies/lines-096';(O/'omitted-damage-hosts.json').write_text(json.dumps(list(rows.values()),indent=2));print(json.dumps(list(rows.values()),indent=2));print('PROOFHOSTS',[(o.name,[m.name for m in o.data.materials if m],[m.name for m in o.modifiers]) for o in bpy.data.objects if o.type=='MESH' and (o.name in ['Solid concrete 45 degree support.004','Tapered column structural volume.004'] or any(m.type=='BOOLEAN' and m.name.startswith('059') for m in o.modifiers))])
