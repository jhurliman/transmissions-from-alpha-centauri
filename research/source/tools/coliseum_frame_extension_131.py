"""Extend the accepted bent Tower10 frame to just below its surviving coping."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def apply(C):
 if any(o.get('131 upper frame extension')for o in C.objects):return {'already_applied':True}
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
  me=bpy.data.meshes.new('COL131 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.to_mesh(me);bm.free()
  if bad or vol<=0:raise RuntimeError('Invalid armature tube '+name)
  ob=bpy.data.objects.new('COL131 Tower10 '+name,me);C.objects.link(ob)
  for m in mats:me.materials.append(m)
  light=Vector((-.45,-.7,1)).normalized()
  for f in me.polygons:f.material_index=1 if f.normal.dot(light)>.64 else(2 if f.normal.dot(light)<-.25 else 0)
  ob['bay']=10;ob['tier']=3;ob['coliseum_role']='detail';ob['feature']='bent steel connection into surviving spine';ob['131 upper frame extension']=True
  return {'object':ob.name,'nonmanifold_edges':bad,'positive_volume':vol}

 rows=[]
 tips={i:center(bpy.data.objects['COL123 Tower10 bent upright'+str(i)],3) for i in(0,2)}
 top=max((F.inverted()@(core.matrix_world@v.co)).z for v in core.data.vertices)
 rr=77.66;z=top-.36
 start=p(rr,.45,z);end=p(rr,-2.5,z);direction=(end-start).normalized();hit=tree.ray_cast(start,direction,(end-start).length)
 if hit[0] is None:raise RuntimeError('Missing near-coping masonry anchor')
 wall=hit[0];embedded=wall+direction*.22;outside=wall-direction*.12
 upper=p(77.65,.45,top-.58)
 # Continue two accepted uprights with unequal kinks, joining a bent top rail.
 left=[tips[0],tips[0].lerp(upper,.48)+Vector((.025,-.025,0)),upper]
 righttop=p(77.54,1.93,top-.91)
 right=[tips[2],tips[2].lerp(righttop,.55)+Vector((.035,.025,-.04)),righttop]
 for name,points,radius,idx in [('left upright extension',left,.068,0),('right upright extension',right,.063,2)]:
  row=tube(name,points,radius);row.update({'connected_existing_object':'COL123 Tower10 bent upright'+str(idx),'endpoint_center_distance_m':0.0,'points_world':[list(q)for q in points]});rows.append(row)
 rail=[embedded,outside,upper,upper.lerp(righttop,.57)+Vector((0,-.025,-.085)),righttop]
 row=tube('upper kinked coping tie',rail,.061);row.update({'masonry_owner':core.name,'masonry_contact':list(wall),'embedded_endpoint':list(embedded),'embed_world_m':.22,'anchor_authored_z':(F.inverted()@wall).z,'core_top_authored_z':top,'distance_below_core_top_authored_m':top-(F.inverted()@wall).z,'joins_new_uprights_at_centers':True,'points_world':[list(q)for q in rail]});rows.append(row)
 return {'target':core.name,'new_connections':rows,'new_objects':3,'existing_rods_and_masonry_preserved':True,'new_materials':0,'scope':'Two unequal kinked upright extensions and one supported top tie anchored immediately under surviving coping; existing frame retained','authored_core_top':top}
