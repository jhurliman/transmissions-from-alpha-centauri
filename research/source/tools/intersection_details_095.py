"""Local detail ink proof; preserves accepted scene assets."""
import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/lines-095';sys.path.insert(0,str(R/'tools'))
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-094/scene-C.blend'))
s=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get()
rocks=[o for o in bpy.data.objects if o.get('scatter_zone')=='road' and 1.2<o.location.x<3.0 and -5.9<o.location.y<-3.3]
print('SELECTED',[(o.name,list(o.location)) for o in rocks],flush=True)
proxy=bpy.data.collections.new('095 temporary details proxy');s.collection.children.link(proxy)
for o in bpy.data.objects:
 if o.type=='MESH':o.lineart.usage='EXCLUDE'
for rock in rocks:
 mesh=bpy.data.meshes.new_from_object(rock.evaluated_get(dep),depsgraph=dep);obj=bpy.data.objects.new('095 proxy '+rock.name,mesh);proxy.objects.link(obj);obj.matrix_world=rock.matrix_world;obj.lineart.usage='INCLUDE'
ground=bpy.data.objects['Street foundation'];mesh=ground.evaluated_get(dep).to_mesh();mesh.calc_loop_triangles()
v=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3)
f=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('vertices',f);f=f.reshape(-1,3)
# Exact existing triangles, no resampling.
cent=v[f].mean(axis=1);keep=np.zeros(len(f),dtype=bool)
for rock in rocks:
 bounds=np.array([rock.matrix_world@Vector(p) for p in rock.bound_box]);lo=bounds.min(axis=0)-.015;hi=bounds.max(axis=0)+.015
 keep|=(cent[:,0]>lo[0])&(cent[:,0]<hi[0])&(cent[:,1]>lo[1])&(cent[:,1]<hi[1])
sel=f[keep]
used=np.unique(sel);remap=np.full(len(v),-1,dtype=np.int32);remap[used]=np.arange(len(used));pm=bpy.data.meshes.new('095 exact details ground');pm.from_pydata(v[used].tolist(),[],remap[sel].tolist());po=bpy.data.objects.new(pm.name,pm);proxy.objects.link(po);po.matrix_world=ground.matrix_world;po.lineart.usage='INCLUDE';ground.evaluated_get(dep).to_mesh_clear()
# Close physical camera; cloned geometry is only for generating the line strokes.
s.camera.location=(4,-8,3.5);s.camera.rotation_euler=(Vector((2.1,-4.65,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=2.45
ink=add_intersection_ink(proxy,'095 Rock contact intersection ink',radius=.004);n=bake_intersection_ink(ink)
for o in list(proxy.objects):bpy.data.objects.remove(o,do_unlink=True)
s.render.resolution_x=900;s.render.resolution_y=750;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_freestyle=False
s.render.engine='BLENDER_EEVEE';s.render.threads_mode='FIXED';s.render.threads=4
(O/'details-audit.json').write_text(json.dumps({'rocks':[o.name for o in rocks],'baked_strokes':n,'native_ground_triangles':len(sel),'camera_specific':True,'line_radius':.004,'materials_changed':False,'geometry_changed':False},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'details-rocks.blend'))
if '--render' in sys.argv:
 ink.hide_render=True;s.render.filepath=str(O/'details-rocks-before.png');bpy.ops.render.render(write_still=True)
 ink.hide_render=False;s.render.filepath=str(O/'details-rocks-after.png');bpy.ops.render.render(write_still=True)
print('DETAILS_READY',n,flush=True)
