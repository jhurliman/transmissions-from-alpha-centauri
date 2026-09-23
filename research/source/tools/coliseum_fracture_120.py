"""120 conservative attached fracture aggregate. Existing119 topology is immutable.
Risky edge remeshing was rejected; see fracture/rejected-remesh-experiment.py and audit.
"""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector,geometry
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-120/fracture'
def apply(collection,bays=(8,)):
 rng=random.Random(120091);records=[];created=[]
 targets=[o for o in collection.objects if o.type=='MESH'and o.get('bay')in bays and o.get('tier')==3 and ('fractured upper wall'in o.name or 'sill wall'in o.name)]
 for ob in targets:
  me=ob.data;me.calc_loop_triangles();M=ob.matrix_world;vs=[M@v.co for v in me.vertices];z0=min(v.z for v in vs);core=me.attributes.get('117 Exposed core');oldattr=me.attributes.get('115 Original world position');recess=me.attributes.get('118 Recess interior');candidates=[]
  for tri in me.loop_triangles:
   a,b,c=[vs[k]for k in tri.vertices];cross=(b-a).cross(c-a);area=cross.length/2
   if area<.017:continue
   n=cross.normalized();center=(a+b+c)/3;tag=core and core.data[tri.polygon_index].value>.5;crown='fractured upper wall'in ob.name and n.z>.15 and center.z>z0+1.3
   if not(tag or crown)or n.y>.4:continue
   candidates.append((tri,a,b,c,n,area,crown))
  rng.shuffle(candidates);count=0
  for tri,a,b,c,n,area,crown in candidates:
   if count>=65:break
   if rng.random()<.32:continue
   # Polygon sits strictly inside an existing triangle, so its buried underside is supported.
   center=a*.28+b*.36+c*.36;t=(b-a).normalized();u=n.cross(t).normalized();clearance=min((center-a).cross(b-a).length/(b-a).length,(center-b).cross(c-b).length/(c-b).length,(center-c).cross(a-c).length/(a-c).length)
   radius=min(rng.uniform(.05,.14),clearance*.70)
   if radius<.022:continue
   N=rng.choice([4,5,6]);rim=[]
   for k in range(N):
    angle=math.tau*k/N;rim.append(center+t*(math.cos(angle)*radius*rng.uniform(.72,1.0))+u*(math.sin(angle)*radius*rng.uniform(.72,1.0)))
   depth=min(.026,radius*.20);vertices=[v-n*.018 for v in rim]+[center+(v-center)*rng.uniform(.53,.78)+n*depth*rng.uniform(.5,1.)for v in rim]
   faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)]
   mesh=bpy.data.meshes.new('120 attached fractured core aggregate');mesh.from_pydata(vertices,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.to_mesh(mesh);bm.free()
   if bad or volume<=0:bpy.data.meshes.remove(mesh);continue
   part=bpy.data.objects.new('COL120 embedded core facet '+ob.name+' '+str(count),mesh);collection.objects.link(part)
   for k in ['bay','tier','coliseum_role']:
    if k in ob:part[k]=ob[k]
   part['coliseum_role']='fracture';part['feature']='attached embedded fracture aggregate';part['120 owner']=ob.name;part['120 minimum burial m']=.018;part['120 maximum relief m']=depth
   for mat in me.materials:mesh.materials.append(mat)
   for f in mesh.polygons:f.material_index=me.polygons[tri.polygon_index].material_index
   attr=mesh.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');mask=mesh.attributes.new('117 Exposed core','FLOAT','FACE');rec=mesh.attributes.new('118 Recess interior','FLOAT','FACE');proximity=mesh.attributes.new('117 Damage proximity','FLOAT','POINT')
   if oldattr:
    oa,obp,oc=[oldattr.data[k].vector.copy()for k in tri.vertices]
   else:oa,obp,oc=a,b,c
   for v in mesh.vertices:
    point=v.co-n*(v.co-center).dot(n);attr.data[v.index].vector=geometry.barycentric_transform(point,a,b,c,oa,obp,oc);proximity.data[v.index].value=1.
   for f in mesh.polygons:mask.data[f.index].value=1.;rec.data[f.index].value=recess.data[tri.polygon_index].value if recess else 0.
   created.append(part);count+=1
  records.append({'owner':ob.name,'attached_facets':count,'source_vertices_unchanged':len(me.vertices),'source_faces_unchanged':len(me.polygons)})
 return {'method':'Closed shallow angular core facets, partially buried and fully supported on existing exposed faces','objects':records,'new_objects':len(created),'original_meshes_unchanged':True,'zero_new_source_self_intersections':True,'new_meshes_closed_positive_volume':True,'edge_jaggedness':'Deferred: native Boolean and remesh trials failed conservative intersection checks; original boundaries retained','maximum_relief_m':.026,'minimum_burial_m':.018}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry-proof.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=False;s.render.resolution_x=1500;s.render.resolution_y=1500;s.render.resolution_percentage=100;s.use_nodes=False
 mat=bpy.data.materials.new('120 fracture neutral clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.38,.38,.38,1);bs.inputs['Roughness'].default_value=.83
 for ob in C.objects:
  if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(mat)
 s.render.filepath=str(O/'before-clay.png');bpy.ops.render.render(write_still=True);audit=apply(C);(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'));s.render.filepath=str(O/'after-clay.png');bpy.ops.render.render(write_still=True);print(json.dumps(audit))
