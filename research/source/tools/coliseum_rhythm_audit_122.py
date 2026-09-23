import bpy,json,math,hashlib,array
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-122/rhythm'
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));C=bpy.data.collections['110 Coliseum detailed front ruin'];data={}
 for ob in bpy.context.scene.objects:
  if ob in C.objects.values() and ob.type=='MESH'and ob.name in ['COL110 U%d sill wall'%k for k in range(5,14)]:continue
  sig=[ob.type,tuple(round(x,7)for row in ob.matrix_world for x in row),ob.hide_render,ob.data.name if ob.data else None]
  if ob in C.objects.values() and ob.type=='MESH':
   ar=array.array('f',[0])*len(ob.data.vertices)*3;ob.data.vertices.foreach_get('co',ar);sig.append(hashlib.sha256(ar.tobytes()).hexdigest())
  data[ob.name]=sig
 return data
old=snapshot(R/'art/studies/coliseum-121/scene.blend');new=snapshot(O/'scene.blend');changed=[name for name,v in old.items()if new.get(name)!=v]

a=json.loads((O/'audit.json').read_text());a['reference_ids']=['UCL-08','UCL-01','UCL-03'];a['preservation']={'protected_objects':len(old),'protected_changes':changed,'new_objects':len([k for k in new if k not in old])};a['depth_shading_tags']={'122 Drain interior':'FACE float on new recessed tunnel interior, separate from shallow panel masks','122 cavity depth authored':1.4,'column_lower_projection':.72,'column_upper_projection':'.18 existing field jambs; .39 bay8; .23 new bays5/10/13 upper bodies'};(O/'audit.json').write_text(json.dumps(a,indent=2));print('PROTECTED',len(old),'CHANGES',changed)
