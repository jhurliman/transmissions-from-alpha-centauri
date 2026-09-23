import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-074';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-073/scene.blend'));s=bpy.context.scene;cam=s.camera.matrix_world.copy();steel=bpy.data.materials['Structure | charcoal steel']
for ob in bpy.data.objects:
 if ob.type=='MESH' and ob.name.startswith('073 bracket gusset'):
  ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(steel)
# Replace applied-on closure plates with the column's own finished solid return.
fixed=[]
for col in bpy.data.collections:
 jamb=next((o for o in col.objects if o.name.startswith('Inset window jamb return')),None)
 if not jamb:continue
 m=jamb.data.materials[0]
 for ob in list(col.objects):
  if ob.name.startswith(('073 kick side column return','Inset window jamb return')):bpy.data.objects.remove(ob,do_unlink=True)
  elif ob.name.startswith('Pier backing'):
   ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(m)
   # Match the exact inner edge of the facing panel and kick, removing the lip.
   for v in ob.data.vertices:
    if abs(abs(v.co.x)-.975)<.001:v.co.x=math.copysign(.99,v.co.x)
   fixed.append(ob.name)
# Move only the y=8 round service train, preserving each prefab's dimensions.
T=Matrix.Translation((9.8,5.25,0))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation((-9,-8,0));moved=[]
for ob in list(s.objects):
 p=ob.matrix_world.translation
 if ob.instance_collection and not ob.hide_render and abs(p.x-9)<.001 and abs(p.y-8)<.001 and 'PIP' in ob.instance_collection.name:
  ob.matrix_world=T@ob.matrix_world;moved.append(ob.name)
# Remove old facade fastenings and elbow/receiver; rebuild for the tighter wall datum.
for ob in list(s.objects):
 if ob.name.startswith(('Round riser wall elbow','Round wall receiver')):
  ob.hide_render=True;ob.hide_viewport=True
 if ob.type=='MESH' and ob.name.startswith(('Riser wall standoff','073 standoff wall extension')):
  pts=[ob.matrix_world@Vector(v) for v in ob.bound_box]
  if abs(sum(p.y for p in pts)/8-8)<.001 and sum(p.x for p in pts)/8>0:bpy.data.objects.remove(ob,do_unlink=True);continue
 if ob.instance_collection and ob.name.startswith('073 bolted wall shoe') and abs(ob.location.y-8)<.001:bpy.data.objects.remove(ob,do_unlink=True)
C=bpy.data.collections.new('074 Side alley pipe relocation');s.collection.children.link(C)
def mesh(n,vs,fs,m):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.materials.append(m);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);C.objects.link(o);return o
def box(n,p,d,m):
 vs=[(p[0]+i*d[0]/2,p[1]+j*d[1]/2,p[2]+k*d[2]/2) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 o=mesh(n,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m);b=o.modifiers.new('Manufactured chamfer','BEVEL');b.width=.008;b.segments=1;return o
metal=bpy.data.materials.get('DUCT | muted blue-gray sheet');shoe=bpy.data.collections['KIT | 073 bolted wall shoe'];narrow=shoe.copy();narrow.name='KIT | 074 narrow pilaster wall shoe';narrow.asset_mark()
# Rebuild width only; keep steel thickness, length, bolt sizes and gussets unchanged.
for ob in list(narrow.objects):
 narrow.objects.unlink(ob);q=ob.copy();q.data=ob.data.copy();narrow.objects.link(q)
 if 'backplate' in q.name:
  for v in q.data.vertices:v.co.x*=.48
 elif 'anchor' in q.name:
  center=sum(v.co.x for v in q.data.vertices)/len(q.data.vertices)
  for v in q.data.vertices:v.co.x-=math.copysign(.11,center)
for z in [1.2,3.9,6.6,9.3,12]:
 box('074 short pipe arm',(9.8,5.5375,z),(.16,.575,.12),steel)
 o=bpy.data.objects.new('074 pilaster shoe',None);o.instance_type='COLLECTION';o.instance_collection=narrow;C.objects.link(o);o.location=(9.8,5.825,z)
# Top quarter bend enters an attached receiver above the pilaster, with no open terminal.
pts=[Vector((9.8,5.25,14.92))]+[Vector((9.8,5.25+.35*(1-math.cos(i*math.pi/32)),14.92+.35*math.sin(i*math.pi/32))) for i in range(1,17)]+[Vector((9.8,5.95,15.27))]
vs=[];N=32
for i,p in enumerate(pts):
 t=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized();u=Vector((1,0,0));v=t.cross(u).normalized()
 vs.extend([tuple(p+.2*(u*math.cos(j*math.tau/N)+v*math.sin(j*math.tau/N))) for j in range(N)])
fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(len(pts)-1) for j in range(N)]
o=mesh('074 wall entry elbow',vs,fs,metal)
for f in o.data.polygons:f.use_smooth=True
box('074 wall receiver',(9.8,5.87,15.27),(.65,.28,.65),metal)
box('074 floor penetration curb',(9.8,5.25,.08),(.64,.64,.16),steel)
assert s.camera.matrix_world==cam
K=R/'art/components/facades/v074';K.mkdir(exist_ok=True);bpy.data.libraries.write(str(K/'wall-shoes.blend'),{shoe,narrow},fake_user=True)
(O/'changes.json').write_text(json.dumps({'moved_pipe_components':moved,'integrated_column_returns':fixed,'pipe_axis':[9.8,5.25],'wall_mount_datum':5.825,'endpoints':['floor penetration curb','wall receiver at 15.27m'],'gussets':'same charcoal steel as arms','camera_preserved':True},indent=2))
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=2880;s.render.resolution_y=2160;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.62;s.render.border_max_x=1;s.render.border_min_y=.22;s.render.border_max_y=.95;s.render.filepath=str(O/'right.png');bpy.ops.render.render(write_still=True)
