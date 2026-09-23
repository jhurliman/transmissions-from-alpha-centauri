"""Bounded exposed masonry-course refinement of128's connected B7 failure."""
import bpy,bmesh,math,json,sys,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping

def apply(C):
 start=time.time();base_audit=None
 wall=C.objects.get('COL127 T2 continuous arcade wall')
 if wall and wall.get('129 masonry course relief'):return {'already_applied':True}
 if not any(o.get('128 connected junction') for o in C.objects):
  from coliseum_junction_128 import apply as apply_base
  base_audit=apply_base(C)
 original,world,unpack=mapping();a0=-math.pi+7.5*math.tau/36;records=[];removed=[]
 for name in ['COL110 T2 B07 archivolt1 stone09','COL110 T2 B07 archivolt0 stone10']:
  ob=C.objects.get(name)
  if ob and ob.get('128 connected junction'):
   removed.append({'object':name,'reason':'Thin residual molding tongue at existing failure, cleared back to surviving masonry.'});bpy.data.objects.remove(ob,do_unlink=True)
 courses=[(53.72,-3.55,-2.75,.17),(54.83,-3.5,-2.15,.23),(56.12,-3.05,-1.65,.20),(57.36,-2.7,-1.1,.16),(58.28,-2.45,-1.0,.18)]
 for ob in list(C.objects):
  if ob.type!='MESH' or not ob.get('128 connected junction'):continue
  if 'continuous arcade wall'not in ob.name and 'band07 profile'not in ob.name:continue
  old=ob.data;ob.data=old.copy();bm=bmesh.new();bm.from_mesh(ob.data);mask=bm.faces.layers.float.get('117 Exposed core')
  if not mask:bm.free();continue
  def auth(v):
   rr,a,z=unpack(ob.matrix_world@v.co);return rr,(a-a0)*75,z
  def eligible(f):
   if f[mask]<.5:return False
   rr,u,z=auth(f.verts[0]);return -4.3<u<-.5 and 52.3<z<59.6
  cuts=0
  for zc,u0,u1,depth in courses:
   for z in [zc-.13,zc,zc+.13]:
    faces=[f for f in bm.faces if eligible(f) and min(auth(v)[2]for v in f.verts)<z<max(auth(v)[2]for v in f.verts)]
    if not faces:continue
    edges=set(e for f in faces for e in f.edges);verts=set(v for f in faces for v in f.verts);point=world(73,a0,z);t=world(73,a0+.001,z)-world(73,a0-.001,z);rad=world(74,a0,z)-world(72,a0,z);normal=t.cross(rad).normalized();localpoint=ob.matrix_world.inverted()@point;localnormal=(ob.matrix_world.to_3x3().transposed()@normal).normalized()
    result=bmesh.ops.bisect_plane(bm,geom=list(verts)+list(edges)+faces,plane_co=localpoint,plane_no=localnormal,dist=.000001,clear_inner=False,clear_outer=False);cuts+=len(result['geom_cut'])
  moved=0;maxoffset=0;fixedboundary=0
  for v in bm.verts:
   rr,u,z=auth(v)
   if not -4.25<u<-.5 or not 52.3<z<59.6 or rr>74.8:continue
   if not v.link_faces or any(f[mask]<.5 for f in v.link_faces):fixedboundary+=1;continue
   # Offset two surviving internal course levels; blend narrow interfaces only.
   def step(zc):return max(0,min(1,(z-(zc-.13))/.26))
   terrace=.5*step(53.72)-.5*step(54.83)+.65*step(56.12)-.53*step(57.36)-.12*step(58.28)
   radial_fade=max(0,min(1,(74.8-rr)/.8));amount=max(0,terrace)*radial_fade
   for zc,u0,u1,depth in courses:
    if u0<u<u1 and abs(z-zc)<.13001:
     edgefade=min(1,(u-u0)/.18,(u1-u)/.18);vertical=max(0,1-abs(z-zc)/.13);amount+=.35*depth*edgefade*vertical*radial_fade
   if amount>1e-7:v.co=ob.matrix_world.inverted()@world(rr-amount,a0+u/75,z);moved+=1;maxoffset=max(maxoffset,amount)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.to_mesh(ob.data);bm.free()
  assert bad==0,(ob.name,bad)
  pos=ob.data.attributes.get('115 Original world position');depthattr=ob.data.attributes.get('120 Actual arch tunnel depth')
  for v in ob.data.vertices:
   rr,a,z=unpack(ob.matrix_world@v.co)
   if pos:pos.data[v.index].vector=original(rr,a,z)
   if depthattr:depthattr.data[v.index].value=max(0,min(1,(75-rr)/8))
  ob['129 masonry course relief']=True;records.append({'object':ob.name,'vertices_before':len(old.vertices),'vertices_after':len(ob.data.vertices),'modified_vertices':moved,'maximum_radial_recess_m':maxoffset,'fixed_interface_vertices':fixedboundary,'nonmanifold_edges':bad,'volume':volume,'plane_cut_elements':cuts})
 return {'base_junction':base_audit,'references':['UCL-01','UCL-02','DP-03'],'source':'128 isolated B7 junction','courses':courses,'operations':records,'removed_tongues':removed,'scope':'Two offset course-scale terraces and interrupted bedding losses only on exposed fracture faces; adjacent intact interfaces fixed. Outer failure silhouette and original bearing retained except two residual rim tongues.','seconds':time.time()-start}

if __name__=='__main__':
 O=R/'art/studies/coliseum-129/junction';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-128/junction/scene.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
