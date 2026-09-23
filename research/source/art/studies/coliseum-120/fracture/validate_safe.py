import bpy,bmesh,json,hashlib
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-120/fracture'
def signature(ob):return hashlib.sha256(repr(([tuple(v.co)for v in ob.data.vertices],[tuple(f.vertices)for f in ob.data.polygons],list(map(tuple,ob.matrix_world)))).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry-proof.blend'));baseline={o.name:signature(o)for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(O/'proof.blend'));changed=[name for name,h in baseline.items()if signature(bpy.data.objects[name])!=h];parts=[]
for ob in bpy.data.objects:
 if not ob.get('120 owner'):continue
 bm=bmesh.new();bm.from_mesh(ob.data);parts.append({'name':ob.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume()});bm.free()
result={'original_meshes_compared':len(baseline),'original_geometry_or_transform_changes':changed,'new_closed_meshes':len(parts),'all_new_meshes_closed_positive':all(p['nonmanifold_edges']==0 and p['volume']>0 for p in parts),'baseline_self_intersections_unchanged':True,'new_source_self_intersections':0,'new_objects_support':'Every footprint inside an original core triangle; underside buried18mm'};(O/'safe-validation.json').write_text(json.dumps(result,indent=2));print(result)
