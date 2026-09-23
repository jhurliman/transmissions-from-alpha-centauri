"""Read-only native upperwall inventory for controlled post119 assembly planning."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-119';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-116/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin']
with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(s,d):d.objects=['COL110 U4 fractured upper wall L']
a=d.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=a.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;inv=P.inverted();bpy.data.objects.remove(a);results=[]
vis=json.loads((R/'art/studies/coliseum-118/visibility-audit.json').read_text())['bays']
for j in [5,6,7,9,11,12]:
 ac=-math.pi+(j+.5)*math.tau/36;vs=[];fs=[];objects=[];data=[]
 for ob in C.objects:
  if ob.type!='MESH'or ob.get('bay')!=j or ob.get('tier')!=3 or ob.get('coliseum_role')!='wall':continue
  at=ob.data.attributes.get('115 Original world position')
  if not at:continue
  coords=[inv@d.vector for d in at.data];off=len(vs);vs+=coords;fs.extend(tuple(off+k for k in f.vertices)for f in ob.data.polygons);uv=[]
  for p in coords:
   ang=math.atan2(p.y,p.x)
   if ang>math.pi/2:ang-=math.tau
   uv.append(((ang-ac)*75,p.z))
  data+=uv;objects.append({'name':ob.name,'u_range':[min(u for u,z in uv),max(u for u,z in uv)],'z_range':[min(z for u,z in uv),max(z for u,z in uv)]})
 tree=BVHTree.FromPolygons(vs,fs);profiles=[]
 for u in [-5,-3,0,3,5]:
  ang=ac+u/75;direction=Vector((-math.cos(ang),-math.sin(ang),0));zs=[]
  for k in range(45):
   z=59+k*.5;rr=76*(1-.055*z/78);origin=Vector((rr*math.cos(ang),rr*math.sin(ang),z));hit=tree.ray_cast(origin,direction,12)
   if hit[0]is not None:zs.append(z)
  runs=[]
  for z in zs:
   if not runs or z-runs[-1][1]>.51:runs.append([z,z])
   else:runs[-1][1]=z
  profiles.append({'u':u,'solid_z_intervals_half_meter_sampling':runs})
 v=next(v for v in vis if v['bay']==j);results.append({'bay':j,'wall_objects':objects,'authored_z_range':[min(z for u,z in data),max(z for u,z in data)],'radial_front_occupancy':profiles,'previous_main_visibility':v})
report={'source':'art/studies/coliseum-116/scene.blend','coordinates':'Authored original ring meters, tangential u relative each bay center and z. Occupancy ray probes radial inward through original-world wall mesh; 0.5m z samples are planning evidence, not certified clearance.','bays':results,'state':'Inventory only; source scene read, never saved or mutated on disk.'};(O/'assembly-inventory.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
