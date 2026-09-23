import bpy,bmesh,json,sys,math,types
from pathlib import Path
from mathutils import geometry
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from coliseum_crown_repair_123 import strict_crossings
O=R/'art/studies/coliseum-134/topology-diagnostics';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-134/standalone/scene.blend'));dg=bpy.context.evaluated_depsgraph_get()
issues=json.loads((R/'art/studies/coliseum-134/evaluated-crossings-baseline.json').read_text())['issues'];rows=[]
def components(me):
 parent=list(range(len(me.vertices)))
 def root(i):
  while i!=parent[i]:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in me.edges:
  a,b=[root(i)for i in e.vertices];parent[a]=b
 return [root(i)for i in range(len(parent))]
def inspect(ob,evaluated=True):
 ev=ob.evaluated_get(dg)if evaluated else ob;me=ev.to_mesh()if evaluated else ob.data;tmp=types.SimpleNamespace(data=me,matrix_world=ev.matrix_world);pairs=strict_crossings(tmp,True);me.calc_loop_triangles();cc=components(me);ts=list(me.loop_triangles);same=0;other=0;lengths=[];depths=[]
 for i,j in pairs:
  A=[ev.matrix_world@me.vertices[k].co for k in ts[i].vertices];B=[ev.matrix_world@me.vertices[k].co for k in ts[j].vertices]
  if cc[ts[i].vertices[0]]==cc[ts[j].vertices[0]]:same+=1
  else:other+=1
  hits=[];dep=0
  for V,W in [(A,B),(B,A)]:
   n=(W[1]-W[0]).cross(W[2]-W[0]).normalized()
   for k in range(3):
    a,b=V[k],V[(k+1)%3];d=b-a
    if d.length<1e-10:continue
    d0=(a-W[0]).dot(n);d1=(b-W[0]).dot(n)
    if d0*d1>=0:continue
    h=geometry.intersect_ray_tri(*W,d.normalized(),a,True)
    if h is not None and -1e-6<(h-a).dot(d.normalized())<d.length+1e-6:hits.append(h);dep=max(dep,min(abs(d0),abs(d1)))
  lengths.append(max(((a-b).length for a in hits for b in hits),default=0));depths.append(dep)
 def stats(a):
  a=sorted(a);return {'max_m':max(a,default=0),'median_m':a[len(a)//2]if a else 0,'p95_m':a[min(len(a)-1,int(len(a)*.95))]if a else 0}
 res={'strict_crossings':len(pairs),'components':len(set(cc)),'same_component_pairs':same,'different_component_pairs':other,'intersection_segment':stats(lengths),'plane_crossing_depth_proxy':stats(depths),'ngons':sum(len(p.vertices)>4 for p in me.polygons),'quads':sum(len(p.vertices)==4 for p in me.polygons),'triangles':sum(len(p.vertices)==3 for p in me.polygons)}
 if evaluated:ev.to_mesh_clear()
 return res
for i in issues:
 ob=bpy.data.objects[i['object']];r={'object':ob.name,'raw':inspect(ob,False),'evaluated':inspect(ob,True),'modifiers':[(m.name,m.type)for m in ob.modifiers]};rows.append(r)
(O/'classification.json').write_text(json.dumps(rows,indent=2));print('CLASSIFIED',len(rows),flush=True)
trials=[]
for name in ['COL110 U15 fractured upper wall R','COL110 U10 fractured upper wall L','COL110 U9 fractured upper wall R','COL110 U9 aperture head']:
 src=bpy.data.objects[name];base=inspect(src,True)
 for mode in ['BEAUTY','EAR_CLIP']:
  ob=src.copy();ob.data=src.data.copy();bpy.context.scene.collection.objects.link(ob);orig=[v.co.copy()for v in ob.data.vertices];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method=mode);bm.to_mesh(ob.data);bm.free();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();after=inspect(ob,True);beforeverts={tuple(v)for v in orig};delta=max((min((v.co-a).length for a in orig)for v in ob.data.vertices if tuple(v.co)not in beforeverts),default=0)
  trials.append({'object':name,'method':mode,'baseline':base,'candidate':after,'vertex_delta_m':delta,'vertex_count_delta':len(ob.data.vertices)-len(orig)})
  bpy.data.objects.remove(ob,do_unlink=True)
(O/'triangulation-trials.json').write_text(json.dumps(trials,indent=2));print('TRIALS',len(trials),flush=True)
