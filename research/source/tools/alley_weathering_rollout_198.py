"""198 facade material and native damage rollout; apply to fresh197-derived scene.
Native Boolean recesses on simple panel skins; private instance collections for
shared kit faces. Originals and services retained. No render state changes.
"""
import bpy,math,random,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-weathering-198';sys.path.insert(0,str(R/'tools'))

def finish(base,post=False):
 base.use_fake_user=True
 m=base.copy();m.name='198 Connected coating '+base.name;n=m.node_tree.nodes;l=m.node_tree.links
 em=next((x for x in n if x.type=='EMISSION'),None)
 if not em or not em.inputs[0].is_linked:return m
 old=em.inputs[0].links[0].from_socket
 def mathn(op,a,b):
  q=n.new('ShaderNodeMath');q.operation=op;q.label='198 '+op
  for i,x in enumerate((a,b)):
   if isinstance(x,(int,float)):q.inputs[i].default_value=x
   else:l.new(x,q.inputs[i])
  return q.outputs[0]
 def mapn(a,lo,hi):
  q=n.new('ShaderNodeMapRange');q.clamp=True;q.interpolation_type='SMOOTHSTEP';l.new(a,q.inputs[0]);q.inputs[1].default_value=lo;q.inputs[2].default_value=hi;return q.outputs[0]
 def mix(f,a,b,op='MIX'):
  q=n.new('ShaderNodeMixRGB');q.blend_type=op;q.label='198 native connected coating'
  for i,x in enumerate((f,a,b)):
   if isinstance(x,(tuple,list,int,float)):q.inputs[i].default_value=x
   else:l.new(x,q.inputs[i])
  return q.outputs[0]
 pos=n.new('ShaderNodeNewGeometry').outputs['Position']
 def noise(scale,detail):
  q=n.new('ShaderNodeTexNoise');l.new(pos,q.inputs['Vector']);q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.67;return q.outputs['Fac']
 macro=noise(.82,2.3);medium=noise(4.1,3.2);fine=noise(21,2)
 # A broad domain determines groups; medium ragged islands carry the silhouette.
 field=mathn('ADD',mathn('MULTIPLY',macro,.56),mathn('MULTIPLY',medium,.44))
 islands=mapn(mathn('ADD',field,mathn('MULTIPLY',fine,.045)),.47,.60)
 film=mathn('MULTIPLY',mapn(macro,.30,.72),.24)
 body=mix(film,old,mix(1,old,(.72,.76,.82,1),'MULTIPLY'))
 body=mix(mathn('MULTIPLY',islands,.58),body,mix(1,body,((1.85,1.60,1.39,1)if post else(.64,.70,.79,1)),'MULTIPLY'))
 fringe=mathn('MULTIPLY',mapn(medium,.41,.53),mapn(mathn('SUBTRACT',.61,field),0,.13))
 body=mix(mathn('MULTIPLY',fringe,.32),body,mix(1,body,(1.23,1.19,1.12,1),'MULTIPLY'))
 l.new(body,em.inputs[0]);m['198 role']='Broad connected irregular coating islands, finer broken fringes; original lit palette below';return m

def cut_material(base):
 m=base.copy();m.name='198 Dark exposed substrate '+base.name
 em=next((x for x in m.node_tree.nodes if x.type=='EMISSION'),None)
 if em and em.inputs[0].is_linked:
  old=em.inputs[0].links[0].from_socket;q=m.node_tree.nodes.new('ShaderNodeMixRGB');q.blend_type='MULTIPLY';q.inputs[0].default_value=1;q.inputs[2].default_value=(.34,.32,.32,1);m.node_tree.links.new(old,q.inputs[1]);m.node_tree.links.new(q.outputs[0],em.inputs[0])
 return m

def visible(s,dg,p):
 d=p-s.camera.matrix_world.translation;q=s.ray_cast(dg,s.camera.matrix_world.translation,d.normalized(),distance=d.length+.02)
 return q[0] and (q[1]-p).length<.045

