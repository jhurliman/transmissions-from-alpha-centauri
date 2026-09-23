import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/lines-095';sys.path.insert(0,str(R/'tools'))
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-094/scene-C.blend'));s=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get();p=json.loads((R/'art/reviews/xenon-069/placements.json').read_text())[1]
for o in bpy.data.objects:
 if o.type=='MESH':o.lineart.usage='EXCLUDE'
c=bpy.data.collections.new('095 detail material-boundary proxy');s.collection.children.link(c)
found=[]
for ins in dep.object_instances:
 if ins.object.name==p['part']:
  mesh=bpy.data.meshes.new_from_object(ins.object,depsgraph=dep);ob=bpy.data.objects.new('095 proxy fracture panel',mesh);c.objects.link(ob);ob.matrix_world=ins.matrix_world;ob.lineart.usage='INCLUDE';found.append(ob)
# Nearby visible solids only, retained solely for occlusion during line bake.
center=Vector(p['center'])
for ins in dep.object_instances:
 source=ins.object
 if source.type!='MESH' or source.name==p['part'] or source.hide_render or len(source.data.polygons)>20000:continue
 bounds=[ins.matrix_world@Vector(v) for v in source.bound_box]
 lo=Vector([min(v[i] for v in bounds) for i in range(3)]);hi=Vector([max(v[i] for v in bounds) for i in range(3)])
 if any(lo[i]>center[i]+3 or hi[i]<center[i]-3 for i in range(3)):continue
 mesh=bpy.data.meshes.new_from_object(source,depsgraph=dep);ob=bpy.data.objects.new('095 occluder '+source.name,mesh);c.objects.link(ob);ob.matrix_world=ins.matrix_world;ob.lineart.usage='OCCLUSION_ONLY';found.append(ob)
print('FOUND',len(found),flush=True)
center=Vector(p['center']);s.camera.location=center+Vector((4,-2,1));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=2.5
ink=add_intersection_ink(c,'095 Weathering material boundary ink',radius=.0025);ink.modifiers[0].use_intersection=False;ink.modifiers[0].use_material=True
n=bake_intersection_ink(ink)
for o in found:bpy.data.objects.remove(o,do_unlink=True)
s.render.resolution_x=800;s.render.resolution_y=700;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_freestyle=False;s.render.engine='BLENDER_EEVEE';s.render.threads_mode='FIXED';s.render.threads=4
bpy.ops.wm.save_as_mainfile(filepath=str(O/'details-weather.blend'));print('WEATHER_READY',n,flush=True)
