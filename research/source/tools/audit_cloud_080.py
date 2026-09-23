"""Read-only invariants for the isolated cloud revision."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 return {'camera':{'name':s.camera.name,'matrix':[list(row) for row in s.camera.matrix_world],'lens':s.camera.data.lens},'objects':{o.name:{'matrix':[list(row) for row in o.matrix_world],'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []} for o in s.objects if not o.name.startswith('080 ')}}
a=snapshot(R/'art/reviews/xenon-079/scene.blend');b=snapshot(R/'art/studies/cloud-080/scene.blend');C=bpy.data.collections['080 Native cloud banks'];records=json.loads(C['audit']);result={'camera_unchanged':a['camera']==b['camera'],'baseline_object_count':len(a['objects']),'candidate_noncloud_object_count':len(b['objects']),'changed_noncloud_objects':[k for k in a['objects'] if a['objects'][k]!=b['objects'].get(k)],'added_noncloud_objects':list(set(b['objects'])-set(a['objects'])),'all_insets_lower_frequency':all(r['inset_frequency'] is None or r['inset_frequency']<r['outer_frequency'] for r in records),'cloud_records':records,'native_cloud_objects':len(C.objects),'note':'Checks transforms, vertex counts, material assignments, camera, and frequency hierarchy. Visual render review is separate.'};(R/'art/studies/cloud-080/audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
