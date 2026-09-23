"""Bounded motif grammar: routes -> quiet spans/events -> compatible components."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/components/services/grammar-v002';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
with bpy.data.libraries.load(str(R/'art/components/services/v002/service-kit.blend'),link=False) as (f,t):t.collections=[n for n in f.collections if n.startswith('PIP_')]
A={c['part_id']:c for c in t.collections if c and c.get('part_id')}
C=bpy.data.collections.new('Generated service bank');s.collection.children.link(C)
paint=bpy.data.materials.get('PIPE | aged blue enamel')
if not paint:paint=next(m for m in bpy.data.materials if 'enamel' in m.name.lower())
steel=next(m for m in bpy.data.materials if 'steel' in m.name.lower());duct=next(m for m in bpy.data.materials if 'muted blue-gray' in m.name)
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65;return m
wall=mat('Quiet backing',(.13,.16,.19));dark=mat('Vent interior',(.012,.02,.027))
def box(n,p,d,m,col=None):
 x,y,z=p;a,b,c=[v/2 for v in d];v=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);me.materials.append(m);ob=bpy.data.objects.new(n,me);(col or C).objects.link(ob);be=ob.modifiers.new('Edge radius','BEVEL');be.width=.008;be.segments=2;return ob
# Long quiet spans are dimensioned geometry, not stretched instances.
new=[]
for length in [2,3]:
 key='quiet_'+str(length);col=bpy.data.collections.new('PIP_'+key);col['part_id']=key;col.asset_mark();N=40;vs=[]
 for z,r in [(0,.2),(length,.2),(0,.172),(length,.172)]:vs += [(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for i in range(N)]
 fs=[]
 for i in range(N):
  j=(i+1)%N;fs += [(i,j,N+j,N+i),(2*N+j,2*N+i,3*N+i,3*N+j),(j,i,2*N+i,2*N+j),(N+i,N+j,3*N+j,3*N+i)]
 me=bpy.data.meshes.new(key);me.from_pydata(vs,[],fs);me.materials.append(paint)
 for face in me.polygons:face.use_smooth=True
 ob=bpy.data.objects.new(key,me);col.objects.link(ob)
 ports=[{'position':[0,0,z],'outward':[0,0,-1 if z==0 else 1],'bore_diameter':.344,'interface':'plain_spigot_v1'} for z in [0,length]]
 col['ports_json']=json.dumps(ports);A[key]=col;new.append(col)
# A framed vent provides local regularity inside one larger event.
col=bpy.data.collections.new('PIP_vent_terminal');col['part_id']='vent_terminal';col.asset_mark()
for x in [-.28,.28]:box('Vent inlet side',(x,0,.14),(.024,.38,.28),duct,col)
for y in [-.19,.19]:box('Vent inlet side',(0,y,.14),(.56,.024,.28),duct,col)
for x in [-.62,.62]:box('Vent case edge',(x,0,.86),(.10,.70,1.24),paint,col)
box('Vent roof',(0,0,1.48),(1.34,.70,.10),paint,col);box('Vent base',(0,0,.29),(1.34,.70,.10),paint,col)
box('Dark recessed cavity',(0,.28,.87),(1.18,.06,1.1),dark,col)
for z in [.43+i*.17 for i in range(6)]:
 ob=box('Regular louver blade',(0,0,0),(1.15,.30,.04),steel,col);ob.location=(0,-.20,z);ob.rotation_euler.x=math.radians(15)
col['ports_json']=json.dumps([json.loads(A['duct_M']['ports_json'])[0]]);A['vent_terminal']=col;new.append(col)
# A grammar chooses whole motifs, never independent random fittings.
G={'name':'service_bank','children':[
 {'name':'dominant_return','role':'primary','root':[-3.5,-.60,8.2],'down':True,'children':[
  {'name':'quiet_inlet','parts':['quiet_2']},
  {'name':'maintenance_event','parts':['flange_joint','housing','flange_joint']},
  {'name':'quiet_drop','parts':['quiet_3']},
  {'name':'bottom_return','parts':['bend_180']},
  {'name':'shorter_return_leg','parts':['quiet_3','quiet_2','blind']}]},
 {'name':'thin_companion','role':'secondary','root':[-1.72,.12,.4],'children':[{'name':'quiet_companion','parts':['spool_small']*7}]},
 {'name':'vent_feed','role':'secondary','root':[1.10,-.05,.5],'children':[
  {'name':'profile_change','parts':['spool','round_rect_M']},
  {'name':'quiet_duct','parts':['duct_M']*2},
  {'name':'wall_offset','parts':['duct_offset']},
  {'name':'quiet_duct','parts':['duct_M']},
  {'name':'terminal_event','parts':['joint_M','vent_terminal']}]}],
 'rules':{'max_maintenance_events_per_primary':1,'motif_depth_limit':3,'primary_standoff':.60,'secondary_standoff':.05,'intra_motif_regularity':'Preserve compatible dimensions, regular louvers, paired flanges','inter_motif_variation':'Long quiet spans, displaced heights, unequal endpoints, one empty lane','recursion':'Bank -> route group -> motif -> component; do not recursively add fittings forever'}}
G['children'].insert(2,{'name':'companion_wall_entry','role':'secondary','root':[-.65,-.12,.4],'rotation_z':90,'children':[
 {'name':'short_inlet','parts':['spool']},
 {'name':'lower_maintenance_event','parts':['flange_joint','housing','flange_joint']},
 {'name':'quiet_rise','parts':['quiet_2']},
 {'name':'wall_entry','parts':['bend_90','sleeve','blind']}]})
(O/'grammar.json').write_text(json.dumps(G,indent=2))
def ports(k):return json.loads(A[k]['ports_json'])
def frame(p):
 z=Vector(p['outward']);y=Vector(p.get('up',[0,1,0]));y=(y-z*y.dot(z)).normalized();x=y.cross(z);return Matrix.Translation(Vector(p['position']))@Matrix((x,y,z)).transposed().to_4x4()
records=[];joins=[]
def inst(k,M,group,motif):
 ob=bpy.data.objects.new(group+' | '+motif+' | '+k,None);ob.instance_type='COLLECTION';ob.instance_collection=A[k];ob.matrix_world=M;C.objects.link(ob);records.append({'group':group,'motif':motif,'part':k,'position':list(M.translation)});return (k,M,ob)
def join(parent,k,group,motif):
 pk,PM,_=parent;a=ports(pk)[1];b=ports(k)[0];assert a['interface']==b['interface']
 for d in ['width','height'] if a.get('profile')=='rect' else ['bore_diameter']:assert abs(a[d]-b[d])<1e-5
 M=PM@frame(a)@Matrix.Rotation(math.pi,4,'Y')@frame(b).inverted();err=(PM@Vector(a['position'])-M@Vector(b['position'])).length;assert err<1e-5;joins.append(err);return inst(k,M,group,motif)
def build(tree):
 for route in tree['children']:
  M=Matrix.Translation(Vector(route['root']))@Matrix.Rotation(math.radians(route.get('rotation_z',0)),4,'Z')@(Matrix.Rotation(math.pi,4,'X') if route.get('down') else Matrix.Identity(4));q=None
  for motif in route['children']:
   for key in motif['parts']:q=inst(key,M,route['name'],motif['name']) if q is None else join(q,key,route['name'],motif['name'])
  # Shared mount datums are a construction rhythm independent of equipment events.
  x,y,z=route['root']
  for level in [1.5,4.1,6.7]:
   if route['name'] in ['vent_feed','companion_wall_entry'] and level>5.5:continue
   box('Wall saddle',(x,(y+.53)/2,level),(.12,.53-y,.10),steel)
# Workshop background and one fixed camera/light setup for both layouts.
S=bpy.data.collections.new('Studio');s.collection.children.link(S)
box('Backing plane',(0,.66,4.5),(9,.18,9),wall,S);box('Floor',(0,-.7,-.09),(11,5,.18),wall,S)
s.world=bpy.data.worlds.new('Workshop world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.21,.26,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for n,pos,power,size in [('Key',(-5,-8,12),1800,8),('Fill',(6,-4,7),1000,7)]:
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.size=size;ob=bpy.data.objects.new(n,d);S.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,4))-ob.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Comparison camera');cam=bpy.data.objects.new('Comparison camera',d);S.objects.link(cam);cam.location=(8,-26,11);cam.rotation_euler=(Vector((-.2,0,4.3))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=11.1;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.compositing_node_group=None
build(G);bpy.context.view_layer.update();s.render.filepath=str(O/'hierarchy.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'hierarchy.blend'));bpy.ops.render.render(write_still=True)
(O/'placements.json').write_text(json.dumps(records,indent=2));(O/'audit.json').write_text(json.dumps({'joins':len(joins),'max_port_error':max(joins),'unit_scale':all(all(abs(v-1)<1e-5 for v in ob.scale) for ob in C.objects),'image_textures':0,'scope':'Motif grammar prototype; qualitative comparison, not a matched part-count experiment'},indent=2));bpy.data.libraries.write(str(O/'grammar-extension-masters.blend'),set(new),fake_user=True)
C.hide_render=True;C=bpy.data.collections.new('Flat repeated control');s.collection.children.link(C)
control={'children':[{'name':'pipe_'+str(i),'root':[x,-.35,.4],'children':[{'name':'repeat','parts':['spool','housing','flange_joint']*3+['blind']}]} for i,x in enumerate([-3.5,-2.5,-1.5])]}
control['children'].append({'name':'duct','root':[1.1,-.35,.4],'children':[{'name':'repeat','parts':['duct_M','joint_M']*5+['vent_terminal']}]})
build(control);s.render.filepath=str(O/'flat-control.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'flat-control.blend'));bpy.ops.render.render(write_still=True)
print('SERVICE_GRAMMAR_DONE')
