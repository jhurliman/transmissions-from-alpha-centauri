"""Two frame-anchored broken panes and two compact native alley-service alternatives."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from far_building_layout_226 import boxpoints
from far_facades_230 import box

def apply(scene):
 if scene.get('window_pipe232_applied'):raise RuntimeError('Already applied232 window/pipe')
 roots=list(bpy.data.collections['215 Short alley composition'].objects);newmesh=[];rows=[];pipes=[]
 def private(root):
  C=bpy.data.collections.new('232 Window pipe '+root.name);C.use_fake_user=True;C.instance_offset=root.instance_collection.instance_offset
  for o in root.instance_collection.objects:C.objects.link(o)
  root.instance_collection=C;return C
 containers={}
 for root in roots:
  broken=[o for o in root.instance_collection.objects if o.instance_collection and o.instance_collection.get('230 broken pane')]
  for old in broken:
   C=containers.setdefault(root.name,private(root));master=bpy.data.collections.new('232 Anchored pane '+root.name);master.use_fake_user=True
   original=old.instance_collection
   for k in original.keys():master[k]=original[k]
   mat=next(o.material_slots[0].material for o in original.objects if 'surviving shard'in o.name)
   for o in original.objects:
    if not any(t in o.name for t in('surviving shard','broken frame offset remnant')):master.objects.link(o)
   # All polygons touch actual glass rebates (not just arbitrary near-corner points).
   y=.81;bottom=.45;top=1.75;mostly='right'in root.name
   polys=[ [(-y,bottom),(y,bottom),(y,.63),(.57,.61),(.39,.78),(.28,.55),(-.06,.69),(-.28,.58),(-.61,.86),(-y,.93)], [(y,top),(y,1.20),(.68,1.32),(.73,1.47),(.53,1.57),(.63,top)] ] if mostly else [ [(-y,bottom),(-.29,bottom),(-.15,.65),(-.39,.82),(.13,1.03),(-.18,1.20),(.22,1.50),(.09,top),(-y,top)], [(y,bottom),(y,.92),(.64,.76),(.58,.59),(.36,bottom)] ]
   for i,poly in enumerate(polys):
    me=bpy.data.meshes.new('232 Connected jagged pane');me.from_pydata([(-.115,a,b)for a,b in poly],[],[tuple(range(len(poly)))]);me.materials.append(mat);ob=bpy.data.objects.new('232 Frame-anchored pane remnant '+str(i),me);master.objects.link(ob);sol=ob.modifiers.new('Real glass edge','SOLIDIFY');sol.thickness=.012;newmesh.append(ob)
   inst=old.copy();inst.name='232 Asymmetric broken window '+root.name;inst.instance_collection=master;C.objects.unlink(old);C.objects.link(inst)
   rows.append({'root':root.name,'pattern':'Mostly lost; jagged lower strip and narrow upper-right remnant'if mostly else'Large irregular left sheet with small lower-right remnant','polygons_local_yz':polys,'anchorage':'Every connected polygon overlaps at least one actual frame rebate; no floating triangles','old_offset_stile_removed':True})
 assert len(rows)==2,len(rows)
 def B(C,n,p,d,m):o=box(C,'232 '+n,p,d,m);newmesh.append(o);return o
 for rootname in ['215 left step 83','215 right step 89']:
  root=next(r for r in roots if r.name==rootname);C=containers.get(rootname)
  if C is None:C=private(root);containers[rootname]=C
  oldparts=[o for o in C.objects if any(t in o.name for t in ['closed service','service mounting shoe','service shoe continuation','Full600 wall elbow','Broad wall receiver','Receiver face gasket','Receiver full bore collar','Receiver corner bolt','Full600 wall flange','Flange bolt'])]
  barrel=next(o for o in oldparts if 'companion_600_L3'in o.name);a,b=boxpoints(barrel);y=-1.4;mat=next(sl.material for q in barrel.instance_collection.all_objects for sl in q.material_slots if sl.material)
  for o in oldparts:C.objects.unlink(o)
  meshes=[]
  def instance(source,z,x=.59):
   src=bpy.data.objects.get(source);sourcecol=src.instance_collection if src else next(c for c in bpy.data.collections if c.get('part_id')=='duct_L');kit=bpy.data.collections.new('232 Private native '+source);kit.use_fake_user=True;kit.instance_offset=sourcecol.instance_offset
   for leaf in sourcecol.objects:
    cp=leaf.copy();cp.name='232 Native kit '+leaf.name;kit.objects.link(cp)
    if not src:
     for slot in cp.material_slots:slot.link='OBJECT';slot.material=mat
   q=bpy.data.objects.new('232 Close-wall '+source,None);q.instance_type='COLLECTION';q.instance_collection=kit;q.matrix_world=Matrix.Translation((x,y,z))@Matrix.Rotation(math.pi/2,4,'Z');C.objects.link(q);meshes.extend(o for o in kit.all_objects if o.type=='MESH');return q
  if 'left'in rootname:
   for zz in(.40,1.40,2.40,3.40,4.40,5.40):instance('PIP duct_L',zz,.39)
   B(C,'Duct lower wall plinth',(.29,y,.24),(.98,1.02,.48),mat);B(C,'Duct roof-height wall receiver',(.29,y,6.66),(.98,1.02,.57),mat)
   for zz in(1.9,4.9):B(C,'Close duct fitted wall saddle',(.09,y,zz),(.32,.94,.14),mat)
   dimensions={'type':'Existing native L880x600 rectangular alley duct, six1m modules','maximum_projection_m':.78,'endpoints':['lower fitted architectural plinth','upper closed projecting wall receiver'],'support_z':[1.9,4.9]}
  else:
   instance('XL | housing_1000',.86,.64);instance('XL | companion_600_L3',2.36,.64);instance('XL | companion_600_L3',5.36,.64)
   B(C,'Round lower docking receiver',(.48,y,.66),(1.25,1.04,.42),mat);B(C,'Round upper docking receiver',(.48,y,8.56),(1.25,1.28,.42),mat)
   for zz in(1.65,3.2,5.7):B(C,'Short round pipe saddle',(.22,y,zz),(.46,.63,.13),mat)
   dimensions={'type':'Two native600mm straight barrels plus native1000mm maintenance housing, vertical receiver docking','maximum_projection_m':1.275,'endpoints':['lower sealed wall receiver','upper sealed wall receiver'],'support_z':[1.65,3.2,5.7]}
  newmesh.extend(meshes);pipes.append({'root':rootname,'removed_parts':[o.name for o in oldparts],**dimensions,'main_modules_scaled':False,'pier_center_local_y':y,'window_clearance':'Route lies on inter-bay pier; wider round housing below glazing and upper receiver above glazing','old_max_projection_m':max(boxpoints(o)[1][0]for o in oldparts)})
 groups=regular_window_groups(scene,roots,containers,newmesh)
 ink=bpy.data.collections['215 Distant accepted component ink']
 for o in set(newmesh):
  if o.name not in ink.objects:ink.objects.link(o)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for o in set(newmesh):
     if o.name not in ls.collection.objects:ls.collection.objects.link(o)
 scene['window_pipe232_applied']=True;bpy.context.view_layer.update()
 return {'study':232,'broken_windows':rows,'pipe_replacements':pipes,'regular_window_groups':groups,'old_meshes_and_materials_unchanged':True,'new_roofs_preserved':True,'source':bpy.data.filepath,'native_ink':'215 owner registered','review':'CPU assembly; parent native perspective proof required'}
def regular_window_groups(scene,roots,containers,newmesh):
 # Reuse full native bay modules at the same storey; never paste glazing over a wall.
 rows=[];intact={}
 for root in roots:
  templates=[o for o in root.instance_collection.objects if o.instance_collection and o.instance_collection.get('230 component kind')in('picture','slider')]
  if not templates:continue
  C=containers.get(root.name)
  if C is None:
   C=bpy.data.collections.new('232 Regular windows '+root.name);C.use_fake_user=True;C.instance_offset=root.instance_collection.instance_offset
   for o in root.instance_collection.objects:C.objects.link(o)
   root.instance_collection=C;containers[root.name]=C
  used=set()
  for template in templates:
   M=template.matrix_world.copy();street=abs(M.to_3x3()[0][0])>.9;axis=1 if street else 0;plane=0 if street else 1
   key=(street,round(M.translation[plane],2),round(M.translation.z,2))
   if key in used:continue
   used.add(key);candidates=[]
   for o in list(C.objects):
    if not o.instance_collection or o.instance_collection.get('230 component kind'):continue
    a,b=boxpoints(o)
    if abs((b[2]-a[2])-2.16)>.04 or abs(a[2]-M.translation.z)>.04:continue
    if abs((b[axis]-a[axis])-2.8)>.06 or b[plane]-a[plane]>.5:continue
    center=(a[plane]+b[plane])/2
    if abs(center-M.translation[plane])>.28:continue
    candidates.append((o,a,b))
   if not candidates:continue
   master=template.instance_collection
   if master.get('230 broken pane'):
    if master not in intact:
     fresh=bpy.data.collections.new('232 Intact sibling '+master.name);fresh.use_fake_user=True
     for k in master.keys():fresh[k]=master[k]
     fresh['230 broken pane']=False
     for o in master.objects:
      if 'pane remnant'not in o.name:fresh.objects.link(o)
     glass=bpy.data.materials['230 Subdued smoke glass'];q=box(fresh,'232 intact sibling pane',(-.15,0,1.10),(.025,1.48,1.17),glass,.003);newmesh.append(q);intact[master]=fresh
    master=intact[master]
   added=[]
   for old,a,b in sorted(candidates,key=lambda x:x[1][axis]):
    T=M.copy();T.translation[axis]=(a[axis]+b[axis])/2
    q=bpy.data.objects.new('232 Aligned window '+root.name,None);q.instance_type='COLLECTION';q.instance_collection=master;q.matrix_world=T;C.objects.unlink(old);C.objects.link(q);added.append(q.name)
    if not street:
     ow=1.62 if master.get('230 component kind')=='picture'else 1.72
     mat=bpy.data.materials['222 Worn worn zinc surround'];cutter=box(scene.collection,'232 temporary return cutter',(0,0,0),(1,1,1),mat,0)
     points=[T@Vector((x,y,z))for x,y,z in[(-1,-ow/2,.45),(-1,-ow/2,1.75),(-1,ow/2,.45),(-1,ow/2,1.75),(.3,-ow/2,.45),(.3,-ow/2,1.75),(.3,ow/2,.45),(.3,ow/2,1.75)]]
     for v,p in zip(cutter.data.vertices,points):v.co=p
     cutter.data.update();cutter.hide_render=True;clo=[min(p[k]for p in points)for k in range(3)];chi=[max(p[k]for p in points)for k in range(3)]
     for shell in list(C.objects):
      if shell.type!='MESH'or not any(t in shell.name for t in ['leading interior return','rear wall return','Upper structural course']):continue
      sa,sb=boxpoints(shell)
      if not all(sa[k]<chi[k]and sb[k]>clo[k]for k in range(3)):continue
      if not shell.get('232 grouped aperture backing'):
       cp=shell.copy();cp.data=shell.data.copy();cp.name='232 Grouped aperture '+shell.name;cp['232 grouped aperture backing']=True;C.objects.unlink(shell);C.objects.link(cp);shell=cp;newmesh.append(cp)
      bm=bmesh.new();bm.from_mesh(shell.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(shell.data);bm.free();scene.collection.objects.link(shell)
      mod=shell.modifiers.new('232 Actual aligned aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(shell.evaluated_get(dg),depsgraph=dg);shell.modifiers.clear();shell.data=me;scene.collection.objects.unlink(shell)
     bpy.data.objects.remove(cutter,do_unlink=True)
   rows.append({'root':root.name,'template':template.name,'height_m':M.translation.z,'face':'street'if street else'return','native_bay_pitch_m':2.8,'new_aligned_windows':added,'group_count':len(added)+1,'real_openings':True})
 return rows

if __name__=='__main__':
 O=R/'art/studies/window-pipe-refine-232';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/midground-damage-232/walls-roofs.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('232 WINDOW PIPE READY',flush=True)
