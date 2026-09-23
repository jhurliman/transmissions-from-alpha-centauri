"""Native crown-strip monotone erosion; accepted125 triangles and macro openings retained."""
import bpy,bmesh,math,json,random,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-126/crown-deform';sys.path.insert(0,str(R/'tools'))
from coliseum_fine_fracture_125 import triangulate_render
from coliseum_crown_repair_123 import NAMES,topology
from coliseum_fracture_seed_126 import piece

def apply(C):
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-111/scene.blend'),link=False)as(src,dst):dst.objects=[next(n for n in src.objects if n=='COL110 U4 fractured upper wall L')]
 anchor=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=anchor.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(anchor)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);Y=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=Y@A@P;Fi=F.inverted();ac=-math.pi+8.5*math.tau/36;rows=[]
 profiles=json.loads((R/'art/studies/coliseum-126/fracture-seed/audit.json').read_text())['records']
 def uz(q):
  a=math.atan2(q.y,q.x);a=-math.pi/2+(a+math.pi/2)/.68
  return(a-ac)*75,q.z
 for ni,name in enumerate(NAMES):
  ob=bpy.data.objects[name];old=ob.data;triangulate_render(ob);base=topology(ob);me=ob.data;ctrl=profiles[ni]['original_control_profile'];curves=profiles[ni]['notch_profiles'];curves=[[(u,d*2.0)for u,d in c]for c in curves if ni==0 or c[0][0]>4.8]
  at=me.attributes.get('118 Recess interior');protected={i for f in me.polygons if at and at.data[f.index].value>.5 for i in f.vertices};pv=[uz(Fi@(ob.matrix_world@me.vertices[i].co))for i in protected]
  bm=bmesh.new();bm.from_mesh(me)
  # Shared edge subdivision keeps the original triangle surfaces exactly before deformation.
  eligible=[e for e in bm.edges if all((lambda uzv: uzv[1]>piece(uzv[0],ctrl)-1.6)(uz(Fi@(ob.matrix_world@v.co))) for v in e.verts)]
  bmesh.ops.subdivide_edges(bm,edges=eligible,cuts=7,use_grid_fill=True);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();sub=topology(ob)
  if sub['nonmanifold']or sub['strict_crossings']:ob.data=old;raise RuntimeError('Invalid subdivision '+name+str(sub))
  protected_sub={i for f in me.polygons if me.attributes.get('118 Recess interior') and me.attributes['118 Recess interior'].data[f.index].value>.5 for i in f.vertices}
  before=[v.co.copy()for v in me.vertices];moved=0;maxd=0;protected_change=0;iv=ob.matrix_world.inverted();attr=me.attributes.get('115 Original world position')
  for v in me.vertices:
   q=Fi@(ob.matrix_world@v.co);u,z=uz(q);height=piece(u,ctrl)
   if not height:continue
   # A conservative local protected-feature ceiling keeps all recessed macro vertices fixed.
   z0=max(height-1.5,max((pz+.025 for pu,pz in pv if abs(pu-u)<.65),default=0));h=height-z0
   if h<=.05 or z<=z0:continue
   d=min(max((piece(u,c)for c in curves),default=0),h*.45);t=max(0,min(1,(z-z0)/h));f=t*t*t*(t*(t*6-15)+10);delta=d*f
   if delta<1e-9:continue
   q.z-=delta;v.co=iv@(F@q);moved+=1;maxd=max(maxd,delta)
   if attr:attr.data[v.index].vector-=P.to_3x3()@Vector((0,0,delta))
  me.update();after=topology(ob);protected_change=max(((me.vertices[i].co-before[i]).length for i in protected_sub),default=0)
  if protected_change>1e-6:ob.data=old;raise RuntimeError('Protected recess moved '+str(protected_change))
  if after['nonmanifold']or after['strict_crossings']or after['volume']<=0:ob.data=old;raise RuntimeError('Invalid deformation '+name+str(after))
  if after['volume']>base['volume']+.001:ob.data=old;raise RuntimeError('Unexpected volume growth')
  rows.append({'object':name,'before':base,'subdivided':sub,'after':after,'moved_vertices':moved,'max_author_z_reduction':maxd,'derivative_lower_bound':1-1.875*.45,'protected_macro_vertices':len(protected),'protected_subdivided_max_change':protected_change,'method':'x/y fixed in accepted transformed author frame; quintic z fade above protected recess ceiling','new_objects':0});ob['126 monotone crown erosion']=True
 return rows
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-125/scene.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(O/'baseline.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print(a,flush=True)
