import bpy,json,math,hashlib,array
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-121/upper'
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));C=bpy.data.collections['110 Coliseum detailed front ruin'];data={}
 for ob in bpy.context.scene.objects:
  if ob in C.objects.values() and ob.type=='MESH'and ob.get('bay')in[6,7,9,11,12]and ob.get('tier')==3 and ob.get('coliseum_role')=='wall':continue
  sig=[ob.type,tuple(round(x,7)for row in ob.matrix_world for x in row),ob.hide_render,ob.data.name if ob.data else None]
  if ob in C.objects.values() and ob.type=='MESH':
   ar=array.array('f',[0])*len(ob.data.vertices)*3;ob.data.vertices.foreach_get('co',ar);sig.append(hashlib.sha256(ar.tobytes()).hexdigest())
  data[ob.name]=sig
 return data
old=snapshot(R/'art/studies/coliseum-120/scene.blend');new=snapshot(O/'scene.blend');changed=[name for name,v in old.items()if new.get(name)!=v]
with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
a=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=a.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean
plan=json.loads((R/'art/studies/coliseum-119/assembly-feature-plan.json').read_text());audit=json.loads((O/'audit.json').read_text());regions=[]
for report in audit['bay_reports']:
 j=report['bay'];spec=next(x for x in plan['bays']if x['bay']==j);rr=[]
 for idx,(u0,u1,z0,z1)in enumerate(spec['fields_u0_u1_z0_z1']):
  ang=-math.pi+(j+.5)*math.tau/36+(u0+.3)/75;z=z1-.1;r=75*(1-.055*z/78);center=P@Vector((r*math.cos(ang),r*math.sin(ang),z));rr.append({'name':'bay%d field%d lintel edge'%(j,idx),'center':list(center),'radius':.55,'runoff_length':1.4})
 report['weathering_regions_original_world']=rr;regions+=rr
C=bpy.data.collections['110 Coliseum detailed front ruin'];feature=[]
for ob in C.objects:
 if ob.type!='MESH'or not(ob.name.startswith('COL121')or str(ob.get('damage_region','')).startswith('121')):continue
 mask=ob.data.attributes.get('118 Recess interior');feature.append({'object':ob.name,'original_position_attribute':ob.data.attributes.get('115 Original world position')is not None,'recess_faces':sum(d.value>.5 for d in mask.data)if mask else 0})
audit['weathering_regions_original_world']=regions;audit['preservation']={'protected_object_count':len(old),'protected_changes':changed,'new_object_count':len([n for n in new if n not in old]),'method':'All nonlandmark objects plus existing coliseum objects except selected upperwall meshes: world transforms, visibility, data identity; coliseum protected vertex arrays also hashed.'};audit['feature_masks']=feature;(O/'audit.json').write_text(json.dumps(audit,indent=2));print('PROTECTED',len(old),'CHANGES',changed,'REGIONS',len(regions),'RECESSFACES',sum(x['recess_faces']for x in feature))
