"""UCL-01/UCL-02/DP-03: native ordered crown height-graph fracture BEFORE119 macro openings.
Only prepared U8 L/R meshes are handed back to current scene. Not a voxel or image asset.
"""
import bpy,bmesh,math,random,json,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-126/fracture-seed';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import NAMES,topology,strict_crossings

def apply_prepared(C, allow_incomplete_study=False):
 if not allow_incomplete_study:
  raise RuntimeError("126 is a held study: secondary119 losses did not replay. No production integration authorized.")
 targets={name:bpy.data.objects[name]for name in NAMES}
 with bpy.data.libraries.load(str(O/'construction.blend'),link=False)as(src,dst):dst.objects=list(NAMES)
 rows=[]
 for name,new in zip(NAMES,dst.objects):
  ob=targets[name];materials=list(ob.data.materials);ob.data=new.data.copy();ob.data.materials.clear()
  for mat in materials:ob.data.materials.append(mat)
  wall=next((i for i,m in enumerate(materials)if m and m.get('role')=='wall'),0);core=next((i for i,m in enumerate(materials)if m and m.name.startswith('117 Exposed masonry core')),wall);mask=ob.data.attributes.get('117 Exposed core')
  for f in ob.data.polygons:f.material_index=core if mask and mask.data[f.index].value>.5 else wall
  ob['126 profile-first fracture']=True;rows.append({'object':name,**topology(ob)});bpy.data.objects.remove(new,do_unlink=True)
 return rows

def piece(u,curve):
 for (x,a),(y,b)in zip(curve,curve[1:]):
  if x<=u<=y:return a+(b-a)*(u-x)/(y-x)
 return 0.

