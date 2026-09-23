"""Repeat the selected Tower10 blind arched inset on matching middle-tier shafts."""
import bpy,bmesh,math,json,sys,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping

def apply(C):
 original,world,unpack=mapping();audit=[];removed=[];new=[];start=time.time()
 def mesh(name,vs,fs):
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);C.objects.link(o);return o
 def prism(j,name,outline,r0,r1):
  a=-math.pi+j*math.tau/36;vs=[world(r,a+u/75,z)for r in [r0,r1]for u,z in outline];N=len(outline);return mesh(name,vs,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)])
 def boolean(target,cutter,operation):
  m=target.modifiers.new('129 native inset '+operation,'BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=cutter;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=m.name)
 def attrs(ob):
  p=ob.data.attributes.get('115 Original world position')or ob.data.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
  for v in ob.data.vertices:
   r,a,z=unpack(ob.matrix_world@v.co);p.data[v.index].vector=original(r,a,z)
 for j in [1,4,7,13,16]:
  ob=C.objects.get(f'COL110 Tower{j} core')
  if ob is None:continue
  if ob.get('129 selected middle inset'):continue
  currentmats=[s.material for s in ob.material_slots];before=ob.data;beforeworld=[ob.matrix_world@v.co for v in before.vertices];beforetree=BVHTree.FromPolygons(beforeworld,[tuple(f.vertices)for f in before.polygons]);tmp=ob.copy();tmp.data=before.copy();tmp.modifiers.clear();C.objects.link(tmp);tmp.name=f'129 temp Tower{j}'
  if j==7:
   # Recover the actual clean front surface from pre-channel native geometry, not an applied cover.
   with bpy.data.libraries.load(str(R/'art/studies/coliseum-120/scene.blend'),link=False)as(src,dst):dst.objects=[f'COL110 Tower{j} core']
   clean=dst.objects[0];C.objects.link(clean);clean.modifiers.clear();region=prism(j,'129 old channel repair volume',[(-1.05,42.35),(1.05,42.35),(1.05,54.9),(-1.05,54.9)],76.9,79)
   boolean(clean,region,'INTERSECT');bpy.data.objects.remove(region,do_unlink=True)
   clean.data.materials.clear()
   for mat in currentmats:clean.data.materials.append(mat)
   for f in clean.data.polygons:f.material_index=0
   boolean(tmp,clean,'UNION');bpy.data.objects.remove(clean,do_unlink=True)
  # Three radial stages exactly match selected Tower10's true narrow arched cavity.
  width=.60;z0=46.7;z1=54.2;spring=z1-width;shape=[(-width,z0),(width,z0),(width,spring)]+[(width*math.cos(math.pi*k/10),spring+width*math.sin(math.pi*k/10))for k in range(1,11)];N=len(shape);a=-math.pi+j*math.tau/36;vs=[]
  for rr,scale in [(77.55,.88),(77.74,.88),(78.13,1.06)]:
   vs.extend(world(rr,a+u*scale/75,z0+(z-z0)*(.995 if scale<1 else 1.002))for u,z in shape)
  fs=[tuple(range(N-1,-1,-1)),tuple(range(2*N,3*N))]+[(r*N+k,r*N+(k+1)%N,(r+1)*N+(k+1)%N,(r+1)*N+k)for r in range(2)for k in range(N)];tool=mesh('129 matched arched inset',vs,fs);precavity=tmp.data.copy();tree=BVHTree.FromPolygons([tmp.matrix_world@v.co for v in precavity.vertices],[tuple(f.vertices)for f in precavity.polygons]);boolean(tmp,tool,'DIFFERENCE');bpy.data.objects.remove(tool,do_unlink=True)
  bm=bmesh.new();bm.from_mesh(tmp.data);bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.free()
  if bad or volume<=0:audit.append({'tower':j,'rejected_nonmanifold':bad,'volume':volume});bpy.data.objects.remove(tmp,do_unlink=True);continue
  me=tmp.data;mask=me.attributes.get('118 Recess interior')or me.attributes.new('118 Recess interior','FLOAT','FACE');newfaces=0
  for f in me.polygons:
   rr,aa,z=unpack(tmp.matrix_world@f.center);u=(aa-a)*75
   if j==7 and abs(u)<1.1 and 42.2<z<55:mask.data[f.index].value=0
   hit=tree.find_nearest(tmp.matrix_world@f.center)
   if abs(u)<.72 and 46.65<z<54.3 and hit and hit[3]>.0015:mask.data[f.index].value=1;newfaces+=1
  surface=BVHTree.FromPolygons([tmp.matrix_world@v.co for v in me.vertices],[tuple(f.vertices)for f in me.polygons]);outside_error=0
  for point in beforeworld:
   r0,aold,zold=unpack(point);uold=(aold-a)*75
   if abs(uold)>1.1 or zold<42.2 or zold>55:
    hit=surface.find_nearest(point);outside_error=max(outside_error,hit[3]if hit and hit[0]is not None else 999)
  assert outside_error<.003,(j,outside_error)
  ob.data=me;bpy.data.objects.remove(tmp,do_unlink=True)
  for i,mat in enumerate(currentmats):
   if i<len(ob.material_slots):ob.material_slots[i].link='OBJECT';ob.material_slots[i].material=mat
  attrs(ob);ob['129 selected middle inset']=True
  if j==7:
   for x in list(C.objects):
    if 'Tower7 middle shallow panel inset sill'in x.name:removed.append(x.name);bpy.data.objects.remove(x,do_unlink=True)
  # Reuse exact selected Tower10 sill profiles, remapped in native authored angle.
  for source in [x for x in C.objects if 'Tower10 middle blind niche inset sill'in x.name]:
   q=source.copy();q.data=source.data.copy();q.name=source.name.replace('Tower10',f'Tower{j}')+' matched129';q.modifiers.clear();q.matrix_world=ob.matrix_world.copy();iv=q.matrix_world.inverted()
   for v,sv in zip(q.data.vertices,source.data.vertices):
    rr,aa,z=unpack(source.matrix_world@sv.co);v.co=iv@world(rr,aa+(j-10)*math.tau/36,z)
   C.objects.link(q);q['bay']=j;q['129 selected middle inset']=True;attrs(q)
   # Copy the tower's exact rigid spacing transform, preserving shared group inputs.
   for mod in ob.modifiers:
    if mod.type=='NODES':
     mm=q.modifiers.new(mod.name,'NODES');mm.node_group=mod.node_group
     for item in mod.node_group.interface.items_tree:
      if item.item_type=='SOCKET'and item.in_out=='INPUT'and item.name!='Geometry':
       try:getattr(mm.properties.inputs,item.identifier).value=getattr(mod.properties.inputs,item.identifier).value
       except Exception:pass
   new.append(q.name)
  audit.append({'tower':j,'accepted':True,'width_m':1.2,'height_m':7.5,'bottom_top':[46.7,54.2],'outside_inset_surface_error_m':outside_error,'new_cavity_faces':newfaces,'nonmanifold_edges':bad,'volume':volume,'vertices_before_after':[len(before.vertices),len(me.vertices)]})
 # Match the actual selectedTower10 cavity graph (.65 multiply, violet-tinted deposit).
 shader_updates=[];cache={}
 for ob in C.objects:
  if ob.type!='MESH' or not ob.get('129 selected middle inset') or not ob.data.attributes.get('118 Recess interior'):continue
  for slot in ob.material_slots:
   src=slot.material
   if not src or not src.use_nodes:continue
   if any(n.type=='ATTRIBUTE' and n.attribute_name=='118 Recess interior' for n in src.node_tree.nodes):continue
   if src not in cache:
    m=src.copy();m.name='129 Matched tower inset '+src.name;n,l=m.node_tree.nodes,m.node_tree.links;em=next((q for q in n if q.type=='EMISSION'),None)
    if em is None or not em.inputs['Color'].is_linked:continue
    old=em.inputs['Color'].links[0].from_socket;attr=n.new('ShaderNodeAttribute');attr.attribute_name='118 Recess interior';factor=n.new('ShaderNodeMath');factor.operation='MULTIPLY';factor.inputs[1].default_value=.65;l.new(attr.outputs['Fac'],factor.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.label='118 Modeled recess deposit shade';mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.42,.38,.48,1);l.new(factor.outputs[0],mix.inputs[0]);l.new(old,mix.inputs[1]);l.new(mix.outputs[0],em.inputs['Color']);cache[src]=m
   slot.link='OBJECT';slot.material=cache[src];shader_updates.append({'object':ob.name,'source':src.name,'copy':cache[src].name})
 return {'cavity_shader_updates':shader_updates,'cavity_shader_strength':.65,'references':['UCL-01','UCL-02','DP-03'],'source':'128 scene','matched_source':'Tower10 middle blind arched niche','towers':audit,'removed_old_long_panel_sills':removed,'new_matching_sills':new,'preserved':'Tower10 selected niche, upper channels, structural cores outside middle inset, collars/crowns/group pose; original OBJECT material overrides.','seconds':time.time()-start}
if __name__=='__main__':
 O=R/'art/studies/coliseum-129/pillars';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-128/scene.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
 for o in bpy.data.objects:
  if 'Landmark contact ink'in o.name:o.hide_render=True
 s.render.use_freestyle=False;s.render.use_border=False;s.render.resolution_x=2560;s.render.resolution_y=1923;s.render.resolution_percentage=100;s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
