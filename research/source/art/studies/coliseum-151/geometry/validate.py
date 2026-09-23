import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from coliseum_arch_ratio_125 import mapping
O=R/'art/studies/coliseum-151/geometry';bpy.ops.wm.open_mainfile(filepath=str(O/'study.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.type=='MESH'and('volume'in ob.name.lower()or ob.hide_render):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;inv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();org=cam.matrix_world.translation;_,_,unpack=mapping();names=['COL110 U4 fractured upper wall R','COL110 U5 fractured upper wall L'];pixels=[];allupper=[];raw=[]
for n in names:
 ob=bpy.data.objects[n];me=ob.data;raw.append({'target':n,'zero_area_faces_below_1e-12':sum(p.area<1e-12 for p in me.polygons),'smallest_face_area':min(p.area for p in me.polygons)})
for y in range(470,560):
 for x in range(1470,1590):
  q=inv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-org).normalized();ok,p,n,fi,ob,m=s.ray_cast(dg,org,di)
  if ok and ob.name in names:
   r,a,z=unpack(p)
   if z>67.8:allupper.append([x,y])
   if z>67.8 and r<74.6:pixels.append([x,y])
box=lambda pp:[min(x for x,y in pp),min(y for x,y in pp),max(x for x,y in pp)+1,max(y for x,y in pp)+1]if pp else None
out={'native_visible_return_definition':'Actual locked-camera rays hit either target above authored67.8 and more than0.4m behind nominal75m front radial plane. Transparent atmosphere excluded for ray traversal only.','visible_return_bbox':box(pixels),'visible_return_pixel_count':len(pixels),'all_upper_target_bbox':box(allupper),'visible_return_pixels':pixels,'target_face_checks':raw};(O/'projected-audit.json').write_text(json.dumps(out));print('VISIBLE',box(pixels),len(pixels),raw)