def run():
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-111/scene.blend'));anchor=next(o for o in bpy.data.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name);lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=anchor.matrix_world@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;Pi=P.inverted();ac=-math.pi+8.5*math.tau/36;profiles={}
 for name in NAMES:
  ob=bpy.data.objects[name];ctrl=[]
  for i in range(21,28):
   p=Pi@(ob.matrix_world@ob.data.vertices[i].co);ctrl.append(((math.atan2(p.y,p.x)-ac)*75,p.z))
  profiles[name]=ctrl
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);Y=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=Y@A@P
 def point(rr,u,z,warp=True):
  r=rr*(1-.055*z/78);a=ac+u/75
  if warp:
   outer=75*(1-.055*z/78)
   if r<outer:r=outer+.55*(r-outer)
   a=-math.pi/2+.68*(a+math.pi/2)
  return (F if warp else P)@Vector((r*math.cos(a),r*math.sin(a),z))
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-116/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];records=[]
 for ni,name in enumerate(NAMES):
  ob=bpy.data.objects[name];old=ob.data;iv=ob.matrix_world.inverted();ctrl=profiles[name];u0,u1=ctrl[0][0],ctrl[-1][0];rng=random.Random(12680+ni);notches=[]
  # Uneven groups; quiet stretches are deliberate, particularly beneath existing coping.
  centers=[-6.1,-5.3,-1.55]if ni==0 else[1.6,3.1,4.35,5.2,6.05]
  for ci,c in enumerate(centers):
   for k in range(rng.choice([2,3,4])):
    center=c+rng.uniform(-.27,.27);width=rng.uniform(.13,.36);depth=rng.uniform(.16,.43)
    if k==0:width*=1.55;depth*=1.18
    low=max(u0+.045,center-width*.5);high=min(u1-.045,center+width*.5)
    if high-low<.055:continue
    curve=[(low,0),(low+(high-low)*rng.uniform(.22,.4),depth*rng.uniform(.66,.88)),(low+(high-low)*rng.uniform(.53,.73),depth),(high,0)];notches.append(curve)
  us=sorted(set([u0,u1]+[u for u,z in ctrl]+[u for curve in notches for u,z in curve]+[u0+(u1-u0)*k/32 for k in range(1,32)]));rs=[67.,67.35,68.1,69.7,71.5,73.4,74.2,74.62,75.];nu,nr=len(us),len(rs)
  patches=[(rng.uniform(u0+.25,u1-.25),rng.uniform(68.2,73.8),rng.uniform(.18,.48),rng.uniform(.65,1.7),rng.uniform(.06,.22))for _ in range(11)];vs=[];original=[]
  for top in [False,True]:
   for rr in rs:
    for u in us:
     z=62.559986
     if top:
      base=piece(u,ctrl);front=max((piece(u,c)for c in notches),default=0);frontweight=max(0,1-(75-rr)/1.55);rearweight=max(0,1-(rr-67)/.8)*.42
      # Coherent sloping fracture return, finer chipped rim; bounded pits in broad core.
      pocket=max((amp*max(0,1-abs((u-cu)/ru)-abs((rr-cr)/rd))for cu,cr,ru,rd,amp in patches),default=0)
      z=base-front*(frontweight+rearweight)-pocket
     vs.append(iv@point(rr,u,z));original.append(point(rr,u,z,False))
  layer=nu*nr;faces=[];iscore=[]
  def face(ids,core=False):faces.append(tuple(ids));iscore.append(core)
  for j in range(nr-1):
   for i in range(nu-1):
    a=j*nu+i;b=a+1;c=b+nu;d=a+nu;face((a,d,c));face((a,c,b))
    a+=layer;b+=layer;c+=layer;d+=layer
    if (i+j)%3:face((a,b,c),True);face((a,c,d),True)
    else:face((a,b,d),True);face((b,c,d),True)
  for i in range(nu-1):
   a=i;b=i+1;face((a,b,b+layer));face((a,b+layer,a+layer));a=(nr-1)*nu+i;b=a+1;face((a,a+layer,b+layer));face((a,b+layer,b))
  for j in range(nr-1):
   a=j*nu;b=(j+1)*nu;face((a,a+layer,b+layer));face((a,b+layer,b));a=j*nu+nu-1;b=(j+1)*nu+nu-1;face((a,b,b+layer));face((a,b+layer,a+layer))
  me=bpy.data.meshes.new('126 ordered crown '+name);me.from_pydata(vs,[],faces);me.update()
  for mat in old.materials:me.materials.append(mat)
  attr=me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
  for d,v in zip(attr.data,original):d.vector=v
  mask=me.attributes.new('117 Exposed core','FLOAT','FACE');me.attributes.new('117 Damage proximity','FLOAT','POINT');me.attributes.new('118 Recess interior','FLOAT','FACE')
  for d,b in zip(mask.data,iscore):d.value=float(b)
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob.data=me;check=topology(ob)
  if check['nonmanifold']or check['strict_crossings']or check['volume']<=0:raise RuntimeError('Invalid ordered seed '+name+str(check))
  records.append({'object':name,'seed':check,'original_control_profile':ctrl,'notch_profiles':notches,'core_depressions':patches,'grid_u':nu,'grid_depth':nr,'minimum_retained_height_authored_m':min(piece(u,ctrl)-max((piece(u,c)for c in notches),default=0)-62.559986 for u in us)})
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'seed.blend'));print('SEED_VALID',records,flush=True)
 text=(R/'tools/coliseum_structure_119.py').read_text().split("if __name__=='__main__':")[0];text=text.replace('du=.14*math.sin(k*2.17+ring*1.3)*math.sin(math.pi*t);dz=.16*math.cos(k*1.71-ring*.8)*math.sin(math.pi*t)','du=0.;dz=0.');text=text.replace("old=ob.data;ob.data=old.copy();before=", "old=ob.data;before_cross=strict_crossings(ob);ob.data=old.copy();before=");text=text.replace("if bad or (after[0]and volume<=0):", "after_cross=strict_crossings(ob)\n   if bad or (after[0]and volume<=0) or after_cross>before_cross:");text=text.replace("'volume':volume});continue", "'volume':volume,'strict_before':before_cross,'strict_after':after_cross});continue");text=text.replace("'outside_cutter_max_error_m':outside_error", "'outside_cutter_max_error_m':outside_error,'strict_before':before_cross,'strict_after':after_cross")
 ns={'__file__':str(R/'tools/coliseum_structure_119.py'),'__name__':'replay119_seed126','strict_crossings':strict_crossings};exec(compile(text,'<126 macro replay>','exec'),ns);replay=ns['build_visible_bay'](C)
 for row in records:row['after_macro']=topology(bpy.data.objects[row['object']])
 audit={'references':['UCL-01','UCL-02','DP-03'],'method':'Ordered single-valued negative crown height graph on clean111, exactE/yaw, then guarded119 macro replay','records':records,'replay':replay,'preview_source':'125 scene; accepted20% width/5% height independent of crown geometry'};(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'construction.blend'))
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-125/scene.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(O/'baseline.blend'));integration=apply_prepared(bpy.data.collections['110 Coliseum detailed front ruin'],allow_incomplete_study=True);(O/'integration.json').write_text(json.dumps(integration,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print('COMPLETE',integration,flush=True)
if __name__=='__main__':run()
