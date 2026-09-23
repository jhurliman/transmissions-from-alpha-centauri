"""235: readable construction and connected facing loss on eight transition walls.
No finish/color rollout: parent owns final material and ink treatment.
"""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/ruined-wall-structure-235';sys.path.insert(0,str(R/'tools'))
NAMES=['133 L0 broken camera-facing cross wall','133 L1 standing street wall','133 L2 standing street wall','133 L2 broken camera-facing cross wall','133 R3 standing street wall','133 R4 standing street wall','133 R4 broken camera-facing cross wall','133 R5 standing street wall']
PROFILES=[ [(-.50,-.36),(-.34,-.50),(.15,-.47),(.27,-.28),(.49,-.18),(.44,.15),(.23,.22),(.31,.48),(-.06,.50),(-.19,.31),(-.45,.23),(-.39,-.05)], [(-.30,-.50),(.26,-.48),(.39,-.20),(.25,-.07),(.49,.12),(.35,.42),(.02,.50),(-.22,.35),(-.44,.28),(-.50,.04),(-.29,-.16)], [(-.45,-.43),(-.02,-.50),(.23,-.32),(.47,-.30),(.43,.04),(.27,.17),(.30,.44),(-.02,.50),(-.39,.34),(-.32,.08),(-.49,-.06)], [(-.28,-.50),(.09,-.43),(.42,-.24),(.33,.08),(.49,.30),(.14,.47),(-.19,.50),(-.45,.26),(-.30,.07),(-.47,-.16)] ]

def material(base,role):
 m=base.copy();m.name='235 Broken wall '+role+' | '+base.name;m['235 wall role']=role
 # Preserve the actual prior illumination/palette source; final pigment comes from parent.
 em=next(x for x in m.node_tree.nodes if x.type=='EMISSION'and x.inputs['Color'].is_linked)
 old=next((n.outputs[0]for n in m.node_tree.nodes if n.type=='GROUP'and n.node_tree and n.node_tree.name.startswith('204 Half')),em.inputs['Color'].links[0].from_socket)
 mul=m.node_tree.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(.80,.83,.88,1)if role=='core'else(1.11,1.08,1.04,1);m.node_tree.links.new(old,mul.inputs[1]);m.node_tree.links.new(mul.outputs[0],em.inputs['Color']);return m

