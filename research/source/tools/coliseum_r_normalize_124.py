"""Normalize repaired123 R crown tessellation by canceling exact reversed triangle pairs.
No positional change, remesh, epsilon welding, or blind hole fill.
"""
import bpy,bmesh,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-124/repair';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import topology
NAME='COL110 U8 fractured upper wall R'
def apply(C):
 ob=bpy.data.objects[NAME];old=ob.data;before=topology(ob);old.calc_loop_triangles();tris=list(old.loop_triangles);groups={}
 for i,t in enumerate(tris):groups.setdefault(tuple(sorted(t.vertices)),[]).append(i)
 remove=set();pairs=[]
 for vertices,ids in groups.items():
  if len(ids)!=2:continue
  a,b=[tris[i]for i in ids]
  if a.normal.dot(b.normal)>-.9999:continue
  remove.update(ids);pairs.append({'vertex_ids':vertices,'triangle_ids':ids,'source_faces':[a.polygon_index,b.polygon_index],'area_local_m2':a.area})
 keep=[t for i,t in enumerate(tris)if i not in remove];me=bpy.data.meshes.new('124 normalized repaired R');me.from_pydata([v.co.copy()for v in old.vertices],[],[tuple(t.vertices)for t in keep]);me.update()
 for mat in old.materials:me.materials.append(mat)
 for f,t in zip(me.polygons,keep):f.material_index=old.polygons[t.polygon_index].material_index
 for attr in old.attributes:
  if attr.name not in ['115 Original world position','117 Damage proximity','117 Exposed core','118 Recess interior']:continue
  a=me.attributes.new(attr.name,attr.data_type,attr.domain)
  for i,d in enumerate(a.data):
   src=attr.data[i if attr.domain=='POINT'else keep[i].polygon_index]
   if attr.data_type=='FLOAT_VECTOR':d.vector=src.vector
   else:d.value=src.value
 ob.data=me;after=topology(ob)
 if after['strict_crossings']or after['nonmanifold']or after['volume']<=0:ob.data=old;raise RuntimeError('Normalization rejected '+json.dumps(after))
 # Volume of exact rendered source triangles, using stable BMesh centered coordinates.
 tm=bpy.data.meshes.new('124 volume source');tm.from_pydata([v.co.copy()for v in old.vertices],[],[tuple(t.vertices)for t in tris]);tm.update();bm=bmesh.new();bm.from_mesh(tm);rendered_volume=bm.calc_volume();bm.free();bpy.data.meshes.remove(tm)
 if abs(after['volume']-rendered_volume)>1e-6:ob.data=old;raise RuntimeError('Unexpected rendered volume change')
 ob['124 duplicate sheet cancellation']=len(pairs)
 return {'object':NAME,'before_polygon':before,'before_rendered_volume':rendered_volume,'after':after,'removed_opposite_triangle_pairs':pairs,'vertex_position_delta_m':0.,'rendered_volume_delta':after['volume']-rendered_volume,'original_polygon_volume_is_not_rendered_volume':True}
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-123/repair/geometry.blend'));d=apply(bpy.data.collections['110 Coliseum detailed front ruin']);O.mkdir(parents=True,exist_ok=True);(O/'normalization-audit.json').write_text(json.dumps(d,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'normalized.blend'));print(json.dumps(d))
