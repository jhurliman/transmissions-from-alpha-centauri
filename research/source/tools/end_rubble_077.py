"""Replace legacy low flat debris polygons with grouped, volumetric end rubble."""
import bpy,bmesh,math,random,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/end-rubble-077'
def apply(scene):
 old=bpy.data.collections.get('077 End rubble depth clusters')
 if old:return {'already_applied':True}
 rng=random.Random(77108);col=bpy.data.collections.new('077 End rubble depth clusters');scene.collection.children.link(col)
 hidden=[]
 for ob in scene.objects:
  if 'collapsed rubble' in ob.name:
   ob.hide_render=True;hidden.append(ob.name)
 source=bpy.data.collections['075 Scrap integration'];scrap=[o for o in source.all_objects if o.get('zone')=='end' and o.type=='MESH']
 matcache={}
 def quiet(m):
  if m in matcache:return matcache[m]
  q=m.copy();q.name='077 End rubble | '+m.name.split('|')[-1].strip();matcache[m]=q
  if q.use_nodes:
   for n in q.node_tree.nodes:
    if n.type=='BSDF_GLOSSY':n.inputs['Color'].default_value=(.025,.02,.017,1);n.inputs['Roughness'].default_value=.65
  return q
 mats=[quiet(bpy.data.materials['075 Scrap | mineral dusty slate']),quiet(bpy.data.materials['075 Scrap | muted oxidized metal']),quiet(bpy.data.materials['075 Scrap | accepted service metal darkened'])]
 def shard(name,x,y,z,r,h,mat):
  N=rng.choice([5,6,7]);angles=[math.tau*j/N+rng.uniform(-.1,.1) for j in range(N)];rr=[r*rng.uniform(.72,1.12) for j in range(N)];vs=[]
  for k in range(2):
   for j,a in enumerate(angles):vs.append((x+rr[j]*math.cos(a)*(1 if k==0 else rng.uniform(.55,.9)),y+rr[j]*math.sin(a)*(1 if k==0 else rng.uniform(.55,.9)),z if k==0 else z+h*rng.uniform(.5,1)))
  fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat);return ob
 audit=[];ni=0;ns=0
 # Low debris through an extended near-to-city transition. The meandering path stays open.
 layers=[(34,7.5,5),(43,10,6),(56,13,6),(73,18,6),(96,25,5),(125,35,5),(165,45,4),(220,60,4)]
 for layer,(depth,spread,groups) in enumerate(layers):
  for j in range(groups):
   sign=-1 if j%2==0 else 1;x=sign*rng.uniform(4.4,spread);y=depth+rng.uniform(-2.2,2.2);radius=rng.uniform(1.2,2.5)*(1+.09*layer);height=rng.uniform(.32,.68)*(1+.07*layer);count=18 if layer<3 else 13 if layer<5 else 8
   audit.append({'center':[x,y],'radius':radius,'height':height})
   for k in range(count):
    a=rng.uniform(0,math.tau);d=radius*math.sqrt(rng.random());px=x+math.cos(a)*d;py=y+math.sin(a)*d
    corridor=math.sin(py*.033)*2.2
    if abs(px-corridor)<1.15:continue
    rr=rng.uniform(.18,.6)*(1+.05*layer);h=height*rng.uniform(.4,1.2)*(1-.35*d/radius)
    if k<2:rr*=1.8;h*=1.2
    shard('077 layered masonry fragment',px,py,-.025,rr,h,rng.choice([mats[0],mats[0],mats[1],mats[2]]));ni+=1
   for k in range(5 if layer<5 else 3):
    src=rng.choice(scrap);o=src.copy();o.data=src.data.copy();
    for mi,mm in enumerate(o.data.materials):
     if mm:o.data.materials[mi]=quiet(mm)
    o.name='077 bent industrial scrap remnant';col.objects.link(o);o.location=(x+rng.uniform(-radius,radius),y+rng.uniform(-radius,radius),rng.uniform(.02,.2));o.rotation_euler=(rng.uniform(.7,1.6) if 'hollow casing' in src.name else rng.uniform(-.25,.35),rng.uniform(-.3,.3),rng.uniform(-math.pi,math.pi));scale=rng.uniform(.45,.95)*(1+.05*layer);o.scale=(scale,scale,scale);o['zone']='end depth';ns+=1
 # Alternating low broken tongues interrupt the former straight empty boulevard.
 for cx,cy in [(-1.3,37),(3.3,47),(-.5,60),(3,79),(-2,102)]:
  for k in range(22):
   px=cx+rng.uniform(-1.6,1.6);py=cy+rng.uniform(-1.1,1.1)
   if abs(px-math.sin(py*.033)*2.2)<.9:continue
   shard('077 broken low rubble tongue',px,py,-.025,rng.uniform(.16,.6),rng.uniform(.12,.45),rng.choice(mats));ni+=1
 # Sparse chips connect clusters rather than continuous flat islands.
 for j in range(150):
  y=rng.uniform(31,105);x=rng.uniform(-14,14)
  if abs(x-math.sin(y*.033)*2.2)<1.4 and rng.random()<.65:continue
  shard('077 interstitial small debris',x,y,-.025,rng.uniform(.06,.22),rng.uniform(.04,.14),rng.choice(mats));ni+=1
 return {'collection':col.name,'hidden_old_collapsed_rubble':len(hidden),'mineral_fragments':ni,'shared_scrap_instances':ns,'clusters':audit,'preserved':'near scrap geometry, alley architecture, camera, depth gap; meandering passage and low alternating rubble tongues'}
