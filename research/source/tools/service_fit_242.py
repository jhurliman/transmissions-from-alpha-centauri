"""Native side-clearance brackets and clean receiver roof termination."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def prism_mesh(name,poly,z0,z1):
 n=len(poly);v=[(x,y,z) for z in (z0,z1)for x,y in poly];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update();return m

def apply(scene):
 if scene.get('242 service fit'):return {'already_applied':True}
 changes=[]
 for suffix in ['', '.001','.002','.003']:
  ob=bpy.data.objects['U-return bracket'+suffix];old=ob.data
  pts=[ob.matrix_world@v.co for v in old.vertices];wall=min(v.x for v in pts);z0=min(v.z for v in pts);z1=max(v.z for v in pts)
  # Folded dogleg bypasses the duct on its far-Y side, retaining the pipe clamp.
  poly=[(wall,5.97),(-8.25,5.97),(-8.25,5.415),(-8.08,5.415),(-8.08,6.14),(wall,6.14)]
  me=prism_mesh('242 clearance dogleg '+suffix,poly,z0,z1)
  inv=ob.matrix_world.inverted()
  for v in me.vertices:v.co=inv@v.co
  for m in old.materials:me.materials.append(m)
  ob.data=me;ob['242 route']='Pipe clamp to wall plate, bypass duct far-Y side'
  plate=bpy.data.objects['U-return wall plate'+suffix]
  # Existing boxes have world-space vertices and identity origins.
  plate.data=plate.data.copy();delta=6.055-5.5
  for v in plate.data.vertices:v.co.y+=delta
  changes.append({'bracket':ob.name,'wall_plate':plate.name,'height_m':(z0+z1)/2,'route_xy':poly,'wall_plate_y':6.055})
 pier=bpy.data.objects['Vertical structural pier.003'];pier.data=pier.data.copy();inv=pier.matrix_world.inverted();before=max((pier.matrix_world@v.co).z for v in pier.data.vertices)
 for v in pier.data.vertices:
  p=pier.matrix_world@v.co
  if p.z>12.50:p.z=12.50;v.co=inv@p
 pier.data.update();scene['242 service fit']=True
 return {'brackets':changes,'pier':{'object':pier.name,'old_top_m':before,'new_top_m':12.5,'receiver_roof_m':12.57,'sealed_mesh':True},'materials':'Original slots retained unchanged','guard_implications':'Original objects retained; no new scene objects. Freestyle follows corrected geometry. Check baked contact ink at old brackets in final render.'}
if __name__=='__main__':
 O=R/'art/studies/service-fit-242';O.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/hybrid-finish-241/scene.blend'));a=apply(bpy.context.scene)
 (O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
 print(json.dumps(a),flush=True)
