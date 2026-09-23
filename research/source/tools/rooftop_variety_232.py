"""232 varied native roof services; shorter cabinets, preserved roof slabs/ladders."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from far_building_layout_226 import boxpoints

def apply(scene):
 if scene.get('rooftops232_applied'):raise RuntimeError('232 rooftops already applied')
 roots=sorted([o for o in bpy.data.collections['215 Short alley composition'].objects if o.instance_collection],key=lambda o:(o.location.y,o.name));added=[];edited=[];rows=[]
 def mesh(C,n,vs,fs,mat):
  me=bpy.data.meshes.new('232 '+n);me.from_pydata(vs,[],fs);me.update();me.materials.append(mat);ob=bpy.data.objects.new('232 '+n,me);C.objects.link(ob);ob['232 roof service']=True;added.append(ob);return ob
 def box(C,n,p,size,mat):
  x,y,z=p;a,b,c=[v/2 for v in size];vs=[(x+i*a,y+j*b,z+k*c)for i,j,k in[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];o=mesh(C,n,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat);b=o.modifiers.new('232 subtle rolled edge','BEVEL');b.width=.016;b.segments=1;return o
 def tube(C,n,ps,r,mat,sides=16):
  ps=[Vector(p)for p in ps];vs=[]
  for j,p in enumerate(ps):
   t=(ps[min(j+1,len(ps)-1)]-ps[max(0,j-1)]).normalized();ref=Vector((0,1,0))if abs(t.y)<.95 else Vector((1,0,0));u=t.cross(ref).normalized();v=t.cross(u).normalized();vs.extend(p+r*(math.cos(i*math.tau/sides)*u+math.sin(i*math.tau/sides)*v)for i in range(sides))
  fs=[]
  for j in range(len(ps)-1):
   for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;fs.append((a,b,b+sides,a+sides))
  fs.extend([tuple(reversed(range(sides))),tuple((len(ps)-1)*sides+i for i in range(sides))]);return mesh(C,n,vs,fs,mat)
 for idx,root in enumerate(roots):
  old=root.instance_collection;C=bpy.data.collections.new('232 Roof variants '+root.name);C.use_fake_user=True;C.instance_offset=old.instance_offset
  for o in old.objects:C.objects.link(o)
  root.instance_collection=C
  cabinet=next(o for o in C.objects if 'Condenser cabinet'in o.name);lo,hi=boxpoints(cabinet);base=lo[2];H=hi[2]-lo[2];mat=cabinet.material_slots[0].material
  dark=bpy.data.materials.get('230 Recessed service metal')or mat
  changed=[]
  for ob in list(C.objects):
   if ob.type!='MESH':continue
   isbody=any(t in ob.name for t in ['Condenser cabinet','Condenser intake','Condenser dark fan well','Fan guard'])
   isservice='Condenser roof service'in ob.name
   if not(isbody or isservice):continue
   q=ob.copy();q.data=ob.data.copy();q.name='232 shortened '+ob.name;C.objects.unlink(ob);C.objects.link(q);q['232 shortened condenser']=True
   for v in q.data.vertices:
    if isbody or v.co.z>base:v.co.z=base+(v.co.z-base)*.75
   added.append(q);edited.append({'source':ob.name,'private':q.name});changed.append(q.name)
  roofbounds=[(o,*boxpoints(o))for o in C.objects if 'real roof slab'in o.name];assert roofbounds
  # Choose an unoccupied roof bay where possible; remain well inside its actual slab.
  cabY=(lo[1]+hi[1])/2;roof=max(roofbounds,key=lambda r:abs((r[1][1]+r[2][1])/2-cabY));_,a,b=roof;y=(a[1]+b[1])/2;z=b[2];seed=int(hashlib.sha256(root.name.encode()).hexdigest()[:8],16);kind=idx%5;shift=((seed%7)-3)*.055;x=-4.20+shift
  pattern=[]
  def plenum(px,py,w=.82,d=.64,h=.52):
   box(C,'Seated vent curb',(px,py,z+.075),(w+.12,d+.12,.15),dark);box(C,'Compact intake plenum',(px,py,z+.15+h/2),(w,d,h),mat)
   for j in range(4):box(C,'Plenum intake slat',(px+w/2+.015,py,z+.24+j*h*.16),(.038,d*.77,.035),dark)
   pattern.append({'terminal':'screened box intake','roof_seat_z':z,'position':[px,py],'size':[w,d,h]})
  if kind==0:
   plenum(x,y-.20,.92,.70,.44+.05*(idx%3));plenum(x+1.24,y+.40,.62,.55,.72)
  elif kind in(1,4):
   # Low sealed rectangular L-run, two saddles, integral roof penetration at one end.
   endy=y+(.63 if kind==1 else -.63);startx=x-.65;endx=x+1.10
   box(C,'Rectangular duct long run',((startx+endx)/2,y,z+.34),(endx-startx,.43,.38),mat)
   box(C,'Rectangular duct return',(endx,(y+endy)/2,z+.34),(.43,abs(endy-y)+.43,.38),mat)
   box(C,'Rectangular sealed roof leg',(startx,y,z+.14),(.43,.43,.36),mat)
   for xx in(startx+.45,endx-.25):box(C,'Duct roof saddle',(xx,y,z+.077),(.16,.62,.155),dark)
   plenum(endx,endy,.73,.70,.59 if kind==1 else .81);pattern.append({'route':'Low rectangular L duct','endpoints':['sealed roof penetration','screened receiver plenum'],'height_m':.38,'roof_saddles':2})
   if kind==4:
    tube(C,'Vent offset riser',[(x-.60,y+.70,z-.03),(x-.60,y+.70,z+.82)],.12,mat);tube(C,'Vent mushroom rain cap',[(x-.60,y+.70,z+.82),(x-.60,y+.70,z+.91)],.20,mat);pattern.append({'terminal':'capped vent riser'})
  elif kind==2:
   # Broad bent round bridge with both ends physically penetrating this roof.
   xa=x-.58;xb=x+1.00;yy=y+.11;h=.76+.07*(idx%3);r=.23
   ps=[(xa,yy,z-.04),(xa,yy,z+h-.22)]
   for j in range(1,9):t=math.pi*j/16;ps.append((xa+.22-.22*math.cos(t),yy,z+h-.22+.22*math.sin(t)))
   ps.append((xb-.22,yy,z+h))
   for j in range(1,9):t=math.pi*j/16;ps.append((xb-.22+.22*math.sin(t),yy,z+h-.22+.22*math.cos(t)))
   ps.append((xb,yy,z-.04));tube(C,'Bent round roof service bridge',ps,r,mat)
   for xx in(xa,xb):tube(C,'Round roof flashing',[(xx,yy,z-.018),(xx,yy,z+.08)],.32,dark)
   pattern.append({'route':'Bent full-diameter round bridge','diameter_m':.46,'endpoints':['sealed roof collar A','sealed roof collar B']})
  else:
   # Unequal paired exhaust stacks, closed rain caps; no open accidental spool.
   for j,dy in enumerate((-.44,.45)):
    h=.92+.32*j+.05*(idx%2);px=x+.29*j;py=y+dy
    tube(C,'Twin exhaust stack',[(px,py,z-.025),(px,py,z+h)],.17+.025*j,mat)
    tube(C,'Stack base flashing',[(px,py,z-.025),(px,py,z+.09)],.27+.025*j,dark)
    tube(C,'Stack rain cap',[(px,py,z+h+.04),(px,py,z+h+.14)],.26+.025*j,mat)
    for dx in(-.11,.11):box(C,'Rain cap supporting tab',(px+dx,py,z+h+.025),(.04,.05,.12),mat)
   pattern.append({'route':'Unequal twin exhaust stacks','endpoints':['sealed roof penetrations','supported rain caps with exhaust gap']})
  rows.append({'root':root.name,'cabinet_height_before_m':H,'cabinet_height_after_m':H*.75,'cabinet_height_ratio':.75,'cabinet_base_fixed_z':base,'fans_louvers_follow_height':True,'ladder_and_roof_slabs_unchanged':True,'new_roof_bay':roof[0].name,'pattern_index':kind,'pattern':pattern,'changed_private_parts':changed})
 ink=bpy.data.collections['215 Distant accepted component ink']
 for o in added:
  if o.name not in ink.objects:ink.objects.link(o)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for o in added:
     if o.name not in ls.collection.objects:ls.collection.objects.link(o)
 scene['rooftops232_applied']=True;bpy.context.view_layer.update()
 return {'study':232,'source':bpy.data.filepath,'roots':len(roots),'rows':rows,'new_or_private_meshes':len(added),'private_condenser_edits':edited,'old_geometry_unchanged':True,'ink':'Existing215 far native owner; excluded near linesets','final_contact_ink':'Parent reclip110 after all232 geometry; retain225 lost-contact cleanup','review':'CPU native assembly; actual perspective review pending'}
if __name__=='__main__':
 O=R/'art/studies/rooftop-variety-232';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/midground-arches-231/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('232 ROOFS READY',flush=True)
