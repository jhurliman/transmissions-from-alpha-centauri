"""Reusable native facing losses and fractures on the existing ruined transition kit.
Only the133bridge family changes. Inputs are native camera-visibility samples;
all cuts are physical solids and all old material graphs remain intact.
"""
import bpy,bmesh,math,random,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-transition-200'
CNAME='133 Ruined transition structures'

def _mesh_digest(ob):
 return hashlib.sha256(repr(([tuple(v.co)for v in ob.data.vertices],[tuple(p.vertices)for p in ob.data.polygons],[p.material_index for p in ob.data.polygons])).encode()).hexdigest()

def _closed(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-12 for f in bm.faces);bm.free();return dict(nonmanifold_edges=bad,tiny_faces=zero,vertices=len(ob.data.vertices),faces=len(ob.data.polygons))

def _wear_material(old):
 m=old.copy();m.name='200 Broad worn facing | '+old.name;n=m.node_tree.nodes;l=m.node_tree.links
 out=next(q for q in n if q.type=='OUTPUT_MATERIAL');em=out.inputs['Surface'].links[0].from_node
 original=em.inputs['Color'].links[0].from_socket
 geo=n.new('ShaderNodeNewGeometry');broad=n.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=1.25;broad.inputs['Detail'].default_value=2.1;broad.inputs['Roughness'].default_value=.73;l.new(geo.outputs['Position'],broad.inputs['Vector'])
 detail=n.new('ShaderNodeTexNoise');detail.inputs['Scale'].default_value=9.;detail.inputs['Detail'].default_value=2.;l.new(geo.outputs['Position'],detail.inputs['Vector'])
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.30;l.new(broad.outputs['Fac'],mix.inputs[1]);l.new(detail.outputs['Fac'],mix.inputs[2])
 ramp=n.new('ShaderNodeValToRGB');ramp.label='200 Clustered eroded facing, retained quiet planes';ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(.47,.43,.48,1);ramp.color_ramp.elements[1].position=.52;ramp.color_ramp.elements[1].color=(1.04,1.02,1.0,1);l.new(mix.outputs[0],ramp.inputs[0])
 mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=.50;l.new(original,mul.inputs[1]);l.new(ramp.outputs[0],mul.inputs[2]);l.new(mul.outputs[0],em.inputs['Color']);return m

def _core_material(old):
 m=old.copy();m.name='200 Exposed recessed masonry | '+old.name
 for n in m.node_tree.nodes:
  if n.type=='VALTORGB'and n.label=='133 Broken-building shade families':
   for el in n.color_ramp.elements:
    c=el.color;el.color=(c[0]*.66,c[1]*.59,c[2]*.57,c[3])
 return m

