import bpy,json,sys
from pathlib import Path
from mathutils import Vector,geometry
from bpy_extras.object_utils import world_to_camera_view
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-149/geometry';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;ob=bpy.data.objects['COL110 U9 fractured upper wall L'];src=json.load(open(O/'target-source.json'));oldvs=[Vector(q)for q in src['vertices']];orig=[Vector(q)for q in src['original']];tris=src['faces']
def convert(vs):
 out=[]
 for v in vs:
  q=world_to_camera_view(s,s.camera,v);out.append([q.x*3840,(1-q.y)*2885])
 return out
out={'before':{'vertices':convert(oldvs),'faces':tris},'after':{'vertices':convert([ob.matrix_world@v.co for v in ob.data.vertices]),'faces':[list(p.vertices)for p in ob.data.polygons]}};(O/'projected-silhouette.json').write_text(json.dumps(out))
anchors=[]
for name,w in [('core',Vector((5.2,198.5,50.1))),('fracture source',Vector((5.1,198.6,51.0)))]:
 t=tris[14] if name=='core' else min(tris,key=lambda t:(geometry.closest_point_on_tri(w,*[oldvs[k]for k in t])-w).length_squared);p=geometry.closest_point_on_tri(w,*[oldvs[k]for k in t]);N=(oldvs[t[1]]-oldvs[t[0]]).cross(oldvs[t[2]]-oldvs[t[0]]).normalized();X=Vector((0,0,1)).cross(N).normalized();Y=N.cross(X).normalized()
 def origmap(p):return geometry.barycentric_transform(p,*[oldvs[k]for k in t],*[orig[k]for k in t])
 a=origmap(p);bf=tris[14];bn=(oldvs[bf[1]]-oldvs[bf[0]]).cross(oldvs[bf[2]]-oldvs[bf[0]]).normalized();bx=Vector((0,0,1)).cross(bn).normalized();by=bn.cross(bx).normalized();bm=lambda q:geometry.barycentric_transform(q,*[oldvs[k]for k in bf],*[orig[k]for k in bf]);ax=bm(p+bx)-bm(p);ay=bm(p+by)-bm(p);anchors.append({'role':name,'world':list(p),'normal_world':list(N),'original_world':list(a),'across_original_unit':list(ax.normalized()),'up_original_unit':list(ay.normalized()),'original_units_per_world_across':ax.length,'original_units_per_world_up':ay.length})
mask=ob.data.attributes['149 Exposed crown core'];inds=set(i for p in ob.data.polygons if mask.data[p.index].value>.5 for i in p.vertices);pts=[ob.data.attributes['115 Original world position'].data[i].vector for i in inds];(O/'material-anchors.json').write_text(json.dumps({'object':ob.name,'face_mask':'149 Exposed crown core','anchors':anchors,'exposed_core_original_bounds':[[min(p[k]for p in pts),max(p[k]for p in pts)]for k in range(3)],'exposed_core_faces':sum(d.value>.5 for d in mask.data)},indent=2))
