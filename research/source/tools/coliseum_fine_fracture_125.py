"""UCL-01/UCL-02/DP-03: clustered negative crown chips, constrained to clean bay8 L/R.
Native convex Boolean removal; each cut independently checked and rolled back.
"""
import bpy,bmesh,math,random,json,sys
from pathlib import Path
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-125/fracture'
sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import NAMES,topology,strict_crossings,apply_prepared

def tree(ob):
 me=ob.data;me.calc_loop_triangles();v=[ob.matrix_world@x.co for x in me.vertices];f=[tuple(x.vertices)for x in me.loop_triangles]
 return BVHTree.FromPolygons(v,f,all_triangles=True),v,f

def triangulate_render(ob):
 old=ob.data;old.calc_loop_triangles();alltris=list(old.loop_triangles);groups={}
 for i,t in enumerate(alltris):groups.setdefault(tuple(sorted(t.vertices)),[]).append(i)
 drop=set()
 for ids in groups.values():
  if len(ids)==2 and alltris[ids[0]].normal.dot(alltris[ids[1]].normal)<-.9999:drop.update(ids)
 tris=[t for i,t in enumerate(alltris)if i not in drop];m=bpy.data.meshes.new(old.name+'125 triangle baseline');m.from_pydata([v.co.copy()for v in old.vertices],[],[tuple(t.vertices)for t in tris]);m.update()
 for mat in old.materials:m.materials.append(mat)
 for f,t in zip(m.polygons,tris):f.material_index=old.polygons[t.polygon_index].material_index
 for at in old.attributes:
  if at.name not in ['115 Original world position','117 Damage proximity','117 Exposed core','118 Recess interior']:continue
  dest=m.attributes.new(at.name,at.data_type,at.domain)
  for i,d in enumerate(dest.data):
   src=at.data[i if at.domain=='POINT'else tris[i].polygon_index]
   if at.data_type=='FLOAT_VECTOR':d.vector=src.vector
   else:d.value=src.value
 bm=bmesh.new();bm.from_mesh(m);loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bm.to_mesh(m);bm.free();ob.data=m;ob['125 unused points removed']=len(loose);check=topology(ob)
 if check['strict_crossings']or check['nonmanifold']:ob.data=old;raise RuntimeError('Invalid triangulated baseline '+ob.name+str(check))

