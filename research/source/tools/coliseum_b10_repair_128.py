"""Surgical clean111 B10 spall recovery within authoritative127 joined wall."""
import bpy,bmesh,math,sys,json,statistics
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-128/b10-repair';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import topology
from coliseum_arch_ratio_125 import mapping
TARGET='COL127 T2 continuous arcade wall';SOURCE='COL110 T2 B10 loadbearing arch tunnel'
def apply(C):
 original,world,unpack=mapping();target=bpy.data.objects[TARGET];before=topology(target);old=target.data;oldvs=[v.co.copy()for v in old.vertices];ac=-math.pi+10.5*math.tau/36;half=math.tau/36*.34;amin=ac-half;amax=ac+half
 existing_angles=[unpack(target.matrix_world@v.co)[1]for v in old.vertices];amin=statistics.median(a for a in existing_angles if abs(a-amin)<2e-5);amax=statistics.median(a for a in existing_angles if abs(a-amax)<2e-5)
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-111/scene.blend'),link=False)as(src,dst):dst.objects=[SOURCE,'COL110 U4 fractured upper wall L']
 src,anchor=dst.objects;lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=anchor.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;Pi=P.inverted();coords=[]
 # Retain113's accepted deep left-shoulder cavity, replayed on the clean pre112 surface.
 C.objects.link(src);bpy.context.view_layer.update();outline=[(-4.8,61.6),(-2.2,61.6),(-2.2,60.4),(-2.65,60.2),(-2.4,59.5),(-2.95,58.9),(-2.7,58.2),(-3.15,57.7),(-2.85,56.8),(-3.10,56.1),(-2.95,55.3),(-3.5,54.4),(-3.25,53.7),(-3.9,52.3),(-4.45,52.0),(-4.8,53.2),(-4.45,54.5),(-4.9,55.7),(-4.55,57.2),(-4.85,58.5)];N=len(outline)
 vs=[P@Vector((rr*(1-.055*z/78)*math.cos(ac+u/75),rr*(1-.055*z/78)*math.sin(ac+u/75),z))for rr in [70.5,76.8]for u,z in outline];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)]
 cm=bpy.data.meshes.new('128 exact113 shoulder');cm.from_pydata(vs,[],fs);cm.update();cut=bpy.data.objects.new('128 temporary shoulder cutter',cm);C.objects.link(cut);bpy.context.view_layer.objects.active=src;mod=src.modifiers.new('128 restore113 shoulder','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True);replaycheck=topology(src)
 if replaycheck['nonmanifold']or replaycheck['strict_crossings']:raise RuntimeError('113 clean replay unsafe '+str(replaycheck))

 for v in src.data.vertices:
  p=Pi@(src.matrix_basis@v.co);z=p.z;r=math.hypot(p.x,p.y)/(1-.055*z/78);a=math.atan2(p.y,p.x)
  if a>math.pi/2:a-=math.tau
  if abs(a-amin)<2e-5:a=amin
  if abs(a-amax)<2e-5:a=amax
  if abs(r-67)<.001:r=67.
  if abs(r-75)<.001:r=75.
  if abs(z-57.72)<.001:z=57.72
  if abs(z-51.085)<.001:z=51.085
  coords.append((r,a,z))
 sourcefaces=[tuple(f.vertices)for f in src.data.polygons];sourceinfo={'verts':len(coords),'faces':len(sourcefaces)}
 bpy.data.objects.remove(src);bpy.data.objects.remove(anchor)
 me=old.copy();target.data=me;bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table();oldcoords=[unpack(target.matrix_world@v.co)for v in bm.verts];remove=[]
 for f in bm.faces:
  angles=[oldcoords[v.index][1]for v in f.verts];mid=sum(angles)/len(angles)
  if min(angles)>=amin-2e-5 and max(angles)<=amax+2e-5 and amin+1e-5<mid<amax-1e-5:remove.append(f)
 localmaterial={f.material_index for f in remove};wallslot=next((i for i in localmaterial if me.materials[i] and me.materials[i].get('role')=='wall'),min(localmaterial));depthslot=next((i for i,ma in enumerate(me.materials)if ma and 'Two-depth interior'in ma.name),wallslot)
 bmesh.ops.delete(bm,geom=remove,context='FACES');layer=bm.verts.layers.float_vector.get('115 Original world position');dl=bm.verts.layers.float.get('120 Actual arch tunnel depth');new=[];iv=target.matrix_world.inverted()
 for r,a,z in coords:
  v=bm.verts.new(iv@world(r,a,z));new.append(v)
  if layer:v[layer]=original(r,a,z)
  if dl:v[dl]=max(0,min(1,(75-r)/8))
 caps=0
 for ids in sourcefaces:
  aa=[coords[i][1]for i in ids]
  if max(aa)-min(aa)<2e-5 and min(abs(sum(aa)/len(aa)-amin),abs(sum(aa)/len(aa)-amax))<2e-5:caps+=1;continue
  f=bm.faces.new([new[i]for i in ids]);f.material_index=wallslot if all(abs(coords[i][0]-75)<.001 for i in ids)else depthslot
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0005)
 # Conform exact long replacement side edges to the retained old seam points.
 splits=0
 for angle in [amin,amax]:
  vertices=[v for v in bm.verts if abs(unpack(target.matrix_world@v.co)[1]-angle)<2e-5];points=[v.co.copy()for v in vertices]
  edges=[e for e in bm.edges if len(e.link_faces)==1 and all(abs(unpack(target.matrix_world@v.co)[1]-angle)<2e-5 for v in e.verts)]
  for edge in edges:
   if not edge.is_valid:continue
   start,end=edge.verts;a=start.co.copy();d=end.co-a
   if d.length_squared<1e-12:continue
   pp=[]
   for p in points:
    t=(p-a).dot(d)/d.length_squared
    if 1e-5<t<1-1e-5 and (a+d*t-p).length<.0005:pp.append((t,p))
   last=-1
   for t,p in sorted(pp,key=lambda x:x[0]):
    if t-last<1e-5:continue
    last=t;fac=(p-start.co).length/(end.co-start.co).length
    if not 1e-5<fac<1-1e-5:continue
    ne,nv=bmesh.utils.edge_split(edge,start,fac);nv.co=p;start=nv;edge=next(e for e in nv.link_edges if end in e.verts);splits+=1
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0005)
 holes=[e for e in bm.edges if len(e.link_faces)==1]
 if holes:
  if not all(any(all(abs(unpack(target.matrix_world@v.co)[1]-a)<2e-5 for v in e.verts)for a in [amin,amax])for e in holes):raise RuntimeError('Boundary outside repaired interfaces')
  bmesh.ops.holes_fill(bm,edges=holes,sides=0)
 for angle in [amin,amax]:
  vertices=[v for v in bm.verts if abs(unpack(target.matrix_world@v.co)[1]-angle)<2e-5];points=[v.co.copy()for v in vertices]
  edges=[e for e in bm.edges if len(e.link_faces)==1 and all(abs(unpack(target.matrix_world@v.co)[1]-angle)<2e-5 for v in e.verts)]
  for edge in edges:
   if not edge.is_valid:continue
   start,end=edge.verts;a=start.co.copy();d=end.co-a
   if d.length_squared<1e-12:continue
   pp=[]
   for p in points:
    t=(p-a).dot(d)/d.length_squared
    if 1e-5<t<1-1e-5 and (a+d*t-p).length<.0005:pp.append((t,p))
   last=-1
   for t,p in sorted(pp,key=lambda x:x[0]):
    if t-last<1e-5:continue
    last=t;fac=(p-start.co).length/(end.co-start.co).length
    if not 1e-5<fac<1-1e-5:continue
    ne,nv=bmesh.utils.edge_split(edge,start,fac);nv.co=p;start=nv;edge=next(e for e in nv.link_edges if end in e.verts);splits+=1
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0005)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();from coliseum_seam_repair_127 import apply as repair_seam
 repair_seam(C);after=topology(target)
 return {'before':before,'after':after,'source':sourceinfo,'113_replay':replaycheck,'removed_faces':len(remove),'omitted_source_caps':caps,'edge_splits':splits,'material_slots':[(i,me.materials[i].name if me.materials[i]else'')for i in localmaterial]}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-127/scene.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(O/'baseline.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print(a)