def ledge(scene,host,c,n,u,length,height,mat,index):
 """Intersect a battered ledge with a translated host volume: no floating/end rectangles."""
 c=Vector(c);n=Vector(n);u=Vector(u);up=Vector((0,0,1))
 profile=[(-.5,-.40),(-.41,-.50),(.35,-.50),(.50,-.20),(.44,.28),(.29,.5),(-.42,.5),(-.5,.13)]
 vs=[c+u*(x*length)+up*(z*height)+n*d for d in(-.055,.105)for x,z in profile];N=len(profile)
 fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N)for j in range(N)]
 me=bpy.data.meshes.new('235 broken slab ledge');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat)
 ob=bpy.data.objects.new('235 Interrupted slab remnant '+str(index)+' '+host.name,me);scene.collection.objects.link(ob)
 mask=host.copy();mask.data=host.data.copy();mask.name='235 temporary host mask';mask.modifiers.clear();mask.matrix_world.translation+=n*.105;scene.collection.objects.link(mask)
 mod=ob.modifiers.new('235 silhouette-following host intersection','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=mask;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(mask,do_unlink=True)
 scene.collection.objects.unlink(ob);bpy.data.collections['133 Ruined transition structures'].objects.link(ob);ob['235 structure']=True;ob['235 host']=host.name
 ink=bpy.data.collections['230 Broken transition wall ink targets'];ink.objects.link(ob)
 return ob

def apply(scene):
 from broken_wall_weathering_refine_232 import camera_samples
 from city_transition_refinement_200 import _cut,_closed,_mesh_digest
 C=bpy.data.collections['133 Ruined transition structures'];hosts=[bpy.data.objects[n]for n in NAMES];assert not any(o.get('235 structure')for o in hosts),'Apply235 once'
 original={o.name:(o.data,tuple(v for r in o.matrix_world for v in r),tuple(sl.material for sl in o.material_slots))for o in bpy.data.objects if o.type=='MESH'}
 samples,probe=camera_samples(scene,set(NAMES));rows=[];additions=[];cores={};lips={}
 for idx,ob in enumerate(hosts):
  pts=samples[ob.name];assert len(pts)>10,(ob.name,len(pts))
  # Camera rays establish the visible major face rather than hidden centers behind atmosphere.
  bins={}
  for p in pts:
   n=Vector(p['normal']);key=tuple(round(v)for v in n)
   if abs(n.z)<.15:bins.setdefault(key,[]).append(p)
  key=max(bins,key=lambda k:len(bins[k]));pts=bins[key];normal=Vector(key).normalized();u=normal.cross(Vector((0,0,1))).normalized()
  world=[Vector(p['point'])for p in pts];amin,amax=min(q.dot(u)for q in world),max(q.dot(u)for q in world);zmin,zmax=min(q.z for q in world),max(q.z for q in world)
  before=_mesh_digest(ob);mats=[sl.material for sl in ob.material_slots];indices=[p.material_index for p in ob.data.polygons];ob.data=ob.data.copy();ob.data.materials.clear()
  for m in mats:ob.data.materials.append(m)
  for sl in ob.material_slots:sl.link='DATA'
  for p,i in zip(ob.data.polygons,indices):p.material_index=i
  base=mats[0]
  if base not in cores:cores[base]=material(base,'core');lips[base]=material(base,'lip')
  core,lip=cores[base],lips[base];ob.data.materials.append(core);ob.data.materials.append(lip)
  # Bake existing tiny bevel before new construction, preserving actual visible source shape.
  bpy.context.view_layer.objects.active=ob
  for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
  center=min(world,key=lambda q:(q.dot(u)-(amin+(amax-amin)*(.45 if idx%2 else .58)))**2+(q.z-(zmin+(zmax-zmin)*.58))**2)
  width=min(1.48,max(.72,(amax-amin)*.60));height=min(2.25,max(.95,(zmax-zmin)*.50));outline=[(x*width,z*height)for x,z in PROFILES[idx%len(PROFILES)]]
  features=[_cut(ob,center,normal,outline,.060 if idx%2 else .078,'235 connected exposed facing loss',core)]
  # Sparse construction joints at storey/panel scale; unlike decorative scratches these span surviving fabric.
  levels=[z for z in (1.05,2.42,3.86,5.26)if zmin+.18<z<zmax-.20];seams=[]
  for j,z in enumerate(levels):
   near=min(world,key=lambda q:(q.z-z)**2);c=near.copy();c.z=z
   widthfull=(amax-amin)+.40
   profile=[(-widthfull/2,-.015),(widthfull/2,-.015),(widthfull/2,.015),(-widthfull/2,.015)]
   c+=u*((amin+amax)/2-c.dot(u));seams.append(_cut(ob,c,normal,profile,.018,'235 shallow horizontal construction joint',core))
   if j%2==idx%2:
    s=c+u*((-.21 if j%2 else .24)*(amax-amin))+Vector((0,0,.40));seams.append(_cut(ob,s,normal,[(-.012,-.40),(.012,-.40),(.012,.40),(-.012,.40)],.013,'235 staggered short panel joint',core))
  # A single interrupted projecting slab/lintel fragment establishes former floors without adding a full band.
  if levels and idx in (0,1,2,3,5,6,7):
   z=levels[min(1,len(levels)-1)];c=min(world,key=lambda q:(q.z-z)**2+(q.dot(u)-(amin+(amax-amin)*.33))**2).copy();c.z=z+.075
   new=ledge(scene,ob,c,normal,u,min(1.45,max(.62,(amax-amin)*.49)),.16,lip,idx);health=_closed(new);assert len(new.data.polygons)>0 and health['nonmanifold_edges']==0,(new.name,health);additions.append({'object':new.name,'host':ob.name,'health':health})
  ob['235 structure']=True;health=_closed(ob);assert health['nonmanifold_edges']==0,(ob.name,health)
  rows.append({'object':ob.name,'visible_samples':len(pts),'major_face_normal':list(normal),'visible_surface_bounds':[amin,zmin,amax,zmax],'large_facing_loss':features,'construction_joints':seams,'before_hash':before,'after_hash':_mesh_digest(ob),'health':health})
 names=set(NAMES)
 for name,(mesh,M,mats)in original.items():
  ob=bpy.data.objects[name];assert tuple(v for r in ob.matrix_world for v in r)==M
  if name not in names:assert ob.data==mesh and tuple(sl.material for sl in ob.material_slots)==mats,name
 return {'study':235,'source':'far-weathering-234','scope':'Eight most visible133 broken wall faces only','camera_probe':probe,'rows':rows,'added_structural_remnants':additions,'private_core_lip_materials':len(cores)+len(lips),'all_unrelated_original_meshes_material_bindings_transforms_exact':True,'references':['UCL-01','UCL-02','DP-03'],'status':'CPU candidate; parent finish and actual combined proof pending'}

if __name__=='__main__':
 O.mkdir(exist_ok=True,parents=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/far-weathering-234/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('235 STRUCTURE READY',len(a['rows']),len(a['added_structural_remnants']),flush=True)
