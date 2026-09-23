"""Additive reveal-through spring stones and upper-sill pyramids; native shared warp."""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]

def apply(scene):
 from coliseum_arch_ratio_125 import mapping
 from coliseum_arch_thickness_129 import params
 original,world,_=mapping();P=dict(zip(original.__code__.co_freevars,[x.cell_contents for x in original.__closure__]))['P'];Pi=P.inverted()
 C=bpy.data.collections['110 Coliseum detailed front ruin'];assert not any(o.get('231 ornament')for o in C.objects)
 wall=bpy.data.objects['COL127 T0 continuous arcade wall'];landmark_matrix=wall.matrix_world.copy();warp=next(m for m in wall.modifiers if m.type=='NODES'and '127'in m.name);group=warp.node_group
 def unpack_original(p):
  q=Pi@p;a=math.atan2(q.y,q.x)
  if a>math.pi/2:a-=math.tau
  return math.hypot(q.x,q.y)/(1-.055*q.z/78),a,q.z
 def new(name,coords,faces,source,role):
  me=bpy.data.meshes.new(name);me.from_pydata([world(*p)for p in coords],[],faces);me.materials.append(next(m for m in source.data.materials if m));a=me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
  for d,p in zip(a.data,coords):d.vector=original(*p)
  dep=me.attributes.new('120 Actual arch tunnel depth','FLOAT','POINT')
  for d,(r,angle,z)in zip(dep.data,coords):d.value=max(0,min(1,(75-r)/8))
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.to_mesh(me);bm.free();assert bad==0 and vol>0,(name,bad,vol)
  ob=bpy.data.objects.new(name,me);ob.matrix_world=landmark_matrix.copy();C.objects.link(ob);mod=ob.modifiers.new('231 Existing equal-clearance arch warp','NODES');mod.node_group=group
  for sock in group.interface.items_tree:
   if sock.item_type=='SOCKET'and sock.in_out=='INPUT'and sock.name!='Geometry':
    value=getattr(warp.properties.inputs,sock.identifier).value;getattr(mod.properties.inputs,sock.identifier).value=value
  ob['231 ornament']=role;ob['tier']=int(source['tier']);ob['bay']=int(source['bay']);ob['coliseum_role']='band';ob['231 source stone']=source.name
  return ob
 records=[];pairs=[];extensions=[];pyramids=[]
 imposts=sorted((o for o in C.objects if ' impost 'in o.name and not o.hide_render),key=lambda o:o.name);assert len(imposts)==108
 for source in imposts:
  at=source.data.attributes['115 Original world position'];coords=[unpack_original(d.vector)for d in at.data];rmin=min(p[0]for p in coords);amin=min(p[1]for p in coords);amax=max(p[1]for p in coords);zmin=min(p[2]for p in coords);zmax=max(p[2]for p in coords)
  # Attachment penetrates the existing front stone. The continuous stem runs
  # through the entire radial reveal; a slightly wider rear cap wraps its back.
  attach=rmin+.08;rear=66.70;neck=67.18;spread=.07/75
  footprint=[(attach,amin),(attach,amax),(neck,amax),(neck,amax+spread),(rear,amax+spread),(rear,amin-spread),(neck,amin-spread),(neck,amin)]
  pts=[(r,a,z)for z in(zmin,zmax)for r,a in footprint];N=len(footprint);faces=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
  ob=new('COL231 '+source.name.removeprefix('COL110 ')+' continuous reveal return',pts,faces,source,'reveal-through impost');pairs.append((source,ob));extensions.append((ob,source,pts));records.append({'object':ob.name,'source':source.name,'tier':ob['tier'],'bay':ob['bay'],'attachment_overlap_authored_m':.08,'front_attachment_radius':attach,'actual_reveal_back_radius':67,'rear_wrap_radius':rear,'rear_wrap_overlap_authored_m':.48,'profile_height_authored_m':zmax-zmin,'through_depth_authored_m':attach-rear,'single_closed_connected_mesh':True,'rear_cap_additional_width_each_side_authored_m':.07})
 platforms=sorted((o for o in C.objects if o.get('125 inset platform')and o.get('tier')in(1,2)and not o.hide_render),key=lambda o:o.name);assert len(platforms)==36
 for source in platforms:
  tier,bay=int(source['tier']),int(source['bay']);ac=-math.pi+(bay+.5)*math.tau/36;base=2.73+tier*18.33+.35+1.25+float(source['platform authored height']);rx,rz,spring=params(tier,bay);inset=.75*(.83+.03);crown=spring+rz-inset;clear=crown-base;assert clear>0
  width=.40*2*(rx-inset);height=.10*clear;center_r=74.48;M=landmark_matrix
  width_world=(M@world(center_r,ac+width/(2*75),base)-M@world(center_r,ac-width/(2*75),base)).length;radial_world=(M@world(center_r+.5,ac,base)-M@world(center_r-.5,ac,base)).length;dr=min(.64,width_world/(2*radial_world));embed=.02
  pts=[(center_r-dr,ac-width/(2*75),base-embed),(center_r-dr,ac+width/(2*75),base-embed),(center_r+dr,ac+width/(2*75),base-embed),(center_r+dr,ac-width/(2*75),base-embed),(center_r,ac,base+height)];faces=[(0,3,2,1),(0,1,4),(1,2,4),(2,3,4),(3,0,4)]
  ob=new(f'COL231 T{tier} B{bay:02d} centered sill pyramid',pts,faces,source,'upper sill pyramid');pairs.append((source,ob));pyramids.append((ob,source,pts));records.append({'object':ob.name,'source':source.name,'tier':tier,'bay':bay,'height_ratio_to_actual_clear_opening':.10,'opening_clear_height_authored_m':clear,'pyramid_height_authored_m':height,'base_width_authored_m':width,'base_depth_authored_m':2*dr,'sill_top_authored_z':base,'embedded_base_authored_m':embed,'front_radius':center_r+dr,'platform_coping_front_radius':75.24,'ground_level_unobstructed':True})
 # Inherit existing source stone ownership in every live/native ink selection.
 ownership=[]
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if not ls.select_by_collection or not ls.collection:continue
   members=set(ls.collection.all_objects);added=[]
   for source,ob in pairs:
    if source in members and ob.name not in ls.collection.objects:ls.collection.objects.link(ob);added.append(ob.name)
   if added:ownership.append({'layer':vl.name,'line_set':ls.name,'mode':ls.collection_negation,'added':len(added)})
 # Existing215 isolated native pass bypasses atmospheric boundary occlusion.
 farink=bpy.data.collections['215 Distant accepted component ink']
 for source,ob in pairs:
  if ob.name not in farink.objects:farink.objects.link(ob)
 ownership.append({'layer':'215 Distant ink without atmospheric boundary','line_set':'215 Distant component architecture','mode':'INCLUSIVE','added':len(pairs)})
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();validation=[]
 from mathutils.bvhtree import BVHTree
 for ob,source,coords in extensions+pyramids:
  e=ob.evaluated_get(dg);me=e.to_mesh();ps=[e.matrix_world@v.co for v in me.vertices];bm=bmesh.new();bm.from_mesh(me);bad=sum(not ed.is_manifold for ed in bm.edges);bm.free();assert bad==0,ob.name
  se=source.evaluated_get(dg);sm=se.to_mesh();sv=[se.matrix_world@v.co for v in sm.vertices];tree=BVHTree.FromPolygons(sv,[tuple(p.vertices)for p in sm.polygons]);nearest=[tree.find_nearest(p)[3]for p in ps[:(8 if ob['231 ornament']=='reveal-through impost'else 4)]]
  if ob['231 ornament']=='upper sill pyramid':
   assert max(nearest)<.09,(ob.name,nearest)
   ratio=(ps[-1].z-sum(p.z for p in ps[:4])/4)/next(r['opening_clear_height_authored_m']for r in records if r['object']==ob.name)
  else:ratio=None
  validation.append({'object':ob.name,'native_nonmanifold_edges':bad,'world_bbox_min':[min(p[k]for p in ps)for k in range(3)],'world_bbox_max':[max(p[k]for p in ps)for k in range(3)],'source_surface_distances_m':nearest,'pyramid_world_height_per_authored_opening_height':ratio})
  e.to_mesh_clear();se.to_mesh_clear()
 return {'objects':records,'new_objects':144,'continuous_impost_extensions':108,'upper_pyramids':36,'upper_tiers':[1,2],'ground_pyramids':0,'world_fit_validation':validation,'ink_ownership':ownership,'original_facade_and_tunnel_geometry_unchanged':True,'materials_reused':sorted({o.data.materials[0].name for _,o in pairs}),'native_mapping':'Original stone paint coordinates plus identical shared127 equal-clearance warp and selected70percent landmark transform.'}
