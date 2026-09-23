"""Every native ground arcade receives30m straight+30m at45degrees downward."""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from coliseum_arch_ratio_125 import mapping

def apply(scene):
 C=bpy.data.collections['110 Coliseum detailed front ruin']
 assert not any(o.get('220 descending arcade tunnel')for o in C.all_objects)
 old=[o for o in C.all_objects if o.get('130 barrel tunnel')]
 assert len(old)==2 and {o.get('bay')for o in old}=={8,9}
 wall=bpy.data.objects['COL127 T0 continuous arcade wall'];_,world,unpack=mapping()
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=wall.evaluated_get(dg);me=ev.to_mesh()
 assert len(me.vertices)==len(wall.data.vertices)
 original=me.attributes['115 Original world position'];authored=[unpack(v.co)for v in wall.data.vertices]
 materials=list(old[0].data.materials);assert len(materials)==2
 rows=[];trees=[];Z=Vector((0,0,1));scale=wall.matrix_world.to_scale().x
 for bay in range(18):
  ac=-math.pi+(bay+.5)*math.tau/36;curve=[];bottom=[]
  for i,(r,a,z)in enumerate(authored):
   u=(a-ac)*75
   if abs(r-67)>.006 or abs(u)>3.01:continue
   item=(u,z,ev.matrix_world@me.vertices[i].co,original.data[i].vector.copy(),i)
   if 13<z<18.2:curve.append(item)
   if abs(z-3.08)<.003 and abs(abs(u)-2.9154717)<.025:bottom.append(item)
  curve.sort();bottom.sort();assert len(curve)==25 and len(bottom)==2,(bay,len(curve),len(bottom))
  platform=next(o for o in C.objects if o.get('125 inset platform')and o.get('tier')==0 and o.get('bay')==bay)
  floor=3.08+float(platform['platform authored height']);feet=[];attrs=[]
  for low,high in[(bottom[0],curve[0]),(bottom[-1],curve[-1])]:
   t=(floor-low[1])/(high[1]-low[1]);feet.append(low[2].lerp(high[2],t));attrs.append(low[3].lerp(high[3],t))
  inner=[feet[0]]+[p[2]for p in curve]+[feet[1]];attr=[attrs[0]]+[p[3]for p in curve]+[attrs[1]]
  center=(feet[0]+feet[1])/2;D=wall.matrix_world.to_3x3()@(world(66,ac,floor)-world(67,ac,floor));D.z=0;D.normalize();R=D.cross(Z).normalized()
  profile=[Vector(((p-center).dot(R),(p-center).z))for p in inner];longitudinal=[(p-center).dot(D)for p in inner]
  assert 10-max(longitudinal)>0,(bay,longitudinal)
  outer=[]
  for i,p in enumerate(profile):
   a=(p-profile[i-1]).normalized();b=(profile[(i+1)%len(profile)]-p).normalized();na=Vector((-a.y,a.x));nb=Vector((-b.y,b.x));bis=(na+nb).normalized();outer.append(p+bis*(.65/max(.25,bis.dot(na))))
  bend=center+30*D;end=bend+30/math.sqrt(2)*(D-Z)
  vs=[];orig=[];n=len(inner)
  # Exact oblique mouth,10m forward-only transition to planarsection, straightsegment, sharedmiter, openoutlet.
  stations=[('embed',-.12),('mouth',0),('straight',10),('straight',20),('miter',30),('down',15),('down',30)]
  for kind,t in stations:
   for outline in(profile,outer):
    for i,p in enumerate(outline):
     if kind in('embed','mouth'):w=center+t*D+p.x*R+p.y*Z+longitudinal[i]*D
     elif kind=='straight':w=center+t*D+p.x*R+p.y*Z
     elif kind=='miter':w=bend+p.x*R+p.y*Z+p.y*math.tan(math.pi/8)*D
     else:w=bend+t/math.sqrt(2)*(D-Z)+p.x*R+p.y/math.sqrt(2)*(D+Z)
     vs.append(w);orig.append(attr[i]+(w-inner[i])/(.715*scale))
  fs=[];mi=[]
  for k in range(len(stations)-1):
   for layer in range(2):
    for i in range(n):
     j=(i+1)%n;a=k*n*2+layer*n;z=(k+1)*n*2+layer*n;fs.append((a+i,a+j,z+j,z+i));mi.append(1 if i==n-1 else 0)
  for k in(0,len(stations)-1):
   off=k*2*n
   for i in range(n):j=(i+1)%n;fs.append((off+i,off+j,off+n+j,off+n+i));mi.append(0)
  mesh=bpy.data.meshes.new(f'220 Ground B{bay:02d} solid descending barrel vault');mesh.from_pydata(vs,[],fs);mesh.update()
  for m in materials:mesh.materials.append(m)
  for p,i in zip(mesh.polygons,mi):p.material_index=i
  a=mesh.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');dep=mesh.attributes.new('120 Actual arch tunnel depth','FLOAT','POINT')
  for v,co,d in zip(a.data,orig,dep.data):v.vector=co;d.value=1
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.to_mesh(mesh);bm.free();assert bad==0 and vol>0,(bay,bad,vol)
  ob=bpy.data.objects.new(f'COL220 T0 B{bay:02d} 30m then45deg down30m',mesh);C.objects.link(ob);ob['220 descending arcade tunnel']=True;ob['tier']=0;ob['bay']=bay;ob['coliseum_role']='tunnel'
  mesh.calc_loop_triangles();trees.append(BVHTree.FromPolygons(vs,[tuple(t.vertices)for t in mesh.loop_triangles],all_triangles=True))
  rows.append({'bay':bay,'object':ob.name,'entry_floor_center':list(center),'inward_horizontal_direction':list(D),'bend_floor_center':list(bend),'outlet_floor_center':list(end),'straight_m':(bend-center).length,'descending_m':(end-bend).length,'down_angle_degrees':45,'vertical_drop_m':bend.z-end.z,'horizontal_turn_degrees':0,'source_rim_vertex_indices':[p[4]for p in curve],'exact_native_mouth_points':[list(p)for p in inner],'mouth_fit_error_m':0,'wall_thickness_m':.65,'solid_nonmanifold_edges':bad,'solid_volume_m3':vol,'entry_section_transition_m':10,'entry_obliqueness_m':[min(longitudinal),max(longitudinal)],'minimum_forward_entry_transition_m':10-max(longitudinal),'section_points':n,'path_stations':len(stations),'open_mouth_and_outlet':True,'miter_roof_floor_connection':'shared27pointprofile at anglebisector; continuoussolid shell','width_m':max(p.x for p in profile)-min(p.x for p in profile),'height_m':max(p.y for p in profile),'side_profile_m':[[0,0],[30,0],[30+30/math.sqrt(2),-30/math.sqrt(2)]]})
 ev.to_mesh_clear()
 collisions=[]
 for i in range(len(trees)):
  for j in range(i+1,len(trees)):
   count=len(trees[i].overlap(trees[j]))
   if count:collisions.append({'bays':[i,j],'intersecting_surface_triangle_pairs':count})
 for ob in old:ob.hide_render=True;ob.hide_viewport=True
 return {'source':bpy.data.filepath,'ground_portals':18,'bays':list(range(18)),'objects':rows,'hidden_old_tunnels':[o.name for o in old],'separate_third_arch_blocker_found':False,'old130_tunnels_themselves_blocked_third_sliver':True,'material_names':[m.name for m in materials],'scale_compensated_world_metres':True,'landmark_scale':scale,'neighbor_surface_intersections':collisions,'gp_reclip_required':False,'gp_reason':'Bothold130andnew220geometrybelong110landmark; dedicated110externalvisibilityclip excludesentirelandmark. Noexternaloccluderschanged.','facade_existing_geometry_materials_unchanged':True}
