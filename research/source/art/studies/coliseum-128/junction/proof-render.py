import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();O=R/'art/studies/coliseum-128/junction';sys.path.insert(0,str(R/'tools'));from coliseum_arch_ratio_125 import mapping
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));_,world,unpack=mapping();s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];wall=C.objects['COL127 T2 continuous arcade wall'];p=world(75,-math.pi+7.5*math.tau/36-2.5/75,55.9);probe=wall.copy();me=bpy.data.meshes.new('probe');me.from_pydata([p],[],[]);probe.data=me;C.objects.link(probe);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=probe.evaluated_get(dg);mm=ev.to_mesh();target=ev.matrix_world@mm.vertices[0].co;ev.to_mesh_clear();bpy.data.objects.remove(probe,do_unlink=True)
cam=s.camera.copy();cam.data=cam.data.copy();s.collection.objects.link(cam);cam.name='128 Junction proof camera';cam.data.type='ORTHO';cam.data.ortho_scale=10.8;forward=cam.matrix_world.to_quaternion()@Vector((0,0,-1));cam.location=target-forward*75;s.camera=cam
for ob in bpy.data.objects:
 if ob.type=='GREASEPENCIL':ob.hide_render=True
s.render.use_freestyle=False;s.render.use_border=False;s.render.resolution_x=1280;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(O/'close-painted.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'));bpy.ops.render.render(write_still=True)
m=bpy.data.materials.new('128 neutral clay');m.diffuse_color=(.45,.45,.45,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.45,.45,.45,1);bs.inputs['Roughness'].default_value=.85
for ob in C.objects:
 if ob.type=='MESH':
  for slot in ob.material_slots:slot.link='OBJECT';slot.material=m
s.render.filepath=str(O/'close-clay.png');bpy.ops.render.render(write_still=True)
