"""Native visible perimeter ownership and remove ink physically hidden by new plinth."""
import bpy
from mathutils.bvhtree import BVHTree

def apply(scene):
 ob=bpy.data.objects['242 Single concrete footing for left service cluster']
 c=bpy.data.collections.new('242 Shared footing explicit native contours');c.use_fake_user=True;c.objects.link(ob)
 for layer in scene.view_layers:
  for ls in layer.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE' and ob.name not in ls.collection.objects:ls.collection.objects.link(ob)
 layer=scene.view_layers['215 Distant ink without atmospheric boundary'];src=scene.view_layers['ViewLayer'].freestyle_settings.linesets['Selective geometry contours']
 ls=layer.freestyle_settings.linesets.new('242 Service footing visible contour');ls.select_by_collection=True;ls.collection=c;ls.collection_negation='INCLUSIVE';ls.select_by_visibility=True;ls.visibility='VISIBLE';ls.select_by_edge_types=True
 for k in ('silhouette','border','crease','ridge_valley','suggestive_contour','material_boundary','contour','external_contour','edge_mark'):
  if hasattr(ls,'select_'+k):setattr(ls,'select_'+k,k in ('silhouette','border','external_contour','crease'))
 ls.edge_type_combination='OR';ls.linestyle=src.linestyle.copy();ls.linestyle.name='242 Footing foreground contour'
 bpy.context.view_layer.update();e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();me.calc_loop_triangles();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True);e.to_mesh_clear()
 origin=scene.camera.matrix_world.translation;counts={}
 for name in ('096 contacts ink','097 Broken soil ink'):
  gp=bpy.data.objects[name];count=0
  for lay in gp.data.layers:
   for f in lay.frames:
    for st in f.drawing.strokes:
     for p in st.points:
      w=gp.matrix_world@p.position;d=w-origin
      # Only native world points actually behind the footing surface are removed.
      hit=tree.ray_cast(origin,d.normalized(),d.length)
      if hit[0] is not None and hit[3]<d.length-.015 and p.opacity>0:p.opacity=0;count+=1
  counts[name]=count
 return {'hidden_native_GP_points':counts,'explicit_owner':layer.name,'width':ls.linestyle.thickness,'method':'Actual footing BVH occlusion of existing world-space ink; no screen painted patch'}
