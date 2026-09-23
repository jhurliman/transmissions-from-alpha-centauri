"""One connected cornice/arch loss; source-world geometry remains beneath127 spacing."""
import bpy,bmesh,math,json,sys,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping

def apply(C):
 start=time.time();original,world,unpack=mapping();a0=-math.pi+7.5*math.tau/36;rows=[];changed=[]
 outline=[(-3.82,52.65),(-3.03,52.77),(-2.91,53.4),(-2.45,53.74),(-2.57,54.53),(-1.78,55.02),(-1.65,56.1),(-1.16,56.53),(-1.32,57.21),(-.84,57.59),(-.91,59.3),(-2.48,59.3),(-2.43,58.54),(-2.98,58.11),(-2.91,57.35),(-3.2,56.91),(-3.05,55.63),(-3.69,55.02),(-3.68,53.98),(-4.03,53.52)]
 # Coherent oblique loss with offset contours through thickness, rather than an extruded notch.
 rings=[(70.1,.60,-.22,.12),(72.8,.78,.05,-.08),(75.0,1,0,0),(79.8,1.03,.03,0)]
 vs=[];uc=-2.46;zc=55.95;N=len(outline)
 for rr,scale,du,dz in rings:
  for k,(u,z)in enumerate(outline):vs.append(world(rr,a0+(uc+(u-uc)*scale+du)/75,zc+(z-zc)*scale+dz))
 fs=[tuple(range(N-1,-1,-1)),tuple(range((len(rings)-1)*N,len(rings)*N))]
 for j in range(len(rings)-1):
  for k in range(N):
   v=j*N+k;v1=j*N+(k+1)%N;fs.extend([(v,v1,v1+N),(v,v1+N,v+N)])
 me=bpy.data.meshes.new('128 connected failure tool');me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True)
 for v in bm.verts:
  rr,aa,zz=unpack(v.co);uu=(aa-a0)*75
  if rr<79:
   # Bounded relief on the cutter's fracture floor/returns; intact wall stays untouched.
   relief=.12*math.sin(uu*4.7+zz*3.2)+.065*math.sin(uu*10.3-zz*7.1)
   rr+=relief;uu+=.045*math.sin(zz*9.1+uu*2.7);zz+=.045*math.sin(uu*8.2-zz*4.3)
   v.co=world(rr,a0+uu/75,zz)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();cutter=bpy.data.objects.new('128 connected failure tool',me);C.objects.link(cutter)
 cb=[Vector(v)for v in vs];lo=[min(v[k]for v in cb)for k in range(3)];hi=[max(v[k]for v in cb)for k in range(3)]
 names=[o for o in C.objects if o.type=='MESH'and (o.name=='COL127 T2 continuous arcade wall' or o.name.startswith('COL110 T2 B07 archivolt') or o.name.startswith('COL110 T2 band07 profile'))]
 coremat=bpy.data.materials.get('117 Exposed warm masonry core')
 if coremat is None:
  coremat=next((m for m in bpy.data.materials if 'exposed'in m.name.lower()and 'core'in m.name.lower()),None)
 for ob in names:
  bb=[ob.matrix_world@v.co for v in ob.data.vertices]
  if any(max(p[k]for p in bb)<lo[k]or min(p[k]for p in bb)>hi[k]for k in range(3)):continue
  old=ob.data;oldtree=BVHTree.FromPolygons(bb,[tuple(p.vertices)for p in old.polygons]);tmp=ob.copy();tmp.data=old.copy();tmp.modifiers.clear();C.objects.link(tmp);tmp.name='128 temporary '+ob.name
  mod=tmp.modifiers.new('128 genuine connected masonry loss','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=tmp
  try:bpy.ops.object.modifier_apply(modifier=mod.name)
  except Exception as e:rows.append({'object':ob.name,'error':str(e)});bpy.data.objects.remove(tmp,do_unlink=True);continue
  bm=bmesh.new();bm.from_mesh(tmp.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.free();verts=len(tmp.data.vertices)
  if bad or (verts and vol<=0):rows.append({'object':ob.name,'rejected_nonmanifold':bad,'volume':vol});bpy.data.objects.remove(tmp,do_unlink=True);continue
  if not verts or ('archivolt' in ob.name and vol<.002):
   rows.append({'object':ob.name,'removed':True});bpy.data.objects.remove(tmp,do_unlink=True);bpy.data.objects.remove(ob,do_unlink=True);continue
  surface=BVHTree.FromPolygons([tmp.matrix_world@v.co for v in tmp.data.vertices],[tuple(p.vertices)for p in tmp.data.polygons]);err=0
  for p in bb:
   if any(p[k]<lo[k]-.002 or p[k]>hi[k]+.002 for k in range(3)):
    hit=surface.find_nearest(p);err=max(err,hit[3]if hit and hit[0]is not None else 999)
  if err>.004:rows.append({'object':ob.name,'rejected_outside_change':err});bpy.data.objects.remove(tmp,do_unlink=True);continue
  if len(old.vertices)==len(tmp.data.vertices)and len(old.polygons)==len(tmp.data.polygons):bpy.data.objects.remove(tmp,do_unlink=True);continue
  ob.data=tmp.data;bpy.data.objects.remove(tmp,do_unlink=True);me=ob.data
  pos=me.attributes.get('115 Original world position')or me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');depth=me.attributes.get('120 Actual arch tunnel depth');mask=me.attributes.get('117 Exposed core')or me.attributes.new('117 Exposed core','FLOAT','FACE');exposed=0
  slot=None
  if coremat:
   slot=next((i for i,m in enumerate(me.materials)if m==coremat),None)
   if slot is None:slot=len(me.materials);me.materials.append(coremat)
  for v in me.vertices:
   rr,a,z=unpack(ob.matrix_world@v.co);pos.data[v.index].vector=original(rr,a,z)
   if depth:depth.data[v.index].value=max(0,min(1,(75-rr)/8))
  for p in me.polygons:
   hit=oldtree.find_nearest(ob.matrix_world@p.center)
   rr,aa,zz=unpack(ob.matrix_world@p.center);uu=(aa-a0)*75
   if hit and hit[0]is not None and hit[3]>.002 and -4.2<uu<-.5 and 52.3<zz<59.5:
    mask.data[p.index].value=1;exposed+=1;p.use_smooth=False
    if slot is not None:p.material_index=slot
  ob['128 connected junction']='B7 upper arcade to cornice';changed.append(ob.name);rows.append({'object':ob.name,'vertices_before':len(old.vertices),'vertices_after':len(me.vertices),'exposed_faces':exposed,'nonmanifold_edges':bad,'volume':vol,'outside_cutter_error_m':err})
 # Test dentil upper attachment against the same native negative volume before grouping.
 def in_outline(u,z):
  inside=False
  for k,(x,y)in enumerate(outline):
   xx,yy=outline[k-1]
   if (y>z)!=(yy>z) and u<(xx-x)*(z-y)/(yy-y)+x:inside=not inside
  return inside
 for ob in list(C.objects):
  if not ob.name.startswith('COL120 bay7 ') or ob.get('tier')!=2:continue
  groupmods=[m for m in ob.modifiers if m.name=='127 Equal edge-clearance layout']
  for m in groupmods:m.show_viewport=False
  bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mm=ev.to_mesh();coords=[unpack(ev.matrix_world@v.co)for v in mm.vertices];ev.to_mesh_clear()
  for m in groupmods:m.show_viewport=True
  top=max(z for r,a,z in coords);uu=sum((a-a0)*75 for r,a,z in coords)/len(coords)
  if in_outline(uu,top):rows.append({'object':ob.name,'removed_unsupported_dentil':True});bpy.data.objects.remove(ob,do_unlink=True)
 bpy.data.objects.remove(cutter,do_unlink=True)
 return {'references':['UCL-01','UCL-02','DP-03'],'property':'Connected loss follows a damaged arch shoulder into layered cornice; offset broken returns expose thickness while leaving backing/bearing intact.','source':'127 locked scene','site':{'bay':7,'tier':2,'outline_authored_u_z':outline,'radial_rings':rings},'changed_objects':changed,'operations':rows,'scope':'No B10 repair, tower core/pose/other scene changes. Source grouping modifier remains last. Native negative geometry, no added debris.','seconds':time.time()-start}

if __name__=='__main__':
 O=R/'art/studies/coliseum-128/junction';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-127/scene.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
 for ob in bpy.data.objects:
  if 'Landmark contact ink'in ob.name:ob.hide_render=True
 s.render.use_freestyle=False;s.render.resolution_x=2560;s.render.resolution_y=1923;s.render.resolution_percentage=100;s.render.use_border=False;s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
