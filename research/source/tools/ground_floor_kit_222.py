"""Reusable native closed garage and recessed gated pedestrian passage."""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix

TARGETS=[('right_horizontal_utility',['Utility base.020','Utility base.021','Utility base.022','Utility base.023'],(9.15,28.,.12),3.6,2.16),('right_vertical_galleries',['Gallery base panel.011','Gallery base panel.012'],(9.85,10.2,.12),2.1,2.16)]

def box(c,name,center,size,mat=None,bevel=.012):
 x,y,z=center;a,b,d=[v/2 for v in size];v=[(x+i*a,y+j*b,z+k*d)for i,j,k in[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);c.objects.link(ob)
 if mat:me.materials.append(mat)
 if bevel:
  mod=ob.modifiers.new('Small manufactured edge','BEVEL');mod.width=bevel;mod.segments=1
 return ob

def finish(name,color,wear=True):
 clean=bpy.data.materials.new('222 Clean '+name);clean.use_nodes=True;n=clean.node_tree.nodes;l=clean.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');l.new(em.outputs[0],out.inputs['Surface']);dif=n.new('ShaderNodeBsdfDiffuse');dif.inputs['Color'].default_value=(.65,.65,.65,1);rgb=n.new('ShaderNodeShaderToRGB');l.new(dif.outputs[0],rgb.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(rgb.outputs[0],bw.inputs[0]);light=n.new('ShaderNodeMapRange');light.clamp=True;light.inputs['From Max'].default_value=.8;light.inputs['To Min'].default_value=.46;light.inputs['To Max'].default_value=1.13;l.new(bw.outputs[0],light.inputs[0]);mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[1].default_value=(*color,1);l.new(light.outputs[0],mul.inputs[2]);l.new(mul.outputs[0],em.inputs['Color']);clean.use_fake_user=True
 if not wear:return clean
 m=clean.copy();m.name='222 Worn '+name;m['222 clean source']=clean.name;n=m.node_tree.nodes;l=m.node_tree.links;em=next(q for q in n if q.type=='EMISSION');base=em.inputs['Color'].links[0].from_socket
 # Separate optional pigment finish: fine chips and sparse gravity-biased oxidation, no blob camouflage.
 geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=23;noise.inputs['Detail'].default_value=2;l.new(geo.outputs['Position'],noise.inputs['Vector']);mask=n.new('ShaderNodeMapRange');mask.clamp=True;mask.inputs['From Min'].default_value=.67;mask.inputs['From Max'].default_value=.82;mask.inputs['To Max'].default_value=.35;l.new(noise.outputs['Fac'],mask.inputs[0]);chip=n.new('ShaderNodeMixRGB');chip.label='222 Optional fine mineral / steel chips';l.new(mask.outputs[0],chip.inputs[0]);l.new(base,chip.inputs[1]);chip.inputs[2].default_value=(*[min(.7,v*1.3)for v in color],1)
 low=n.new('ShaderNodeMapRange');low.clamp=True;low.inputs['From Min'].default_value=.12;low.inputs['From Max'].default_value=.85;low.inputs['To Min'].default_value=.14;low.inputs['To Max'].default_value=0;l.new(sep.outputs['Z'],low.inputs[0]);mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY';l.new(low.outputs[0],mult.inputs[0]);l.new(noise.outputs['Fac'],mult.inputs[1]);rust=n.new('ShaderNodeMixRGB');rust.label='222 Optional restrained bottom oxide wash';l.new(mult.outputs[0],rust.inputs[0]);l.new(chip.outputs[0],rust.inputs[1]);rust.inputs[2].default_value=(.16,.07,.043,1);l.new(rust.outputs[0],em.inputs['Color']);return m

def cut_hosts(scene):
 rows=[];mappings=[]
 for rootname,names,origin,width,height in TARGETS:
  root=bpy.data.objects[rootname];old=root.instance_collection;private=old.copy();private.name='222 Private fitted '+rootname;old.use_fake_user=True;root.instance_collection=private;T=root.matrix_world@Matrix.Translation(-old.instance_offset);mapping={}
  x,y,z=origin;cutter=box(scene.collection,'222 Temporary opening cutter',(0,0,0),(1,1,1),bevel=0)
  # Only facade skin, never the structural support beam at2.30m or a service.
  worldcorners=[Vector((xx,yy,zz))for xx,yy,zz in[(x-.16,y-width/2,z-.02),(x-.16,y-width/2,z+height),(x-.16,y+width/2,z-.02),(x-.16,y+width/2,z+height),(x+.30,y-width/2,z-.02),(x+.30,y-width/2,z+height),(x+.30,y+width/2,z-.02),(x+.30,y+width/2,z+height)]]
  for v,p in zip(cutter.data.vertices,worldcorners):v.co=p
  cutter.hide_render=True;changed=[]
  for name in names:
   source=bpy.data.objects[name];assert source.name in private.objects,(rootname,name)
   bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=source.evaluated_get(dg)
   native=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg);native.transform(T@source.matrix_world);native.update()
   ob=source.copy();ob.name='222 Opened '+source.name;ob.modifiers.clear();ob.parent=None;ob.matrix_world=Matrix.Identity(4);ob.data=native;scene.collection.objects.link(ob)
   mod=ob.modifiers.new('222 Actual facade opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
   cutter.data.update();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg);mesh.name='222 Native cut '+name;ob.modifiers.clear();ob.data=mesh
   scene.collection.objects.unlink(ob);private.objects.unlink(source);private.objects.link(ob);ob.matrix_world=T.inverted();mapping[source.name]=ob.name
   changed.append({'source':name,'replacement':ob.name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'original_mesh_preserved':True})
  bpy.data.objects.remove(cutter,do_unlink=True);mappings.append(mapping);rows.append({'root':rootname,'original_collection':old.name,'private_collection':private.name,'opening_origin':origin,'clear_width':width,'clear_height':height,'cut_objects':changed,'all_other_members_shared_exactly':True})
 # Preserve original selection ownership for copied facade parts only.
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if not ls.collection:continue
   extra=[bpy.data.objects[new]for mp in mappings for old,new in mp.items()if old in ls.collection.all_objects]
   if extra:
    c=bpy.data.collections.new('222 Selection alias '+ls.collection.name);c.use_fake_user=True
    for ob in set(ls.collection.all_objects)|set(extra):c.objects.link(ob)
    ls.collection=c
 groups=json.loads(scene.get('212 source name groups','[]'));groups.extend(mappings);scene['212 source name groups']=json.dumps(groups)
 return rows

