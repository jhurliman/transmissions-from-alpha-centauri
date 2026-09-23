"""Bounded true chips and broken return facets; preserves119 authored aperture paths.
UCL01/UCL02/DP03 and user120 annotated crops: clustered fine losses, interrupted core planes.
"""
import bpy,bmesh,math,random,json,os
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-120/fracture'

def apply(collection,bays=(8,)):
 rng=random.Random(120814);report=[]
 targets=[o for o in collection.objects if o.type=='MESH' and o.get('bay') in bays and o.get('tier')==3 and ('fractured upper wall' in o.name or 'sill wall' in o.name)]
 for ob in targets:
  old=ob.data;oldcount=len(old.vertices);M=ob.matrix_world.copy();Mi=M.inverted();origin=M@old.vertices[0].co;T=Matrix.Translation(-origin)@M;Ti=T.inverted();ob.data=old.copy();ob.data.transform(T);ob.matrix_world.identity();me=ob.data
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0000001);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='FIXED',ngon_method='EAR_CLIP');bm.normal_update();bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table();core=bm.faces.layers.float.get('117 Exposed core')or bm.faces.layers.float.new('117 Exposed core');recess=bm.faces.layers.float.get('118 Recess interior')or bm.faces.layers.float.new('118 Recess interior');z0=min(v.co.z for v in bm.verts)
  # Existing crown facets have no legacy core tags. Upward-facing broken upper-wall returns are exposed core too.
  crown=0
  if 'fractured upper wall'in ob.name:
   for f in bm.faces:
    if f.normal.z>.12 and f.calc_center_median().z>z0+1.25:f[core]=1.;crown+=1
  # Boundary only: one core face meets intact front/side. Fine teeth do not invent a new fracture path.
  candidates=[]
  for e in bm.edges:
   if len(e.link_faces)!=2:continue
   f,g=e.link_faces
   if (f[core]>.5)==(g[core]>.5):continue
   intact=g if f[core]>.5 else f
   if intact.normal.y>-.10:continue
   length=e.calc_length()
   if length<.13:continue
   a,b=[v.co.copy()for v in e.verts];num=max(1,int(length/.29))
   for k in range(num):
    if rng.random()<.36:continue
    t=(k+rng.uniform(.2,.8))/num;p=a.lerp(b,t);candidates.append((p,(b-a).normalized(),intact.normal.copy()))
  candidates.sort(key=lambda q:q[0].y);selected=[]
  for item in candidates:
   if all((item[0]-q[0]).length>.20 for q in selected):selected.append(item)
   if len(selected)>=48:break
  bm.to_mesh(me);bm.free();cuts=0;rejected=[]
  # Small independent convex cutters, batched with strict manifold and outside-box preservation checks.
  for off in range(0,len(selected),6):
   group=selected[off:off+6];cbm=bmesh.new();boxes=[]
   for idx,(center,tangent,norm)in enumerate(group):
    side=tangent.cross(norm).normalized();radius=rng.uniform(.055,.13);depth=rng.uniform(.035,.095);length=radius*rng.uniform(.75,1.8);pts=[]
    for ring,z in enumerate([-1.,-.15,1.]):
     for k in range(7):
      a=math.tau*k/7+rng.uniform(-.12,.12);s=rng.uniform(.72,1.15);p=center+tangent*(math.cos(a)*length*s)+side*(math.sin(a)*radius*s)+norm*(z*depth);pts.append(cbm.verts.new(p))
    bmesh.ops.convex_hull(cbm,input=pts,use_existing_faces=False);boxes.append((Vector(tuple(min(v.co[k]for v in pts)-.002 for k in range(3))),Vector(tuple(max(v.co[k]for v in pts)+.002 for k in range(3)))))
   bmesh.ops.recalc_face_normals(cbm,faces=list(cbm.faces));cm=bpy.data.meshes.new('120 local chip cutters');cbm.to_mesh(cm);cbm.free();cutter=bpy.data.objects.new('120 temporary true fracture chips',cm);collection.objects.link(cutter);before=ob.data;ob.data=before.copy();mod=ob.modifiers.new('120 Local chip subtraction','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;mod.use_self=True;bpy.context.view_layer.objects.active=ob
   try:bpy.ops.object.modifier_apply(modifier=mod.name)
   except Exception:
    if mod.name in ob.modifiers:ob.modifiers.remove(mod)
    ob.data=before;bpy.data.objects.remove(cutter,do_unlink=True);rejected.append('boolean exception');continue
   check=bmesh.new();check.from_mesh(ob.data);bad=sum(not e.is_manifold for e in check.edges);volume=check.calc_volume();check.free();error=0.
   if not bad and volume>0:
    tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[tuple(f.vertices)for f in ob.data.polygons])
    for v in before.vertices:
     if any(all(lo[k]<=v.co[k]<=hi[k]for k in range(3))for lo,hi in boxes):continue
     hit=tree.find_nearest(v.co);error=max(error,hit[3]if hit and hit[0]is not None else 100.)
   if bad or volume<=0 or error>.004:ob.data=before;rejected.append({'bad_edges':bad,'volume':volume,'outside_error':error})
   else:
    cuts+=len(group)
    # New exposed faces retain old tags; mark every newly cut surface explicitly.
    src=BVHTree.FromPolygons([v.co for v in before.vertices],[tuple(f.vertices)for f in before.polygons]);tag=ob.data.attributes.get('117 Exposed core')or ob.data.attributes.new('117 Exposed core','FLOAT','FACE')
    for f in ob.data.polygons:
     hit=src.find_nearest(f.center)
     if hit and hit[0]is not None and hit[3]>.001:tag.data[f.index].value=1.
   bpy.data.objects.remove(cutter,do_unlink=True)
  # Exact Boolean on inherited skinny crown triangles may fail. Topology-preserving inward
  # edge remeshing adds bounded negative teeth to those same paths without a second cut volume.
  boundary_bm=bmesh.new();boundary_bm.from_mesh(ob.data);cfield=boundary_bm.faces.layers.float.get('117 Exposed core');border=[]
  for e in boundary_bm.edges:
   if len(e.link_faces)!=2 or e.calc_length()<.10:continue
   f,g=e.link_faces
   if (f[cfield]>.5)==(g[cfield]>.5):continue
   intact=g if f[cfield]>.5 else f
   if intact.normal.y<-.10:border.append(e)
  oldverts=set(boundary_bm.verts)
  if border:bmesh.ops.subdivide_edges(boundary_bm,edges=border,cuts=2,use_grid_fill=True)
  boundary_bm.normal_update();teeth=0
  for v in boundary_bm.verts:
   if v in oldverts or rng.random()<.28:continue
   cf=[f for f in v.link_faces if f[cfield]>.5];outer=[f for f in v.link_faces if f[cfield]<.5]
   if not cf or not outer:continue
   face=max(outer,key=lambda f:f.calc_area());n=sum((f.normal for f in cf),Vector()).normalized();n-=face.normal*n.dot(face.normal)
   if n.length<.01:continue
   distance=min(rng.uniform(.016,.063),min(e.calc_length()for e in v.link_edges)*.28);v.co-=n.normalized()*distance;teeth+=1
  bmesh.ops.recalc_face_normals(boundary_bm,faces=list(boundary_bm.faces));boundary_bm.to_mesh(ob.data);boundary_bm.free()
  # Subdivide only marked core planes; world-space pits and irregular facets stay attached to solid masonry.
  bm=bmesh.new();bm.from_mesh(ob.data);core=bm.faces.layers.float.get('117 Exposed core');beforecore=sum(f[core]>.5 for f in bm.faces);kernels=[]
  for f in list(bm.faces):
   if f[core]<.5 or f.calc_area()<.018:continue
   n=f.normal.copy();t=n.cross(Vector((0,0,1)))
   if t.length<.01:t=n.cross(Vector((1,0,0)))
   t.normalize();u=n.cross(t).normalized();count=min(8,max(1,int(f.calc_area()*22)))
   if rng.random()>min(.75,f.calc_area()*6):continue
   vv=list(f.verts)
   for k in range(count):
    q=f.calc_center_median().lerp(rng.choice(vv).co,rng.uniform(.05,.65));kernels.append((q,n,t,u,rng.uniform(.09,.24),rng.uniform(.008,.026),rng.uniform(.6,1.5)))
  for repeat in range(3):
   edges=[e for e in bm.edges if e.calc_length()>.15 and any(f[core]>.5 for f in e.link_faces)]
   if not edges:break
   bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
  bm.normal_update();moved=0;maxmove=0.
  for v in bm.verts:
   if not v.link_faces or not all(f[core]>.5 for f in v.link_faces):continue
   displacement=Vector((0,0,0))
   for p,n,t,u,r,d,aspect in kernels:
    delta=v.co-p
    if abs(delta.dot(n))>.065:continue
    x=delta.dot(t)/r;y=delta.dot(u)/(r*aspect);rr=max(abs(x),abs(y),abs(x+y)*.63);weight=max(0,1-rr)
    if weight:displacement-=n*(d*weight)
   if displacement.length>.028:displacement.normalize();displacement*=.028
   if displacement.length>.0001:
    # Existing narrow fracture triangles must never be folded by a displacement taller than their altitude.
    altitude=min(2*f.calc_area()/max(e.calc_length()for e in f.edges)for f in v.link_faces)
    limit=min(.028,altitude*.18)
    if displacement.length>limit:displacement*=limit/displacement.length
    saved=v.co.copy();accepted=False
    for fraction in [1.,.5,.25]:
     v.co=saved+displacement*fraction;valid=True
     for face in v.link_faces:
      vv=[q.co for q in face.verts];cross=sum(((vv[k]-vv[0]).cross(vv[k+1]-vv[0])for k in range(1,len(vv)-1)),Vector())
      if cross.dot(face.normal)<1e-12:valid=False;break
     if valid:accepted=True;break
    if accepted:moved+=1;maxmove=max(maxmove,(v.co-saved).length)
    else:v.co=saved
  bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if f[core]>.5 and len(f.verts)>3]);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.to_mesh(ob.data);bm.free()
  # Restore original object transform, preserving original-world coordinate attribute carried through interpolation.
  ob.data.transform(Ti);ob.matrix_world=M;ob['120 fracture detailed']=True;ob['120 maximum inset m']=maxmove
  report.append({'object':ob.name,'vertices_before':oldcount,'vertices_after':len(ob.data.vertices),'crown_core_faces':crown,'chip_cutters_accepted':cuts,'inward_edge_teeth':teeth,'rejected_batches':rejected,'core_kernels':len(kernels),'moved_interior_vertices':moved,'max_core_relief_m':maxmove,'nonmanifold_edges':bad,'positive_world_volume':volume,'attributes':[a.name for a in ob.data.attributes]})
 return {'target_bays':list(bays),'objects':report,'method':'Bounded convex edge subtraction plus attached piecewise planar core recesses','main_path_preserved':True,'max_edge_cutter_radius_m':.13}

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry-proof.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=False;s.render.resolution_x=1500;s.render.resolution_y=1500;s.render.resolution_percentage=100;s.use_nodes=False
 # Matched neutral clay uses actual lighting and shadows only.
 mat=bpy.data.materials.new('120 fracture neutral clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.38,.38,.38,1);bs.inputs['Roughness'].default_value=.83
 for ob in C.objects:
  if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(mat)
 s.render.filepath=str(O/'before-clay.png');bpy.ops.render.render(write_still=True);audit=apply(C);(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'));s.render.filepath=str(O/'after-clay.png');bpy.ops.render.render(write_still=True);print(json.dumps(audit))
