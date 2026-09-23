"""Editable, seeded recessed masonry spalls across the colosseum wall family.
Source 188, user requested broad repeatable weathering; no projected artwork.
Run Blender --python this.py -- build. apply(collection) is reusable by integration.
"""
import bpy, math, random, json, sys, hashlib, time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1]
O=R/'art/studies/coliseum-190'

def substrate(base, suffix, gain):
 m=base.copy();m.name='190 '+suffix+' '+base.name
 em=next((n for n in m.node_tree.nodes if n.type=='EMISSION'),None)
 if em and em.inputs[0].is_linked:
  source=em.inputs[0].links[0].from_socket
  mult=m.node_tree.nodes.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[2].default_value=(gain,gain*.985,gain*.975,1)
  mult.label='Shallow exposed substrate; inherited masonry light response'
  m.node_tree.links.new(source,mult.inputs[1]);m.node_tree.links.new(mult.outputs[0],em.inputs[0])
 m['190 role']=suffix;m['190 native geometry']='Only Boolean-created exposed cut surfaces'
 return m

def geometry(ob):
 dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
 vs=[ob.matrix_world@v.co for v in me.vertices]
 tris=[tuple(t.vertices)for t in me.loop_triangles]
 tree=BVHTree.FromPolygons(vs,tris,all_triangles=True)
 candidates=[];camera=bpy.context.scene.camera.matrix_world.translation
 for tri in me.loop_triangles:
  a,b,c=[vs[i]for i in tri.vertices];normal=(b-a).cross(c-a);area=normal.length/2
  if area<.03:continue
  normal.normalize();center=(a+b+c)/3
  mat=me.materials[tri.material_index]if tri.material_index<len(me.materials)else None
  if not mat or any(q in mat.name for q in ['shade','depth','joint','core']):continue
  if abs(normal.z)>.28 or normal.dot((camera-center).normalized())<.22:continue
  candidates.append((a,b,c,normal,area,tri.material_index))
 ev.to_mesh_clear();return tree,candidates

def basis(normal):
 v=Vector((0,0,1));v=(v-normal*v.dot(normal)).normalized();u=v.cross(normal).normalized();return u,v

def surface(tree,p,n):
 hit=tree.ray_cast(p+n*.5,-n,1.0)
 return hit[0] is not None and abs((hit[0]-p).dot(n))<.045 and hit[1].dot(n)>.97

def cut_shape(name,p,n,ru,rv,depth,rng,tree,coll,mats,core,rim,custom_coords=None):
 u,v=basis(n);count=rng.choice([11,13,15]);coords=[]
 phase=rng.random()*math.tau
 for i in range(count):
  a=math.tau*i/count;f=rng.uniform(.76,1.12)*(1+.1*math.sin(3*a+phase))
  coords.append((math.cos(a)*ru*f,math.sin(a)*rv*f))
 if custom_coords is not None:coords=custom_coords;count=len(coords)
 if not all(surface(tree,p+u*x+v*y,n)for x,y in coords):return None
 # A jagged rim slopes into a smaller irregular floor. The top lies outside the wall.
 verts=[p+u*x+v*y+n*.24 for x,y in coords]
 verts += [p+u*(x*.82)+v*(y*.82)-n*depth for x,y in coords]
 faces=[tuple(reversed(range(count))),tuple(range(count,count*2))]
 faces += [(i,(i+1)%count,(i+1)%count+count,i+count)for i in range(count)]
 # Correct winding explicitly; Boolean uses manifold volume orientation.
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 import bmesh
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 for m in mats:me.materials.append(m)
 for f in me.polygons:f.material_index=core if f.index==1 else rim
 provenance=me.attributes.new('190 Material provenance','INT','FACE')
 for f in me.polygons:provenance.data[f.index].value=f.material_index+1
 ob=bpy.data.objects.new(name,me);coll.objects.link(ob);ob['190 damage role']='shallow spall cutter';ob['190 recess depth']=depth;ob['190 seed shape']=True
 return ob

