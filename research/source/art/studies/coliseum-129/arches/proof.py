import bpy,sys,math,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from coliseum_arch_thickness_129 import apply,params,closest;from coliseum_arch_ratio_125 import mapping;from coliseum_b10_prepared_128 import apply as repair
O=R/'art/studies/coliseum-129/arches';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-128/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];repair(C);bpy.ops.wm.save_as_mainfile(filepath=str(O/'baseline.blend'));_,_,unpack=mapping();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();outer={};crown={}
for ob in C.objects:
 if ob.type!='MESH'or'archivolt'not in ob.name:continue
 t,b=int(ob['tier']),int(ob['bay']);rx,rz,sp=params(t,b);ac=-math.pi+(b+.5)*math.tau/36;ev=ob.evaluated_get(dg)
 for v in ob.data.vertices:
  rr,a,z=unpack(ob.matrix_world@v.co);u=(a-ac)*75;d,nx,ny=closest(u,z-sp,rx,rz)
  if abs(d-.83)<.002:outer[(ob.name,v.index)]=(ob.matrix_world@v.co,ev.matrix_world@ev.data.vertices[v.index].co)
 if t==2 and b==8 and 'stone06'in ob.name:
  vv=[]
  for v in ob.data.vertices:
   rr,a,z=unpack(ob.matrix_world@v.co);u=(a-ac)*75;d,nx,ny=closest(u,z-sp,rx,rz);vv.append((rr,z,d,v.index))
  i=9 if 'archivolt0' in ob.name else 13;crown[ob.name]=(i,ev.matrix_world@ev.data.vertices[i].co)
a=apply(C);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();raw=0.;evaluated=0.
for (name,i),(p,q)in outer.items():
 ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);raw=max(raw,(ob.matrix_world@ob.data.vertices[i].co-p).length);evaluated=max(evaluated,(ev.matrix_world@ev.data.vertices[i].co-q).length)
def pixel(p):
 q=world_to_camera_view(bpy.context.scene,bpy.context.scene.camera,p);return(q.x*3840,q.y*2885)
oldp=[];newp=[]
for name,(i,p)in sorted(crown.items()):
 ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);oldp.append(pixel(p));newp.append(pixel(ev.matrix_world@ev.data.vertices[i].co))
a['outer_profile_audit']={'vertices':len(outer),'raw_world_max_delta':raw,'evaluated_group_max_delta':evaluated};a['crown_pixels']={'before':math.dist(*oldp),'after':math.dist(*newp),'before_points':oldp,'after_points':newp};(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print('PROOF',a['outer_profile_audit'],a['crown_pixels'],flush=True)
for label,path in [('before',O/'baseline.blend'),('after',O/'geometry.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.use_freestyle=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.43;s.render.border_max_x=.53;s.render.border_min_y=.69;s.render.border_max_y=.80;s.render.filepath=str(O/(label+'-main4k.png'));bpy.ops.render.render(write_still=True)
 s.render.resolution_x=7680;s.render.resolution_y=5770;s.render.filepath=str(O/(label+'-painted-close.png'));bpy.ops.render.render(write_still=True)
 s.render.engine='BLENDER_WORKBENCH';s.render.use_compositing=False;s.render.use_freestyle=False;s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.5,.5,.5);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;keep=set(bpy.data.collections['110 Coliseum detailed front ruin'].objects)
 for ob in s.objects:
  if ob.type not in ['LIGHT','CAMERA']and ob not in keep:ob.hide_render=True
 s.render.filepath=str(O/(label+'-clay.png'));bpy.ops.render.render(write_still=True)
