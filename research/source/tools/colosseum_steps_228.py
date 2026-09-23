"""Five native curved masonry courses fit the terrain-supported Colosseum front.
No existing foundation, tunnel, terrain or architecture vertices are modified.
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
COUNT=5;TREAD=.95

def apply(scene):
 if scene.get('steps228_applied'):raise RuntimeError('228 already applied')
 C=bpy.data.collections['110 Coliseum detailed front ruin'];foundation=scene.objects['COL110 half-ring structural foundation'];ground=scene.objects['Street foundation'];dg=bpy.context.evaluated_depsgraph_get();ev=foundation.evaluated_get(dg);me=ev.to_mesh();L=len(me.vertices)//4;assert L==145
 edge=[ev.matrix_world@v.co for v in me.vertices[3*L:4*L]];attr=me.attributes['115 Original world position'];paint=[attr.data[3*L+i].vector.copy()for i in range(L)];ev.to_mesh_clear();inv=ground.matrix_world.inverted();normals=[]
 for i in range(L):
  t=edge[min(L-1,i+1)]-edge[max(0,i-1)];normals.append(Vector((t.y,-t.x,0)).normalized())
 def floor(p):
  ok,q,_,_=ground.ray_cast(inv@Vector((p.x,p.y,10)),Vector((0,0,-1)))
  return (ground.matrix_world@q).z if ok else None
 valid=[i for i,p in enumerate(edge)if all(floor(p+normals[i]*d)is not None for d in(0,TREAD*COUNT+.03))]
 start,end=min(valid),max(valid);assert valid==list(range(start,end+1));ids=list(range(start,end+1));N=len(ids);assert N>40
 # Use native existing band material and packed original-world paint coordinates.
 material=foundation.material_slots[0].material;factor=.715*scene.objects['COL127 T0 continuous arcade wall'].matrix_world.to_scale().x
 def ringpoint(i,ring):
  if ring==0:return edge[i].copy()
  wear=.018*math.sin(i*1.83+ring*.74)+.007*math.sin(i*4.71+ring)
  return edge[i]+normals[i]*(ring*TREAD+wear)
 objects=[];rows=[];meshverts=[]
 for k in range(1,COUNT+1):
  rb=COUNT-k;rf=rb+1;vs=[];paintcoords=[];gz=[];rise=[]
  for top in(False,True):
   for ring in(rb,rf):
    for i in ids:
     p=ringpoint(i,ring);g=floor(p);assert g is not None
     z=g+(edge[i].z-g)*k/COUNT if top else g-.035
     if top and k<COUNT:z-=.005*(.5+.5*math.sin(i*2.14+k*.31))
     p.z=z
     # Rear overlap avoids open seams under the next higher course/foundation.
     if ring==rb:p-=normals[i]*.015
     vs.append(p);paintcoords.append(paint[i]+(p-edge[i])/factor);gz.append(g)
     if top:rise.append((edge[i].z-g)/COUNT)
  fs=[]
  for j in range(N-1):fs.extend([(j,j+1,N+j+1,N+j),(2*N+j,3*N+j,3*N+j+1,2*N+j+1),(j,2*N+j,2*N+j+1,j+1),(N+j,N+j+1,3*N+j+1,3*N+j)])
  fs.extend([(0,N,3*N,2*N),(N-1,3*N-1,4*N-1,2*N-1)])
  mesh=bpy.data.meshes.new(f'228 Curved stone step{k}');mesh.from_pydata(vs,[],fs);mesh.update();mesh.materials.append(material)
  a=mesh.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
  for q,p in zip(a.data,paintcoords):q.vector=p
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.to_mesh(mesh);bm.free();assert bad==0 and volume>0
  marks=mesh.attributes.new("freestyle_edge","BOOLEAN","EDGE")
  for e in mesh.edges:
   a,b=e.vertices
   if 3*N<=a<4*N and 3*N<=b<4*N and abs(a-b)==1:marks.data[e.index].value=True
  ob=bpy.data.objects.new(f'COL228 Ground curved step{k} of5',mesh);C.objects.link(ob);ob['228 stone step']=True;ob['tier']=0;ob['coliseum_role']='band';ob['tread_world_m']=TREAD;ob['course_from_ground']=k
  bevel=ob.modifiers.new('228 small worn stone arris','BEVEL');bevel.width=.012;bevel.segments=1;bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(35)
  objects.append(ob);meshverts.extend(vs);rows.append({'object':ob.name,'course':k,'nominal_tread_m':TREAD,'riser_range_m':[min(rise),max(rise)],'terrain_embed_m':.035,'foundation_join_overlap_m':.015 if k==COUNT else None,'front_edge_subtle_plan_wear_m':.025,'nonmanifold_edges':bad,'positive_solid_volume_m3':volume,'material':material.name,'top_joins_foundation':k==COUNT})
 # Use the existing atmosphere-free far native ink view map; no new render layer.
 ink=bpy.data.collections['215 Distant accepted component ink']
 for o in objects:ink.objects.link(o)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for o in objects:
     if o.name not in ls.collection.objects:ls.collection.objects.link(o)
 bpy.context.view_layer.update()
 # Only original foundation contact strokes truly hidden by the new courses may be clipped.
 from mathutils.bvhtree import BVHTree
 vv=[];tt=[]
 for o in objects:
  eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());em=eo.to_mesh();em.calc_loop_triangles();off=len(vv);vv.extend(eo.matrix_world@v.co for v in em.vertices);tt.extend(tuple(off+i for i in t.vertices)for t in em.loop_triangles);eo.to_mesh_clear()
 tree=BVHTree.FromPolygons(vv,tt,all_triangles=True);gp=scene.objects['110 Landmark contact ink'];origin=scene.camera.matrix_world.translation;affected=[]
 for li,layer in enumerate(gp.data.layers):
  for fi,fr in enumerate(layer.frames):
   for si,st in enumerate(fr.drawing.strokes):
    ps=[gp.matrix_world@Vector(p.position)for p in st.points]
    for a,b in zip(ps,ps[1:]):
     for p in(a,(a+b)/2,b):
      d=p-origin;hit=tree.ray_cast(origin,d.normalized(),max(0,d.length-.02))
      if hit[0]is not None:affected.append([li,fi,si]);break
     if affected and affected[-1]==[li,fi,si]:break
 # Stair geometry never covers an original front-contact line above its foundation join.
 # If it does, leave no silent draw-through: caller must run a provenance-scoped native clip.
 assert not affected,('228 new steps occlude old landmark contact; scoped clip required',affected)
 px=[]
 for i in(start,end):
  p=ringpoint(i,COUNT);p.z=floor(p);q=world_to_camera_view(scene,scene.camera,p);px.append([q.x*3840,(1-q.y)*2885])
 scene['steps228_applied']=True
 return {'iteration':228,'source':bpy.data.filepath,'course_count':5,'foundation_edge_indices':[start,end],'terrain_supported_arc_samples':N,'foundation_top_world_z_range_m':[min(edge[i].z for i in ids),max(edge[i].z for i in ids)],'steps':rows,'nominal_total_run_m':COUNT*TREAD,'top_foundation_height_error_m':0,'native_endpoint_screen_pixels':px,'terrain_geometry_unchanged':True,'existing_objects_unchanged':True,'existing_contact_ink_changed':False,'native_contact_occlusion_probes':'Each old GP segment endpoint and midpoint tested against evaluated new steps; no occlusions beyond2cm','new_ink_owner':'215 Distant component architecture; native atmosphere-free pass','materials':'Existing foundation painted masonry band graph and original-world paint coordinates reused','review':'CPU fit only; actual camera proof pending'}
if __name__=='__main__':
 O=R/'art/studies/colosseum-steps-228';O.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/far-building-layout-226/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('228 READY',flush=True)
