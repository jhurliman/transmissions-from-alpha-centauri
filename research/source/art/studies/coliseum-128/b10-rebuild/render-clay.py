import bpy,sys,math,json
from pathlib import Path
from mathutils import Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from coliseum_arch_ratio_125 import mapping
O=R/'art/studies/coliseum-128/b10-rebuild'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-127/scene.blend'));s=bpy.context.scene;_,_,unpack=mapping();ob=bpy.data.objects['COL127 T2 continuous arcade wall'];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());ac=-math.pi+10.5*math.tau/36;pts=[]
for v in ob.data.vertices:
 rr,a,z=unpack(ob.matrix_world@v.co)
 if abs(a-ac)<.09 and z>49:pts.append(world_to_camera_view(s,s.camera,ev.matrix_world@ev.data.vertices[v.index].co))
x0=max(0,min(p.x for p in pts)-.009);x1=min(1,max(p.x for p in pts)+.009);y0=max(0,min(p.y for p in pts)-.013);y1=min(1,max(p.y for p in pts)+.013);(O/'camera.json').write_text(json.dumps([x0,x1,y0,y1]))
for label,path in [('before',R/'art/studies/coliseum-127/scene.blend'),('after',O/'prepared.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0;s.render.border_max_x=x1;s.render.border_min_y=y0;s.render.border_max_y=y1;s.render.use_freestyle=False;s.render.filepath=str(O/(label+'-main4k.png'))
 s.render.resolution_x=7680;s.render.resolution_y=5770;s.render.filepath=str(O/(label+'-painted-close.png'))
 m=bpy.data.materials.new('128 neutral repair clay');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.45,.45,.45,1);b.inputs['Roughness'].default_value=.9
 for ob in s.objects:
  if ob.type=='MESH' and ob.name.startswith(('COL','127','126')):
   for slot in ob.material_slots:slot.material=m
 s.view_layers[0].material_override=m;s.use_nodes=False
 for ob in s.objects:
  if ob.type=='LIGHT':ob.hide_render=True
 light=bpy.data.lights.new('128 clay raking light','SUN');light.energy=2.2;sun=bpy.data.objects.new('128 clay raking light',light);s.collection.objects.link(sun);sun.matrix_world=s.camera.matrix_world@Matrix.Rotation(math.radians(35),4,'Y')
 s.world=bpy.data.worlds.new('128 neutral clay world');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.15,.15,.15,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.3
 
 keep=set(bpy.data.collections['110 Coliseum detailed front ruin'].objects)
 for ob in s.objects:
  if ob.type not in ['LIGHT','CAMERA']and ob not in keep:ob.hide_render=True
 s.render.use_compositing=False;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.5,.5,.5);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.render.filepath=str(O/(label+'-clay-close.png'));bpy.ops.render.render(write_still=True)
