import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 return {'camera':{'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'lens':s.camera.data.lens},'objects':{o.name:{'matrix':[list(r) for r in o.matrix_world],'hidden':o.hide_render,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []} for o in s.objects if not o.name.startswith(('080 ','082 '))}}
a=snapshot(R/'art/studies/soil-081/selected-scene.blend');b=snapshot(R/'art/studies/cloud-082/scene.blend')
result={'camera_unchanged':a['camera']==b['camera'],'baseline_noncloud_objects':len(a['objects']),'candidate_noncloud_objects':len(b['objects']),'changed_noncloud_objects':[k for k,v in a['objects'].items() if v!=b['objects'].get(k)],'added_noncloud_objects':sorted(set(b['objects'])-set(a['objects'])),'scope':'Read-only checks of camera, transforms, visibility, vertex counts and material assignments. Cloud layers and sky-only world changes are excluded; visual review remains separate.'}
(R/'art/studies/cloud-082/audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
