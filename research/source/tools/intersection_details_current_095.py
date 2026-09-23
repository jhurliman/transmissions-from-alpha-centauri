"""Add selected detail ink using the CURRENT scene/camera; do not regenerate assets.
Call after loading a finalscene, before render. Baked output is camera-specific.
"""
import bpy, numpy as np, json
from pathlib import Path
from mathutils import Vector
from intersection_ink_095 import add_intersection_ink, bake_intersection_ink
R=Path('/PATH/TO/transmissions-from-alpha-centauri')

def add_selected_rock_contacts(radius=.004):
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
    ink=add_intersection_ink(proxy,'095 Rock contact intersection ink',radius=radius)
    n=bake_intersection_ink(ink)
    for obj in list(proxy.objects): bpy.data.objects.remove(obj,do_unlink=True)
    return ink,n

def add_selected_weathering_boundaries(radius=.0025, placement_index=7):
    s=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get();p=json.loads((R/'art/reviews/xenon-069/placements.json').read_text())[placement_index]
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
    ink=add_intersection_ink(c,'095 Weathering material boundary ink',radius=radius)
    ink.modifiers[0].use_intersection=False
    ink.modifiers[0].use_material=True
    n=bake_intersection_ink(ink)
    for obj in found: bpy.data.objects.remove(obj,do_unlink=True)
    return ink,n
