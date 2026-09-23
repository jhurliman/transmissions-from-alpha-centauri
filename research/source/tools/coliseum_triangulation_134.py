"""Conservative pre-layout triangulation for two proven tessellation defects.
No coordinates changed; preserve parent-face attributes/materials and restore per-corner normals.
"""
import bpy,bmesh,types
from coliseum_crown_repair_123 import strict_crossings
NAMES=('COL110 U12 fractured upper wall R','COL127 T2 continuous arcade wall')
def _evaluated_crossings(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 try:return strict_crossings(types.SimpleNamespace(data=me,matrix_world=ev.matrix_world))
 finally:ev.to_mesh_clear()
def apply(C):
 rows=[]
 for name in NAMES:
  ob=next(o for o in C.all_objects if o.name==name and not o.library)
  if ob.get('134 safe prelayout triangulation'):raise RuntimeError('Use fresh untriangulated source: '+name)
  old=ob.data;before=_evaluated_crossings(ob);coords=[tuple(v.co)for v in old.vertices];normals={(p.index,old.loops[i].vertex_index):tuple(old.corner_normals[i].vector)for p in old.polygons for i in p.loop_indices};mats=[p.material_index for p in old.polygons]
  new=old.copy();new.name='134 stable pre-layout '+old.name;tag=new.attributes.new('134 temporary original polygon','INT','FACE')
  for i,v in enumerate(tag.data):v.value=i
  bm=bmesh.new();bm.from_mesh(new);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bm.to_mesh(new);bm.free();new.update();parents=[v.value for v in new.attributes['134 temporary original polygon'].data]
  if [tuple(v.co)for v in new.vertices]!=coords:raise RuntimeError('Unexpected vertex change '+name)
  if any(p.material_index!=mats[parents[p.index]]for p in new.polygons):raise RuntimeError('Material inheritance failed '+name)
  restore=[normals[(parents[p.index],new.loops[i].vertex_index)]for p in new.polygons for i in p.loop_indices];new.normals_split_custom_set(restore);normal_error=max((max(abs(a-b)for a,b in zip(n.vector,ref))for n,ref in zip(new.corner_normals,restore)),default=0.)
  attr_errors=[];checked=[];unsupported=[]
  fields={'FLOAT':'value','INT':'value','BOOLEAN':'value','FLOAT_VECTOR':'vector','FLOAT_COLOR':'color','BYTE_COLOR':'color','FLOAT2':'vector'}
  old_loop={(p.index,old.loops[i].vertex_index):i for p in old.polygons for i in p.loop_indices}
  old_edge={tuple(sorted(e.vertices)):e.index for e in old.edges}
  def value(d,k):
   v=getattr(d,k)
   try:return tuple(v)
   except TypeError:return v
  for at in old.attributes:
   if at.name in ('.corner_edge','material_index'):continue # Topology indices remap; polygon materials checked above.
   field=fields.get(at.data_type)
   if not field:unsupported.append([at.name,at.data_type]);continue
   target=new.attributes.get(at.name)
   if target is None:attr_errors.append([at.name,'missing']);continue
   if at.domain=='POINT':pairs=[(i,i)for i in range(len(new.vertices))]
   elif at.domain=='FACE':pairs=[(i,parent)for i,parent in enumerate(parents)]
   elif at.domain=='CORNER':pairs=[(i,old_loop[(parents[p.index],new.loops[i].vertex_index)])for p in new.polygons for i in p.loop_indices]
   elif at.domain=='EDGE':pairs=[(e.index,old_edge[tuple(sorted(e.vertices))])for e in new.edges if tuple(sorted(e.vertices))in old_edge]
   else:unsupported.append([at.name,at.domain]);continue
   if at.name.startswith('.select'):
    for i,j in pairs:setattr(target.data[i],field,value(at.data[j],field))
   errors=sum(value(target.data[i],field)!=value(at.data[j],field)for i,j in pairs)
   if errors:attr_errors.append([at.name,errors])
   checked.append(at.name)
  if attr_errors:raise RuntimeError('Attribute preservation failed '+str((name,attr_errors)))
  new.attributes.remove(new.attributes['134 temporary original polygon']);ob.data=new;bpy.context.view_layer.update();after=_evaluated_crossings(ob);bm=bmesh.new();bm.from_mesh(new);bad=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free()
  if after or bad or zero:
   ob.data=old;bpy.data.meshes.remove(new);bpy.context.view_layer.update();raise RuntimeError('Triangulation rejected '+str((name,after,bad,zero)))
  ob['134 safe prelayout triangulation']=True;rows.append({'object':name,'before_evaluated_crossings':before,'after_evaluated_crossings':after,'nonmanifold_edges':bad,'zero_area_faces':zero,'vertices_bit_exact':True,'material_indices_inherited':True,'parent_face_attributes_preserved':'BMesh native custom-data propagation','point_attributes_preserved':True,'attributes_checked_exact':checked,'unsupported_attribute_types':unsupported,'per_corner_normals_restored':True,'max_normal_component_roundtrip_error':normal_error,'faces_before':len(old.polygons),'faces_after':len(new.polygons)})
 return {'objects':rows,'method':'BEAUTY triangulation before existing127 GeometryNodes; vertex coordinates fixed; original parent-face/vertex normal mapping restored','other_objects_changed':False,'limitations':'Normal custom-data encoding roundtrip error reported; no all-landmark certificate.'}
