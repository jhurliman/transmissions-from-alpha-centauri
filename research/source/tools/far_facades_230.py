"""Opening-based distant facade identities; original shared masters are immutable."""
import bpy,bmesh,math,json,hashlib
from mathutils import Matrix,Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]

def box(C,name,center,size,mat,bevel=.018):
 vs=[tuple(Vector(center)+Vector((a*size[0]/2,b*size[1]/2,c*size[2]/2)))for a,b,c in((-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1))];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat);ob=bpy.data.objects.new('230 '+name,me);C.objects.link(ob)
 if bevel:q=ob.modifiers.new('Manufactured edge catch','BEVEL');q.width=bevel;q.segments=1
 return ob

def apply(scene):
 from alley_repeat_212 import verts
 C=bpy.data.collections['215 Short alley composition'];roots=sorted((o for o in C.objects if o.instance_collection),key=lambda o:(o.location.x>0,o.location.y));assert len(roots)>=12
 # Freeze all bounds and source material reads before any dependency graph changes.
 bounds={};paint={}
 def material(o):
  leaves=list(o.instance_collection.all_objects)if o.instance_collection else[o]
  choices=[sl.material for q in leaves for sl in q.material_slots if sl.material]
  return next((m for m in choices if any(t in m.name.lower()for t in('coating','facade','seam loss'))),choices[0])
 for root in roots:
  for ob in root.instance_collection.objects:
   if ob not in bounds:
    ps=list(verts(ob));bounds[ob]=([min(v[k]for v in ps)for k in range(3)],[max(v[k]for v in ps)for k in range(3)])if ps else None
    if ob.instance_collection and 'layout_'in ob.name:paint[ob]=material(ob)
 # Resolve only missing named receiver UVs in private copies.
 from entrance_weathering_227 import adapt_receiver_coordinates
 adapted={}
 for ob,mat in list(paint.items()):
  if any(n.type=='UVMAP' for n in mat.node_tree.nodes):
   if mat not in adapted:
    q=mat.copy();q.name='230 Facade receiver '+mat.name;adapt_receiver_coordinates(q);adapted[mat]=q
   paint[ob]=adapted[mat]
 frame=next(m for m in bpy.data.materials if m.name=='222 Worn worn zinc surround');dark=next(m for m in bpy.data.materials if m.name=='222 Worn charcoal iron gate')
 glass=dark.copy();glass.name='230 Subdued smoke glass';em=next(n for n in glass.node_tree.nodes if n.type=='EMISSION');em.inputs['Color'].default_value=(.057,.069,.088,1)
 for l in list(em.inputs['Color'].links):glass.node_tree.links.remove(l)
 fragment=glass.copy();fragment.name='230 Broken pane cool edge';next(n for n in fragment.node_tree.nodes if n.type=='EMISSION').inputs['Color'].default_value=(.18,.225,.25,1)
 recess=dark.copy();recess.name='230 Deep unlit interior';em=next(n for n in recess.node_tree.nodes if n.type=='EMISSION')
 for l in list(em.inputs['Color'].links):recess.node_tree.links.remove(l)
 em.inputs['Color'].default_value=(.022,.019,.026,1)
 masters={};newmesh=[];rows=[];cutrows=[];identity=[];aliases=[]
 def make(kind,mat,variant=0,broken=False):
  key=(kind,mat.name,variant,broken)
  if key in masters:return masters[key]
  col=bpy.data.collections.new('230 Prefab '+kind+(' broken'if broken else'')+' '+str(len(masters)));col.use_fake_user=True;masters[key]=col;parts=[]
  def B(n,c,d,m=mat,bev=.018):q=box(col,n,c,d,m,bev);parts.append(q);newmesh.append(q);return q
  W,H=2.8,2.16
  if kind=='entry':ow,oh,base=(1.08 if variant%2 else 1.36),1.90,0
  else:ow,oh,base=(1.62 if kind=='picture'else 1.72),1.30,.45
  top=base+oh
  B('receiver left',(-.045,-(W+ow)/4,H/2),(.18,(W-ow)/2,H));B('receiver right',(-.045,(W+ow)/4,H/2),(.18,(W-ow)/2,H))
  if base:B('receiver below',(-.045,0,base/2),(.18,ow,base))
  B('receiver lintel',(-.045,0,(top+H)/2),(.18,ow,H-top))
  for y in(-ow/2,ow/2):B('deep frame jamb',(-.20,y,base+oh/2),(.56,.085,oh+.07),frame)
  B('deep sill',(-.17,0,base+.005),(.65,ow+.16,.09),frame);B('deep head',(-.17,0,top),(.56,ow+.16,.085),frame)
  B('interior dark recess',(-.64,0,base+oh/2),(.055,ow-.08,oh-.08),recess,0)
  if kind=='entry':
   B('closed recessed entry',(-.31,0,oh/2),(.095,ow-.14,oh-.10),frame)
   if variant%3==0:
    for j in range(5):B('door ventilation slot',(-.253,0,1.31+j*.055),(.015,ow*.47,.022),dark,.003)
   elif variant%3==1:B('door small glazed upper light',(-.251,0,1.48),(.025,ow*.54,.38),glass,.005)
   else:
    for j in range(3):B('door pressed lower panel',(-.248,0,.43+j*.39),(.025,ow*.72,.31),mat,.01)
   B('entry handle',(-.23,ow*.28,.94),(.075,.07,.23),dark,.006)
   B('small utility address plaque',(.065,-ow/2-.15,1.64),(.045,.18,.12),frame,.005)
  elif broken:
   # Surviving irregular rim shards leave most of the real opening empty.
   shards=[((-ow/2+.06,base+.04),(-ow/2+.47,base+.04),(-ow/2+.24,base+.33)),((ow/2-.05,top-.04),(ow/2-.49,top-.04),(ow/2-.21,top-.44)),((-ow/2+.05,top-.05),(-ow/2+.47,top-.05),(-ow/2+.15,top-.29)),((ow/2-.05,base+.04),(ow/2-.35,base+.04),(ow/2-.10,base+.43))]
   for j,tri in enumerate(shards):
    me=bpy.data.meshes.new('230 Jagged surviving pane');me.from_pydata([(-.115,y,z)for y,z in tri],[],[(0,1,2)]);me.materials.append(fragment);q=bpy.data.objects.new('230 broken window surviving shard '+str(j),me);col.objects.link(q);sol=q.modifiers.new('Actual glass edge','SOLIDIFY');sol.thickness=.012;newmesh.append(q)
   B('broken frame offset remnant',(-.085,ow*.08,top-.24),(.045,.035,.42),frame,.005)
  else:
   B('recessed glass pane',(-.15,0,base+oh/2),(.025,ow-.14,oh-.13),glass,.003)
   if kind=='slider':
    B('sliding sash meeting stile',(-.09,.065,base+oh/2),(.085,.060,oh-.07),frame,.005)
    B('sliding lower track',(-.09,0,base+.09),(.10,ow-.07,.035),frame,.005)
   else:B('box picture frame lower lip',(.05,0,base-.015),(.16,ow+.22,.045),frame,.005)
  col['230 component kind']=kind;col['230 actual opening']=True;col['230 broken pane']=broken;return col
 def add(root,col,old,kind,broken=False,variant=0):
  lo,hi=bounds[old];dx,dy=hi[0]-lo[0],hi[1]-lo[1];center=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]));street=dx<.5
  if street:M=Matrix.Translation((.015,center.y,lo[2]))
  else:
   sign=1 if center.y>0 else-1;M=Matrix.Translation((center.x,sign*max(abs(lo[1]),abs(hi[1])),lo[2]))@Matrix.Rotation(sign*math.pi/2,4,'Z')
  master=make(kind,paint[old],variant,broken);q=bpy.data.objects.new('230 facade '+kind+' '+root.name+(' BROKEN'if broken else''),None);q.instance_type='COLLECTION';q.instance_collection=master;q.matrix_world=M;col.objects.link(q);col.objects.unlink(old)
  row={'root':root.name,'removed_private_container_reference':old.name,'new':q.name,'kind':kind,'broken':broken,'street_face':street,'local_matrix':[list(r)for r in M]};rows.append(row)
  # Side-return structural backing is less than20cm behind the painted skin.
  # Cut that private shell as well; window well and far backpanel remain real.
  if not street:
   ow,oh,base=(1.62 if kind=='picture'else 1.72),1.30,.45
   cutter=box(scene.collection,'temporary private return opening',(0,0,0),(1,1,1),mat=frame,bevel=0)
   pts=[M@Vector((x,y,z))for x,y,z in((-1,-ow/2,base),(-1,-ow/2,base+oh),(-1,ow/2,base),(-1,ow/2,base+oh),(.3,-ow/2,base),(.3,-ow/2,base+oh),(.3,ow/2,base),(.3,ow/2,base+oh))]
   for v,p in zip(cutter.data.vertices,pts):v.co=p
   cutter.data.update();cutter.hide_render=True
   for shell in list(col.objects):
    if shell.type!='MESH' or not any(t in shell.name for t in('leading interior return','rear wall return','Upper structural course')):continue
    a,b=bounds.get(shell,(None,None))
    if a is None:
     ps=[shell.matrix_world@Vector(p)for p in shell.bound_box];a=[min(p[k]for p in ps)for k in range(3)];b=[max(p[k]for p in ps)for k in range(3)]
    clo=[min(p[k]for p in pts)for k in range(3)];chi=[max(p[k]for p in pts)for k in range(3)]
    if not all(a[k]<chi[k] and b[k]>clo[k]for k in range(3)):continue
    if not shell.get('230 private backing'):
     original=shell;copy=shell.copy();copy.data=shell.data.copy();copy.name='230 private backing '+shell.name;copy['230 private backing']=True;copy['230 source object']=shell.name;col.objects.unlink(shell);col.objects.link(copy);shell=copy;newmesh.append(shell);aliases.append({original.name:shell.name})
    # Apply in common prefab-local space; original shell normals may be inverted.
    bm=bmesh.new();bm.from_mesh(shell.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(shell.data);bm.free()
    scene.collection.objects.link(shell);mod=shell.modifiers.new('230 true return aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(shell.evaluated_get(dg),depsgraph=dg);shell.modifiers.clear();shell.data=mesh;scene.collection.objects.unlink(shell);cutrows.append({'root':root.name,'shell':shell.name,'vertices':len(mesh.vertices),'window':q.name})
   bpy.data.objects.remove(cutter,do_unlink=True)
  return q
 for index,root in enumerate(roots):
  oldcol=root.instance_collection;col=bpy.data.collections.new('230 Private facade '+root.name);col.use_fake_user=True;col.instance_offset=oldcol.instance_offset
  for ob in oldcol.objects:col.objects.link(ob)
  root.instance_collection=col;root['230 facade private container']=True
  panels=[o for o in oldcol.objects if o in paint and bounds[o]and abs(bounds[o][1][2]-bounds[o][0][2]-2.16)<.04]
  street=[o for o in panels if bounds[o][1][0]-bounds[o][0][0]<.5];ground=[o for o in street if bounds[o][0][2]<.10]
  assert ground,root.name
  has_pipe=any('closed service'in o.name for o in oldcol.objects)
  entry=sorted(ground,key=lambda o:bounds[o][0][1])[-1 if has_pipe else index%len(ground)];add(root,col,entry,'entry',variant=index%3)
  upper=[o for o in street if bounds[o][0][2]>3]
  if upper:
   # The two tall chosen facades use prominent high windows for visible damage.
   chosen=sorted(upper,key=lambda o:(bounds[o][0][2],bounds[o][0][1]))[-1 if 'right step'in root.name else index%len(upper)]
   add(root,col,chosen,'picture'if index%2==0 else'slider',broken=False)
  side=-1 if root.location.x<0 else 1
  ends=[o for o in panels if bounds[o][1][0]-bounds[o][0][0]>2.5 and bounds[o][1][1]-bounds[o][0][1]<.5 and ((bounds[o][0][1]+bounds[o][1][1])/2)*side>0 and bounds[o][0][2]>2]
  if ends:
   ordered=sorted(ends,key=lambda o:(bounds[o][0][2],-bounds[o][1][0]));selected=[ordered[index%len(ordered)]]
   if 'right step'in root.name:selected=[ordered[-2]]
   if 'left step'in root.name:
    selected=[ordered[0],ordered[len(ordered)//2],ordered[-2]];selected=list(dict.fromkeys(selected))
   for j,e in enumerate(selected):add(root,col,e,'picture'if j%2==0 else'slider',broken=(('left step'in root.name and j==len(selected)-1)or'right step'in root.name),variant=index)
  identity.append({'root':root.name,'original_master':oldcol.name,'private_master':col.name,'entry_variant':index%3,'new_openings':[r for r in rows if r['root']==root.name]})
 ink=bpy.data.collections['215 Distant accepted component ink']
 for o in newmesh:
  if o.name not in ink.objects:ink.objects.link(o)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for o in newmesh:
     if o.name not in ls.collection.objects:ls.collection.objects.link(o)
 maps=json.loads(scene.get('212 source name groups','[]'));maps.extend(aliases);scene['212 source name groups']=json.dumps(maps)
 assert sum(r['broken']for r in rows)==2
 return {'buildings':len(roots),'identities':identity,'openings':rows,'backing_cuts':cutrows,'new_native_mesh_objects':len(newmesh),'reusable_masters':[c.name for c in masters.values()],'broken_windows':2,'original_shared_master_meshes_unchanged':True,'no_foreground_changes':True}
