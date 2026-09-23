"""148-only exposed cornice color proof; immutable older core materials."""
import bpy,hashlib
NAMES=['COL110 T1 band07 profile'+str(i)for i in [1,2,3]]
COLORS=[(.062,.041,.058,1),(.089,.052,.069,1),(.159,.089,.073,1),(.217,.130,.092,1)]
def apply(C):
 out=[];copies={}
 for name in NAMES:
  ob=C.objects[name];me=ob.data;mask=me.attributes['148 Cornice fracture'];faces=[f for f in me.polygons if mask.data[f.index].value>.5];slots={f.material_index for f in faces};changes=[]
  for slot in slots:
   source=me.materials[slot]
   if not source.name.startswith('117 Exposed masonry core'):raise RuntimeError('Unexpected existing core '+source.name)
   if source.name not in copies:
    ma=source.copy();ma.name='148 Local warm-violet cornice core';r=ma.node_tree.nodes['Color Ramp'].color_ramp
    if len(r.elements)!=4:raise RuntimeError('Core ramp changed')
    for e,c in zip(r.elements,COLORS):e.color=c
    copies[source.name]=ma
   ma=copies[source.name];me.materials.append(ma);new=len(me.materials)-1
   for f in faces:
    if f.material_index==slot:f.material_index=new
   changes.append({'old_material':source.name,'new_material':ma.name,'face_count':sum(f.material_index==new for f in faces)})
  out.append({'object':name,'assignments':changes,'geometry_modified':False})
 return {'targets':out,'changed_fields':'Only local cutface materialindices and one cloned color ramp','ramp_linear_rgba':COLORS,'older_damage_materials_unchanged':True}