def trim_old_contacts(scene):
 from coliseum_contact_clip_169 import snapshot,run,digest
 boxes=[[(x-.10,x+.20),(y-w/2,y+w/2),(z-.005,z+h+.005)]for _,_,(x,y,z),w,h in TARGETS]
 def interval(a,b,box):
  lo,hi=0.,1.
  for i,(mn,mx)in enumerate(box):
   d=b[i]-a[i]
   if abs(d)<1e-10:
    if not mn<=a[i]<=mx:return None
   else:
    p,q=sorted(((mn-a[i])/d,(mx-a[i])/d));lo=max(lo,p);hi=min(hi,q)
    if hi<=lo:return None
  return lo,hi
 reports=[]
 for gp in list(scene.objects):
  if gp.type!='GREASEPENCIL'or gp.hide_render or not gp.name.startswith(('096','097')):continue
  before=snapshot(gp);changes=[];M=gp.matrix_world.copy()
  for rec in before:
   for si,st in enumerate(rec['strokes']):
    pts=st['point'].get('position',[])
    if len(pts)<2:continue
    removed=[]
    for i in range(len(pts)-1):
     a,b=M@Vector(pts[i]),M@Vector(pts[i+1])
     for box in boxes:
      v=interval(a,b,box)
      if v:removed.append((i+v[0],i+v[1]))
    if not removed:continue
    merged=[]
    for a,b in sorted(removed):
     if merged and a<=merged[-1][1]+1e-7:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
     else:merged.append((a,b))
    kept=[];start=0
    for a,b in merged:
     if a-start>1e-6:kept.append((start,a))
     start=b
    if len(pts)-1-start>1e-6:kept.append((start,len(pts)-1))
    runs=[run(st,a,b)for a,b in kept]
    for r in runs:
     if 'cyclic'in r['curve']:r['curve']['cyclic']=False
    changes.append((rec,si,runs))
  if not changes:reports.append({'object':gp.name,'changed_strokes':0});continue
  old=gp.data;old.use_fake_user=True;gp.data=old.copy();retained=[]
  for rec in before:
   edits=[(si,runs)for r,si,runs in changes if r is rec]
   if not edits:continue
   dr=gp.data.layers[rec['layer']].frames[rec['frame']].drawing;ids=sorted(si for si,_ in edits);expect=[st for i,st in enumerate(rec['strokes'])if i not in ids];dr.remove_strokes(indices=ids);off=sum(len(st.points)for st in dr.strokes);base=len(dr.strokes);new=[r for _,runs in edits for r in runs]
   if new:
    dr.add_strokes(sizes=[len(r['point']['position'])for r in new])
    for j,r in enumerate(new):
     for k,vals in r['point'].items():
      for i,v in enumerate(vals):setattr(dr.attributes[k].data[off+i],rec['schema'][k]['prop'],v)
     for k,v in r['curve'].items():setattr(dr.attributes[k].data[base+j],rec['schema'][k]['prop'],v)
     off+=len(r['point']['position'])
   retained.append((rec['layer'],rec['frame'],expect))
  after=snapshot(gp)
  for li,fi,expect in retained:assert next(r for r in after if r['layer']==li and r['frame']==fi)['strokes'][:len(expect)]==expect
  reports.append({'object':gp.name,'changed_strokes':len(changes),'source_digest':digest(before),'result_digest':digest(after),'all_unaffected_attributes_exact':True,'original_drawing_retained':old.name,'scope':'Only spans on six removed facade panel footprints; new gate depth and support beams excluded.'})
 return reports