def apply(C):
 rng=random.Random(12573);rows=[]
 from coliseum_r_normalize_124 import apply as normalize_r
 normalization=normalize_r(C)
 for name in NAMES:triangulate_render(bpy.data.objects[name])
 normalization['unused_points_removed']={name:bpy.data.objects[name].get('125 unused points removed',0)for name in NAMES}
 for name in NAMES:
  ob=bpy.data.objects[name]
  if strict_crossings(ob):raise RuntimeError('Chips require crossing-free repaired base: '+name)
  initial=topology(ob);me=ob.data;vs=[ob.matrix_world@v.co for v in me.vertices];normalmat=ob.matrix_world.to_3x3().inverted().transposed();norms=[(normalmat@f.normal).normalized()for f in me.polygons]
  adjacent={}
  for f in me.polygons:
   for e in f.edge_keys:adjacent.setdefault(tuple(sorted(e)),[]).append(f.index)
  ymin=min(v.y for v in vs);ymax=max(v.y for v in vs);zmin=min(v.z for v in vs)
  candidates=[];mask=me.attributes.get('117 Exposed core')
  for (a,b),fi in adjacent.items():
   if len(fi)!=2:continue
   A,B=vs[a],vs[b];mid=(A+B)*.5;length=(A-B).length;n0,n1=[norms[i]for i in fi]
   if length<.24 or n0.dot(n1)>.83:continue
   front=mid.y<ymin+(ymax-ymin)*.17
   crown=max(n0.z,n1.z)>.35 and mid.z>zmin+2.2
   breach=bool(mask and any(mask.data[i].value>.5 for i in fi))and front and mid.z>zmin+1.0
   if not((front and crown)or breach):continue
   candidates.append((A.copy(),B.copy(),(n0+n1).normalized(),length))
  # Cluster unequal notches around a sparse selection of existing edge segments.
  attempts=[]
  for edge in candidates:
   A,B,out,length=edge
   if rng.random()>.88:continue
   clusters=max(1,min(7,int(length/.48)))
   for k in range(clusters):
    t=(k+rng.uniform(.18,.82))/clusters
    count=rng.choice([1,2,2,3])
    for q in range(count):
     tt=max(.07,min(.93,t+(q-(count-1)/2)*rng.uniform(.025,.065)))
     radius=rng.uniform(.085,.18);center=A.lerp(B,tt)+out*radius*.18
     attempts.append((center,radius,(B-A).normalized(),out))
  # Small shallow negative pockets in broad visible exposed return faces.
  eligible=[]
  for f in me.polygons:
   if not mask or mask.data[f.index].value<.5:continue
   center=ob.matrix_world@f.center;n=norms[f.index]
   if f.area>.04 and center.z>zmin+1.2 and n.z>.15 and center.y<ymin+(ymax-ymin)*.7:eligible.append((f.area,center,n))
  rng.shuffle(eligible)
  for area,center,n in eligible[:12]:
   rad=min(.18,max(.07,math.sqrt(area)*.28));axis=n.cross(Vector((0,0,1))).normalized()
   if axis.length<.1:axis=Vector((1,0,0))
   attempts.append((center+n*rad*.66,rad,axis,n))
  accepted=0;reject=[]
  for index,(center,radius,tangent,outward)in enumerate(attempts):
   old=ob.data;before_volume=topology(ob)['volume'];oldtree,oldv,oldf=tree(ob);oldattr=old.attributes.get('115 Original world position');oldorig=[x.vector.copy()for x in oldattr.data]if oldattr else oldv
   # Convex irregular octahedron: asymmetric unequal radii create fracture facets, never beads.
   axis=tangent;cross=axis.cross(outward).normalized();up=cross.cross(axis).normalized()
   coords=[center+axis*radius*rng.uniform(1.2,1.9),center-axis*radius*rng.uniform(1.0,1.6),center+cross*radius*rng.uniform(.7,1.4),center-cross*radius*rng.uniform(.7,1.4),center+up*radius*rng.uniform(.9,1.4),center-up*radius*rng.uniform(.9,1.4)]
   bm=bmesh.new();[bm.verts.new(v)for v in coords];bmesh.ops.convex_hull(bm,input=list(bm.verts));cm=bpy.data.meshes.new('123 temporary convex chip');bm.to_mesh(cm);bm.free();cut=bpy.data.objects.new('123 temporary convex chip',cm);C.objects.link(cut)
   ob.data=old.copy();mod=ob.modifiers.new('123 negative edge chip','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=ob
   try:
    bpy.ops.object.modifier_apply(modifier=mod.name);triangulate_render(ob);state=topology(ob);newtree,_,_=tree(ob);low=[min(v[k]for v in coords)-.004 for k in range(3)];high=[max(v[k]for v in coords)+.004 for k in range(3)]
    samples=oldv+[(oldv[t[0]]+oldv[t[1]]+oldv[t[2]])/3 for t in oldf];outside=max((newtree.find_nearest(v)[3]for v in samples if any(v[k]<low[k]or v[k]>high[k]for k in range(3))),default=0)
    if state['strict_crossings']or state['nonmanifold']or state['volume']<=0 or state['volume']>before_volume+.00001 or outside>.004:raise ValueError(json.dumps({'state':state,'outside':outside}))
    if len(ob.data.vertices)==len(old.vertices):ob.data=old
    else:
     m=ob.data;core=m.attributes.get('117 Exposed core')or m.attributes.new('117 Exposed core','FLOAT','FACE');recess=m.attributes.get('118 Recess interior')or m.attributes.new('118 Recess interior','FLOAT','FACE');attr=m.attributes.get('115 Original world position')or m.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');m.attributes.get('117 Damage proximity')or m.attributes.new('117 Damage proximity','FLOAT','POINT')
     slots=[i for i,ma in enumerate(m.materials)if ma and any(x in ma.name.lower()for x in ['fracture','core','cavity'])];slot=next((i for i,ma in enumerate(m.materials)if ma and ma.name.startswith('117 Exposed masonry core')),slots[0]if slots else 0)
     for f in m.polygons:
      h=oldtree.find_nearest(ob.matrix_world@f.center)
      if h[3]>.002:core.data[f.index].value=1.;recess.data[f.index].value=0.;f.material_index=slot
     for v in m.vertices:
      w=ob.matrix_world@v.co;hit=oldtree.find_nearest(w);tri=oldf[hit[2]];attr.data[v.index].vector=geometry.barycentric_transform(hit[0],*[oldv[i]for i in tri],*[oldorig[i]for i in tri])
     accepted+=1;rows.append({'object':name,'cut':index,'accepted':True,'radius_m':radius,'center_world':list(center),'strict_crossings':0,'nonmanifold':0,'outside_max_error_m':outside})
   except Exception as e:
    if mod.name in ob.modifiers:ob.modifiers.remove(mod)
    ob.data=old;reject.append({'cut':index,'reason':str(e)})
   bpy.data.objects.remove(cut,do_unlink=True)
  ob['125 fine negative chips']=accepted
  rows.append({'object':name,'summary':True,'candidate_edges':len(candidates),'attempts':len(attempts),'accepted':accepted,'rejected':reject,'before':initial,'after':topology(ob)})
 return {'method':'convex negative cutouts in irregular clusters on existing crown/breach edges','references':['UCL-01','UCL-02','DP-03'],'targets':NAMES,'normalization':normalization,'cuts':rows,'new_objects':0}

def run():
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-124/B/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin']
 for ob in list(C.objects):
  if ob.get('120 owner')in NAMES:bpy.data.objects.remove(ob,do_unlink=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'baseline.blend'));audit=apply(C);(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print(json.dumps(audit),flush=True)
if __name__=='__main__':run()