def apply_detail(scene):
 """Add intersecting structural silhouettes; independent from approved077 base."""
 from mathutils import Vector
 name='078 End rubble tangled structural remnants'
 if bpy.data.collections.get(name):return {'already_applied':True}
 col=bpy.data.collections.new(name);scene.collection.children.link(col);rng=random.Random(78041)
 mats=[m for m in bpy.data.materials if m.name.startswith('077 End rubble |')]
 if not mats:raise RuntimeError('Run apply(scene) before apply_detail(scene)')
 metal=next((m for m in mats if 'service metal' in m.name),mats[0]);rust=next((m for m in mats if 'oxidized' in m.name),metal);stone=next((m for m in mats if 'mineral' in m.name),metal)
 def mesh(label,vs,fs,mat):
  me=bpy.data.meshes.new(label);me.from_pydata(vs,[],fs);me.materials.append(mat);ob=bpy.data.objects.new(label,me);col.objects.link(ob);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return ob
 def beam(a,b,w,mat):
  # An actual hollow channel with two flanges and a web, jagged severed end.
  a=Vector(a);v=Vector(b)-a;L=v.length
  local_rng=random.Random(str(tuple(a))+str(tuple(b)))
  for _ in range(12):rng.random() # Preserve the established placement random stream.
  bend_y=local_rng.uniform(-.15,.15);bend_z=local_rng.uniform(-.14,.19);kink=local_rng.uniform(.4,.68)
  for part,(yy,zz,wy,wz) in enumerate([(0,0,w,.045),(0,w*.46,w,.045),(-w*.46,w*.23,.045,w*.5)]):
   vs=[]
   for ring,t in enumerate([0,kink,1]):
    dy=bend_y*(t/kink if t<kink else (1-t)/(1-kink));dz=bend_z*(t/kink if t<kink else (1-t)/(1-kink))
    for cy,cz in [(-1,-1),(-1,1),(1,1),(1,-1)]:
     xx=L*t+(local_rng.uniform(-.18,.09) if ring==2 else local_rng.uniform(-.055,.055) if ring==0 else 0)
     vs.append((xx,yy+cy*wy/2+dy,zz+cz*wz/2+dz))
   fs=[(3,2,1,0),(8,9,10,11)]
   for ring in range(2):
    for j in range(4):fs.append((ring*4+j,ring*4+(j+1)%4,(ring+1)*4+(j+1)%4,(ring+1)*4+j))
   ob=mesh('078 severed kinked channel '+str(part),vs,fs,mat);ob.location=a;ob.rotation_euler=v.to_track_quat('X','Z').to_euler()

 def slab(x,y,z,w,h,angle,mat):
  outline=[(-w/2,0),(-w*.46,h*.8),(-w*.31,h),(-w*.13,h*.88),(w*.19,h*.96),(w*.26,h*.72),(w*.5,h*.66),(w*.47,0)];vs=[(xx,dd,zz) for dd in [-.065,.065] for xx,zz in outline];n=len(outline);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];ob=mesh('078 torn projecting sheet',vs,fs,mat);ob.location=(x,y,z);ob.rotation_euler=(math.radians(angle),rng.uniform(-.45,.45),rng.uniform(-1,1))
 def pipe(x,y,z,L,r,angle):
  N=12;vs=[]
  for zz in [0,L]:
   for rad in [r,r*.76]:
    for i in range(N):vs.append((rad*math.cos(i*math.tau/N),rad*math.sin(i*math.tau/N),zz+(rng.uniform(-.1,.1) if zz else 0)))
  fs=[]
  for i in range(N):
   j=(i+1)%N;fs.extend([(i,j,2*N+j,2*N+i),(N+j,N+i,3*N+i,3*N+j),(2*N+i,2*N+j,3*N+j,3*N+i)])
  ob=mesh('078 hollow severed pipe',vs,fs,metal);ob.location=(x,y,z);ob.rotation_euler=(math.radians(angle),.4,rng.uniform(-2,2))
 groups=[(-6,31.8,1.0),(6.6,33.4,1.1),(-5,40,.85),(8.2,44,.95),(-8.7,54,1.0),(10,61,.85)]
 for k,(x,y,scale) in enumerate(groups):
  sign=1 if x<0 else -1
  beam((x-sign*rng.uniform(.6,1.4),y-.3,.12),(x+sign*rng.uniform(.5,1.9),y+rng.uniform(-.5,1.5),rng.uniform(.7,1.8)*scale),.32*scale,rust if k%2 else metal)
  beam((x+sign*rng.uniform(.7,1.5),y-.7,.15),(x-sign*rng.uniform(.2,.9),y+rng.uniform(.4,2),rng.uniform(.25,.75)*scale),.21*scale,metal)
  beam((x-1.5,y+.9,.18),(x+1.1,y+.65,.5),.18,rust)
  slab(x+.5,y+.3,.12,1.7*scale,1.1*scale,52 if k%2 else 38,stone if k%3==0 else rust)
  if k in [0,1,3]:pipe(x-.6,y+.5,.12,1.4*scale,.25*scale,58)
 return {'collection':name,'objects':len(col.objects),'structural_groups':len(groups),'preserved':'base077 objects, approved near geometry, camera; no additional rocks','intent':'intersecting 20–55 degree channel silhouettes, torn sheets and hollow pipes'}

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-075/scene.blend'));s=bpy.context.scene;report=apply(s);(O/'changes.json').write_text(json.dumps(report,indent=2));s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
 s.render.resolution_x=2880;s.render.resolution_y=2160;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.30;s.render.border_max_x=.69;s.render.border_min_y=.49;s.render.border_max_y=.66;s.render.filepath=str(O/'end.png');bpy.ops.render.render(write_still=True)