def clip_new_receiver_occlusion(scene):
 """Only old096 ink hidden by the new jambs/sidewalls, using native210 attribute-safe clip."""
 from mathutils.bvhtree import BVHTree
 import landmark_contact_visibility_210 as clip
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();vs=[];ts=[];owners=[];names=set()
 for ins in dg.object_instances:
  ob=ins.object;name=ob.original.name
  if not name.startswith(('222 passage entry jamb','222 passage diagonal sidewall')) or ob.hide_render:continue
  if not ins.is_instance:continue
  me=ob.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ins.matrix_world@v.co for v in me.vertices);ts.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);owners.extend([name]*len(me.loop_triangles));names.add(name);ob.to_mesh_clear()
 assert len(names)==8,(len(names),names)
 tree=BVHTree.FromPolygons(vs,ts,all_triangles=True);inventory={'scope':'Only eight new222 passage jamb/sidewall components','names':sorted(names),'triangles':len(ts)}
 oldname,oldtree=clip.NAME,clip.external_tree;reports=[]
 try:
  clip.external_tree=lambda scene:(tree,owners,inventory)
  for name in ('096 contacts ink','096 damage ink'):
   clip.NAME=name;r=clip.apply(scene,max_pixel_step=.5,gap_m=.012);r['scope']='Only old096 spans actually behind new222 passage jambs and sidewalls; other geometry is excluded from this visibility test.';reports.append(r)
 finally:clip.NAME,clip.external_tree=oldname,oldtree
 return reports


