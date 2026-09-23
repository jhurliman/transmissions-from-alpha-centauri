import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-081';bpy.ops.wm.open_mainfile(filepath=str(O/'selected-scene.blend'));g=bpy.data.objects['Street foundation'];audit=json.loads((O/'junction-audit.json').read_text());names=set(x['object'] for x in audit['selected-scene.blend']['bad_points'])
tri=[]
for f in g.data.polygons:
 if f.material_index!=1 or len(f.vertices)!=3:continue
 p=[g.matrix_world@g.data.vertices[i].co for i in f.vertices];a=sum(p[i].x*p[(i+1)%3].y-p[(i+1)%3].x*p[i].y for i in range(3))
 if abs(a)<1e-9:continue
 if a<0:p.reverse()
 tri.append(p)
def split(poly,a,b):
 inside=[];outside=[]
 def d(v):return (b.x-a.x)*(v.y-a.y)-(b.y-a.y)*(v.x-a.x)
 for i,p in enumerate(poly):
  q=poly[(i+1)%len(poly)];dp=d(p);dq=d(q)
  (inside if dp>=0 else outside).append(p)
  if (dp>=0)!=(dq>=0):v=p.lerp(q,dp/(dp-dq));inside.append(v);outside.append(v)
 return inside,outside
for name in names:
 ob=bpy.data.objects[name];ob.data.calc_loop_triangles();vs=[];fs=[]
 for f in ob.data.loop_triangles:
  pieces=[[ob.matrix_world@ob.data.vertices[i].co for i in f.vertices]]
  for t in tri:
   if not pieces:break
   if max(v.x for v in t)<min(v.x for p in pieces for v in p) or min(v.x for v in t)>max(v.x for p in pieces for v in p) or max(v.y for v in t)<min(v.y for p in pieces for v in p) or min(v.y for v in t)>max(v.y for p in pieces for v in p):continue
   result=[]
   for p in pieces:
    current=p
    for k in range(3):
     if len(current)<3:break
     current,other=split(current,t[k],t[(k+1)%3])
     if len(other)>=3:result.append(other)
   pieces=result
  for p in pieces:
   for i in range(1,len(p)-1):
    if (p[i]-p[0]).cross(p[i+1]-p[0]).length<1e-10:continue
    start=len(vs);vs.extend([tuple(ob.matrix_world.inverted()@v) for v in [p[0],p[i],p[i+1]]]);fs.append((start,start+1,start+2))
 me=bpy.data.meshes.new(name+' exact planar clipping');me.from_pydata(vs,[],fs)
 for m in ob.data.materials:me.materials.append(m)
 ob.data=me
bpy.ops.wm.save_as_mainfile(filepath=str(O/'selected-scene.blend'));print('PLANAR CLEANUP',list(names))
