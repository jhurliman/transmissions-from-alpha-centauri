"""Ruled cap/end-return reconstruction from retained front/back profile chains."""
import bpy,bmesh,sys,json,types,math
from pathlib import Path
from mathutils import Vector,geometry
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping
from coliseum_crown_continuation_154 import robust_crossings
NAME='COL110 U15 fractured upper wall R'
FAN_FACES=[18, 731, 733, 734, 736, 737, 791, 792, 793, 794, 795, 2253, 2267]
def run(C):
 ob=C.objects[NAME];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());src=bpy.data.meshes.new_from_object(ev,depsgraph=bpy.context.evaluated_depsgraph_get());M=ev.matrix_world.copy();_,_,unpack=mapping();cc=[unpack(M@v.co)for v in src.vertices];amin=min(p[1]for p in cc);amax=max(p[1]for p in cc);floor=min(p[2]for p in cc);norms=[n.vector.copy()for n in src.corner_normals];orig=[d.vector.copy()for d in src.attributes['115 Original world position'].data]
 d={'source':'156','pre112_domain':'Pre112 46-vertex 27-face radial wall with uneven stepped crown; pre112-domain.json','object':NAME,'protected':'Exact nonempty front/back/bottom faces; both angular ends retained below authored z66.1. Cap and upper end strips reconstructed.','explicit_corner_fan_faces':FAN_FACES,'before_crossings':len(robust_crossings(types.SimpleNamespace(data=src,matrix_world=M))),'accepted':False}
 bm=bmesh.new();bm.from_mesh(src);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();vi=bm.verts.layers.int.new('160 source vertex');fi=bm.faces.layers.int.new('160 source face');li=bm.loops.layers.int.new('160 source corner');keep=[];cut=[]
 for v in bm.verts:v[vi]=v.index
 for f in bm.faces:
  f[fi]=f.index
  for l,i in zip(f.loops,src.polygons[f.index].loop_indices):l[li]=i
  c=[cc[v.index]for v in f.verts];protected=(all(p[0]>=74.85 for p in c)or all(p[0]<=67.15 for p in c)or all(p[1]<amin+.0003 and p[2]<66.1 for p in c)or all(p[1]>amax-.0003 and p[2]<66.1 for p in c)or all(p[2]<floor+.05 for p in c))and f.calc_area()>=1e-10 and f.index not in FAN_FACES
  (keep if protected else cut).append(f)
 keepids=[f.index for f in keep];d['protected_faces']=len(keep);d['reconstructed_source_faces']=len(cut);bmesh.ops.delete(bm,geom=cut,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 edges={e for e in bm.edges if e.is_boundary};degree={v:sum(e.is_boundary for e in v.link_edges)for e in edges for v in e.verts};d['boundary_branch_vertices']=sum(n!=2 for n in degree.values())
 if d['boundary_branch_vertices']:
  d['boundary_branch_details']=[{'original_vertex':v[vi],'authored':list(unpack(M@v.co)),'boundary_degree':n,'protected_source_faces':[f[fi] for f in v.link_faces],'boundary_neighbors':[{'vertex':e.other_vert(v)[vi],'authored':list(unpack(M@e.other_vert(v).co))}for e in v.link_edges if e.is_boundary]}for v,n in degree.items()if n!=2]
  probe=bpy.data.meshes.new('160 right protected diagnostic');bm.to_mesh(probe);probe.calc_loop_triangles();pairs=robust_crossings(types.SimpleNamespace(data=probe,matrix_world=M));d['protected_surface_crossings']=len(pairs);d['protected_crossing_source_face_pairs']=[[probe.attributes['160 source face'].data[probe.loop_triangles[i].polygon_index].value for i in pair] for pair in pairs];d['branch_incident_faces']=[{'index':f.index,'vertices':[list(cc[i])for i in f.vertices]}for f in src.polygons if f.index in {idx for row in d['boundary_branch_details'] for idx in row['protected_source_faces']}]
  d['reason']='Protected boundary still branches';return d
 loops=[]
 while edges:
  e=edges.pop();loop=[e.verts[0],e.verts[1]];v=loop[-1]
  while v!=loop[0]:
   e=next((e for e in v.link_edges if e in edges),None)
   if e is None:break
   edges.remove(e);v=e.other_vert(v)
   if v!=loop[0]:loop.append(v)
  loops.append(loop)
 d['boundary_loop_lengths']=[len(l)for l in loops]
 if len(loops)!=1:
  d['small_loops']=[{'vertices':[{'id':v[vi],'authored':list(unpack(M@v.co))}for v in l],'neighbor_faces':sorted({f[fi]for v in l for f in v.link_faces})}for l in loops if len(l)<10]
  d['reason']='Protected boundary not one connected return strip';return d
 loop=loops[0];front=[unpack(M@v.co)[0]>=74.85 for v in loop];starts=[i for i,x in enumerate(front)if x and not front[i-1]]
 if len(starts)!=1:d['reason']='Front boundary is not a single ordered profile';d['front_runs']=len(starts);return d
 st=starts[0];loop=loop[st:]+loop[:st];fend=next((i for i,v in enumerate(loop)if unpack(M@v.co)[0]<74.85),len(loop));backs=[i for i,v in enumerate(loop)if unpack(M@v.co)[0]<=67.15];bs=min(backs);be=max(backs)+1
 if backs!=list(range(bs,be)):d['reason']='Back boundary is not a single ordered profile';return d
 F=loop[:fend];B=list(reversed(loop[bs:be]));E1=[F[-1]]+loop[fend:bs]+[B[-1]];E0=[B[0]]+loop[be:]+[F[0]]
 (R/'art/studies/coliseum-160/right-repair/v3/profile-chains.json').write_text(json.dumps({label:[{'source_vertex':v[vi],'authored':list(unpack(M@v.co))}for v in seq]for label,seq in [('front',F),('back',B)]},indent=2))
 def cumulative(seq):
  c=[unpack(M@v.co)for v in seq];length=[0.]
  for a,b in zip(c,c[1:]):length.append(length[-1]+math.hypot((a[1]-b[1])*75,a[2]-b[2]))
  if length[-1]<1e-8:length=[i/(len(seq)-1)for i in range(len(seq))]
  else:length=[x/length[-1]for x in length]
  return length
 # Pair actual pre112 masonry-step corners rather than total-profile arclength.
 anchors=[(7,0),(19,16),(26,24),(32,28),(40,34),(38,35),(45,44),(15,14),(13,6)]
 if F[0][vi]==13:anchors=list(reversed(anchors))
 def step_parameters(seq,side):
  indices=[next(i for i,v in enumerate(seq)if v[vi]==pair[side])for pair in anchors]
  if indices!=sorted(indices):raise RuntimeError('Nonmonotone source masonry correspondence')
  params=[0.]*len(seq)
  for domain,(a,b)in enumerate(zip(indices,indices[1:])):
   local=cumulative(seq[a:b+1])
   for i,t in enumerate(local):params[a+i]=(domain+t)/(len(indices)-1)
  return params,indices
 fs,fa=step_parameters(F,0);bs2,ba=step_parameters(B,1)
 d['step_corner_correspondence']=anchors;d['masonry_domains']=len(anchors)-1
 uvmap={v:Vector((s,0))for v,s in zip(F,fs)};uvmap.update({v:Vector((s,1))for v,s in zip(B,bs2)})
 for seq,s in [(E1,1),(E0,0)]:
  lengths=[0.]
  for a,b in zip(seq,seq[1:]):lengths.append(lengths[-1]+(M@a.co-M@b.co).length)
  for v,x in zip(seq,lengths):uvmap[v]=Vector((s,x/lengths[-1]if s else 1-x/lengths[-1]))
 uv=[uvmap[v]for v in loop];worldvals=[v.co.copy()for v in loop];attrs=[orig[v[vi]].copy()for v in loop]
 def interp(seq,params,s):
  for i,(a,b)in enumerate(zip(params,params[1:])):
   if a<=s<=b and b>a:
    t=(s-a)/(b-a);return seq[i].co.lerp(seq[i+1].co,t),orig[seq[i][vi]].lerp(orig[seq[i+1][vi]],t)
  return seq[-1].co.copy(),orig[seq[-1][vi]].copy()
 constraints=[(i,(i+1)%len(loop))for i in range(len(loop))]
 for domain in range(len(anchors)-1):
  for j in range(1,5):
   ss=(domain+j/5)/(len(anchors)-1);p,a=interp(F,fs,ss);q,b=interp(B,bs2,ss)
   for t in [.2,.4,.6,.8]:uv.append(Vector((ss,t)));worldvals.append(p.lerp(q,t));attrs.append(a.lerp(b,t))
 for domain in range(1,len(anchors)-1):
  ss=domain/(len(anchors)-1);p,a=interp(F,fs,ss);q,b=interp(B,bs2,ss);ids=[loop.index(F[fa[domain]])]
  for t in [.2,.4,.6,.8]:
   ids.append(len(uv));uv.append(Vector((ss,t)));worldvals.append(p.lerp(q,t));attrs.append(a.lerp(b,t))
  ids.append(loop.index(B[ba[domain]]));constraints.extend(zip(ids,ids[1:]))
 vv,ee,ff,vorig,_,_=geometry.delaunay_2d_cdt(uv,constraints,[list(range(len(loop)))],1,1e-9,True);d['profile_chain_lengths']=[len(F),len(B),len(E1),len(E0)];d['cdt_generated_unmapped_vertices']=sum(not ids for ids in vorig);d['cdt_merged_input_vertices']=sum(len(ids)>1 for ids in vorig)
 if any(len(ids)!=1 for ids in vorig):d['reason']='Boundary CDT merges or invents vertices; exact source-boundary correspondence not certified';return d
 mapped=[];newattrs={}
 for ids in vorig:
  k=ids[0]
  if k<len(loop):v=loop[k]
  else:v=bm.verts.new(worldvals[k]);v[vi]=-1;newattrs[v]=attrs[k]
  mapped.append(v)
 for face in ff:
  f=bm.faces.new([mapped[i]for i in face]);f[fi]=-1
  for l in f.loops:l[li]=-1
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.verts.index_update();attrvalues={v.index:(orig[v[vi]]if v[vi]>=0 else newattrs[v])for v in bm.verts};out=bpy.data.meshes.new('160 right ruled return candidate');bm.to_mesh(out);bm.free();out.update()
 for mat in src.materials:out.materials.append(mat)
 a=out.attributes.get('115 Original world position')or out.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
 for i,p in attrvalues.items():a.data[i].vector=p
 restored=[]
 for i,n in enumerate(out.corner_normals):
  idx=out.attributes['160 source corner'].data[i].value;restored.append(norms[idx]if idx>=0 else n.vector.copy())
 out.normals_split_custom_set(restored);out.calc_loop_triangles();src.calc_loop_triangles();protected_keys={tuple(sorted(tuple(src.vertices[i].co)for i in t.vertices))for t in src.loop_triangles if t.polygon_index in keepids};new_keys={tuple(sorted(tuple(out.vertices[i].co)for i in t.vertices))for t in out.loop_triangles};d['protected_triangle_loss']=len(protected_keys-new_keys)
 bm=bmesh.new();bm.from_mesh(out);d.update(after_nonmanifold=sum(not e.is_manifold for e in bm.edges),after_zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();d['after_crossings']=len(robust_crossings(types.SimpleNamespace(data=out,matrix_world=M)));d['accepted']=d['after_nonmanifold']==0 and d['after_zero_faces']==0 and d['after_crossings']==0 and d['protected_triangle_loss']==0
 d['reason']='Candidate passes structural gates; current-view shape/attribute proof still required'if d['accepted']else'Candidate held: exact protected boundary retained but one or more strict structural gates fail'
 # Isolated diagnostic native mesh only. Parent scene remains unchanged.
 for a in list(out.attributes):
  if a.name.startswith('160 source'):out.attributes.remove(a)
 candidate=bpy.data.objects.new('160 isolated U15R candidate',out);collection=bpy.data.collections.new('160 isolated return candidate');bpy.context.scene.collection.children.link(collection);collection.objects.link(candidate);candidate.matrix_world=M
 bpy.data.libraries.write(str(R/'art/studies/coliseum-160/right-repair/v3/candidate.blend'),{collection},fake_user=True)
 return d
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));d=run(bpy.data.collections['110 Coliseum detailed front ruin']);(R/'art/studies/coliseum-160/right-repair/v3/strip-candidate-audit.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
