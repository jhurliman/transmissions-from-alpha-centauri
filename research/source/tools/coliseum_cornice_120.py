"""Native shared under-cornice dentils, reference UCL-03 Roman detail, UCL-01 and UCL-02."""
import bpy,bmesh,math,json,ast,time,sys,os
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-120/cornice';O.mkdir(parents=True,exist_ok=True)
def add_cornice_blocks(C,bays=(8,),width=.55,clear_gap=1.10,height=.95):
 started=time.time()
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
 a=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=a.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(a);Pi=P.inverted()
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=yaw@A@P
 # Reuse only the pure GeometryNodes group factory, never the linked-study execution code.
 tree=ast.parse((R/'tools/coliseum_linked_116.py').read_text());factory=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='group');ns={'bpy':bpy,'math':math};exec(compile(ast.Module(body=[factory],type_ignores=[]),'<shared native warp>','exec'),ns);group=ns['group']();group.name='120 Shared dentil original coordinates and E warp'
 vs=[];fs=[];names=[];bandbounds={}
 for ob in C.objects:
  if ob.type!='MESH':continue
  at=ob.data.attributes.get('115 Original world position')
  if not at:continue
  coords=[Pi@d.vector for d in at.data];off=len(vs);vs+=coords;fs.extend(tuple(off+i for i in f.vertices)for f in ob.data.polygons);names.extend([ob.name]*len(ob.data.polygons))
  if ob.get('coliseum_role')=='band':bandbounds[ob.name]={'bay':ob.get('bay'),'z':[min(p.z for p in coords),max(p.z for p in coords)],'rmax':max(math.hypot(p.x,p.y)/(1-.055*p.z/78)for p in coords),'angles':[min(math.atan2(p.y,p.x)if math.atan2(p.y,p.x)<math.pi/2 else math.atan2(p.y,p.x)-math.tau for p in coords),max(math.atan2(p.y,p.x)if math.atan2(p.y,p.x)<math.pi/2 else math.atan2(p.y,p.x)-math.tau for p in coords)]}
 support=BVHTree.FromPolygons(vs,fs);master={};added=[];skipped=[];rowcounts={}
 mat=next(o.data.materials[0] for o in C.objects if o.type=='MESH'and o.get('coliseum_role')=='band'and len(o.data.materials))
 def make_master(h,projection):
  key=(h,projection)
  if key in master:return master[key]
  # Chamfered head, shallow sloping underside, rear tail embedded in real wall.
  yz=[(-.18,0),(projection-.08,0),(projection,-.09),(projection/3+.025,-h+.08),(projection/3,-h),(-.18,-h)]
  v=[(x,y,z)for x in [-width/2,width/2]for y,z in yz];N=len(yz);f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)]
  me=bpy.data.meshes.new('120 Shared chamfered dentil %.2f %.2f'%(h,projection));me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat);master[key]=me;return me
 def point(ang,r,z):return Vector((r*(1-.055*z/78)*math.cos(ang),r*(1-.055*z/78)*math.sin(ang),z))
 def valid(ang,z,h,projection,base=75):
  for du in [-width*.42,0,width*.42]:
   aa=ang+du/75;top=point(aa,base+projection*.8,z-.10);hit=support.ray_cast(top,Vector((0,0,1)),.22)
   if hit[0]is None or not any(w in names[hit[2]].lower()for w in ['band','entablature','coping','collar','belt','sill']):return False,'no overhead bearing'
   for zz in [z-h+.06,z-.15]:
    start=point(aa,base+1.0,zz);d=Vector((-math.cos(aa),-math.sin(aa),0));rear=support.ray_cast(start,d,1.35)
    if rear[0]is None:return False,'no rear wall bearing'
  return True,''
 for j in bays:
  rows=[('arcade%d'%t,2.73+(t+1)*18.33+.25,height,.83,t)for t in range(3)]+[('upper entablature',65.31,.46*(height/.65),.49,3)]
  coping=next((v for n,v in bandbounds.items()if v['bay']==j and 'surviving coping'in n),None)
  if coping:rows.append(('surviving coping',coping['z'][0],.42*(height/.65),.27,3))
  center=-math.pi+(j+.5)*math.tau/36
  rows=[(*row,75,center,6.2)for row in rows]
  for name,bounds in bandbounds.items():
   if bounds['bay']!=j:continue
   tower=('stepped belt2'in name or 'collar'in name and 'step1'in name)
   sill=('niche sill'in name or 'high aperture sill'in name)
   if not(tower or sill):continue
   z=bounds['z'][0]
   if z<4:continue
   aa,bb=bounds['angles'];projection=.83 if tower else .32;base=bounds['rmax']-projection-.035
   if tower:
    ang=(aa+bb)/2;zz=z-.6*(height/.65)+.08;probe=point(ang,bounds['rmax']+1,zz);hit=support.ray_cast(probe,Vector((-math.cos(ang),-math.sin(ang),0)),5)
    if hit[0]is not None:
     rear=math.hypot(hit[0].x,hit[0].y)/(1-.055*zz/78);base=rear-.12;projection=round((bounds['rmax']-base-.035)/.05)*.05
     if not(.25<projection<3.5):continue
   rows.append((name,z,(.6 if tower else .32)*(height/.65),projection,-1 if tower else 3,base,(aa+bb)/2,(bb-aa)*75/2-.08))
  for family,z,h,projection,tier,base,center,halfu in rows:
   rowcounts[f'{j}:{family}']=0
   count=max(1,int((2*halfu+clear_gap)/(width+clear_gap)))
   for k in range(count):
    u=(k-(count-1)/2)*(width+clear_gap);ang=center+u/75;ok,why=valid(ang,z,h,projection,base)
    if not ok:skipped.append({'bay':j,'family':family,'u':u,'reason':why});continue
    ob=bpy.data.objects.new('COL120 bay%d %s dentil%02d'%(j,family,k),make_master(h,projection));C.objects.link(ob);ob['bay']=j;ob['tier']=tier;ob['coliseum_role']='band';ob['feature']='shared undercornice dentil';ob['120 family']=family
    # Affine local tangent placement in original author space; nonlinear E warp remains native modifier.
    batter=1-.055*z/78;rad=Vector((math.cos(ang),math.sin(ang),0));tan=Vector((-math.sin(ang),math.cos(ang),0));origin=point(ang,base,z+.022);M=Matrix.Identity(4)
    for c,vec in enumerate([tan*batter,rad*batter,Vector((0,0,1))-rad*(base*.055/78)]):
     for r in range(3):M[r][c]=vec[r]
    M.translation=origin;mod=ob.modifiers.new('120 Shared native dentil warp','NODES');mod.node_group=group
    for prefix,T in [('Auth',M),('Original',P@M),('Final',F)]:
     for suffix,value in [(str(i),tuple(T[i][k]for k in range(3)))for i in range(3)]+[('T',tuple(T.translation))]:
      socket=next(s for s in group.interface.items_tree if s.item_type=='SOCKET'and s.in_out=='INPUT'and s.name==prefix+suffix);getattr(mod.properties.inputs,socket.identifier).value=value
    added.append(ob);rowcounts[f'{j}:{family}']+=1
 bpy.context.view_layer.update()
 audit={'reference_ids':['UCL-03','UCL-01','UCL-02'],'reference':'UCL-03 supplied Roman Colosseum undercornice detail; used for editable native geometry, never projected','parameters':{'authored_width':width,'clear_gap':clear_gap,'pitch':width+clear_gap,'main_height':height,'bottom_depth_fraction':1/3},'bays':list(bays),'new_objects':[o.name for o in added],'counts':rowcounts,'shared_master_meshes':len(master),'skipped':skipped,'support':'Three overhead and six rear radial bearing tests per candidate against existing native geometry. No block placed over an unsupported breach.','geometry':'Taller shared tapered meshes, bottom projection one-third top projection, and common GeometryNodes deformation; per-instance Auth/Original/Final transforms retain E curvature/yaw and original-world paint attribute. Local tangent approximation across0.55m width, not cloned warped meshes.','seconds':time.time()-started,'overhang_inventory':{'implemented':['3 principal arcade cornices','upper entablature','supported surviving crown coping','projecting tower collar main faces','supported niche/high-aperture sills'],'remaining':['side-return tower collar blocks need separate perpendicular profile; no unsupported corner blocks added'],'rollout':'bay8 proof first; common families can pass bays=range(18) after main-camera inspection.'}}
 return added,audit
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];added,audit=add_cornice_blocks(C,bays=tuple(range(18))if os.environ.get('CORNICE_ALL')=='1'else(8,));(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print(json.dumps(audit))
