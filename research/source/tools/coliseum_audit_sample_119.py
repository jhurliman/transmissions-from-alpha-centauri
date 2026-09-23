import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-119'
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));C=bpy.data.collections['110 Coliseum detailed front ruin'];members=set(C.objects);result={}
 for o in bpy.context.scene.objects:
  if o in members:continue
  result[o.name]=(o.type,tuple(round(v,7)for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None)
 return result
old=snap(R/'art/studies/coliseum-116/scene.blend');new=snap(O/'geometry.blend');changes=[k for k,v in old.items()if new.get(k)!=v];added=[k for k in new if k not in old];C=bpy.data.collections['110 Coliseum detailed front ruin'];features=[]
for ob in C.objects:
 if ob.type!='MESH'or not(ob.name.startswith('COL119')or str(ob.get('damage_region','')).startswith('119')or ob.get('feature')=='clean closed upperwall with inherited crown'):continue
 core=ob.data.attributes.get('117 Exposed core');features.append({'object':ob.name,'role':ob.get('coliseum_role'),'bay':ob.get('bay'),'feature':ob.get('feature'),'damage_region':ob.get('damage_region'),'original_position_attribute':ob.data.attributes.get('115 Original world position')is not None,'damage_proximity_attribute':ob.data.attributes.get('117 Damage proximity')is not None,'recess_faces':sum(d.value>.5 for d in ob.data.attributes.get('118 Recess interior').data)if ob.data.attributes.get('118 Recess interior')else 0,'exposed_core_faces':sum(d.value>.5 for d in core.data)if core else 0})
a={'nonlandmark_objects_compared':len(old),'nonlandmark_state_changes':changes,'unexpected_nonlandmark_objects':added,'modified_sample_objects':features,'native_geometry_source':'art/studies/coliseum-119/geometry.blend','isolated_proof':'art/studies/coliseum-119/geometry-proof.blend','proof_images':['sample-clay.png','sample-painted.png'],'main_preview_limitation':'main-geometry.png retains Freestyle and hides stale landmark contact ink. Parent will regenerate landmark contact ink.','crown_preservation':'No source wall regenerated. All cuts below source crown; accepted cuts verify unchanged surfaces outside cutter bounds.','acceptance':'Representative sample only; material integration and independent critique pending; no whole-ring distribution.'};(O/'geometry-handoff.json').write_text(json.dumps(a,indent=2));print('PRESERVATION',len(old),len(changes),len(added),'FEATURES',len(features),'CORE_FACES',sum(r['exposed_core_faces']for r in features))
