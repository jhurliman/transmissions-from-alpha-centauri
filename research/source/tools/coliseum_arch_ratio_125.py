"""UCL-01/UCL-03/DP-03: real narrower/shorter arcade openings, fixed floors and bay envelope."""
import bpy,bmesh,math,json,sys,random
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-125/arch-ratio';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import topology

def mapping():
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
 ob=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=ob.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(ob)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);Y=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=Y@A@P;Fi=F.inverted()
 def original(rr,a,z):return P@Vector((rr*(1-.055*z/78)*math.cos(a),rr*(1-.055*z/78)*math.sin(a),z))
 def world(rr,a,z):
  r=rr*(1-.055*z/78);outer=75*(1-.055*z/78)
  if r<outer:r=outer+.55*(r-outer)
  a=-math.pi/2+.68*(a+math.pi/2);return F@Vector((r*math.cos(a),r*math.sin(a),z))
 def unpack(w):
  q=Fi@w;r=math.hypot(q.x,q.y);a=math.atan2(q.y,q.x)
  if a>math.pi/2:a-=math.tau
  a=-math.pi/2+(a+math.pi/2)/.68;outer=75*(1-.055*q.z/78)
  if r<outer:r=outer+(r-outer)/.55
  return r/(1-.055*q.z/78),a,q.z
 return original,world,unpack