def apply(scene=None):
 s=scene or bpy.context.scene;assert not any(o.get('198 native damage')for o in bpy.data.objects),'Apply198 once to fresh197'
 from alley_damage_145 import cutter,cut
 helper=(R/'tools/scene_integration_138.py').read_text();auditns={};exec(helper[helper.index('def objects('):helper.index("if 'render' not in sys.argv:")],globals(),auditns)
 # Snapshot uses bpy/json/hashlib globals already imported.
 oldgraphs=auditns['material_snapshot']();oldtransforms={o.name:tuple(v for row in o.matrix_basis for v in row)for o in bpy.data.objects};camera=s.camera.name;lights={o.name:tuple(o.location)for o in s.objects if o.type=='LIGHT'}
 rng=random.Random(198);host=bpy.data.objects['Front-left section instance'];C=host.instance_collection
 cache={};finished=[]
 for ob in list(C.all_objects)+[bpy.data.objects['Service bay portal jamb.001']]:
  if ob.type!='MESH' or not ob.get('193 facade40'):continue
  for sl in ob.material_slots:
   base=sl.material
   if not base or not base.name.startswith('193 '):continue
   key=(base.name,ob.name=='Service bay portal jamb.001')
   if key not in cache:cache[key]=finish(base,post=key[1])
   sl.link='OBJECT';sl.material=cache[key]
  finished.append(ob.name)
 dg=bpy.context.evaluated_depsgraph_get();candidates=[]
 for ins in dg.object_instances:
  ob=ins.object.original
  if ob.type!='MESH' or len(ob.data.vertices)!=8 or not ins.parent:continue
  hn=ins.parent.original.name
  primary=hn==host.name
  if not(primary and any(t in ob.name for t in ['Recessed base wall','Upper recessed mass panel','Recessed column face']) or (any(hn.startswith(t)for t in ['Architecture | layout','Architecture | window','035 | window','right_vertical_galleries','right_horizontal_utility']) and ob.name.startswith(('Folded sheet face','Gallery base panel')) and ob.name in ins.parent.original.instance_collection.objects)):continue
  M=ins.matrix_world.copy();vs=[v.co for v in ob.data.vertices];lo=Vector(tuple(min(v[k]for v in vs)for k in range(3)));hi=Vector(tuple(max(v[k]for v in vs)for k in range(3)));W,H=hi.x-lo.x,hi.z-lo.z
  if W<.35 or H<.55:continue
  pp=[world_to_camera_view(s,s.camera,M@v)for v in vs];pb=[min(p.x for p in pp)*3840,(1-max(p.y for p in pp))*2885,max(p.x for p in pp)*3840,(1-min(p.y for p in pp))*2885]
  if pb[2]<20 or pb[0]>3820 or pb[3]<30 or pb[1]>2450 or pb[2]-pb[0]<55 or pb[3]-pb[1]<85:continue
  options=[]
  for u,v in [(.34,.62),(.67,.38),(.62,.77),(.30,.30),(.78,.58)]:
   p=Vector((lo.x+W*u,lo.y,lo.z+H*v));q=world_to_camera_view(s,s.camera,M@p)
   if .012<q.x<.988 and .06<q.y<.98 and visible(s,dg,M@p):options.append((u,v))
  if options:candidates.append((not primary,hn,ob.name,M,lo,hi,pb,options))
 candidates.sort(key=lambda r:(r[0],r[1],r[2]));selected=[];perhost={};sides={'left':0,'right':0};seen=set()
 for row in candidates:
  primary=not row[0];count=perhost.get(row[1],0);side='right'if sum(row[6][::2])*.5>1920 else'left';key=(row[1],row[2]);limit=3 if side=='right'and row[1].startswith('right_')else 2 if side=='right'else 1
  if key in seen or (not primary and(count>=limit or sides[side]>={'left':10,'right':8}[side])):continue
  selected.append(row);perhost[row[1]]=count+1;seen.add(key)
  if not primary:sides[side]+=1
 # Verify the actual side-edge point before construction, independently of interior visibility.
 edgeplans={};edge_sides=set()
 for row in selected:
  secondary,hn,on,M,lo,hi,pb,opts=row
  if not secondary:continue # Preserve the inspected primary recess/impact composition.
  side='right'if sum(pb[::2])*.5>1920 else'left'
  if side in edge_sides:continue
  W,H=hi.x-lo.x,hi.z-lo.z
  for which,x in [('left',lo.x+.012),('right',hi.x-.012)]:
   found=False
   for f in [.37,.66,.48]:
    p=Vector((x,lo.y,lo.z+H*f));q=world_to_camera_view(s,s.camera,M@p)
    if .015<q.x<.985 and .10<q.y<.94 and visible(s,dg,M@p):
     edgeplans[(hn,on)]={'edge':which,'center':tuple(p),'radius_x':min(.19,W*.25),'radius_z':min(.29,H*.24),'matrix':[list(r)for r in M],'side':side,'verified_projection_4k':[q.x*3840,(1-q.y)*2885]};edge_sides.add(side);found=True;break
   if found:break
 temp=bpy.data.collections.new('198 Temporary native cutters');s.collection.children.link(temp);privates={};geom=[];cutcache={};edge_cuts=[]
 for i,(secondary,hn,on,M,lo,hi,pb,opts)in enumerate(selected):
  source=bpy.data.objects[on];source.use_fake_user=True;ob=source
  if secondary:
   h=bpy.data.objects[hn]
   if hn not in privates:
    old=h.instance_collection;private=bpy.data.collections.new('198 Private facade '+hn)
    for ch in old.children:private.children.link(ch)
    for q in old.objects:private.objects.link(q)
    h.instance_collection=private;privates[hn]=private
   private=privates[hn];ob=source.copy();ob.name='198 '+hn+' '+on;private.objects.unlink(source);private.objects.link(ob)
   # Preserve memberships in native ink include collections for copied faces.
   for col in source.users_collection:
    if 'ink'in col.name.lower() and ob.name not in col.objects:col.objects.link(ob)
  ob.data=ob.data.copy();original=ob.data.copy();original.name='198 SOURCE '+ob.name;original.use_fake_user=True
  slots=[sl.material for sl in ob.material_slots];indices=[p.material_index for p in ob.data.polygons];ob.data.materials.clear()
  for m in slots:ob.data.materials.append(m)
  for sl in ob.material_slots:sl.link='DATA'
  for p,j in zip(ob.data.polygons,indices):p.material_index=j
  base=next(m for m in slots if m is not None)
  if base.name not in cutcache:cutcache[base.name]=cut_material(base)
  substrate=cutcache[base.name];ob.data.materials.append(substrate);slot=len(ob.data.materials)-1
  temp.objects.link(ob);W,H,T=hi.x-lo.x,hi.z-lo.z,hi.y-lo.y
  rng=random.Random(int(hashlib.sha256(('198v2'+hn+on).encode()).hexdigest()[:12],16));u,v=rng.choice(opts);cx,cz=lo.x+W*u,lo.z+H*v
  variant=rng.choices(['recess','impact','crack','edge loss'],[4,1,1,1])[0]
  if on in ['Recessed base wall.030','Recessed base wall.033']:variant='recess'
  if on=='Recessed base wall.030':u,v=min(opts,key=lambda q:q[1]);cx,cz=lo.x+W*u,lo.z+H*v
  if on=='Recessed base wall.033':u,v=max(opts,key=lambda q:q[1]);cx,cz=lo.x+W*u,lo.z+H*v
  if variant=='edge loss'and not visible(s,bpy.context.evaluated_depsgraph_get(),M@Vector((lo.x+W*.62,lo.y,hi.z-.03))):variant='recess'
  paths=[];before=(len(ob.data.vertices),len(ob.data.polygons))
  if variant=='crack':
   line=[];wander=0
   for k in range(7):
    wander+=rng.uniform(-.046,.046)*W;line.append((cx+wander,cz+H*(.26-k*rng.uniform(.075,.085))))
   widths=[rng.uniform(.006,.014)*(1-k/7)for k in range(7)];path=[(x-w,z)for(x,z),w in zip(line,widths)]+[(x+w,z)for(x,z),w in reversed(list(zip(line,widths)))];dep=min(T*.58,.035)
   rings=[[(x,lo.y-.02,z)for x,z in path],[(x,lo.y+dep,z)for x,z in path]];paths.append(rings)
  else:
   if variant=='edge loss':cz=hi.z-.03;cx=lo.x+W*.62
   rx=min(W*.23,.34)*rng.uniform(.65,1.16);rz=min(H*.19,.34)*rng.uniform(.7,1.20)
   if on=='Recessed base wall.030':rx=min(W*.12,.17);rz=min(H*.30,.39)
   if on=='Recessed base wall.033':rx=min(W*.25,.34);rz=min(H*.13,.18)
   if variant=='impact':rx*=.60;rz*=.68
   path=[]
   count=rng.randint(11,18)
   for k in range(count):
    a=math.tau*k/count;f=rng.uniform(.65,1.22);path.append((cx+rx*math.cos(a)*f,cz+rz*math.sin(a)*f))
   dep=T+.045 if variant in ['impact','edge loss']else min(T*rng.uniform(.25,.40),.029)
   rings=[[(x,lo.y-.024,z)for x,z in path],[(cx+(x-cx)*.72,lo.y+dep,cz+(z-cz)*.79)for x,z in path]];paths.append(rings)
   if variant=='recess'and on!='Recessed base wall.030'and(on=='Recessed base wall.033'or rng.random()<.42):
    path2=[(cx+rx*.82+(x-cx)*.37,cz-rz*.66+(z-cz)*.53)for x,z in path];paths.append([[(x,lo.y-.024,z)for x,z in path2],[(cx+rx*.82+(x-cx-rx*.82)*.74,lo.y+dep*.8,cz-rz*.66+(z-cz+rz*.66)*.8)for x,z in path2]])
  for rings in paths:
   c=cutter('198 '+variant+' cutter',rings,temp);c.matrix_world=ob.matrix_world.copy()
   for mat in ob.data.materials:c.data.materials.append(mat)
   for p in c.data.polygons:p.material_index=slot
   cut(ob,c)
  edgeplan=edgeplans.get((hn,on))
  if edgeplan:
   ex,ey,ez=edgeplan['center'];rx,rz=edgeplan['radius_x'],edgeplan['radius_z'];outline=[]
   # Irregular sheet loss crosses a real side boundary; open native return, not a painted dark patch.
   for k in range(13):
    angle=math.tau*k/13;scale=rng.uniform(.69,1.20);outline.append((ex+rx*math.cos(angle)*scale,ez+rz*math.sin(angle)*scale))
   rings=[[(x,lo.y-.03,z)for x,z in outline],[(ex+(x-ex)*.91,hi.y+.055,ez+(z-ez)*.88)for x,z in outline]]
   c=cutter('198 Verified side-edge missing chunk',rings,temp);c.matrix_world=ob.matrix_world.copy()
   for mat in ob.data.materials:c.data.materials.append(mat)
   for p in c.data.polygons:p.material_index=slot
   cut(ob,c);edge_cuts.append({**edgeplan,'host':hn,'source':on,'object':ob.name,'outline_local':outline,'front_y':lo.y,'rear_y':hi.y,'camera_visible_before_cut':True})
  temp.objects.unlink(ob);ob['198 native damage']=variant;ob['198 source mesh']=original.name
  geom.append({'host':hn,'source':on,'object':ob.name,'variant':variant,'before':before,'after':[len(ob.data.vertices),len(ob.data.polygons)],'projected_bounds_4k':pb,'visible_panel_interior_verified':True,'edge_loss_center_relocated_to_top':variant=='edge loss','private_instance':secondary,'new_cut_faces':sum(p.material_index==slot for p in ob.data.polygons),'depth_m':dep,'additional_edge_loss':edgeplan is not None})
 bpy.data.collections.remove(temp)
 # Remove only legacy contact-ink points that now float across a true missing edge.
 ink_cleanup=[]
 def inside(x,z,path):
  hit=False
  for a,b in zip(path,path[1:]+path[:1]):
   if (a[1]>z)!=(b[1]>z)and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 frames=[(Matrix(e['matrix']).inverted(),e)for e in edge_cuts]
 for name in ['096 contacts ink','096 damage ink']:
  ink=s.objects.get(name)
  if not ink:continue
  ink.data=ink.data.copy();count=0
  for layer in ink.data.layers:
   for frame in layer.frames:
    for stroke in frame.drawing.strokes:
     for pt in stroke.points:
      if pt.opacity==0:continue
      world=ink.matrix_world@pt.position
      for inv,e in frames:
       q=inv@world
       if e['front_y']-.025<q.y<e['rear_y']+.025 and inside(q.x,q.z,e['outline_local']):pt.opacity=0;count+=1;break
  ink_cleanup.append({'object':name,'hidden_points_at_missing_edges':count,'data_privately_copied':True})
 report={'study':198,'materials_objects':len(finished),'material_targets':finished,'private_finish_materials':len(cache),'geometry_panels':len(geom),'verified_edge_losses':edge_cuts,'local_legacy_ink_cleanup':ink_cleanup,'native_damage':geom,'private_instance_hosts':list(privates),'candidate_pool':len(candidates),'secondary_side_counts':sides,'revision':'v3 balanced sides plus camera-verified native side-edge missing chunks','preserved':'Camera, lights, architecture transforms, services, beams, bolts, landmark, ground and sky; existing material graphs unchanged. Original panel meshes archived. Shared panel source objects unchanged; selected instance collections privately copied.','visual_status':'Native GPU proof pending; no score or user approval claimed'}
 newgraphs=auditns['material_snapshot']();assert all(newgraphs[k]==v for k,v in oldgraphs.items()),'Original graph modified'
 assert all(tuple(v for row in bpy.data.objects[k].matrix_basis for v in row)==value for k,value in oldtransforms.items()),'Original transform changed'
 assert s.camera.name==camera and lights=={o.name:tuple(o.location)for o in s.objects if o.type=='LIGHT'}
 report['audit']={'original_material_graphs_verified':len(oldgraphs),'original_object_transforms_verified':len(oldtransforms),'camera_and_lights_unchanged':True,'original_graph_changes':0}
 return report

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/beam-rust-197/scene.blend'));a=apply();(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));print('198 READY',a['geometry_panels'],a['materials_objects'])
