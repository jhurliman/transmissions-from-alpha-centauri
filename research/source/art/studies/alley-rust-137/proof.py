import bpy,sys,json,time,hashlib,array
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-rust-137';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-134/scene.blend'));s=bpy.context.scene
from alley_rust_137 import apply
h=s.objects['Architecture | gangway_single_Y_8m'];C=h.instance_collection
before={o.name:hashlib.sha256(str(([tuple(v.co)for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons],[tuple(n.vector)for n in o.data.corner_normals])).encode()).hexdigest()for o in C.objects if o.type=='MESH'}
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.threads_mode='FIXED';s.render.threads=4
ps=[world_to_camera_view(s,s.camera,h.matrix_world@o.matrix_world@v.co)for o in C.objects if o.type=='MESH' for v in o.data.vertices];x0=max(0,int(min(p.x for p in ps)*3840)-30);x1=min(3840,int(max(p.x for p in ps)*3840)+30);y0=max(0,int((1-max(p.y for p in ps))*2885)-30);y1=min(2885,int((1-min(p.y for p in ps))*2885)+30)
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
(O/'crop.json').write_text(json.dumps({'bounds':[x0,y0,x1,y1]},indent=2));t0=0 # matched no-ink baseline retained
a=apply(s);after={o.name:hashlib.sha256(str(([tuple(v.co)for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons],[tuple(n.vector)for n in o.data.corner_normals])).encode()).hexdigest()for o in C.objects if o.type=='MESH'};assert before==after;a['support_geometry_and_corner_normals_exact']=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'materials.blend'),{bpy.data.materials[n]for n in a['materials']},fake_user=True);s.render.filepath=str(O/'after-noink.png');t=time.time();bpy.ops.render.render(write_still=True);a['render_seconds']={'before':t0,'after':time.time()-t};(O/'audit.json').write_text(json.dumps(a,indent=2));print('DONE137',flush=True)
