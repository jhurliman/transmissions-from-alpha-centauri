import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/clouds-199'
def snapshot():
 s=bpy.context.scene;C=bpy.data.collections['082 Derived flat clouds'];clouds={x.name for x in C.all_objects}
 return {'camera':repr(tuple(tuple(row)for row in s.camera.matrix_world)),'world':s.world.name,'world_nodes':[(n.name,n.type,n.label)for n in s.world.node_tree.nodes],'objects':{o.name:(repr(tuple(tuple(row)for row in o.matrix_world)),o.data.name if o.data else None,tuple(x.material.name if x.material else None for x in o.material_slots)if o.name not in clouds else None)for o in bpy.data.objects},'clouds':sorted(clouds)}
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/beam-rust-197/scene.blend'));before=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));after=snapshot();assert before==after
images=[i for i in bpy.data.images if i.name.startswith('199 Native subtle cloud')];assert len(images)==4 and all(i.packed_file for i in images)
audit={'noncloud_materials_and_all_transforms_datablocks_unchanged':True,'camera_and_world_nodes_unchanged':True,'private_packed_images':4,'cloud_objects':after['clouds'],'source_sha256':hashlib.sha256((R/'art/studies/beam-rust-197/scene.blend').read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((O/'candidate.blend').read_bytes()).hexdigest()}
(O/'preservation.json').write_text(json.dumps(audit,indent=2));print('199_PRESERVATION_PASS')
