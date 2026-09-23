"""Reconstruct projected opening volumes from existing recessed ground faces and clip lips."""
import bpy,bmesh,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def apply(s):
 g=bpy.data.objects['Street foundation'];tri=[];grid={}
 for f in g.data.polygons:
  if f.material_index!=1:continue
  pts=[tuple((g.matrix_world@g.data.vertices[i].co)[:2]) for i in f.vertices]
  if len(pts)!=3:continue
  area=sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))
  if abs(area)<1e-8:continue
  if area<0:pts.reverse()
  n=len(tri);tri.append(pts);xs=[p[0] for p in pts];ys=[p[1] for p in pts]
  for x in range(math.floor(min(xs)),math.floor(max(xs))+1):
   for y in range(math.floor(min(ys)),math.floor(max(ys))+1):grid.setdefault((x,y),set()).add(n)
 report=[]
 for ob in list(s.objects):
  if not ob.name.startswith('077 broken earth lip'):continue
  pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(v[j] for v in pts) for j in range(2)];hi=[max(v[j] for v in pts) for j in range(2)];ids=set()
  for x in range(math.floor(lo[0]),math.floor(hi[0])+1):
   for y in range(math.floor(lo[1]),math.floor(hi[1])+1):ids.update(grid.get((x,y),set()))
  vs=[];fs=[]
  for idx in ids:
   p=tri[idx]
   if max(v[0] for v in p)<lo[0] or min(v[0] for v in p)>hi[0] or max(v[1] for v in p)<lo[1] or min(v[1] for v in p)>hi[1]:continue
   k=len(vs);vs.extend([(x,y,z) for z in (-.5,.2) for x,y in p]);fs.extend([(k+2,k+1,k),(k+3,k+4,k+5),(k,k+1,k+4,k+3),(k+1,k+2,k+5,k+4),(k+2,k,k+3,k+5)])
  if not vs:continue
  mesh=bpy.data.meshes.new('081 reconstructed crack void');mesh.from_pydata(vs,[],fs);c=bpy.data.objects.new(mesh.name,mesh);s.collection.objects.link(c)
  bpy.context.view_layer.objects.active=ob;sol=ob.modifiers.new('081 lip volume','SOLIDIFY');sol.thickness=.006;bpy.ops.object.modifier_apply(modifier=sol.name)
  mod=ob.modifiers.new('081 all crossing voids','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.use_self=True;mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True);ob['081_void_clipped']=True;report.append(ob.name)
 return {'reconstructed_projected_recess_triangles':len(tri),'clipped_lips':len(report)}
if __name__=='__main__':
 O=R/'art/studies/soil-081';bpy.ops.wm.open_mainfile(filepath=str(O/'discrete-scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;rep=apply(s);(O/'lip-repair.json').write_text(json.dumps(rep,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'selected-scene.blend'));s.render.filepath=str(O/'selected-main.png');bpy.ops.render.render(write_still=True)
