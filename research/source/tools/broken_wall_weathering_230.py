"""Scoped native erosion and material weathering for existing broken transition walls."""
import bpy,bmesh,json,random,math,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/broken-walls-230'
sys.path.insert(0,str(R/'tools'))

def finish(base,core=False):
 m=base.copy();m.name='230 '+('Exposed mineral ' if core else 'Broken wall weathering ')+base.name;n=m.node_tree.nodes;l=m.node_tree.links
 em=next(x for x in n if x.type=='EMISSION' and x.inputs['Color'].is_linked);old=em.inputs['Color'].links[0].from_socket
 def op(code,a,b):
  q=n.new('ShaderNodeMath');q.operation=code
  for i,v in enumerate((a,b)):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def ramp(v,a,b):
  q=n.new('ShaderNodeMapRange');q.clamp=True;l.new(v,q.inputs[0]);q.inputs[1].default_value=a;q.inputs[2].default_value=b;return q.outputs[0]
 def mix(f,a,b,blend='MIX'):
  q=n.new('ShaderNodeMixRGB');q.blend_type=blend
  for i,v in enumerate((f,a,b)):
   if isinstance(v,(int,float,tuple,list)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 pos=n.new('ShaderNodeNewGeometry').outputs['Position'];sep=n.new('ShaderNodeSeparateXYZ');l.new(pos,sep.inputs[0])
 def noise(scale,stretch=None):
  v=pos
  if stretch:
   q=n.new('ShaderNodeVectorMath');q.operation='MULTIPLY';q.inputs[1].default_value=stretch;l.new(v,q.inputs[0]);v=q.outputs[0]
  q=n.new('ShaderNodeTexNoise');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=2.6;q.inputs['Roughness'].default_value=.72;l.new(v,q.inputs['Vector']);return q.outputs['Fac']
 broad=noise(.7);medium=noise(3.8);fine=noise(32)
 field=op('ADD',op('MULTIPLY',broad,.54),op('MULTIPLY',medium,.46))
 islands=ramp(field,.43,.62)
 body=mix(op('MULTIPLY',islands,.56),old,mix(1,old,(.55,.60,.69,1),'MULTIPLY'))
 mineral=ramp(op('ADD',op('MULTIPLY',medium,.7),op('MULTIPLY',fine,.3)),.47,.63)
 body=mix(op('MULTIPLY',mineral,.40),body,mix(1,old,(1.36,1.28,1.16,1),'MULTIPLY'))
 rain=ramp(noise(1,(11,11,.24)),.54,.68);rain=op('MULTIPLY',rain,ramp(broad,.34,.58))
 body=mix(op('MULTIPLY',rain,.40),body,mix(1,old,(.51,.47,.45,1),'MULTIPLY'))
 basal=op('SUBTRACT',1,ramp(sep.outputs['Z'],.12,2.5));specks=ramp(noise(1,(46,46,90)),.64,.72)
 density=op('ADD',.10,op('MULTIPLY',basal,.73));body=mix(op('MULTIPLY',specks,density),body,(.024,.021,.028,1))
 # Base light mineral splashes interleave dark scuffs; neither covers the entire face.
 splash=op('MULTIPLY',basal,ramp(noise(12),.57,.67));body=mix(op('MULTIPLY',splash,.32),body,mix(1,old,(1.44,1.34,1.18,1),'MULTIPLY'))
 if core:body=mix(1,body,(.76,.78,.82,1),'MULTIPLY')
 l.new(body,em.inputs['Color']);m['230 private weathering']=True;return m

def visible_samples(scene,ob):
 dg=bpy.context.evaluated_depsgraph_get();cam=scene.camera.matrix_world.translation;out=[]
 # Deterministic surface samples on actual existing faces; no image-based paint.
 rng=random.Random(230+sum(map(ord,ob.name)))
 ob.data.calc_loop_triangles()
 for tri in ob.data.loop_triangles:
  if tri.area<.06 or abs(tri.normal.z)>.3:continue
  vs=[ob.matrix_world@ob.data.vertices[i].co for i in tri.vertices];c=sum(vs,Vector())/3
  pts=[c]
  for _ in range(3):
   a,b=rng.sample(vs,2);pts.append(c.lerp(a.lerp(b,rng.random()),rng.uniform(.15,.8)))
  for q in pts:
   proj=world_to_camera_view(scene,scene.camera,q)
   if not(.02<proj.x<.98 and .04<proj.y<.95):continue
   d=q-cam;hit=scene.ray_cast(dg,cam,d.normalized(),distance=d.length+.04)
   if hit[0] and hit[4].original==ob and (hit[1]-q).length<.025:out.append((q,hit[2].copy()))
 return out

def install_ink(scene,targets):
 c=bpy.data.collections.new('230 Broken transition wall ink targets');c.use_fake_user=True
 for o in targets:c.objects.link(o)
 vl=scene.view_layers['215 Distant ink without atmospheric boundary'];ls=vl.freestyle_settings.linesets.new('230 Broken wall readable contours');ls.select_by_collection=True;ls.collection=c;ls.collection_negation='INCLUSIVE';ls.select_by_visibility=True;ls.visibility='VISIBLE'
 ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True;ls.select_external_contour=True;ls.select_edge_mark=False;ls.select_material_boundary=False
 ls.linestyle.color=(.018,.013,.024);ls.linestyle.thickness=1.15
 return {'layer':vl.name,'line_set':ls.name,'thickness':1.15,'visibility':'Native hidden-line visibility; existing atmospheric container excluded only in this ink layer','objects':len(targets)}

def apply(scene):
 from city_transition_refinement_200 import _cut,_closed,_mesh_digest
 C=bpy.data.collections['133 Ruined transition structures'];targets=[o for o in C.objects if o.type=='MESH' and any(k in o.name for k in ('standing street wall','attached return','camera-facing cross wall','remnant return pier'))]
 assert targets and not any(o.get('230 weathered') for o in targets),'Apply230 once to fresh229 source'
 old={o.name:(o.data,tuple(v for r in o.matrix_world for v in r),tuple(sl.material for sl in o.material_slots))for o in bpy.data.objects if o.type=='MESH'}
 cache={};cores={};rows=[]
 samples={o.name:visible_samples(scene,o) for o in targets}
 for ob in targets:
  rng=random.Random(23000+sum((i+1)*ord(c)for i,c in enumerate(ob.name)));before=_mesh_digest(ob)
  mats=[sl.material for sl in ob.material_slots];indices=[p.material_index for p in ob.data.polygons];ob.data=ob.data.copy();ob.data.materials.clear()
  for m in mats:
   if m not in cache:cache[m]=finish(m)
   ob.data.materials.append(cache[m])
  for sl in ob.material_slots:sl.link='DATA'
  for poly,index in zip(ob.data.polygons,indices):poly.material_index=index
  pts=samples[ob.name];features=[];chosen=[]
  if len(pts)>2 and 'pier' not in ob.name:
   source=mats[0]
   if source not in cores:cores[source]=finish(source,True)
   core=cores[source];ob.data.materials.append(core)
   for q,n in sorted(pts,key=lambda x:rng.random()):
    if q.z<.40 or any((q-p).length<.85 for p in chosen):continue
    chosen.append(q);first_normal=n if len(chosen)==1 else first_normal;w=rng.uniform(.40,.95);h=rng.uniform(.65,1.5)
    N=rng.randint(9,14);outline=[]
    for j in range(N):
     a=2*math.pi*j/N;r=rng.uniform(.62,1.0);outline.append((math.cos(a)*w*.5*r,math.sin(a)*h*.5*r))
    features.append(_cut(ob,q,n,outline,rng.uniform(.025,.065),'230 shallow connected face erosion',core))
    if len(chosen)>=min(4,1+len(pts)//16):break
   if chosen:
    q=chosen[0]-Vector((0,0,.42));n=first_normal
    outline=[(-.02,.54),(.045,.27),(.018,.12),(.07,-.08),(.017,-.52),(-.02,-.12),(-.055,.10),(-.01,.32)]
    features.append(_cut(ob,q,n,outline,.025,'230 descending fracture',core))
  ob['230 weathered']=True;health=_closed(ob);assert health['nonmanifold_edges']==0,(ob.name,health)
  rows.append({'object':ob.name,'visible_samples':len(pts),'features':features,'health':health,'before_hash':before,'after_hash':_mesh_digest(ob)})
 ink=install_ink(scene,targets)
 names={o.name for o in targets}
 for name,(mesh,M,mats) in old.items():
  o=bpy.data.objects[name];assert tuple(v for r in o.matrix_world for v in r)==M,name
  if name not in names:assert o.data==mesh and tuple(sl.material for sl in o.material_slots)==mats,name
 return {'study':230,'source':'entry-surround-229','scope':'133 broken transition walls/returns/piers only','targets':len(targets),'private_materials':len(cache)+len(cores),'features':sum(len(r['features'])for r in rows),'rows':rows,'ink':ink,'all_other_meshes_bindings_transforms_preserved':True,'references':['UCL-01','UCL-02','DP-03'],'status':'CPU candidate; actual combined render required; 8–9/10 is user target not awarded score'}

if __name__=='__main__':
 O.mkdir(exist_ok=True,parents=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/entry-surround-229/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('230 READY',a['targets'],a['features'],flush=True)
