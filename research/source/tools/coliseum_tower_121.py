"""UCL01 tower-arches detail / UCL02 / DP03: narrow blind channels and interrupted collars.
Only Tower7 and Tower10 cores; unchanged accepted outline, tilt, and existing cornices.
"""
import bpy,bmesh,math,json,random
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-121/towers'
def apply(C):
 anchorname=next(o.name for o in C.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name)
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=[anchorname]
 anchor=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');delta=anchor.matrix_basis@auth.inverted();P=delta@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(anchor)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=yaw@A@P;Fi=F.inverted();rows=[];regions=[];new=[];owners={};support_rows=[]
 def p(j,rr,u,z):
  r=rr*(1-.055*z/78);outer=75*(1-.055*z/78)
  if r<outer:r=outer+.55*(r-outer)
  a=-math.pi/2+.68*(-math.pi+j*math.tau/36+u/75+math.pi/2);return F@Vector((r*math.cos(a),r*math.sin(a),z))
 def original(w):
  q=Fi@w;r=math.hypot(q.x,q.y);a=math.atan2(q.y,q.x)
  if a>math.pi/2:a-=math.tau
  a=-math.pi/2+(a+math.pi/2)/.68;outer=75*(1-.055*q.z/78)
  if r<outer:r=outer+(r-outer)/.55
  return P@Vector((r*math.cos(a),r*math.sin(a),q.z))
 def attrs(ob):
  a=ob.data.attributes.get('115 Original world position')or ob.data.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
  for v in ob.data.vertices:a.data[v.index].vector=original(ob.matrix_world@v.co)
  ob['121 changed']=True
 def mesh(name,vs,fs,role,j,mats=None):
  me=bpy.data.meshes.new('COL121 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('COL121 '+name,me);C.objects.link(ob);ob['bay']=j;ob['tier']=-1;ob['coliseum_role']=role;ob['feature']='tower architectural recess detail'
  if mats:
   for m in mats:me.materials.append(m)
   attrs(ob);new.append(ob)
  return ob
 def box(j,name,u0,u1,z0,z1,r0,r1,mats):
  owner=owners[j];support=BVHTree.FromPolygons([owner.matrix_world@v.co for v in owner.data.vertices],[tuple(f.vertices)for f in owner.data.polygons]);hits=[]
  for u in [u0,u1]:
   for z in [z0,z1]:
    start=p(j,78.4,u,z);end=p(j,77.60,u,z);hits.append(support.ray_cast(start,(end-start).normalized(),(end-start).length)[0]is not None)
  support_rows.append({'part':name,'corner_anchors':sum(hits),'required':4,'accepted':all(hits)})
  if not all(hits):return None
  outline=[(u0,z0),(u1,z0),(u1,z1),(u0,z1)];vs=[p(j,r,u,z)for r in [r0,r1]for u,z in outline];fs=[(3,2,1,0),(4,5,6,7)]+[(k,(k+1)%4,(k+1)%4+4,k+4)for k in range(4)];return mesh(name,vs,fs,'band',j,mats)
 def outline(width,z0,z1,arched=True):
  if not arched:return[(-width,z0),(width,z0),(width,z1),(-width,z1)]
  spring=z1-width;return[(-width,z0),(width,z0),(width,spring)]+[(width*math.cos(a),spring+width*math.sin(a))for a in [math.pi*k/10 for k in range(1,11)]]
 def cut(ob,j,label,width,z0,z1,arched):
  shape=outline(width,z0,z1,arched);N=len(shape);vs=[]
  for rr,scale in [(77.55,.88),(77.74,.88),(78.13,1.06)]:
   for u,z in shape:vs.append(p(j,rr,u*scale,z0+(z-z0)*(.995 if scale<1 else 1.002)))
  fs=[tuple(range(N-1,-1,-1)),tuple(range(2*N,3*N))]+[(r*N+k,r*N+(k+1)%N,(r+1)*N+(k+1)%N,(r+1)*N+k)for r in range(2)for k in range(N)];cutter=mesh('Tower'+str(j)+' '+label+' cutter',vs,fs,'detail',j);old=ob.data;baseline=BVHTree.FromPolygons([ob.matrix_world@v.co for v in old.vertices],[tuple(f.vertices)for f in old.polygons]);ob.data=old.copy();mod=ob.modifiers.new('121 Shallow tower channel','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=ob
  try:bpy.ops.object.modifier_apply(modifier=mod.name)
  except Exception:
   if mod.name in ob.modifiers:ob.modifiers.remove(mod)
   ob.data=old;bpy.data.objects.remove(cutter,do_unlink=True);rows.append({'tower':j,'feature':label,'rejected':'modifier error'});return False
  bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.free();lo=Vector(tuple(min(v[k]for v in vs)-.003 for k in range(3)));hi=Vector(tuple(max(v[k]for v in vs)+.003 for k in range(3)));tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(f.vertices)for f in ob.data.polygons]);error=0.
  for v in old.vertices:
   w=ob.matrix_world@v.co
   if all(lo[k]<=w[k]<=hi[k]for k in range(3)):continue
   hit=tree.find_nearest(w);error=max(error,hit[3]if hit and hit[0]is not None else 1e3)
  success=not bad and vol>0 and error<.003 and len(ob.data.vertices)>len(old.vertices)
  if not success:ob.data=old
  else:
   field=ob.data.attributes.get('118 Recess interior')or ob.data.attributes.new('118 Recess interior','FLOAT','FACE');num=0
   for f in ob.data.polygons:
    hit=baseline.find_nearest(ob.matrix_world@f.center)
    if hit and hit[0]is not None and hit[3]>.0015:field.data[f.index].value=1.;num+=1
   attrs(ob);ob['121 tower architectural channels']=True
   for height,kind in [(z0,'sill'),(z1,'head')]:regions.append({'name':f'Tower{j} {label} {kind}','center':list(original(p(j,77.8,0,height))),'radius':.65,'runoff_length':1.6})
  rows.append({'tower':j,'feature':label,'accepted':success,'nonmanifold_edges':bad,'positive_local_volume':vol,'outside_cavity_max_error_m':error,'width_authored_m':width*2,'height_authored_m':z1-z0,'radial_depth_authored_m':.25});bpy.data.objects.remove(cutter,do_unlink=True);return success
 for j in [7,10]:
  ob=next(o for o in C.objects if o.type=='MESH'and o.name.startswith('COL110 Tower'+str(j)+' core'));mats=list(ob.data.materials);owners[j]=ob
  specifications=[('upper blind arched channel',.68,60.05,72.2,True),('middle shallow panel',.78,42.6,54.6,False)]if j==7 else[('upper long narrow channel',.49,60.7,74.3,False),('middle blind niche',.60,46.7,54.2,True)]
  for label,width,z0,z1,arched in specifications:
   if cut(ob,j,label,width,z0,z1,arched):
    # Small layered sill inside the existing ribs; no external silhouette expansion.
    for k,(a,b,r)in enumerate([(z0-.22,z0-.10,77.99),(z0-.10,z0+.03,78.12)]):box(j,f'Tower{j} {label} inset sill{k}',-width-.12,width+.12,a,b,77.68,r,mats)
  # One interrupted inset collar per upper shaft, distinct heights and widths.
  height=65.9 if j==7 else 68.4
  for side in [-1,1]:
   u0,u1=(.94,1.60)if side==1 else(-1.60,-.94)
   for k,(dz,hh,r)in enumerate([(0,.18,78.02),(.18,.22,78.14)]):box(j,f'Tower{j} upper shoulder collar{side} {k}',u0,u1,height+dz,height+dz+hh,77.68,r,mats)
 return {'reference_ids':['UCL-01','UCL-02','DP-03'],'owned_towers':[7,10],'cuts':rows,'support_checks':support_rows,'new_supported_parts':len(new),'weathering_regions_original_world':regions,'preserved':'Whole-landmark E warp/yaw, existing tower ribs/crowns/collars,120 cornices and non-tower architecture','121 changed':True}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-120/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];s=bpy.context.scene
 # Isolated upper tower proof, keeping exact authored pose.
 keep={o for o in C.objects if ('Tower7 'in o.name or 'Tower10 'in o.name)};keep.update(o for o in s.objects if o.type in ['CAMERA','LIGHT'])
 for o in s.objects:
  if o not in keep:o.hide_render=True
 mat=bpy.data.materials.new('121 Tower clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.38,.38,.38,1);bs.inputs['Roughness'].default_value=.85
 for o in keep:
  if o.type=='MESH':o.data.materials.clear();o.data.materials.append(mat)
 s.use_nodes=False;s.render.use_freestyle=False;s.render.use_border=False;s.render.resolution_x=1600;s.render.resolution_y=1300;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
 w=bpy.data.worlds.new('121 Neutral towers');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.17,.17,.18,1);w.node_tree.nodes['Background'].inputs[1].default_value=.65;s.world=w
 s.camera.location=(0,95,48);target=Vector((0,198,44));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=38;s.render.filepath=str(O/'before-clay.png');bpy.ops.render.render(write_still=True)
 audit=apply(C);(O/'audit.json').write_text(json.dumps(audit,indent=2));s.render.filepath=str(O/'after-clay.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'));bpy.ops.render.render(write_still=True);print(json.dumps(audit))
