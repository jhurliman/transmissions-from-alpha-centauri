"""Freeze reviewed190v2 geometry for exact replay onto a later unchanged colosseum."""
import bpy,json,sys,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-190'
def meshhash(me):
 a=array.array('f',[0.])*(len(me.vertices)*3);me.vertices.foreach_get('co',a);b=array.array('i',[0])*len(me.loops);me.loops.foreach_get('vertex_index',b);c=array.array('i',[0])*len(me.polygons);me.polygons.foreach_get('loop_total',c);return hashlib.sha256(a.tobytes()+b.tobytes()+c.tobytes()).hexdigest()
names=[r['object']for r in json.loads((O/'build-audit-v2.json').read_text())['changed_walls']]
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-188/scene.blend'));meta={}
for name in names:
 ob=bpy.data.objects[name];meta[name]={'source_hash':meshhash(ob.data),'matrix':[list(r)for r in ob.matrix_world],'source_materials':[sl.material.name if sl.material else None for sl in ob.material_slots]}
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate-v2.blend'));ids=set()
for name in names:
 ob=bpy.data.objects[name];meta[name].update({'candidate_hash':meshhash(ob.data),'mesh_name':ob.data.name,'archive_mesh':ob['190 source mesh'],'materials':[sl.material.name if sl.material else None for sl in ob.material_slots]});ids.add(ob.data);ids.add(bpy.data.meshes[ob['190 source mesh']])
bpy.data.libraries.write(str(O/'payload-v2.blend'),ids,fake_user=True);(O/'payload-v2.json').write_text(json.dumps(meta,indent=2));print('PAYLOAD190',len(names))
