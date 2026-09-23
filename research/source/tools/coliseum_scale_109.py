"""Native untextured coliseum scale gate. No reference projection."""
import bpy,bmesh,math,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-109'
for label,radius,height in [('A',75,78),('B',104,108)]:
 started=time.time();bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/city-108/scene.blend'));s=bpy.context.scene;cam=s.camera.matrix_world.copy();hidden=[]
 for c in bpy.data.collections:
  if 'dome' in c.name.lower():
   hidden.extend(ob.name for ob in list(c.all_objects))
 for name in set(hidden):
  ob=bpy.data.objects.get(name)
  if ob:bpy.data.objects.remove(ob,do_unlink=True)
 C=bpy.data.collections.new('109 Coliseum scale '+label);s.collection.children.link(C);cy=272+radius
 m=bpy.data.materials.new('109 Untextured masonry clay');m.diffuse_color=(.34,.29,.27,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.34,.29,.27,1);bs.inputs['Roughness'].default_value=.85
 def mesh(name,vs,fs):
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('109 '+name,me);C.objects.link(ob);me.materials.append(m);return ob
 def point(r,a,z):return (r*math.cos(a),cy+r*math.sin(a),z)
 def slab(name,ri,ro,z0,z1,a0,a1,n=4):
  vs=[point(r,a0+(a1-a0)*j/n,z) for z in [z0,z1] for r in [ri,ro] for j in range(n+1)];L=n+1;fs=[]
  for j in range(n):fs.extend([(j,j+1,L+j+1,L+j),(2*L+j,3*L+j,3*L+j+1,2*L+j+1),(j,2*L+j,2*L+j+1,j+1),(L+j,L+j+1,3*L+j+1,3*L+j)])
  fs.extend([(0,L,3*L,2*L),(n,2*L+n,3*L+n,L+n)]);return mesh(name,vs,fs)
 count=36;step=math.tau/count;thick=radius*.065;pitch=height*.235;archhalf=radius*step*.34
 slab('continuous foundation',radius-thick*2,radius+1,0,height*.035,0,math.tau,144)
 for tier in range(3):
  bottom=height*.035+tier*pitch;top=bottom+pitch;spring=top-height*.028-archhalf
  for j in range(count):
   a=-math.pi/2+j*step
   slab('arcade pier',radius-thick,radius,bottom,top,a+step*.34,a+step*.66)
   # Actual semicircular soffit, inner and outer faces, closed wall thickness.
   N=24;vs=[]
   for rr in [radius-thick,radius]:
    for k in range(N+1):
     u=-archhalf+2*archhalf*k/N;ang=a+u/radius;lo=spring+math.sqrt(max(0,archhalf*archhalf-u*u));vs.extend([point(rr,ang,lo),point(rr,ang,top)])
   L=2*(N+1);fs=[]
   for k in range(N):
    p=k*2;fs.extend([(p,p+2,p+3,p+1),(L+p,L+p+1,L+p+3,L+p+2),(p,L+p,L+p+2,p+2),(p+1,p+3,L+p+3,L+p+1)])
   fs.extend([(0,1,L+1,L),(2*N,L+2*N,L+2*N+1,2*N+1)]);mesh('deep arch tunnel',vs,fs)
  slab('projecting floor band',radius-thick*1.6,radius+height*.009,top,top+height*.021,0,math.tau,144)
 # Heavy upper wall with sparse actual slots; coarse connected crown loss, not final fracture detail.
 base=height*.761
 for j in range(count):
  a=-math.pi/2+j*step;h=height*([.93,.96,.90,.975,.94,.92][j%6]);slotw=step*.11
  slab('upper wall sill',radius-thick,radius,base,base+height*.045,a-step/2,a+step/2)
  slab('upper wall left',radius-thick,radius,base+height*.045,h,a-step/2,a-slotw)
  slab('upper wall right',radius-thick,radius,base+height*.045,h,a+slotw,a+step/2)
  slab('upper opening head',radius-thick,radius,base+height*.09,h,a-slotw,a+slotw)
 # Towers join piers every sixth bay; rear towers deliberately retained.
 for j in range(0,count,6):
  a=-math.pi/2+(j+.5)*step;w=step*.22
  slab('projecting tower',radius-thick*.6,radius+thick*.6,0,height,a-w,a+w)
  for z in [.04,.275,.51,.745,.96]:slab('tower collar',radius-thick*.65,radius+thick*.73,height*z,height*(z+.019),a-w*1.12,a+w*1.12)
 # Sparse radial floor connections give depth inside selected openings; open court stays open.
 for j in range(0,count,6):
  a=-math.pi/2+j*step
  for z in [.27,.505]:slab('radial interior landing',radius-thick*3,radius-thick,height*z,height*(z+.015),a-step*.25,a+step*.25)
 assert s.camera.matrix_world==cam
 folder=O/label;folder.mkdir(exist_ok=True);s.render.use_border=False;s.render.use_crop_to_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=True;s.render.filepath=str(folder/'main.png')
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'));build=time.time()-started;bpy.ops.render.render(write_still=True)
 (folder/'audit.json').write_text(json.dumps({'radius':radius,'height':height,'nearest_wall':272,'tiers':3,'bays_per_ring':36,'closed_ring':True,'hidden_placeholder_objects':len(set(hidden)),'new_objects':len(C.objects),'camera_preserved':True,'untextured':True,'generation_seconds':build,'render_seconds':time.time()-started-build},indent=2))
