from pathlib import Path
p=Path(__file__).with_name('diagnose.py');exec(compile(p.read_text().split('for i in issues:')[0],str(p),'exec'))
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src=bpy.data.objects['COL110 U15 fractured upper wall R'];ev=src.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);ob=bpy.data.objects.new('134 U15R exact envelope diagnostic',me);bpy.context.scene.collection.objects.link(ob);ob.matrix_world=ev.matrix_world.copy();before=inspect(ob,False)
def health(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);d={'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free();return d
hb=health(ob);oldvs=[ob.matrix_world@v.co for v in ob.data.vertices];oldfs=[tuple(p.vertices)for p in ob.data.polygons];tree=BVHTree.FromPolygons(oldvs,oldfs);lo=[min(v[k]for v in oldvs)-.5 for k in range(3)];hi=[max(v[k]for v in oldvs)+.5 for k in range(3)];vs=[(lo[0]if i==0 else hi[0],lo[1]if j==0 else hi[1],lo[2]if k==0 else hi[2])for i,j,k in[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]];cm=bpy.data.meshes.new('134 containing box');cm.from_pydata(vs,[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);co=bpy.data.objects.new(cm.name,cm);bpy.context.scene.collection.objects.link(co)
mod=ob.modifiers.new('134 Exact self-resolving envelope trial','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=co
for k in ['use_self','use_hole_tolerant']:
 if hasattr(mod,k):setattr(mod,k,True)
bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(co,do_unlink=True);after=inspect(ob,False);ha=health(ob);newvs=[ob.matrix_world@v.co for v in ob.data.vertices];ntree=BVHTree.FromPolygons(newvs,[tuple(p.vertices)for p in ob.data.polygons])if newvs else None
r={'before':before,'after':after,'before_health':hb,'after_health':ha,'new_vertex_to_old_surface_max_m':max((tree.find_nearest(v)[3]for v in newvs),default=None),'old_vertex_to_new_surface_max_m':max((ntree.find_nearest(v)[3]for v in oldvs),default=None)if ntree else None,'source_untouched':True,'method':'Evaluated native copy INTERSECT containing padded box, EXACT use_self+use_hole_tolerant'};(O/'envelope-trial.json').write_text(json.dumps(r,indent=2));bpy.data.libraries.write(str(O/'envelope-candidate.blend'),{ob});print(json.dumps(r))