def _cut(ob,center,normal,outline,depth,label,core):
 n=Vector(normal).normalized();up=Vector((0,0,1));u=n.cross(up).normalized()
 if u.length<.1:u=n.cross(Vector((0,1,0))).normalized();up=u.cross(n).normalized()
 c=Vector(center);vs=[];N=len(outline)
 # Wider entry and irregular narrowing deeper pocket give genuine shaded fracture lips.
 for z,scale in((.035,1.0),(-depth,.77)):
  vs.extend(c+u*(a*scale)+up*(b*scale)+n*z for a,b in outline)
 fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
 me=bpy.data.meshes.new('200 temporary cut');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for slot in ob.material_slots:me.materials.append(slot.material)
 if core.name not in [m.name for m in me.materials if m]:me.materials.append(core)
 cutmat=len(me.materials)-1
 for p in me.polygons:p.material_index=cutmat
 temp=bpy.data.objects.new('200 temporary '+label,me);bpy.context.scene.collection.objects.link(temp)
 mod=ob.modifiers.new('200 '+label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=temp
 bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(temp,do_unlink=True)
 return dict(label=label,center=list(c),normal=list(n),depth=depth,outline=outline)

def _outline(rng,width,height):
 N=11;poly=[]
 for j in range(N):
  a=2*math.pi*j/N;r=rng.uniform(.68,1.0);poly.append((math.cos(a)*width*.5*r,math.sin(a)*height*.5*r))
 return poly

def build(scene):
 C=bpy.data.collections.get(CNAME)
 if C is None:raise RuntimeError('133transition collection missing')
 if any(o.get('200 refined')for o in C.objects):raise RuntimeError('200already applied')
 inventory=json.loads((O/'inventory.json').read_text());visible=inventory['visible_samples'];materials={};rows=[];originals={o.name:_mesh_digest(o)for o in C.objects if o.type=='MESH'}
 coreold=bpy.data.materials['133 exposed warm-gray aggregate'];core=_core_material(coreold)
 for ob in sorted(C.objects,key=lambda o:o.name):
  if ob.type!='MESH':continue
  # Private node graphs shared only among this refinement's slots.
  for sl in ob.material_slots:
   old=sl.material
   if old is None:continue
   if old.name not in materials:materials[old.name]=_wear_material(old)
   sl.link='OBJECT';sl.material=materials[old.name]
  ob['200 refined']=True
  samples=visible.get(ob.name,[])
  wall=any(t in ob.name for t in('standing street wall','attached return','camera-facing cross wall'))
  floor=any(t in ob.name for t in('surviving floor','collapsed floor','grounded broken plate'))
  if not(wall or floor)or len(samples)<8:continue
  rng=random.Random(20000+sum((i+1)*ord(c)for i,c in enumerate(ob.name)))
  ob.data=ob.data.copy()
  for mod in list(ob.modifiers):
   bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
  # Explicit slot index allows Boolean cutter surfaces to inherit only this new core.
  ob.data.materials.append(core)
  if floor:
   candidates=[p for p in samples if p['normal'][2]>.35]
   if not candidates:continue
   edge=min(candidates,key=lambda p:abs(p['point'][0]));features=[_cut(ob,edge['point'],edge['normal'],_outline(rng,.72,.60),.32,'broken exposed slab edge',core)]
   health=_closed(ob)
   if health['nonmanifold_edges']:raise RuntimeError((ob.name,health))
   rows.append(dict(object=ob.name,visible_ray_samples=len(samples),features=features,health=health,before_hash=originals[ob.name],after_hash=_mesh_digest(ob)))
   continue
  candidates=[p for p in samples if abs(p['normal'][2])<.25 and p['point'][2]>.55]
  if not candidates:continue
  pix={(p['pixel'][0],p['pixel'][1])for p in candidates}
  interior=[p for p in candidates if sum((p['pixel'][0]+dx,p['pixel'][1]+dy)in pix for dx,dy in[(4,0),(-4,0),(0,4),(0,-4)])>=3]
  pool=interior or candidates;rng.shuffle(pool);chosen=[];features=[];limit=3 if len(samples)>100 else 2
  for p in pool:
   if all((Vector(p['point'])-Vector(q['point'])).length>1.1 for q in chosen):chosen.append(p)
   if len(chosen)>=limit:break
  for j,p in enumerate(chosen):
   width=rng.uniform(.55,.95);height=rng.uniform(.95,1.55);features.append(_cut(ob,p['point'],p['normal'],_outline(rng,width,height),rng.uniform(.095,.155),'recessed facing loss '+str(j),core))
  # One longer broken fracture per visible ruin; native void tapers, no painted ink-only crack.
  if chosen and len(samples)>35:
   p=chosen[-1];c=Vector(p['point'])+Vector((0,0,.45));profile=[(-.025,.75),(.045,.51),(.025,.26),(.10,.04),(.035,-.30),(.015,-.72),(-.045,-.37),(-.025,-.08),(-.075,.18),(-.025,.42)]
   features.append(_cut(ob,c,p['normal'],profile,.12,'irregular vertical fracture',core))
  # A visible upper edge receives an actual missing chip, opening the otherwise straight rim.
  high=max(candidates,key=lambda p:p['point'][2]);c=Vector(high['point'])+Vector((0,0,.18))
  features.append(_cut(ob,c,high['normal'],_outline(rng,.65,.70),.42,'broken crown edge',core))
  health=_closed(ob)
  if health['nonmanifold_edges']:raise RuntimeError((ob.name,health))
  rows.append(dict(object=ob.name,visible_ray_samples=len(samples),features=features,health=health,before_hash=originals[ob.name],after_hash=_mesh_digest(ob)))
 return dict(version=200,source='beam-rust-197',target_collection=CNAME,objects_with_geometry_edits=len(rows),material_objects=sum(o.type=='MESH'for o in C.objects),features=sum(len(r['features'])for r in rows),rows=rows,old_material_graphs_changed=False,all_other_collections_unchanged=True,object_transforms_unchanged=True,references=['UCL-01','UCL-02','DP-03'],limits='Visibility placement sampled at4px; broader pigment added to57bridgeparts; fracture geometry visible effect must be reviewed in actual native render. No road/new rubble placement changes.')

def apply(scene):
 """Fast checked replay of the native200payload on an unchanged133bridge family."""
 payload=O/'payload.json'
 if not payload.exists():return build(scene)
 j=json.loads(payload.read_text());C=bpy.data.collections.get(CNAME)
 if C is None:raise RuntimeError('133transition collection missing')
 for row in j['rows']:
  ob=bpy.data.objects[row['object']]
  assert ob in list(C.objects) and not ob.get('200 refined'),row['object']
  assert _mesh_digest(ob)==row['before']['mesh_hash'],('Source133geometrychanged',ob.name)
  assert [list(r)for r in ob.matrix_world]==row['before']['matrix'],('Source133transformchanged',ob.name)
  assert [s.material.name if s.material else None for s in ob.material_slots]==row['before']['materials'],('Source133bindingchanged',ob.name)
 with bpy.data.libraries.load(str(O/'payload.blend'),link=False)as(src,dst):
  dst.meshes=j['meshes'];dst.materials=j['materials']
 meshes=dict(zip(j['meshes'],dst.meshes));mats=dict(zip(j['materials'],dst.materials))
 for row in j['rows']:
  ob=bpy.data.objects[row['object']]
  if row['mesh']:
   ob.modifiers.clear();ob.data=meshes[row['mesh']]
  for slot,name in zip(ob.material_slots,row['materials']):slot.link='OBJECT';slot.material=mats[name]if name else None
  ob['200 refined']=True
  assert _mesh_digest(ob)==row['after_mesh_hash'],('Payloadgeometrymismatch',ob.name)
 return dict(version=200,mode='Checked nativepayloadreplay',objects=len(j['rows']),geometry_objects=len(j['meshes']),all_source133hashes_transforms_materialbindings_matched=True,all_candidate_geometry_hashes_matched=True,source='beam-rust-197',payload='art/studies/city-transition-200/payload.blend',references=['UCL-01','UCL-02','DP-03'])

if __name__=='__main__':
 import sys,time
 sys.path.insert(0,str(R/'tools'));bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/beam-rust-197/scene.blend'));t=__import__('time').time();result=build(bpy.context.scene);result['seconds']=__import__('time').time()-t;(O/'audit.json').write_text(json.dumps(result,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));print('200_READY',result['objects_with_geometry_edits'],result['features'],flush=True)