def apply(scene):
 assert not bpy.data.collections.get('222 Ground floor prefab placements')
 host=cut_hosts(scene);contacts=trim_old_contacts(scene);C=bpy.data.collections.new('222 Ground floor prefab placements');scene.collection.children.link(C)
 steel=finish('blue gray garage steel',(.20,.235,.28));frame=finish('worn zinc surround',(.25,.26,.27));iron=finish('charcoal iron gate',(.055,.061,.072));stone=finish('warm passage masonry',(.28,.24,.225));floor=finish('passage mineral floor',(.20,.18,.165));cleanparts=[];placements=[]
 for kind,origin in[('garage',(9.15,28,.12)),('passage',(9.85,10.2,.12))]:
  master=bpy.data.collections.new('222 Clean master '+kind);master.use_fake_user=True;new=[]
  def B(name,center,size,mat=frame,bevel=.012):
   ob=box(master,'222 '+kind+' '+name,center,size,mat,bevel);new.append(ob);return ob
  if kind=='garage':
   w,h=3.6,2.16
   # Broad six-section closed door, actual shallow pressed panels and quiet narrow joins.
   for j in range(6):
    z=(j+.5)*h/6;B('closed section '+str(j),(.075,0,z),(.10,w-.10,h/6-.022),steel,.01)
    B('pressed lower bead '+str(j),(.006,0,z-h/12+.033),(.027,w-.16,.023),frame,.005)
   for side in(-1,1):B('recessed jamb',(-.015,side*(w/2+.065),h/2),(.25,.13,h+.08),frame)
   B('lintel channel',(-.03,0,h+.025),(.24,w+.24,.09),frame)
   B('threshold shoe',(-.015,0,.012),(.38,w+.24,.035),frame,.006)
   for y in(-.62,.62):B('flush lift handle',(-.025,y,.69),(.07,.22,.055),iron,.008)
   for y in(-1.52,1.52):
    for z in(.18,1.04,1.94):B('fastener',(-.064,y,z),(.025,.036,.036),iron,.005)
  else:
   w,h,depth=2.1,2.16,3.25
   # Oblique native passage: entry follows facade, interior turns toward the approach.
   cam=scene.camera.matrix_world.translation;D=Vector((origin[0]-cam.x,origin[1]-cam.y,0)).normalized();A=Vector((-D.y,D.x,0));innerw=1.95
   lead=Vector((.20,0,0));gatecenter=D*(.2*D.x+math.sqrt(1.6**2-(.2*D.y)**2));rearcenter=gatecenter+D*(depth-1.8)
   stations=[(Vector((0,0,0)),Vector((0,1,0)),w/2),(lead,Vector((0,1,0)),w/2),(gatecenter,Vector((0,1,0)),innerw/2),(rearcenter,Vector((0,1,0)),innerw/2)]
   def slab(name,quad,thick,mat):
    verts=[tuple(p+Vector((0,0,z)))for z in(-thick,0)for p in quad];faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);ob=bpy.data.objects.new('222 passage '+name,me);master.objects.link(ob);new.append(ob)
   for j in range(len(stations)-1):
    p,r,half=stations[j];q,t,other=stations[j+1];quad=[p-r*half,q-t*other,q+t*other,p+r*half];slab('native diagonal walkway '+str(j),quad,.12,floor);slab('native diagonal ceiling '+str(j),[v+Vector((0,0,h+.12))for v in quad],.12,stone)
    for sign in(-1,1):
     e=p+r*(half*sign);f=q+t*(other*sign);mid=(e+f)/2;delta=f-e;ob=B('diagonal sidewall',(0,0,h/2),(.15,delta.length,h+.12),stone);ob.rotation_euler.z=-math.atan2(delta.x,delta.y);ob.location=mid
   for side in(-1,1):B('entry jamb',(-.04,side*(w/2+.075),h/2),(.34,.15,h+.08),frame)
   B('entry lintel',(-.04,0,h+.015),(.34,w+.30,.11),frame)
   theta=0.0
   def G(name,center,size,mat=iron,bevel=.006):
    ob=B(name,center,size,mat,bevel);ob.rotation_euler.z=theta;ob.location=gatecenter;return ob
   gh=1.95;leaf=.93
   for side in(-1,1):
    cy=side*.475
    for y in(cy-leaf/2,cy+leaf/2):G('gate leaf vertical frame',(0,y,.08+gh/2),(.065,.038,gh))
    for z in(.10,.58,1.58,2.03):G('gate leaf cross rail',(0,cy,z),(.065,leaf,.038))
    for i in range(1,6):G('gate iron bar',(0,cy-leaf/2+i*leaf/6,1.075),(.036,.022,1.86))
    G('gate low scuffed kick plate',(.014,cy,.225),(.035,leaf-.04,.20))
   for y in(-.945,.945):
    for z in(.35,1.7):G('gate hinge',(-.012,y,z),(.10,.06,.15),frame,.008)
   G('gate latch',(-.065,0,1.1),(.075,.20,.05),frame,.007)
   rear=B('rear masonry wall',(0,0,h/2),(.12,innerw+.20,h),stone);rear.rotation_euler.z=theta;rear.location=rearcenter
   B('threshold step',(-.04,0,-.008),(.42,w+.28,.07),floor,.008)
  root=bpy.data.objects.new('222 Placed '+kind,None);root.instance_type='COLLECTION';root.instance_collection=master;root.location=origin;C.objects.link(root);cleanparts.extend(new);placements.append({'kind':kind,'root':root.name,'master':master.name,'origin':origin,'clear_width_m':w,'clear_height_m':h,'gate_setback_m':1.8 if kind=='passage'else None,'interior_clear_width_m':1.95 if kind=='passage'else w,'components':len(new)})
 ink=bpy.data.collections.new('222 Ground floor component ink');ink.use_fake_user=True
 for ob in cleanparts:ink.objects.link(ob)
 target=scene.view_layers['192 Architecture ink without pigment films']
 for ls in target.freestyle_settings.linesets:
  if ls.select_by_collection and ls.collection_negation=='EXCLUSIVE':
   c=bpy.data.collections.new('222 Ink exclusion '+ls.collection.name);c.use_fake_user=True
   for ob in set(ls.collection.all_objects)|set(cleanparts):c.objects.link(ob)
   ls.collection=c
 ls=target.freestyle_settings.linesets.new('222 Ground floor manufactured details');ls.select_by_collection=True;ls.collection=ink;ls.collection_negation='INCLUSIVE';ls.select_by_visibility=True;ls.visibility='VISIBLE';ls.select_crease=True;ls.select_border=True;ls.select_silhouette=True;ls.linestyle.thickness=.60;ls.linestyle.alpha=.94;ls.linestyle.color=(.026,.023,.034)
 occlusion=clip_new_receiver_occlusion(scene)
 return {'receiver_occlusion_clip':occlusion,'host_modifications':host,'contact_clip':contacts,'placements':placements,'new_component_objects':len(cleanparts),'original_support_services_preserved':True,'opening_head_z_m':2.28,'structural_bearing_bottom_z_m':2.30,'door_closed':True,'native_recess_depth_m':3.25,'wear_separate_clean_material_sources':True,'geometry_sources_editable':True,'notes':['Garage frontage shifted toy26.2–29.8 to preserve adjacent nestedservicepanel.','Existing continuousbeam remains the structural lintel; both openings have2.16mclearheight.']}
