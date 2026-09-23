"""Narrow actual native pyramid bases; keep apex height and suppress ground ornament ink."""
import bpy
from mathutils import Vector

def apply(scene):
 dg=bpy.context.evaluated_depsgraph_get();rows=[];removed=[]
 for o in list(bpy.data.objects):
  role=o.get('231 ornament')
  if role=='upper sill pyramid':
   e=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(e,preserve_all_data_layers=True,depsgraph=dg);assert len(me.vertices)==5
   M=o.matrix_world.copy();iv=M.inverted();ps=[M@v.co for v in me.vertices];center=sum(ps[:4],Vector())/4;apex=ps[4].copy()
   for i in range(4):me.vertices[i].co=iv@(center+(ps[i]-center)*(2/3))
   attr=me.attributes.get('115 Original world position')
   if attr:
    c=sum((d.vector for d in list(attr.data)[:4]),Vector())/4
    for i in range(4):attr.data[i].vector=c+(attr.data[i].vector-c)*(2/3)
   o.data=me;o.modifiers.clear();o['232 base scale']=2/3
   now=[M@v.co for v in me.vertices];assert (now[4]-apex).length<1e-5;assert (sum(now[:4],Vector())/4-center).length<1e-4
   rows.append({'object':o.name,'base_linear_scale':2/3,'base_area_scale':4/9,'apex_world_delta_m':(now[4]-apex).length,'height_preserved':True,'native_editable_evaluated_geometry':True})
  elif role=='reveal-through impost' and o.get('tier')==0:
   for vl in scene.view_layers:
    for ls in vl.freestyle_settings.linesets:
     if ls.select_by_collection and ls.collection and ls.collection_negation=='INCLUSIVE' and o.name in ls.collection.objects:ls.collection.objects.unlink(o);removed.append({'object':o.name,'style':ls.name})
 assert len(rows)==36;assert len({r['object'] for r in removed})==36
 return {'pyramids':rows,'ground_ornament_ink_removed':removed,'ground_ornament_geometry_retained':True}
