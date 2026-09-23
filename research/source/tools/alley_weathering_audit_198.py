import bpy,json,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-weathering-198';src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
def snap():
 out={}
 for o in bpy.data.objects:
  x={'matrix':[list(r)for r in o.matrix_basis],'materials':[sl.material.name if sl.material else None for sl in o.material_slots],'instance':o.instance_collection.name if o.instance_collection else None}
  if o.type=='MESH':
   a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);b=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',b);x['geometry']=hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest()
  out[o.name]=x
 return out
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/beam-rust-197/scene.blend'));before=snap();m=material_snapshot();s=bpy.context.scene;render=[s.render.use_compositing,s.render.use_freestyle,s.camera.name,s.camera.data.lens]
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));after=snap();m2=material_snapshot();a=json.loads((O/'audit.json').read_text());primary={r['object']for r in a['native_damage']if not r['private_instance']};hosts=set(a['private_instance_hosts']);changed={}
for name,x in before.items():
 assert name in after,name
 fields=[k for k,v in x.items()if after[name][k]!=v]
 if fields:changed[name]=fields
 assert 'matrix'not in fields,name
 assert 'geometry'not in fields or name in primary,(name,fields)
 assert 'materials'not in fields or name in set(a['material_targets'])|primary,(name,fields)
 assert 'instance'not in fields or name in hosts,(name,fields)
assert all(m2[k]==v for k,v in m.items())
s=bpy.context.scene;assert render==[s.render.use_compositing,s.render.use_freestyle,s.camera.name,s.camera.data.lens]
p={'original_objects':len(before),'original_material_graphs':len(m),'changes':changed,'old_graph_changes':0,'non_target_geometry_changes':0,'all_original_transforms_unchanged':True,'render_and_camera_unchanged':True,'native_damage_panels':a['geometry_panels'],'new_objects':sorted(set(after)-set(before))};(O/'preservation.json').write_text(json.dumps(p,indent=2));print('198 PRESERVED',len(before),len(m),len(changed))
