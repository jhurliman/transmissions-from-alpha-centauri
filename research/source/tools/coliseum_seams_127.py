"""Weld touching arcade wall/pier solids into continuous masonry without changing openings."""
import bpy,bmesh,math,json
from mathutils import Vector
from coliseum_arch_ratio_125 import mapping

def apply(C,tiers=(0,1,2)):
 original,world,unpack=mapping();audit=[]
 for tier in tiers:
  sources=[o for o in C.objects if o.type=='MESH' and o.get('tier')==tier and ('loadbearing arch tunnel' in o.name or 'solid pier' in o.name)]
  caps=[];coordinates={}
  for o in sources:
   co=[unpack(o.matrix_world@v.co)for v in o.data.vertices];coordinates[o.name]=co;amin=min(x[1]for x in co);amax=max(x[1]for x in co)
   for p in o.data.polygons:
    aa=[co[i][1]for i in p.vertices]
    if max(aa)-min(aa)<2e-5 and min(abs(sum(aa)/len(aa)-amin),abs(sum(aa)/len(aa)-amax))<2e-5:
     caps.append({'object':o,'face':p.index,'a':sum(aa)/len(aa),'zmin':min(co[i][2]for i in p.vertices),'zmax':max(co[i][2]for i in p.vertices),'pier':'solid pier'in o.name})
  capgroups=[]
  for cap in caps:
   group=next((g for g in capgroups if g['object']==cap['object'] and abs(g['a']-cap['a'])<2e-5),None)
   if group:
    group['faces'].append(cap['face']);group['zmin']=min(group['zmin'],cap['zmin']);group['zmax']=max(group['zmax'],cap['zmax'])
   else:capgroups.append(dict(cap,faces=[cap['face']]))
  caps=capgroups
  joints=[];paired=set()
  for i,c in enumerate(caps):
   if c['pier']:continue
   choices=[(abs(c['a']-v['a']),j,v)for j,v in enumerate(caps)if v['pier']and j not in paired]
   if not choices:continue
   delta,j,p=min(choices,key=lambda x:x[0])
   if delta>2e-5:continue
   a=(c['a']+p['a'])/2;zlo=round(c['zmin'],3);zhi=round(c['zmax'],3);joints.append({'a':a,'zlo':zlo,'zhi':zhi,'arch':c,'pier':p});paired.update([i,j])
  cutmap={o.name:[]for o in sources}
  for j in joints:
   for role in ['arch','pier']:cutmap[j[role]['object'].name].append((j,j[role]))
  temp=[]
  for o in sources:
   ob=o.copy();ob.data=o.data.copy();ob.name='127 stitch source '+o.name;C.objects.link(ob);ob.modifiers.clear();temp.append(ob)
   for slot,oldslot in zip(ob.material_slots,o.material_slots):slot.link='DATA';slot.material=oldslot.material
   bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table();iv=ob.matrix_world.inverted();layer=bm.verts.layers.float_vector.get('115 Original world position');dl=bm.verts.layers.float.get('120 Actual arch tunnel depth');remove=[];original_faces=list(bm.faces)
   for joint,cap in cutmap[o.name]:
    a=joint['a'];zlo=joint['zlo'];zhi=joint['zhi']
    for v in bm.verts:
     rr,aa,zz=unpack(ob.matrix_world@v.co)
     if abs(aa-a)>2e-5:continue
     rr=67. if abs(rr-67)<.001 else 75. if abs(rr-75)<.001 else rr
     for z in [zlo,zhi,round(cap['zmin'],3),round(cap['zmax'],3)]:
      if abs(zz-z)<.001:zz=z;break
     v.co=iv@world(rr,a,zz)
     if layer:v[layer]=original(rr,a,zz)
    remove.extend(original_faces[i]for i in cap['faces'])
    if cap['pier']:
     for z0,z1 in [(round(cap['zmin'],3),zlo),(zhi,round(cap['zmax'],3))]:
      if z1-z0<.001:continue
      vs=[]
      for rr,z in [(67,z0),(75,z0),(75,z1),(67,z1)]:
       v=bm.verts.new(iv@world(rr,a,z));vs.append(v)
       if layer:v[layer]=original(rr,a,z)
       if dl:v[dl]=(75-rr)/8
      bm.faces.new(vs)
   bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free()
  me=bpy.data.meshes.new(f'127 T{tier} continuous arcade masonry');joined=bpy.data.objects.new(f'COL127 T{tier} continuous arcade wall',me);C.objects.link(joined)
  bpy.ops.object.select_all(action='DESELECT');joined.select_set(True)
  for ob in temp:ob.select_set(True)
  bpy.context.view_layer.objects.active=joined;bpy.ops.object.join()
  bm=bmesh.new();bm.from_mesh(joined.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0004);splits=0
  # Conform a long pier edge to shorter arch edges before the final weld.
  for j in joints:
   vv=[v for v in bm.verts if abs(unpack(v.co)[1]-j['a'])<2e-5]
   edges=[e for e in bm.edges if len(e.link_faces)==1 and all(abs(unpack(v.co)[1]-j['a'])<2e-5 for v in e.verts)]
   points=[v.co.copy()for v in vv]
   for edge in edges:
    if not edge.is_valid:continue
    start=edge.verts[0];end=edge.verts[1];a=start.co.copy();d=end.co-a;den=d.length_squared
    if den<1e-12:continue
    pp=[]
    for p in points:
     t=(p-a).dot(d)/den
     if 1e-5<t<1-1e-5 and (a+d*t-p).length<.0005:pp.append((t,p))
    last=-1
    for t,p in sorted(pp,key=lambda x:x[0]):
     if t-last<1e-5:continue
     last=t
     fac=(p-start.co).length/(end.co-start.co).length
     if not 1e-5<fac<1-1e-5:continue
     ne,nv=bmesh.utils.edge_split(edge,start,fac);nv.co=p;start=nv;edge=next(e for e in nv.link_edges if end in e.verts);splits+=1
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0005)
  wire=[e for e in bm.edges if not e.link_faces]
  if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
  holes=[e for e in bm.edges if len(e.link_faces)==1]
  if holes:
   assert all(any(all(abs(unpack(v.co)[1]-j['a'])<2e-5 for v in e.verts)for j in joints)for e in holes),'Open edge outside stitched interface'
   bmesh.ops.holes_fill(bm,edges=holes,sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.to_mesh(joined.data);bm.free()
  if bad:
   from pathlib import Path
   b=bmesh.new();b.from_mesh(joined.data);report=[{'faces':len(e.link_faces),'coords':[list(unpack(v.co))for v in e.verts]}for e in b.edges if not e.is_manifold];b.free();Path('/tmp/seam127bad.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath='/tmp/seam127bad.blend');raise RuntimeError(f'Tier{tier} stitch has{bad} nonmanifold edges')
  wall=bpy.data.materials.get('116 115 Painted masonry wall')or next(s.material for s in sources[0].material_slots if s.material);slot=len(joined.data.materials);joined.data.materials.append(wall);front=[]
  for p in joined.data.polygons:
   coords=[unpack(joined.data.vertices[i].co)for i in p.vertices]
   if all(abs(rr-75)<.001 for rr,a,z in coords):p.material_index=slot;p.use_smooth=True;front.append(p.index)
  # Smooth the curved flush face while keeping tunnel returns and cut faces sharp.
  normals=[];frontset=set(front)
  for p in joined.data.polygons:
   for vi in p.vertices:
    if p.index in frontset:
     rr,a,z=unpack(joined.data.vertices[vi].co);da=world(rr,a+.0001,z)-world(rr,a-.0001,z);dz=world(rr,a,z+.01)-world(rr,a,z-.01);normal=da.cross(dz).normalized()
     if normal.dot(p.normal)<0:normal=-normal
     normals.append(normal)
    else:normals.append(p.normal.copy())
  joined.data.normals_split_custom_set(normals);joined['coliseum_role']='wall';joined['tier']=tier;joined['bay']=-1;joined['127 continuous wall interfaces']=True
  for o in sources:bpy.data.objects.remove(o,do_unlink=True)
  audit.append({'tier':tier,'source_objects':len(sources),'welded_interfaces':len(joints),'edge_splits':splits,'nonmanifold_edges':bad,'volume':volume,'flush_front_faces':len(front),'object':joined.name,'changes':'Removed touching internal caps, conformed and welded their boundaries, consistent flush-wall material, smooth front normals'})
 return {'tiers':audit,'openings_and_exterior_positions':'Preserved except submillimetre interface weld tolerance','grouping_order':'Apply shared group map after stitching raw surfaces'}
