"""One native exposed-service cladding prefab and localized rust study.
Reference: UCL-01 exposed left services/Y platform; UP-03 material hierarchy;
DP-08 layered infrastructure. Explicit user-authorized alley edits only.
"""
import bpy,math,json,random,time
from mathutils import Vector,Matrix
from pathlib import Path
R=Path(__file__).resolve().parents[1]

def weather_material(base,kind,cache,exposure=0.):
 key=(base.name,kind,exposure)
 if key in cache:return cache[key]
 m=base.copy();m.name='133 '+kind+(' seam'if exposure else'')+' | '+base.name;nt=m.node_tree;n=nt.nodes;l=nt.links
 em=next((q for q in n if q.type=='EMISSION'and q.outputs[0].is_linked),None)
 if em is None:raise RuntimeError('Expected existing painted emission material '+base.name)
 old=em.inputs['Color'].links[0].from_socket if em.inputs['Color'].is_linked else None
 if old is None:
  q=n.new('ShaderNodeRGB');q.outputs[0].default_value=em.inputs['Color'].default_value;old=q.outputs[0]
 tex=n.new('ShaderNodeTexCoord');physical=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.80 if kind=='oxide steel'else 1.35;noise.inputs['Detail'].default_value=2.;noise.inputs['Roughness'].default_value=.72
 mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';l.new(physical.outputs['Position'],mapping.inputs[0]);mapping.inputs[1].default_value=(1.,1.,1.)if kind=='oxide steel'else(1.3,.65,.13);l.new(mapping.outputs[0],noise.inputs['Vector'])
 midgrain=n.new('ShaderNodeTexNoise');midgrain.inputs['Scale'].default_value=4.5;midgrain.inputs['Detail'].default_value=3.;l.new(physical.outputs['Position'],midgrain.inputs['Vector']);patch=n.new('ShaderNodeMixRGB');patch.inputs[0].default_value=.28;l.new(noise.outputs['Fac'],patch.inputs[1]);l.new(midgrain.outputs['Fac'],patch.inputs[2]);fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=100.;fine.inputs['Detail'].default_value=2.;l.new(physical.outputs['Position'],fine.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.label='133 Connected oxide islands and finite streaks';ramp.color_ramp.elements[0].position=(.465-exposure) if kind=='oxide steel'else .51;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=(.490-exposure) if kind=='oxide steel'else .56;ramp.color_ramp.elements[1].color=(.94,.94,.94,1);l.new(patch.outputs[0],ramp.inputs[0])
 if kind=='rust runoff':
  xyz=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Generated'],xyz.inputs[0]);fade=n.new('ShaderNodeMath');fade.operation='MULTIPLY_ADD';l.new(xyz.outputs['Z'],fade.inputs[0]);fade.inputs[1].default_value=.17;fade.inputs[2].default_value=-.17;combined=n.new('ShaderNodeMath');combined.operation='ADD';l.new(patch.outputs[0],combined.inputs[0]);l.new(fade.outputs[0],combined.inputs[1]);l.new(combined.outputs[0],ramp.inputs[0])
 col=n.new('ShaderNodeValToRGB');col.label='133 Deep oxide, ochre corrosion and fine pits';col.color_ramp.elements[0].position=.33;col.color_ramp.elements[0].color=(.035,.018,.012,1);col.color_ramp.elements[1].position=.67;col.color_ramp.elements[1].color=(.23,.092,.036,1);mid=col.color_ramp.elements.new(.52);mid.color=(.15,.053,.023,1);tone=n.new('ShaderNodeMixRGB');tone.inputs[0].default_value=.70;l.new(midgrain.outputs['Fac'],tone.inputs[1]);l.new(fine.outputs['Fac'],tone.inputs[2]);l.new(tone.outputs[0],col.inputs[0])
 grain=n.new('ShaderNodeMixRGB');grain.blend_type='MULTIPLY';grain.inputs[0].default_value=.13;l.new(col.outputs[0],grain.inputs[1]);l.new(fine.outputs['Fac'],grain.inputs[2]);diffuse=n.new('ShaderNodeBsdfDiffuse');diffuse.inputs['Color'].default_value=(.7,.7,.7,1);rgb=n.new('ShaderNodeShaderToRGB');l.new(diffuse.outputs[0],rgb.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(rgb.outputs[0],bw.inputs[0]);light=n.new('ShaderNodeMapRange');light.clamp=True;light.inputs['From Min'].default_value=0;light.inputs['From Max'].default_value=.9;light.inputs['To Min'].default_value=.34;light.inputs['To Max'].default_value=1.;l.new(bw.outputs[0],light.inputs[0]);lit=n.new('ShaderNodeMixRGB');lit.blend_type='MULTIPLY';lit.inputs[0].default_value=1;l.new(grain.outputs[0],lit.inputs[1]);l.new(light.outputs[0],lit.inputs[2]);mix=n.new('ShaderNodeMixRGB');mix.label='133 Rust over retained existing paint/light response';l.new(ramp.outputs[0],mix.inputs[0]);l.new(old,mix.inputs[1]);l.new(lit.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],em.inputs['Color']);m['133 weathering']=kind;cache[key]=m;return m

def apply(scene):
 if bpy.data.collections.get('133 Alley damage study'):raise RuntimeError('Already applied')
 start=time.time();rng=random.Random(133);C=bpy.data.collections.new('133 Alley damage study');scene.collection.children.link(C);cache={};audit={'references':['UCL-01','UP-03','DP-08'],'changed_instances':[],'seed':133}
 host=scene.objects.get('Front-left section instance');gang=scene.objects.get('Architecture | gangway_single_Y_8m')
 if not host or not gang:raise RuntimeError('Expected accepted left facade/Y assemblies')
 oldcol=host.instance_collection;private=oldcol.copy();private.name='133 Left front facade, one missing panel';host.instance_collection=private
 def center(o):return o.matrix_world@(sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices))
 panels=[o for o in private.objects if o.type=='MESH'and o.name.startswith('Recessed base wall')and center(o).x>2.5 and center(o).z>3.3]
 if len(panels)!=1:raise RuntimeError('Panel selection ambiguous '+str([o.name for o in panels]))
 panel=panels[0];pts=[panel.matrix_world@v.co for v in panel.data.vertices];lo=Vector(tuple(min(v[k]for v in pts)for k in range(3)));hi=Vector(tuple(max(v[k]for v in pts)for k in range(3)));W=hi.x-lo.x;H=hi.z-lo.z;front=.75;z0=lo.z;u=(lo.x+hi.x)/2
 paint=panel.material_slots[0].material;steel=next(o.material_slots[0].material for o in gang.instance_collection.objects if o.name.startswith('Y arm web'))
 private.objects.unlink(panel);audit['removed_panel']={'object':panel.name,'master_bounds':[list(lo),list(hi)],'width':W,'height':H,'replacement_depth':.60};audit['changed_instances'].append(host.name)
 # Private material overrides preserve the geometry/placement of the approved support.
 gcol=bpy.data.collections.new('133 Rusted Y support and ledge');gcol.asset_mark()
 for old in gang.instance_collection.objects:
  ob=old.copy();gcol.objects.link(ob)
  kind='rust runoff'if any(t in old.name for t in ['Folded fascia','Replaceable deck panel'])else'oxide steel'
  for slot in ob.material_slots:
   if slot.material:
    exposure=.065 if any(t in old.name.lower()for t in ['flange','foot','splice','bolt','anchor']) else 0.;replacement=weather_material(slot.material,kind,cache,exposure);slot.link='OBJECT';slot.material=replacement
 gang.instance_collection=gcol;audit['changed_instances'].append(gang.name)
 kit=bpy.data.collections.new('PREFAB133 Missing cladding, exposed connected utilities');kit.asset_mark();kit['part_id']='missing_wall_panel_services';kit['width']=W;kit['height']=H;kit['depth']=.60;kit['mount_plane']='Local Y=0, outward -Y';kit['seed']=133
 def mesh(name,vs,fs,mat,bevel=0):
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mat);ob=bpy.data.objects.new(name,me);kit.objects.link(ob)
  if bevel:
   be=ob.modifiers.new('133 Worn manufactured edge','BEVEL');be.width=bevel;be.segments=2
  return ob
 def box(name,p,d,mat):
  p=Vector(p);d=Vector(d)/2;vs=[p+Vector((x*d.x,y*d.y,z*d.z))for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];return mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],mat,.004)
 def basic(name,color):
  m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();df=n.new('ShaderNodeBsdfDiffuse');df.inputs[0].default_value=(*color,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(df.outputs[0],out.inputs[0]);return m
 dark=basic('133 Cavity backing dark violet',(.018,.022,.03));rubber=basic('133 Aged cable insulation',(.012,.011,.013));oxide=weather_material(steel,'oxide steel',cache)
 box('133 Deep closed service backwall',(0,.60,H/2),(W,.06,H),dark)
 for x in [-W/2+.045,W/2-.045]:box('133 Mounted side carrier',(x,.36,H/2),(.06,.50,H),oxide)
 for z in [.035,H-.035]:box('133 Carrier header/sill',(0,.36,z),(W,.50,.065),oxide)
 for x in [-W*.32,W*.32]:box('133 Rear conduit mounting rail',(x,.51,H/2),(.045,.045,H-.08),oxide)
 # A single closed annular remnant has rough inner returns without floating flakes.
 outer=[]
 for t in [0,.22,.45,.67,.84,1]:outer.append((-W/2+t*W,0))
 for t in [.22,.43,.66,.84,1]:outer.append((W/2,t*H))
 for t in [.22,.44,.66,.84,1]:outer.append((W/2-t*W,H))
 for t in [.22,.43,.66,.84]:outer.append((-W/2,H-t*H))
 inner=[]
 for x,z in outer:
  dx=(.08+rng.uniform(0,.045))*(1 if x<0 else-1)if abs(x)>W/2-.001 else rng.uniform(-.025,.025)
  dz=(.08+rng.uniform(0,.045))*(1 if z<H/2 else-1)if z<.001 or z>H-.001 else rng.uniform(-.025,.025)
  inner.append((x+dx,z+dz))
 N=len(outer);vs=[(x,y,z)for y in [0,.08]for ring in [outer,inner]for x,z in ring];fs=[]
 for i in range(N):
  j=(i+1)%N;fs.extend([(i,j,N+j,N+i),(2*N+j,2*N+i,3*N+i,3*N+j),(j,i,2*N+i,2*N+j),(N+i,N+j,3*N+j,3*N+i)])
 rim=mesh('133 Broken cladding rim with exposed thickness',vs,fs,paint,.002);rim.data.materials.append(oxide)
 for p in rim.data.polygons:
  if p.index%4==3:p.material_index=1
 def tube(name,points,radius,mat,smooth=False):
  cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=radius;cu.bevel_resolution=3;cu.resolution_u=12;cu.use_fill_caps=True
  sp=cu.splines.new('BEZIER'if smooth else'POLY')
  if smooth:
   sp.bezier_points.add(len(points)-1)
   for p,q in zip(sp.bezier_points,points):p.co=q;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
  else:
   sp.points.add(len(points)-1)
   for p,q in zip(sp.points,points):p.co=(*q,1)
  ob=bpy.data.objects.new(name,cu);kit.objects.link(ob);cu.materials.append(mat);return ob
 ports=[]
 for i,(z,rr,depth)in enumerate([(H*.35,.049,.25),(H*.64,.034,.31)]):
  tube('133 Through-wall steel conduit '+str(i),[(-W/2-.08,depth,z),(W/2+.08,depth,z)],rr,oxide)
  for x in [-W*.31,W*.31]:
   tube('133 Fitted pipe clamp',[(x-.018,depth,z),(x+.018,depth,z)],rr+.011,oxide)
   box('133 Clamp standoff to rear rail',(x,(depth+.50)/2,z),(.035,.50-depth,.035),oxide)
  ports.extend([{'pipe':i,'position':[-W/2,depth,z],'mate':'concealed conduit continuation inside left wall'},{'pipe':i,'position':[W/2,depth,z],'mate':'concealed conduit continuation inside right wall'}])
 # Quarter-circle elbow, not a kinked cable masquerading as a pipe.
 x=-W*.28;z=H*.79;r=.13;points=[(x,.41,-.07),(x,.41,z-r)]
 for k in range(1,10):
  a=math.pi-k/9*math.pi/2;points.append((x+r+r*math.cos(a),.41,z-r+r*math.sin(a)))
 points.append((W/2+.08,.41,z));tube('133 Lower riser and fitted elbow',points,.041,oxide);ports.extend([{'pipe':'riser','position':[x,.41,0],'mate':'concealed lower service chase'},{'pipe':'riser','position':[W/2,.41,z],'mate':'concealed right chase'}])
 box('133 Electrical termination enclosure',(W*.19,.27,H*.84),(.28,.14,.19),oxide)
 for x in [-.10,.10]:box('133 Enclosure securing screw',(W*.19+x,.187,H*.84),(.024,.018,.024),oxide)
 for i in range(5):
  x0=-W*.35+i*.13;x1=W*.19-.11+i*.05;low=H*(.14+.035*i)
  pts=[(x0,.18,H+.045),(x0-.045,.13,H*.69),(x0+.04,.135,low+.08),((x0+x1)/2,.12,low),(x1,.16,H*.47),(x1,.18,H*.745)]
  tube('133 Terminated cable loop '+str(i),pts,.009+i*.0013,rubber,True)
  box('133 Cable gland',(x1,.18,H*.745),(.028,.055,.035),oxide)
  ports.extend([{'cable':i,'end':'top concealed chase','position':pts[0]},{'cable':i,'end':'junction box gland','position':pts[-1]}])
 kit['ports_json']=json.dumps(ports);kit['construction']='Closed torn cladding annulus,600mm cavity, mounted rails, fitted pipe clamps, two through-routes and one riser elbow; cable loops terminate in a connected enclosure.'
 instance=bpy.data.objects.new('133 Exposed utility panel instance',None);instance.instance_type='COLLECTION';instance.instance_collection=kit;instance.matrix_world=host.matrix_world@Matrix.Translation((u,front,z0));C.objects.link(instance)
 # Remove only stale baked ink points on the removed cladding face; no broad rebake.
 affected=[];iv=(host.matrix_world).inverted()
 for name in ['096 contacts ink','096 damage ink']:
  ink=scene.objects.get(name)
  if not ink:continue
  ink.data=ink.data.copy();count=0
  for layer in ink.data.layers:
   for frame in layer.frames:
    for stroke in frame.drawing.strokes:
     for p in stroke.points:
      q=iv@(ink.matrix_world@p.position)
      if lo.x-.015<q.x<hi.x+.015 and z0-.015<q.z<hi.z+.015 and front-.07<q.y<front+.13:p.opacity=0;count+=1
  affected.append({'object':name,'removed_panel_ink_points_hidden':count})
 audit.update({'panel_prefab':kit.name,'weathered_support_prefab':gcol.name,'prefab_instance_matrix':[list(r)for r in instance.matrix_world],'pipe_cable_ports':ports,'native_parts':len(kit.objects),'material_copies':[m.name for m in cache.values()],'localized_ink_update':affected,'geometry_scope':'One removed cladding panel replaced by fitted editable service cavity; Y and ledge geometry unchanged, materials privately copied. No other service or landmark edits.','render_note':'Local study disables the frozen128 foreground-ink compositor because this authorized alley change requires a new native ink baseline before final integration.','seconds':time.time()-start})
 return audit