def apply(C, config=None):
 cfg=config or json.loads((R/'config/colosseum-crumbling-190.json').read_text())
 if bpy.data.collections.get('190 Colosseum editable wall crumbling'):raise RuntimeError('190 already present; reopen unmodified source')
 layer=bpy.data.collections.new('190 Colosseum editable wall crumbling');C.children.link(layer)
 cutters=bpy.data.collections.new('190 Editable cutters hidden from render');layer.children.link(cutters)
 rng=random.Random(cfg['seed']);s=bpy.context.scene;targets=[]
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  arcade='continuous arcade wall'in ob.name
  upper=ob.get('coliseum_role')=='wall'and ob.get('tier')==3 and ('fractured upper wall'in ob.name or 'aperture head'in ob.name)
  if arcade or upper:targets.append(ob)
 targets.sort(key=lambda o:o.name)
 materials={};audit=[];patches=[];allaccepted=[];start=time.time()
 for ob in targets:
  tree,faces=geometry(ob)
  if not faces:continue
  arcade='continuous arcade wall'in ob.name
  desired=cfg['arcade_clusters_per_tier']if arcade else 1 if rng.random()<cfg['upper_wall_cluster_probability']else 0
  if not desired:continue
  base=next((m for m in ob.data.materials if m and m.name=='116 115 Painted masonry wall'),None)
  if base is None:base=next((m for m in ob.data.materials if m and 'Painted masonry wall'in m.name),None)
  if base is None:continue
  effective_index=next(i for i,m in enumerate(ob.data.materials)if m==base)
  base=ob.material_slots[effective_index].material
  if base.name not in materials:materials[base.name]=[substrate(base,'fresh fractured rim',cfg.get('rim_gain',.88)),substrate(base,'weathered recessed substrate',cfg.get('substrate_gain',.57))]
  mats=[sl.material for sl in ob.material_slots]+materials[base.name];rim=len(mats)-2;core=len(mats)-1
  per=bpy.data.collections.new('190 Cutters '+ob.name);cutters.children.link(per)
  weights=[f[4]for f in faces];chosen=[];attempts=0
  while len(chosen)<desired and attempts<desired*100:
   attempts+=1;a,b,c,n,area,slot=rng.choices(faces,weights=weights,k=1)[0]
   f1=math.sqrt(rng.random());f2=rng.random();p=a*(1-f1)+b*(f1*(1-f2))+c*(f1*f2)
   if any((p-q).length<3.0 for q in chosen):continue
   ru=rng.uniform(*cfg['primary_radius_m']);rv=ru*rng.uniform(.75,1.7)
   if arcade:rv=min(rv,1.35)
   depth=rng.uniform(*cfg['recess_depth_m'])
   made=cut_shape('190 SPALL '+ob.name+' '+str(len(chosen)),p,n,ru,rv,depth,rng,tree,per,mats,core,rim)
   if made is None:continue
   chosen.append(p);allaccepted.append(p)
   nd=world_to_camera_view(s,s.camera,p)
   row={'owner':ob.name,'tier':int(ob.get('tier',3)),'bay':int(ob.get('bay',-1)),'center':list(p),'radius':[ru,rv],'depth':depth,'projected_pixel_4k':[nd.x*3840,(1-nd.y)*2885],'role':'primary','cutter':made.name}
   patches.append(row)
   u,v=basis(n)
   if rng.random()<cfg.get('fracture_probability',.38):
    length=rng.uniform(1.0,2.6);angle=rng.uniform(-2.5,-.55)
    dx,dy=math.cos(angle),math.sin(angle);px,py=-dy,dx
    chain=[]
    for k in range(6):
     f=k/5;w=rng.uniform(.035,.075)*(1-.75*f)
     wobble=0 if k==0 else rng.uniform(-.15,.15)
     chain.append((dx*f*length+px*wobble,dy*f*length+py*wobble,w))
    coords=[(x+px*w,y+py*w)for x,y,w in chain]+[(x-px*w,y-py*w)for x,y,w in reversed(chain)]
    q=p+u*(dx*ru*.73)+v*(dy*rv*.73)
    crack=cut_shape('190 FRACTURE '+ob.name+' '+str(len(chosen)),q,n,1,1,.075,rng,tree,per,mats,core,core,coords)
    if crack:
     crack['190 damage role']='connected narrow jagged fracture cut'
     patches.append({'owner':ob.name,'tier':row['tier'],'bay':row['bay'],'center':list(q),'role':'fracture','length':length,'cutter':crack.name})
   for j in range(rng.choice([1,2,2,3])):
    side=rng.choice([-1,1]);q=p+u*(side*ru*rng.uniform(.8,1.6))+v*(rv*rng.uniform(-1.25,1.25))
    if not surface(tree,q,n):continue
    sr=rng.uniform(.12,.36)
    sat=cut_shape('190 CHIP '+ob.name+' '+str(len(chosen))+' '+str(j),q,n,sr,sr*rng.uniform(.8,1.8),depth*rng.uniform(.4,.8),rng,tree,per,mats,core,rim)
    if sat:patches.append({'owner':ob.name,'tier':row['tier'],'bay':row['bay'],'center':list(q),'radius':[sr,sr],'role':'companion','cutter':sat.name})
  if not chosen:
   bpy.data.collections.remove(per);continue
  # Single exact Boolean against a disconnected collection avoids repeated destructive solves.
  before=[len(ob.data.vertices),len(ob.data.polygons)]
  effective=[sl.material for sl in ob.material_slots]
  ob.data=ob.data.copy()
  for sl,mat in zip(ob.material_slots,effective):sl.link='DATA';sl.material=mat
  for mat in materials[base.name]:ob.data.materials.append(mat)
  provenance=ob.data.attributes.new('190 Material provenance','INT','FACE')
  for f in ob.data.polygons:provenance.data[f.index].value=f.material_index+1
  mod=ob.modifiers.new('190 Actual shallow wall crumbling','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.operand_type='COLLECTION';mod.collection=per
  if hasattr(mod,'use_self'):mod.use_self=True
  bpy.context.view_layer.update()
  dg=bpy.context.evaluated_depsgraph_get();evaluated=ob.evaluated_get(dg)
  new=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=dg)
  if len(new.polygons)<len(ob.data.polygons)*.6:raise RuntimeError('Unexpected wall loss '+ob.name)
  ids=[v.value for v in new.attributes['190 Material provenance'].data]
  assert all(0<i<=len(mats)for i in ids),'Invalid face provenance '+ob.name
  new.materials.clear()
  for m in mats:new.materials.append(m)
  for f,i in zip(new.polygons,ids):f.material_index=i-1
  # Bake result but keep source as a native datablock and cutters for editable rebuilding.
  ob.data.name='190 SOURCE '+ob.name;ob.data.use_fake_user=True
  ob.data=new
  for sl in ob.material_slots:sl.link='DATA'
  for m in list(ob.modifiers):ob.modifiers.remove(m)
  ob['190 crumbling applied']=True;ob['190 original mesh']='190 SOURCE '+ob.name;ob['190 cutter collection']=per.name
  audit.append({'object':ob.name,'before':before,'after':[len(new.vertices),len(new.polygons)],'primary_clusters':len(chosen),'cutters':len(per.objects),'attempts':attempts})
  print('CRUMBLING190',ob.name,len(chosen),len(per.objects),flush=True)
 cutters.hide_render=True;cutters.hide_viewport=True
 for ob in cutters.all_objects:ob.hide_render=True;ob.hide_set(True)
 report={'source':'188','reference_ids':cfg['references'],'changed_walls':audit,'patches':patches,'primary_clusters':sum(p['role']=='primary'for p in patches),'companion_chips':sum(p['role']=='companion'for p in patches),'fractures':sum(p['role']=='fracture'for p in patches),'wall_objects':len(audit),'unchanged_systems':cfg['fixed'],'method':'Native exact Boolean shallow tapered jagged recesses; cutters and original native meshes retained hidden, inherited masonry lighting for rim and substrate. No image projection.','elapsed_seconds':time.time()-start,'review_status':'Native build only, visual proof pending','user_approved':False}
 return report

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else ['build']
 O.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-188/scene.blend'))
 report=apply(bpy.data.collections['110 Coliseum detailed front ruin'])
 (O/'build-audit.json').write_text(json.dumps(report,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'))
 print('DONE190',report['wall_objects'],report['primary_clusters'],report['companion_chips'])
