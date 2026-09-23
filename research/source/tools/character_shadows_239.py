"""Selected sprites remain unchanged; alpha billboards cast native Eevee shadows only."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def apply(scene):
 C=bpy.data.collections.new('239 Character shadow casters');scene.collection.children.link(C)
 cam=scene.camera;f=cam.data.view_frame(scene=scene);xmin=min(v.x for v in f);xmax=max(v.x for v in f);ymin=min(v.y for v in f);ymax=max(v.y for v in f);z=f[0].z
 def ray(px,py):return (cam.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*px/3840,ymax-(ymax-ymin)*py/2885,z))).normalized()
 dg=bpy.context.evaluated_depsgraph_get();soil=bpy.data.objects['Street foundation'];ev=soil.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();bvh=BVHTree.FromPolygons([soil.matrix_world@v.co for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear();origin=cam.matrix_world.translation;rows=[]
 for row in json.loads((R/'art/studies/pixel-characters-217/assets.json').read_text()):
  x0,y0,x1,y1=row['body_bbox'];foot=bvh.ray_cast(origin,ray((x0+x1)/2,y1),100)[0];assert foot is not None
  # Include original sprite's one-pixel transparent border.
  bounds=(x0-5,y0-6,x1+5,y1+6);corners=[]
  for px,py in [(bounds[0],bounds[3]),(bounds[2],bounds[3]),(bounds[2],bounds[1]),(bounds[0],bounds[1])]:
   d=ray(px,py);corners.append(origin+d*((foot.y-origin.y)/d.y))
  mesh=bpy.data.meshes.new('239 '+row['name']+' shadow silhouette');mesh.from_pydata(corners,[],[(0,1,2,3)]);uv=mesh.uv_layers.new(name='Sprite')
  for loop,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
  ob=bpy.data.objects.new(mesh.name,mesh);C.objects.link(ob)
  m=bpy.data.materials.new(mesh.name);m.use_nodes=True;m.surface_render_method='DITHERED';n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');trans=n.new('ShaderNodeBsdfTransparent');diff=n.new('ShaderNodeBsdfDiffuse');path=n.new('ShaderNodeLightPath');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/row['source_sprite']),check_existing=True);tex.image.pack();tex.interpolation='Closest';mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(path.outputs['Is Shadow Ray'],mul.inputs[0]);l.new(tex.outputs['Alpha'],mul.inputs[1]);l.new(mul.outputs[0],mix.inputs[0]);l.new(trans.outputs[0],mix.inputs[1]);l.new(diff.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface']);mesh.materials.append(m)
  rows.append({'name':row['name'],'foot':list(foot),'caster':ob.name,'sprite_source_unchanged':True})
 # No caster contours and no proxy geometry participation in ink passes.
 for vl in scene.view_layers:
  if vl.name in ['192 Architecture ink without pigment films','215 Distant ink without atmospheric boundary']:
   def exclude(lc):
    if lc.collection==C:lc.exclude=True
    for child in lc.children:exclude(child)
   exclude(vl.layer_collection)
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for ob in C.objects:
     if ob.name not in ls.collection.objects:ls.collection.objects.link(ob)
 return {'casters':rows,'method':'Native alpha billboard shadow-only shader; exact selected compositor sprites remain untouched','sun_light':'Soft warm directional daylight'}
