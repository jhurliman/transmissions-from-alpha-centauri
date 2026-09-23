"""113 distinct tower collapse and deep connected arcade failure; UCL-01.
Native removed volume with thick surviving bearing masonry, no floating debris.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix

def collapse_landmark(collection):
 rad=75.;cy=347.;H=78.;step=math.tau/36;start=-math.pi;lean=Matrix.Rotation(math.radians(2),4,'X')
 anchor=next(o for o in collection.objects if o.get('bay')==4 and 'fractured upper wall L' in o.name)
 auth=Matrix.Translation(Vector((0,cy,0)))@lean@Matrix.Rotation(start+4.5*step,4,'Z');delta=anchor.matrix_world@auth.inverted()
 def p(rr,aa,z):
  b=1-.055*z/H;v=lean@Vector((rr*b*math.cos(aa),rr*b*math.sin(aa),z));return delta@Vector((v.x,cy+v.y,v.z))
 def cutter(name,angle,outline,back,front):
  N=len(outline);vs=[p(rr,angle+u/rad,z)for rr in [back,front]for u,z in outline];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)]
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);collection.objects.link(ob);return ob
 audit=[]
 def zone(label,cut,targets):
  records=[];ca=[cut.matrix_world@Vector(v)for v in cut.bound_box]
  for ob in targets:
   if ob.type!='MESH':continue
   oa=[ob.matrix_world@Vector(v)for v in ob.bound_box]
   if any(max(v[k]for v in ca)<min(v[k]for v in oa)or max(v[k]for v in oa)<min(v[k]for v in ca)for k in range(3)):continue
   old=ob.data;before=len(old.vertices);ob.data=old.copy();mod=ob.modifiers.new('113 structural collapse','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=ob
   bpy.ops.object.modifier_apply(modifier=mod.name)
   bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();after=len(bm.verts);bm.free()
   if bad or (after and vol<=0):ob.data=old;records.append({'object':ob.name,'rejected_nonmanifold':bad});continue
   if not after:records.append({'object':ob.name,'removed':True});bpy.data.objects.remove(ob,do_unlink=True);continue
   if before==after:ob.data=old;continue
   ob['localized_breakage']=label;ob['collapse113']=True;records.append({'object':ob.name,'vertices':after,'nonmanifold':bad,'positive_volume':True})
  bpy.data.objects.remove(cut,do_unlink=True);audit.append({'zone':label,'results':records})
 # One tall left stump survives. Lower center/back mass supports the ragged open termination.
 j=10;aa=start+j*step
 outline=[(-1.02,82),(4.8,82),(4.8,74.6),(2.7,74.6),(2.55,74.0),(1.70,74.25),(1.45,73.1),(.55,73.1),(.35,72.55),(-.32,72.9),(-.6,73.5),(-1.05,73.35),(-.9,74.2),(-.9,75.4),(-1.3,75.7),(-1.3,76.6),(-.75,76.9),(-.75,77.6),(-1.1,78.3),(-.95,78.7)]
 cut=cutter('COL113 tower front collapse cutter',aa,outline,rad-.9,rad+6)
 zone('tower10 open collapsed termination',cut,[o for o in list(collection.objects)if o.get('bay')==10 and 'Tower10' in o.name])
 # Cut down the rear of the former cap: the opening now reaches sky, not another full-height slab.
 outline=[(-.95,82),(4.0,82),(4.0,75.45),(2.5,75.45),(2.30,75.9),(1.5,75.7),(1.2,76.1),(.45,75.8),(.1,76.2),(-.4,76.0),(-.95,76.25)]
 cut=cutter('COL113 tower rear collapse cutter',aa,outline,rad-2.6,rad-.85)
 zone('tower10 lower jagged rear stump',cut,[o for o in list(collection.objects)if o.get('bay')==10 and 'Tower10' in o.name])
 # The original continuous crown cap is lost in this collapse, not left as a cantilevering flag.
 for ob in list(collection.objects):
  if ob.get('bay')==10 and 'Tower10 broken crown' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
 outline=[(-4,81),(-.6,81),(-.6,78.4),(-1.35,78.8),(-1.8,78.3),(-2.15,78.5),(-2.7,78.1),(-4,78.1)]
 cut=cutter('COL113 surviving pier ragged top cutter',aa,outline,rad-2.6,rad+6)
 zone('tower10 surviving left spine fracture',cut,[o for o in list(collection.objects)if o.get('bay')==10 and 'Tower10' in o.name])
 # A major shoulder spall retains~3.5m of the8m wall behind it: no unsupported arch span.
 aa=start+(j+.5)*step
 outline=[(-4.8,61.6),(-2.2,61.6),(-2.2,60.4),(-2.65,60.2),(-2.4,59.5),(-2.95,58.9),(-2.7,58.2),(-3.15,57.7),(-2.85,56.8),(-3.10,56.1),(-2.95,55.3),(-3.5,54.4),(-3.25,53.7),(-3.9,52.3),(-4.45,52.0),(-4.8,53.2),(-4.45,54.5),(-4.9,55.7),(-4.55,57.2),(-4.85,58.5)]
 cut=cutter('COL113 deep arcade shoulder cutter',aa,outline,rad-4.5,rad+1.8)
 zone('bay10 deep connected arch shoulder failure',cut,[o for o in list(collection.objects)if o.get('bay')==10 and ((o.get('tier')==2 and o.get('coliseum_role')in['wall','arch_molding','band','pier'])or(o.get('tier')==3 and o.get('coliseum_role')=='wall'))])
 # Split disconnected remnants before building a physical support graph.
 from mathutils.bvhtree import BVHTree
 components=[];tiny=[]
 for ob in list(collection.objects):
  if ob.type!='MESH' or ob.get('bay')!=10 or 'Tower10' not in ob.name:continue
  bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();remaining=set(bm.verts);groups=[]
  while remaining:
   seed=remaining.pop();stack=[seed];group={seed}
   while stack:
    v=stack.pop()
    for e in v.link_edges:
     other=e.other_vert(v)
     if other in remaining:remaining.remove(other);group.add(other);stack.append(other)
   groups.append(group)
  originals=[]
  for k,group in enumerate(groups):
   faces=[f for f in bm.faces if f.verts[0]in group];gv=list(group);index={v:i for i,v in enumerate(gv)}
   me=bpy.data.meshes.new(ob.name+f' remnant{k}');me.from_pydata([v.co for v in gv],[],[tuple(index[v]for v in f.verts)for f in faces]);me.update()
   for material in ob.data.materials:me.materials.append(material)
   piece=bpy.data.objects.new(ob.name+f' remnant{k}',me);collection.objects.link(piece);piece.matrix_world=ob.matrix_world.copy()
   for key in ob.keys():piece[key]=ob[key]
   test=bmesh.new();test.from_mesh(me);volume=abs(test.calc_volume());test.free()
   if volume<.08 and len(groups)>1 or (volume<.04 and ob.get('collapse113')):
    tiny.append(piece.name);bpy.data.objects.remove(piece,do_unlink=True);continue
   world=[piece.matrix_world@v.co for v in me.vertices];polys=[tuple(f.vertices)for f in me.polygons];tree=BVHTree.FromPolygons(world,polys)
   author=[lean.inverted()@(delta.inverted()@v-Vector((0,cy,0)))for v in world]
   components.append({'ob':piece,'tree':tree,'world':world,'root':min(v.z for v in author)<71.0})
  bm.free();bpy.data.objects.remove(ob,do_unlink=True)
 graph={i:set()for i in range(len(components))}
 for i,a in enumerate(components):
  for j in range(i):
   b=components[j]
   if any(max(v[k]for v in a['world'])<min(v[k]for v in b['world'])-.005 or max(v[k]for v in b['world'])<min(v[k]for v in a['world'])-.005 for k in range(3)):continue
   contact=bool(a['tree'].overlap(b['tree']))
   if not contact:
    contact=any((lambda hit:hit[0]is not None and hit[3]<.015)(b['tree'].find_nearest(v))for v in a['world'])
   if contact:graph[i].add(j);graph[j].add(i)
 supported={i for i,c in enumerate(components)if c['root']};todo=list(supported)
 while todo:
  for j in graph[todo.pop()]:
   if j not in supported:supported.add(j);todo.append(j)
 unsupported=[]
 for i,c in enumerate(components):
  if i not in supported:unsupported.append(c['ob'].name);bpy.data.objects.remove(c['ob'],do_unlink=True)
 # Previously embedded aggregate cannot remain suspended after its supporting cap is removed.
 surface_vertices=[];surface_faces=[]
 for ob in collection.objects:
  if ob.type!='MESH' or 'embedded aggregate' in ob.name:continue
  off=len(surface_vertices);surface_vertices.extend(ob.matrix_world@v.co for v in ob.data.vertices);surface_faces.extend(tuple(off+i for i in f.vertices)for f in ob.data.polygons)
 solid=BVHTree.FromPolygons(surface_vertices,surface_faces);loose_aggregate=[]
 for ob in list(collection.objects):
  if ob.type!='MESH' or 'embedded aggregate' not in ob.name:continue
  vertices=[ob.matrix_world@v.co for v in ob.data.vertices];center=sum(vertices,Vector())/len(vertices);radius=max((v-center).length for v in vertices);near=solid.find_nearest(center)
  if near[0]is None or near[3]>radius*.95:loose_aggregate.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 return {'removed_unsupported_aggregate':loose_aggregate,'support_graph' :{'components':len(components),'supported':len(supported),'removed_unsupported':unsupported,'removed_tiny_slivers':tiny},'reference_ids' :['UCL-01','DP-03','UX-01'],'zones':audit,'retained_rear_arch_wall_m':3.5,'tower_bearing':'full lower core and left pier; lower rear stump','native_geometry_only':True,'camera_unchanged':True}
