import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/ground-085'
def take(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
 def obj(o):return {'matrix':[list(r) for r in o.matrix_world],'hidden':o.hide_render,'verts':[(v.co.x,v.co.y,v.co.z) for v in o.data.vertices] if o.type=='MESH' else [],'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []}
 return {'camera':[list(r) for r in s.camera.matrix_world],'lens':s.camera.data.lens,'objects':{o.name:obj(o) for o in s.objects if not(o.name=='Street foundation' or o.name.startswith(('077 broken earth lip','079 earth bank grit','085 ')))}}
a=take(R/'art/studies/cloud-084/scene.blend');b=take(O/'scene.blend');out={'camera_unchanged':a['camera']==b['camera'] and a['lens']==b['lens'],'preserved_object_count':len(a['objects']),'changed_outside_ground':[k for k,v in a['objects'].items() if b['objects'].get(k)!=v],'new_outside_ground':sorted(set(b['objects'])-set(a['objects']))};(O/'preservation-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
