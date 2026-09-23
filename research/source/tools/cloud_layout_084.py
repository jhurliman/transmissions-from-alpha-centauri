import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/cloud-084';ASSETS=R/'art/studies/cloud-082/assets'
def apply_flat(s):
 for c in list(bpy.data.collections):
  if c.name.startswith(('080 Cloud','082 Native cloud','082 Derived')):
   for o in c.all_objects:o.hide_render=True
 s.world=s.world.copy()
 for n in s.world.node_tree.nodes:
  if n.label=='075 Cloud oxide red':
   for l in list(n.inputs[0].links):s.world.node_tree.links.remove(l)
   n.inputs[0].default_value=0
 C=bpy.data.collections.new('082 Derived flat clouds');s.collection.children.link(C)
 cam=s.camera;frame=cam.data.view_frame(scene=s);xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame)
 placements=[['arch', 570, 41, 440, 850], ['shoulder', 923, 8, 455, 880], ['shoulder', 530, 126, 350, 845], ['arch', 783, 128, 355, 855], ['wisp2', 691, 89, 250, 830], ['shoulder', 992, 170, 295, 865], ['wisp', 575, 191, 190, 840], ['wisp2', 810, 208, 235, 835]]
 for i,(family,px,py,pw,d) in enumerate(placements):
  img=bpy.data.images.load(str(ASSETS/f'{family}-pigment.png'),check_existing=True);img.pack();asp=img.size[1]/img.size[0];ph=pw*asp
  coords=[]
  for u,v in [(px-pw/2,py+ph/2),(px+pw/2,py+ph/2),(px+pw/2,py-ph/2),(px-pw/2,py-ph/2)]:
   p=Vector(((xmin+(xmax-xmin)*u/1440)*d,(ymax-(ymax-ymin)*v/1082)*d,-d));coords.append(cam.matrix_world@p)
  me=bpy.data.meshes.new('082 Native-derived cloud plate');me.from_pydata(coords,[],[(0,1,2,3)]);uv=me.uv_layers.new()
  for k,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[k].uv=p
  ob=bpy.data.objects.new(f'082 {family} authored bank {i}',me);C.objects.link(ob);ob.visible_shadow=False
  m=bpy.data.materials.new(f'082 {family} native-derived pigment');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img;tex.interpolation='Linear';em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs['Color'],em.inputs[0]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');ray=nt.nodes.new('ShaderNodeLightPath');mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(tex.outputs['Alpha'],mul.inputs[0]);nt.links.new(ray.outputs['Is Camera Ray'],mul.inputs[1]);nt.links.new(mul.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);me.materials.append(m)
 for ls in s.view_layers[0].freestyle_settings.linesets:
  if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE' and C.name not in ls.collection.children:ls.collection.children.link(C)
 return C
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-081/selected-scene.blend'));s=bpy.context.scene;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;C=apply_flat(s);s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
 for ob in s.objects:
  if ob.type!='CAMERA' and ob.name not in C.objects:ob.hide_render=True
 s.render.use_freestyle=False;s.render.filepath=str(O/'composed-sky.png');bpy.ops.render.render(write_still=True)
