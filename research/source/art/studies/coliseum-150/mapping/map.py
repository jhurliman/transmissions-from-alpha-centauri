import bpy,sys,json
from pathlib import Path
from mathutils import Vector,geometry
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-150/mapping'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-149/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.type=='MESH' and ('volume' in ob.name.lower() or ob.hide_render):ob.hide_set(True)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;inv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;cache={};rows=[]
for region,xs in [('primary',[1695,1705,1715,1725,1735]),('secondary',[2090,2100,2110,2120,2130])]:
 for y in [555,565,575,585,595,605,620,645,670,695,720,745,760]:
  for x in xs:
   q=inv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;direction=(cam.matrix_world@q.to_3d()-origin).normalized();ok,hit,normal,fi,obj,mat=s.ray_cast(dg,origin,direction)
   if not ok:continue
   if obj.name not in cache:
    me=bpy.data.meshes.new_from_object(obj.evaluated_get(dg),depsgraph=dg);me.calc_loop_triangles();cache[obj.name]=me
   me=cache[obj.name];attr=me.attributes.get('115 Original world position');original=None
   if attr and fi>=0:
    p=obj.matrix_world.inverted()@hit;ts=[t for t in me.loop_triangles if t.polygon_index==fi]
    t=min(ts,key=lambda t:(geometry.closest_point_on_tri(p,*[me.vertices[i].co for i in t.vertices])-p).length_squared)
    original=list(geometry.barycentric_transform(p,*[me.vertices[i].co for i in t.vertices],*[attr.data[i].vector for i in t.vertices]))
   rows.append({'region':region,'pixel':[x,y],'object':obj.name,'world':list(hit),'normal':list(normal),'original_world':original,'face':fi})
(O/'surface-rays.json').write_text(json.dumps(rows,indent=2));print('OBJECTS',sorted(set(r['object']for r in rows)))
