import bpy,sys,json
from pathlib import Path
from mathutils import Vector,geometry
from bpy_extras.object_utils import world_to_camera_view
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-151/mapping'
from coliseum_arch_ratio_125 import mapping
from coliseum_crown_repair_123 import topology
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-149/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.type=='MESH'and('volume'in ob.name.lower()or ob.hide_render):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;inv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;cache={};rows=[];_,_,unpack=mapping()
for y in range(470,576,7):
 for x in range(1440,1621,8):
  q=inv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;direction=(cam.matrix_world@q.to_3d()-origin).normalized();ok,hit,normal,fi,obj,mat=s.ray_cast(dg,origin,direction)
  if not ok or not obj.name.startswith('COL'):continue
  if obj.name not in cache:
   me=bpy.data.meshes.new_from_object(obj.evaluated_get(dg),depsgraph=dg);me.calc_loop_triangles();cache[obj.name]=me
  me=cache[obj.name];attr=me.attributes.get('115 Original world position');original=None
  if attr and fi>=0:
   p=obj.matrix_world.inverted()@hit;ts=[t for t in me.loop_triangles if t.polygon_index==fi];t=min(ts,key=lambda t:(geometry.closest_point_on_tri(p,*[me.vertices[i].co for i in t.vertices])-p).length_squared);original=list(geometry.barycentric_transform(p,*[me.vertices[i].co for i in t.vertices],*[attr.data[i].vector for i in t.vertices]))
  rows.append({'pixel':[x,y],'object':obj.name,'world':list(hit),'authored':list(unpack(hit)),'normal':list(normal),'original_world':original,'face':fi})
audit=[]
for name,me in cache.items():
 if 'upper wall'not in name:continue
 ob=bpy.data.objects[name];tmp=bpy.data.objects.new('151 inspection',me);tmp.matrix_world=ob.matrix_world;vv=[list(unpack(ob.matrix_world@v.co))for v in me.vertices];px=[world_to_camera_view(s,cam,ob.matrix_world@v.co)for v in me.vertices];audit.append({'name':name,'topology':topology(tmp),'verts_authored':vv,'triangles':[list(t.vertices)for t in me.loop_triangles],'attrs':[(a.name,a.domain,a.data_type)for a in me.attributes],'camera_box':[min(p.x for p in px)*3840,min(1-p.y for p in px)*2885,max(p.x for p in px)*3840,max(1-p.y for p in px)*2885]});bpy.data.objects.remove(tmp)
(O/'surface-rays.json').write_text(json.dumps(rows,indent=2));(O/'native-source.json').write_text(json.dumps(audit));print([(a['name'],a['topology'],a['camera_box'])for a in audit])