def apply(C,width_reduction=.20,height_reduction=.05):
 if not(0<=width_reduction<.5 and 0<=height_reduction<.5):raise ValueError('Invalid reduction')
 original,world,unpack=mapping();sw=1-width_reduction;sh=1-height_reduction;half=75*math.tau/36*.34;rows=[];tunnels={};parts=[]
 for ob in list(C.objects):
  if ob.type!='MESH' or ob.get('tier')not in [0,1,2]:continue
  if 'loadbearing arch tunnel'in ob.name:tunnels[(int(ob['tier']),int(ob['bay']))]=ob
  elif any(s in ob.name for s in [' archivolt',' jamb ',' impost ']):parts.append(ob)
 successful=set()
 for (tier,bay),ob in tunnels.items():
  ac=-math.pi+(bay+.5)*math.tau/36;bottom=2.73+tier*18.33;base=bottom+.35;top=bottom+18.33;spring=top-2.184-half;crown=spring+half;nspring=base+sh*(spring-base);ncrown=base+sh*(crown-base);old=ob.data;before=topology(ob);iv=ob.matrix_world.inverted();coords=[unpack(ob.matrix_world@v.co)for v in old.vertices];uv=[(a-ac)*75 for r,a,z in coords];sidefaces=[]
  for f in old.polygons:
   for sign in [-1,1]:
    if all(abs(uv[i]-sign*half)<.01 for i in f.vertices):sidefaces.append(f.index)
  if len(sidefaces)!=2:rows.append({'object':ob.name,'skipped':'unexpected damaged side topology','side_faces':len(sidefaces)});continue
  vs=[];attrs=[]
  for (rr,a,z),u in zip(coords,uv):
   if z<=crown+.0001:zz=base+sh*(z-base);uu=u*sw
   else:
    t=(z-crown)/(top-crown);zz=ncrown+t*(top-ncrown);uu=u*(sw+(1-sw)*t)
   vs.append(iv@world(rr,ac+uu/75,zz));attrs.append(original(rr,ac+uu/75,zz))
  fs=[tuple(f.vertices)for f in old.polygons if f.index not in sidefaces];mats=[f.material_index for f in old.polygons if f.index not in sidefaces]
  wallslot=next((i for i,m in enumerate(old.materials)if m and m.get('role')=='wall'),0);depthslot=next((i for i,m in enumerate(old.materials)if m and 'Two-depth interior'in m.name),wallslot)
  # Reuse exact four side-face vertices, avoiding nominal-coordinate weld gaps.
  for sign in [-1,1]:
   face=next(old.polygons[i]for i in sidefaces if sum(uv[j]for j in old.polygons[i].vertices)*sign>0)
   ids={}
   for i in face.vertices:
    rr,aa,zz=coords[i];ids[(rr>71,zz>spring+.2)]=i
   ii=[]
   for front in [False,True]:
    low=ids[(front,False)];high=ids[(front,True)];rr=coords[low][0];outeru=uv[high];inneru=uv[low]*sw
    for uu in [outeru,inneru]:
     ii.append(len(vs));vs.append(iv@world(rr,ac+uu/75,base));attrs.append(original(rr,ac+uu/75,base))
    ii.extend([low,high])
   local=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(3,0,4,7)]
   fs.extend(tuple(ii[i]for i in f)for f in local);mats.extend([wallslot,wallslot,wallslot,depthslot,wallslot])
  me=bpy.data.meshes.new(old.name+'124 ratio');me.from_pydata(vs,[],fs);me.update()
  for mat in old.materials:me.materials.append(mat)
  for f,i in zip(me.polygons,mats):f.material_index=i
  attr=me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
  for x,v in zip(attr.data,attrs):x.vector=v
  depth=me.attributes.new('120 Actual arch tunnel depth','FLOAT','POINT')
  for v,d in zip(me.vertices,depth.data):rr,_,_=unpack(ob.matrix_world@v.co);d.value=max(0,min(1,(75-rr)/8))
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0002);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob.data=me;after=topology(ob)
  if after['nonmanifold'] or after['strict_crossings']>before['strict_crossings']or after['volume']<=0:ob.data=old;rows.append({'object':ob.name,'rejected':after});continue
  successful.add((tier,bay));ob['125 arch width reduction']=width_reduction;ob['125 arch height reduction']=height_reduction;rows.append({'object':ob.name,'before':before,'after':after,'clear_width_authored_before':half*2,'clear_width_authored_after':half*2*sw,'clear_height_authored_before':crown-base,'clear_height_authored_after':(crown-base)*sh,'base_unchanged':base,'floor_top_unchanged':top,'new_side_masonry_joined':True})
 moved=[]
 for ob in parts:
  tier,bay=int(ob['tier']),int(ob['bay'])
  if (tier,bay)not in successful:continue
  ac=-math.pi+(bay+.5)*math.tau/36;base=2.73+tier*18.33+.35;top=2.73+tier*18.33+18.33;spring=top-2.184-half;nspring=base+sh*(spring-base);iv=ob.matrix_world.inverted();ob.data=ob.data.copy()
  attr=ob.data.attributes.get('115 Original world position')or ob.data.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
  for v in ob.data.vertices:
   rr,a,z=unpack(ob.matrix_world@v.co);u=(a-ac)*75
   if 'archivolt'in ob.name:
    r=math.hypot(u,z-spring);theta=math.atan2(z-spring,u);offset=r-half;rx=half*sw;rz=half*sh;n=Vector((math.cos(theta)/rx,math.sin(theta)/rz)).normalized();uu=rx*math.cos(theta)+n.x*offset;zz=nspring+rz*math.sin(theta)+n.y*offset
   elif 'jamb'in ob.name:uu=u-math.copysign(half*(1-sw),u);zz=base+sh*(z-base)
   else:uu=u-math.copysign(half*(1-sw),u);zz=z+(nspring-spring)
   v.co=iv@world(rr,ac+uu/75,zz);attr.data[v.index].vector=original(rr,ac+uu/75,zz)
  ob.data.update();ob['125 arch width reduction']=width_reduction;ob['125 arch height reduction']=height_reduction;moved.append(ob.name)
 return {'references':['UCL-01','UCL-03','DP-03'],'width_reduction':width_reduction,'height_reduction':height_reduction,'true_width_scale':sw,'true_height_scale':sh,'molding_profile':'Elliptical inner curve plus constant normal offset for preserved molding thickness','preserved':['floor bands','bay exterior widths','column footprints','radial wall depth','front-quarter arch-light parameter'],'wall_changes':rows,'molding_jamb_impost_changes':moved,'successful_bays':len(successful),'column_agent_independent':True}

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-123/scene.blend'));audit=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print('ARCH125',audit['successful_bays'],flush=True)
