"""Bounded native voxel foundation reconstruction of accepted R wall only, without smoothing."""
import bpy,sys,json
from pathlib import Path
from mathutils import geometry
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-126/volumetric';sys.path.insert(0,str(R/'tools'))
from coliseum_fine_fracture_125 import tree,triangulate_render
from coliseum_crown_repair_123 import topology
NAME='COL110 U8 fractured upper wall R'
def apply(C,voxel_size=.04):
 ob=bpy.data.objects[NAME];triangulate_render(ob);old=ob.data;before=topology(ob);bvh,vs,tris=tree(ob);orig=[d.vector.copy()for d in old.attributes['115 Original world position'].data];old.calc_loop_triangles();tri_faces=[t.polygon_index for t in old.loop_triangles];mats=list(old.materials)
 ob.data=old.copy();mod=ob.modifiers.new('126 native closed voxel foundation','REMESH');mod.mode='VOXEL';mod.voxel_size=voxel_size;mod.adaptivity=0.;mod.use_smooth_shade=False;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
 m=ob.data;after=topology(ob)
 if after['nonmanifold']or after['strict_crossings']or after['volume']<=0:ob.data=old;raise RuntimeError('Unsafe remesh '+str(after))
 print('VOXEL_VALID',before,after,flush=True)
 m.materials.clear()
 for ma in mats:m.materials.append(ma)
 attr=m.attributes.get('115 Original world position')or m.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');dist=[]
 for v in m.vertices:
  w=ob.matrix_world@v.co;hit=bvh.find_nearest(w);t=tris[hit[2]];attr.data[v.index].vector=geometry.barycentric_transform(hit[0],*[vs[i]for i in t],*[orig[i]for i in t]);dist.append(hit[3])
 for name in ['117 Exposed core','118 Recess interior']:
  dest=m.attributes.get(name)or m.attributes.new(name,'FLOAT','FACE');src=old.attributes.get(name)
  for f in m.polygons:
   hit=bvh.find_nearest(ob.matrix_world@f.center);index=tri_faces[hit[2]];dest.data[f.index].value=src.data[index].value if src else 0;f.material_index=old.polygons[index].material_index
 m.attributes.get('117 Damage proximity')or m.attributes.new('117 Damage proximity','FLOAT','POINT')
 nb,_,_=tree(ob);reverse=[nb.find_nearest(w)[3]for w in vs];dist.sort();reverse.sort();ob['126 voxel foundation']=voxel_size
 return {'object':NAME,'voxel_size_object_units':voxel_size,'before':before,'after':after,'volume_change_fraction':after['volume']/before['volume']-1,'new_surface_to_original_max_m':max(dist),'new_surface_to_original_p99_m':dist[int(len(dist)*.99)],'original_vertices_to_new_max_m':max(reverse),'original_vertices_to_new_p99_m':reverse[int(len(reverse)*.99)],'no_smoothing':True,'attributes':'115 projected barycentrically;117/118 and material role nearest original triangle','production_integration':False}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-125/scene.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(O/'baseline.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print(a,flush=True)
