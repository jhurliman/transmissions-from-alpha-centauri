"""Native far-only service endpoints and roof equipment. Apply after far_facades_230."""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from far_building_layout_226 import boxpoints

def apply(scene):
 if scene.get('services230_applied'):raise RuntimeError('230 services already applied')
 added=[];removed=[];routes=[];roofs_a=[];exports=[]
 roots=sorted([o for o in bpy.data.collections['215 Short alley composition'].objects if o.instance_collection],key=lambda o:(o.location.y,o.name))
 steel=next(s.material for o in bpy.data.objects['XL | companion_600_L3'].instance_collection.all_objects for s in o.material_slots if s.material)
 dark=steel.copy();dark.name='230 Recessed service metal';dark.diffuse_color=(.06,.065,.085,1)
 # Keep accepted lighting/weathering graph; dark cavity insert uses a modest native multiplier.
 if dark.use_nodes:
  for n in dark.node_tree.nodes:
   if n.type=='EMISSION':
    sock=n.inputs['Color'];old=sock.links[0].from_socket if sock.is_linked else None
    if old:
     m=dark.node_tree.nodes.new('ShaderNodeMixRGB');m.blend_type='MULTIPLY';m.inputs[0].default_value=1;m.inputs[2].default_value=(.36,.39,.44,1);dark.node_tree.links.new(old,m.inputs[1]);dark.node_tree.links.new(m.outputs[0],sock)
 def mesh(C,name,vs,fs,mat=steel,bevel=0):
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(mat);ob=bpy.data.objects.new('230 '+name,me);C.objects.link(ob);ob['230 service roof']=True;added.append(ob)
  if bevel:
   m=ob.modifiers.new('Small manufactured arris','BEVEL');m.width=bevel;m.segments=1
  return ob
 def box(C,n,p,size,mat=steel):
  x,y,z=p;a,b,c=[s/2 for s in size];vs=[(x+i*a,y+j*b,z+k*c)for i,j,k in[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
  return mesh(C,n,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat,.018)
 def tube(C,n,ps,r,mat=steel,sides=20):
  ps=[Vector(p)for p in ps];vs=[]
  for j,p in enumerate(ps):
   t=(ps[min(j+1,len(ps)-1)]-ps[max(0,j-1)]).normalized();ref=Vector((0,1,0))if abs(t.y)<.95 else Vector((1,0,0));u=t.cross(ref).normalized();v=t.cross(u).normalized()
   vs.extend(p+r*(math.cos(i*math.tau/sides)*u+math.sin(i*math.tau/sides)*v)for i in range(sides))
  fs=[]
  for j in range(len(ps)-1):
   for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;fs.append((a,b,b+sides,a+sides))
  fs.extend([tuple(reversed(range(sides))),tuple((len(ps)-1)*sides+i for i in range(sides))]);return mesh(C,n,vs,fs,mat)
 def unlink(C,o,root,reason):C.objects.unlink(o);removed.append({'root':root.name,'component':o.name,'reason':reason})
 for idx,root in enumerate(roots):
  old=root.instance_collection;C=bpy.data.collections.new('230 Services roof '+root.name);C.use_fake_user=True;C.instance_offset=old.instance_offset
  for o in old.objects:C.objects.link(o)
  root.instance_collection=C;exports.append(C)
  roofobs=[o for o in C.objects if 'real roof slab'in o.name];roofbounds=[(o,*boxpoints(o))for o in roofobs];assert roofbounds
  for o in list(C.objects):
   if 'floor_band'in o.name:
    a,b=boxpoints(o)
    if any(abs((a[1]+b[1]-lo[1]-hi[1])/2)<.05 and a[2]>=hi[2]-.06 for _,lo,hi in roofbounds):unlink(C,o,root,'Remove overhanging top-front band; actual roof slab retained')
  service=[o for o in C.objects if any(t in o.name for t in ['closed service','service mounting shoe','service shoe continuation'])]
  if root.name=='215 left service 103':
   for o in service:unlink(C,o,root,'Remove requested middle-left complete large pipe and supports')
  else:
   endpoints=[o for o in service if 'companion_wall_'in o.name]
   for ei,o in enumerate(endpoints):
    a,b=boxpoints(o);y=(a[1]+b[1])/2;upper='False'in o.name;join=a[2]if upper else b[2];direction=1 if upper else -1;z=join+direction*.6
    unlink(C,o,root,'Replace small tapered wall terminal at unchanged main barrel join')
    receiver=(idx+ei)%2==0;endx=.52 if receiver else -.08
    ps=[(1.77,y,join)]
    for j in range(1,13):t=j*math.pi/24;ps.append((1.17+.6*math.cos(t),y,join+direction*.6*math.sin(t)))
    ps.append((endx,y,z));tube(C,'Full600 wall elbow',ps,.30)
    if receiver:
     box(C,'Broad wall receiver',(.20,y,z),(.78,1.14,1.10));box(C,'Receiver face gasket',(.601,y,z),(.032,.79,.79),dark);tube(C,'Receiver full bore collar',[(.54,y,z),(.73,y,z)],.36)
     for dy,dz in [(-.43,-.40),(-.43,.40),(.43,-.40),(.43,.40)]:tube(C,'Receiver corner bolt',[(.596,y+dy,z+dz),(.66,y+dy,z+dz)],.055,sides=6)
    else:
     tube(C,'Full600 wall flange',[(.10,y,z),(.23,y,z)],.44)
     for j in range(8):t=math.tau*j/8;tube(C,'Flange bolt',[(.23,y+.375*math.cos(t),z+.375*math.sin(t)),(.28,y+.375*math.cos(t),z+.375*math.sin(t))],.035,sides=6)
    routes.append({'root':root.name,'terminal':'upper'if upper else'lower','type':'receiver box'if receiver else'full-size flange','barrel_diameter_m':.6,'join_local':[1.77,y,join],'wall_destination':[-.19 if receiver else -.08,y,z],'native_full_diameter_elbow':True})
  # Roof equipment is seated on existing slabs, with different bay choices and sizes.
  chosen=roofbounds[(idx*3+1)%len(roofbounds)];_,lo,hi=chosen;y=(lo[1]+hi[1])/2;z=hi[2];x=-1.35 if idx%3 else -2.15
  width=1.50+.20*(idx%3);depth=1.22;H=.86+.20*(idx%4)
  for dy in(-.42,.42):box(C,'Condenser seated skid',(x,y+dy,z+.075),(width+.14,.12,.15),dark)
  box(C,'Condenser cabinet',(x,y,z+.15+H/2),(width,depth,H))
  # Front louver recess and actual folded louver strips; top fan grille.
  box(C,'Condenser intake recess',(x+width/2+.006,y,z+.15+H*.53),(.018,depth*.80,H*.65),dark)
  for j in range(5):box(C,'Condenser intake louver',(x+width/2+.043,y,z+.15+H*.27+j*H*.13),(.075,depth*.83,.045))
  fanZ=z+.15+H+.018;tube(C,'Condenser dark fan well',[(x,y,fanZ-.015),(x,y,fanZ+.012)],.42,dark,32)
  for radius in(.26,.42):
   ps=[(x+radius*math.cos(j*math.tau/40),y+radius*math.sin(j*math.tau/40),fanZ+.035)for j in range(41)];tube(C,'Fan guard ring',ps,.017,sides=6)
  for dy in(-.14,.14):tube(C,'Fan guard brace',[(x-.39,y+dy,fanZ+.04),(x+.39,y+dy,fanZ+.04)],.018,sides=6)
  # Integral short refrigerant/service pair penetrates roof directly below the unit.
  for dy in(-.09,.09):tube(C,'Condenser roof service',[(x-width/2,y+dy,z+.36),(x-width/2-.23,y+dy,z+.36),(x-width/2-.23,y+dy,z-.025)],.04,sides=10)
  ladder=None
  if idx%3!=1:
   _,la,lh=min(roofbounds,key=lambda r:r[1][1]);endY=la[1]-.31;LZ=lh[2];lx=-3.6
   for dx in(-.32,.32):
    tube(C,'Roof access ladder rail',[(lx+dx,endY,.20),(lx+dx,endY,LZ+.72),(lx+dx,endY+.39,LZ+.72),(lx+dx,endY+.39,LZ+.02)],.045,sides=10)
   for j in range(int((LZ-.35)/.32)+1):tube(C,'Roof access ladder rung',[(lx-.32,endY,.35+j*.32),(lx+.32,endY,.35+j*.32)],.028,sides=8)
   for zz in(.7,LZ*.48,LZ-.35):
    for dx in(-.32,.32):tube(C,'Ladder wall standoff',[(lx+dx,endY,zz),(lx+dx,la[1]+.10,zz)],.032,sides=8)
   ladder={'wall':'leading native end facade','roof_top_m':LZ,'ground_start_m':.20,'standoffs':6,'roof_return_seated':True}
  roofs_a.append({'root':root.name,'roof_slab':chosen[0].name,'roof_top_m':z,'cabinet_size_m':[width,depth,H],'skid_bottom_equals_roof':True,'service_both_ends':'cabinet to sealed roof penetration','ladder':ladder})
 ink=bpy.data.collections['215 Distant accepted component ink']
 for ob in added:ink.objects.link(ob)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for ob in added:
     if ob.name not in ls.collection.objects:ls.collection.objects.link(ob)
 scene['services230_applied']=True;bpy.context.view_layer.update()
 return {'source':bpy.data.filepath,'roots':len(roots),'removed_components':removed,'new_endpoints':routes,'roof_equipment':roofs_a,'added_native_meshes':len(added),'foreground_originals_modified':False,'old_geometry_modified':False,'private_prefab_collections':[c.name for c in exports],'contact_ink':'Parent restores/reclips110 once after final layout and all230 modules; preserve225 cleanup','review':'CPU assembly only; combined native proof pending'}

if __name__=='__main__':
 O=R/'art/studies/far-services-roofs-230';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/entry-surround-229/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));cols={bpy.data.collections[n]for n in a['private_prefab_collections']};bpy.data.libraries.write(str(O/'native-prefabs.blend'),cols,fake_user=True);print('230 SERVICES READY',flush=True)
