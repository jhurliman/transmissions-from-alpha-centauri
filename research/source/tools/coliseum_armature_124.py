"""Extend accepted bent armature into the surviving Tower10 spine; native anchored connections."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def apply(C):
 if any(o.get('124 armature connection')for o in C.objects):return {'already_applied':True}
 anchorname=next(o.name for o in C.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name)
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=[anchorname]
 anchor=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=anchor.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(anchor)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=yaw@A@P
 def p(rr,u,z):
  rr=rr*(1-.055*z/78);outer=75*(1-.055*z/78)
  if rr<outer:rr=outer+.55*(rr-outer)
  a=-math.pi/2+.68*(-math.pi+10*math.tau/36+u/75+math.pi/2);return F@Vector((rr*math.cos(a),rr*math.sin(a),z))
 core=next(o for o in C.objects if o.name.startswith('COL110 Tower10 core'));tree=BVHTree.FromPolygons([core.matrix_world@v.co for v in core.data.vertices],[tuple(f.vertices)for f in core.data.polygons]);mats=list(bpy.data.objects['COL123 Tower10 bent upright0'].data.materials)
 def center(ob,ring):return sum((ob.matrix_world@ob.data.vertices[ring*6+j].co for j in range(6)),Vector())/6
 def tube(name,points,radius):
  vs=[];N=6
  for k,q in enumerate(points):
   t=(points[min(k+1,len(points)-1)]-points[max(0,k-1)]).normalized();axis=Vector((0,0,1));axis=(axis-t*axis.dot(t)).normalized();other=t.cross(axis).normalized()
   vs.extend(q+radius*(math.cos(math.tau*j/N)*axis+math.sin(math.tau*j/N)*other)for j in range(N))
  fs=[tuple(range(N-1,-1,-1)),tuple(range((len(points)-1)*N,len(points)*N))]+[(k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j)for k in range(len(points)-1)for j in range(N)]
  me=bpy.data.meshes.new('COL124 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.to_mesh(me);bm.free()
  if bad or vol<=0:raise RuntimeError('Invalid armature tube '+name)
  ob=bpy.data.objects.new('COL124 Tower10 '+name,me);C.objects.link(ob)
  for m in mats:me.materials.append(m)
  light=Vector((-.45,-.7,1)).normalized()
  for f in me.polygons:f.material_index=1 if f.normal.dot(light)>.64 else(2 if f.normal.dot(light)<-.25 else 0)
  ob['bay']=10;ob['tier']=3;ob['coliseum_role']='detail';ob['feature']='bent steel connection into surviving spine';ob['124 armature connection']=True
  return {'object':ob.name,'nonmanifold_edges':bad,'positive_volume':vol}
 specs=[('upper bent spine connection',0,3,77.68,76.90,.068,-.09),('lower kinked spine connection',0,1,77.65,74.12,.059,.11),('rear diagonal spine connection',3,2,76.05,76.03,.057,-.10)]
 rows=[]
 for name,idx,ring,rr,z,radius,sag in specs:
  upright=bpy.data.objects['COL123 Tower10 bent upright'+str(idx)];endpoint=center(upright,ring);start=p(rr,.40,z);end=p(rr,-2.5,z);direction=(end-start).normalized();hit=tree.ray_cast(start,direction,(end-start).length)
  if hit[0]is None:raise RuntimeError('Missing tall spine support '+name)
  wall=hit[0];embed=wall+direction*.22;outside=wall-direction*.12;middle=outside.lerp(endpoint,.52)+Vector((.025,0,sag));points=[embed,outside,middle,endpoint]
  row=tube(name,points,radius);row.update({'masonry_owner':core.name,'masonry_contact':list(wall),'embed_world_m':.22,'connected_to':upright.name,'target_ring':ring,'endpoint_world':list(endpoint),'anchor_authored_z':(F.inverted()@wall).z});rows.append(row)
 return {'target':core.name,'new_connections':rows,'new_objects':3,'existing_seven_rods_preserved':True,'existing_masonry_unchanged':True,'new_materials':0,'scope':'Three bent ties from accepted framing into actual taller surviving spine, embedded22cm'}
