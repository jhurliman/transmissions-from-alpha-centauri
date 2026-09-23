"""189 occurrence-specific, receiver-conforming native fastener corrosion.
Native mesh pigment films. Original geometry, transforms and materials untouched.
"""
import bpy,math,random,hashlib,json,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1]
OUT=R/'art/studies/rust-189/fasteners'
def rank(s):return int(hashlib.sha256(s.encode()).hexdigest()[:14],16)
def head(n):return n.startswith(('Captive panel screw','Hex head','073 hex anchor','Splice bolt','133 Enclosure securing screw')) or(n.startswith('145 ')and'hex head'in n)
def plate(n):return n.startswith(('073 anchor backplate','Y splice'))
def reset_splice_materials(scene):
 """Remove superseded137 broad rust from both splice plates and their bolt heads."""
 changed=[];cache={}
 for host_name in ['Architecture | gangway_single_Y_8m','Architecture | gangway_single_Y_8m.001']:
  for ob in scene.objects[host_name].instance_collection.all_objects:
   if not ob.name.startswith(('Y splice','Splice bolt')):continue
   for slot in ob.material_slots:
    old=slot.material
    if not old or old.name.startswith('189 Clean splice base'):continue
    if old.name not in cache:
     m=old.copy();m.name='189 Clean splice base | '+old.name
     cor=next((n for n in m.node_tree.nodes if n.label=='137 Finite fastener corrosion over retained steel'),None)
     em=next((n for n in m.node_tree.nodes if n.type=='EMISSION'),None)
     if cor and em and cor.inputs[1].is_linked:m.node_tree.links.new(cor.inputs[1].links[0].from_socket,em.inputs['Color'])
     cache[old.name]=m
    slot.link='OBJECT';slot.material=cache[old.name];changed.append(ob.name)
 return sorted(set(changed))
def apply(scene):
 start=time.time();OUT.mkdir(parents=True,exist_ok=True);reset_objects=reset_splice_materials(scene)
 if bpy.data.collections.get('189 Fastener corrosion films'):raise RuntimeError('189 fasteners already applied')
 dg=bpy.context.evaluated_depsgraph_get();rows=[];plates=[]
 for i in dg.object_instances:
  o=i.object
  if o.type!='MESH' or o.hide_render or not(head(o.name)or plate(o.name)):continue
  mat=i.matrix_world.copy();bb=[Vector(v)for v in o.bound_box];lo=Vector([min(p[k]for p in bb)for k in range(3)]);hi=Vector([max(p[k]for p in bb)for k in range(3)]);center=mat@((lo+hi)/2);axis=min(range(3),key=lambda k:hi[k]-lo[k]);normal=mat.to_3x3()@Vector([int(k==axis)for k in range(3)]);normal.normalize()
  if normal.dot(scene.camera.matrix_world.translation-center)<0:normal=-normal
  bounds=[mat@p for p in bb];radius=sorted([(mat.to_3x3()@Vector([hi[k]-lo[k]if j==k else 0 for j in range(3)])).length for k in range(3)])[1]/2
  key=o.name+'|'+str(i.parent.name if i.parent else '')+'|'+','.join('%.5f'%p for p in center)
  uv=world_to_camera_view(scene,scene.camera,center)
  row=dict(key=key,name=o.name,parent=i.parent.name if i.parent else None,center=center,n=normal,r=radius,bounds=bounds,matrix=mat,source=o.original,uv=list(uv),is_instance=i.is_instance)
  (plates if plate(o.name)else rows).append(row)
 # Same actual receiver and same instance, never arbitrary neighboring screws.
 for p in plates:
  p['bolts']=[b for b in rows if b['parent']==p['parent'] and ((b['name'].startswith('073 hex anchor')and p['name'].startswith('073 anchor'))or(b['name'].startswith('Splice bolt')and p['name'].startswith('Y splice')))]
 plates=[p for p in plates if len(p['bolts'])==4]
 # Four deterministic dispersed camera-facing plates, two per alley side.
 heavy=[p for p in plates if p['name'].startswith('Y splice') and p['center'].x<0][:1];quota=round(len(plates)*.1)
 for side in [-1,1]:
  pool=[p for p in plates if p['center'].x*side>0 and 0<p['uv'][0]<1 and 0<p['uv'][1]<1 and p['uv'][2]>0]
  pool=[p for p in pool if p not in heavy];pool.sort(key=lambda p:p['center'].y)
  for fraction in [.1,.6]:
   if pool and sum(p['center'].x*side>0 for p in heavy)<2:
    idx=min(len(pool)-1,int(len(pool)*fraction));p=pool.pop(idx)
    if p not in heavy:heavy.append(p)
 selection_path=OUT/'heavy-plate-selection.json'
 if selection_path.exists():
  keys=json.loads(selection_path.read_text())['keys'];heavy=[next(p for p in plates if p['key']==key)for key in keys]
 heavy=heavy[:quota]
 for p in sorted(plates,key=lambda p:rank(p['key'])):
  if len(heavy)>=quota:break
  if p not in heavy:heavy.append(p)
 forced={b['key'] for p in heavy for b in p['bolts']};target=round(len(rows)*.8);selected=set(forced)
 for b in sorted(rows,key=lambda p:rank(p['key'])):
  if len(selected)>=target:break
  selected.add(b['key'])
 C=bpy.data.collections.new('189 Fastener corrosion films');scene.collection.children.link(C)
 # Pigment films intentionally excluded from Freestyle, which otherwise outlines every tiny fleck.
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if not ls.select_by_collection:
    ls.select_by_collection=True;ls.collection=C;ls.collection_negation='EXCLUSIVE'
 # Common pigment shader: spatially attached vertex alpha and naturally lit oxide palette.
 m=bpy.data.materials.new('189 Fastener oxide translucent pigment');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 at=n.new('ShaderNodeVertexColor');at.layer_name='Oxide';df=n.new('ShaderNodeBsdfDiffuse');l.new(at.outputs['Color'],df.inputs['Color']);tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(at.outputs['Alpha'],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(df.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0]);m.surface_render_method='DITHERED';m.diffuse_color=(.15,.045,.018,1)
 verts=[];faces=[];colors=[];audit=[];casts=0
 current_receivers=[]
 def receivers(points,nn,own=None):
  found={}
  if own:
   ob,mat=own;found[(ob.name,tuple(round(v,6)for row in mat for v in row))]=(ob,mat,mat.inverted())
  for p in points:
   hit,loc,no,fi,ob,ma=scene.ray_cast(dg,p+nn*.18,-nn,distance=.45)
   if hit:
    key=(ob.name,tuple(round(v,6)for row in ma for v in row));found[key]=(ob.evaluated_get(dg),ma.copy(),ma.inverted())
  return list(found.values())
 def cast(p,n,allowed=None):
  nonlocal casts
  casts+=1;best=None;dist=1e9;origin=p+n*.18
  for ob,ma,inv in current_receivers:
   if allowed and ob.name!=allowed:continue
   direct=inv.to_3x3()@(-n);scale=direct.length;direct.normalize()
   hit,loc,no,fi=ob.ray_cast(inv@origin,direct,distance=.45*scale)
   if not hit:continue
   loc=ma@loc;no=(inv.transposed().to_3x3()@no).normalized();d=(loc-origin).length
   if no.dot(n)<.60 or d>=dist:continue
   best=loc+n*.00065;dist=d
  return best
 def tri(points,cs,normal,allowed=None):
  qs=[cast(p,normal,allowed)for p in points]
  if any(p is None for p in qs):return False
  # No polygon may bridge a receiver step or leave its local supporting plane.
  if max((qs[k]-points[k]).length for k in range(len(qs)))>.17:return False
  residual=[(qs[k]-points[k]).dot(normal)for k in range(len(qs))]
  if max(residual)-min(residual)>.022:return False
  ix=len(verts);verts.extend(qs);faces.append(tuple(range(ix,ix+len(qs))));colors.extend(cs);return True
 palette=[(.105,.027,.016),(.18,.055,.025),(.24,.090,.038)]
 for bi,b in enumerate(rows):
  if bi%500==0:print('189 bolt progress',bi,'/',len(rows),flush=True)
  if b['key']not in selected:continue
  rng=random.Random(rank(b['key']));p=b['center'];nn=b['n'];down=Vector((0,0,-1));down-=nn*down.dot(nn)
  if down.length<.1:down=nn.cross(Vector((1,0,0)))
  down.normalize();across=down.cross(nn).normalized();rr=b['r'];heavybolt=b['key']in forced
  length=rr*rng.uniform(3.0,10.0)*(1.55 if heavybolt else 1);current_receivers=receivers([p,p+across*rr*1.5,p-across*rr*1.5,p+down*(rr+length*.4),p+down*(rr+length)],nn,(b['source'].evaluated_get(dg),b['matrix']));width=rr*rng.uniform(.18,.42);shade=palette[rng.randrange(len(palette))];before=len(faces)
  # Unequal tapered runoff, starting at the seating edge rather than disconnected below.
  for j in range(7):
   t0=j/7;t1=(j+1)/7;w0=width*(1-t0)**.7;w1=width*(1-t1)**.7+.0003;drift=rr*rng.uniform(-.12,.12)
   q0=p+down*(rr*.7+length*t0)+across*drift;q1=p+down*(rr*.7+length*t1)+across*drift*.8
   a0=.62*(1-t0)**.75;a1=.62*(1-t1)**.75
   tri([q0-across*w0,q0+across*w0,q1+across*w1,q1-across*w1],[(*shade,a0),(*shade,a0),(*shade,a1),(*shade,a1)],nn)
  # Broken oxide at the washer root, not identical complete concentric rings.
  for j in range(12):
   if rng.random()>(.88 if heavybolt else .57):continue
   a=j*math.tau/12;aa=(j+1)*math.tau/12;ri=rr*.72;ro=rr*rng.uniform(1.12,1.52 if heavybolt else 1.29)
   pts=[p+(across*math.cos(t)+down*math.sin(t))*r for t,r in [(a,ri),(a,ro),(aa,ro),(aa,ri)]]
   tri(pts,[(*palette[0],rng.uniform(.4,.78))]*4,nn)
  fallback=False
  if len(faces)==before:
   # A fully occluded head still receives an actual surface-bound spot. Using its
   # own native face avoids attributing an invisible head's rust to an occluder.
   obj=b['source'].evaluated_get(dg);nm=b['matrix'].to_3x3().inverted().transposed()
   eligible=[f for f in obj.data.polygons if (nm@f.normal).normalized().dot(nn)>.6]
   if eligible:
    face=max(eligible,key=lambda f:f.area);q=[b['matrix']@obj.data.vertices[k].co for k in face.vertices];c=sum(q,Vector())/len(q);normal=(nm@face.normal).normalized();ix=len(verts)
    verts.extend(c.lerp(v,.62)+normal*.00065 for v in q);faces.append(tuple(range(ix,ix+len(q))));colors.extend([(*palette[0],.55)]*len(q));fallback=True
  audit.append(dict(fallback_head_spot=fallback,key=b['key'],name=b['name'],parent=b['parent'],center=list(p),projection=b['uv'],radius=rr,length=length,heavy_plate_bolt=heavybolt,faces=len(faces)-before))
 # Continuous receiver-fitted plate washes, with shared vertex values and a
 # soft multiscale boundary. No independent per-cell coloring or binary stencil.
 heavy_audit=[]
 for p in heavy:
  rng=random.Random(rank(p['key'])+189);nn=p['n'];down=Vector((0,0,-1));down-=nn*down.dot(nn);down.normalize();across=down.cross(nn).normalized();cen=p['center'];us=[(v-cen).dot(across)for v in p['bounds']];vs=[(v-cen).dot(down)for v in p['bounds']];u0,u1=min(us),max(us);v0,v1=min(vs),max(vs);N=64;fraction=rng.uniform(.32,.70)
  phases=[rng.uniform(0,math.tau)for _ in range(4)]
  def field(u,v):
   return math.sin(u*7+phases[0])+.65*math.sin(v*6+u*3+phases[1])+.28*math.sin(u*19-v*11+phases[2])+.11*math.sin(u*43+v*29+phases[3])+v*.2
  samples=sorted(field((x+.5)/N,(y+.5)/N)for y in range(N)for x in range(N));threshold=samples[min(len(samples)-1,round(len(samples)*(1-fraction)))]
  def color(u,v):
   f=field(u,v);t=max(0,min(1,(f-threshold+.07)/.38));alpha=.74*t*t*(3-2*t)
   # Subtle warm variation stays continuous across adjoining grid cells.
   warm=.5+.5*math.sin(u*8+v*6+phases[1]);shade=tuple(palette[1][k]*(1-.3*warm)+palette[2][k]*.3*warm for k in range(3))
   return (*shade,alpha)
  current_receivers=[(p['source'].evaluated_get(dg),p['matrix'],p['matrix'].inverted())];nface=len(faces);footprint=0;alpha_area=0
  for y in range(N):
   for x in range(N):
    coords=[(x/N,y/N),((x+1)/N,y/N),((x+1)/N,(y+1)/N),(x/N,(y+1)/N)];cs=[color(u,v)for u,v in coords]
    if max(c[3]for c in cs)<.008:continue
    pp=[cen+across*(u0+(u1-u0)*u)+down*(v0+(v1-v0)*v)for u,v in coords]
    if tri(pp,cs,nn,p['name']):
     mean_alpha=sum(c[3]for c in cs)/4;alpha_area+=mean_alpha;footprint+=mean_alpha>.05
  heavy_audit.append(dict(key=p['key'],name=p['name'],parent=p['parent'],projection=p['uv'],center=list(cen),target_area_fraction=fraction,rendered_grid_fraction=footprint/(N*N),alpha_weighted_area=alpha_area/(N*N),native_faces=len(faces)-nface,grid_resolution=N,mask='Continuous shared-vertex field with smooth ragged boundary; footprint measured at mean vertex alpha > .05',all_four_bolts_selected=all(b['key']in selected for b in p['bolts']),all_four_bolts_applied=all(any(a['key']==b['key'] and a['faces']>0 for a in audit)for b in p['bolts'])))
 mesh=bpy.data.meshes.new('189 Receiver fitted oxide meshes');mesh.from_pydata(verts,[],faces);mesh.materials.append(m);mesh.update();attr=mesh.color_attributes.new(name='Oxide',type='FLOAT_COLOR',domain='POINT')
 for v,c in zip(attr.data,colors):v.color=c
 ob=bpy.data.objects.new('189 Scene-wide fastener rust films',mesh);C.objects.link(ob);ob['189 purpose']='Occurrence-specific receiver-conforming bolt runoff and plate washes; no black contour';ob.visible_shadow=False
 result=dict(version=189,references=['RS-01','RS-02','UP-03','UCL-01'],eligible_bolt_occurrences=len(rows),selected_bolt_occurrences=len(selected),selected_fraction=len(selected)/len(rows),eligible_four_bolt_plates=len(plates),heavy_plate_count=len(heavy),heavy_plate_fraction=len(heavy)/len(plates),bolts=audit,heavy_plates=heavy_audit,zero_film_bolts=sum(a['faces']==0 for a in audit),applied_bolt_occurrences=sum(a['faces']>0 for a in audit),fallback_head_spots=sum(a['fallback_head_spot']for a in audit),source_geometry_changed=False,source_materials_changed=True,changed_objects=reset_objects,material_change_scope='Private Y splice plate/bolt copies bypass obsolete137 corrosion; old graphs retained',new_objects=[ob.name],new_collections=[C.name],vertices=len(verts),faces=len(faces),raycasts=casts,seconds=time.time()-start,excluded_shanks_and_washers='Paired with actual head; not counted twice',selection='Exact logical occurrence quota, includes all heavy-plate bolts; deterministic seeded ordering; heavy plates distributed by side/depth',limitations='Logical occurrence coverage includes subpixel/off-frame or occluded fasteners. Receiver rejection reported; no guarantee all selected films visible from game camera.')
 result['shader_correction']=fix_film_shader(scene)
 (OUT/'audit.json').write_text(json.dumps(result,indent=2));return result
def append_payload(scene):
 """Fast integration of the frozen, ray-fitted188-native pigment layer."""
 path=OUT/'candidate.blend';reset_splice_materials(scene)
 if bpy.data.collections.get('189 Fastener corrosion films'):raise RuntimeError('189 fasteners already applied')
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):
  dst.collections=['189 Fastener corrosion films']
 C=dst.collections[0];scene.collection.children.link(C)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if not ls.select_by_collection:
    ls.select_by_collection=True;ls.collection=C;ls.collection_negation='EXCLUSIVE'
 fix_film_shader(scene)
 return json.loads((OUT/'audit.json').read_text())

def ensure_film_ink_exclusion(scene):
 """Preserve existing line filters while excluding native pigment films."""
 films=set(bpy.data.collections['189 Fastener corrosion films'].all_objects);rows=[]
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   base=ls.collection if ls.select_by_collection else None
   if base is None and ls.select_by_collection and ls.collection_negation=='EXCLUSIVE' and ls.name in ('Selective geometry contours','050 Fine structural creases'):
    base=bpy.data.collections['110 Existing ink exclusions']
   if ls.select_by_collection and ls.collection_negation=='INCLUSIVE':
    included=set(base.all_objects)if base else set()
    if films & included:raise RuntimeError('Pigment unexpectedly included in ink group '+ls.name)
    rows.append(dict(view_layer=vl.name,line_set=ls.name,mode='INCLUSIVE',films_excluded=True,preserved_filter=base.name if base else None));continue
   previous=set(base.all_objects)if base else set()
   if not films<=previous:
    name='189 Ink exclusion union | '+(base.name if base else vl.name+' '+ls.name)
    union=bpy.data.collections.get(name)or bpy.data.collections.new(name);union.use_fake_user=True
    for ob in previous|films:
     if ob.name not in union.objects:union.objects.link(ob)
    ls.select_by_collection=True;ls.collection=union;ls.collection_negation='EXCLUSIVE'
   if ls.collection.name.startswith('189 Ink exclusion union'):ls.collection.use_fake_user=True
   current=set(ls.collection.all_objects)
   assert previous<=current and films<=current
   rows.append(dict(view_layer=vl.name,line_set=ls.name,mode='EXCLUSIVE',films_excluded=True,preserved_prior_object_count=len(previous),filter=ls.collection.name,filter_object_count=len(current)))
 return rows

def fix_film_shader(scene):
 """189b: restore oxide hue in the scene's deliberately non-PBR light model.
 Shared native pigment only; geometry, occurrence quota and vertex alpha retained.
 """
 m=bpy.data.materials.get('189 Fastener oxide translucent pigment')
 if not m:raise RuntimeError('189 fastener pigment material absent')
 n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 at=n.new('ShaderNodeVertexColor');at.layer_name='Oxide';at.label='Retained per-vertex oxide pigments and tapered alpha'
 diffuse=n.new('ShaderNodeBsdfDiffuse');diffuse.inputs['Color'].default_value=(.7,.7,.7,1)
 rgb=n.new('ShaderNodeShaderToRGB');l.new(diffuse.outputs[0],rgb.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(rgb.outputs[0],bw.inputs[0])
 response=n.new('ShaderNodeMapRange');response.clamp=True;response.label='189b Bounded actual-light response, oxide never collapses to black';response.inputs['From Min'].default_value=0;response.inputs['From Max'].default_value=.9;response.inputs['To Min'].default_value=.48;response.inputs['To Max'].default_value=1.2;l.new(bw.outputs[0],response.inputs[0])
 lit=n.new('ShaderNodeMixRGB');lit.blend_type='MULTIPLY';lit.inputs[0].default_value=1;l.new(at.outputs['Color'],lit.inputs[1]);l.new(response.outputs[0],lit.inputs[2])
 emission=n.new('ShaderNodeEmission');l.new(lit.outputs[0],emission.inputs['Color'])
 geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.label='189b Fine porous oxide edges, subordinate to bolt and gravity placement';noise.inputs['Scale'].default_value=210;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.72;l.new(geo.outputs['Position'],noise.inputs['Vector'])
 porous=n.new('ShaderNodeMapRange');porous.clamp=True;porous.inputs['From Min'].default_value=.26;porous.inputs['From Max'].default_value=.70;porous.inputs['To Min'].default_value=.28;porous.inputs['To Max'].default_value=1;l.new(noise.outputs['Fac'],porous.inputs[0])
 alpha=n.new('ShaderNodeMath');alpha.operation='MULTIPLY';l.new(at.outputs['Alpha'],alpha.inputs[0]);l.new(porous.outputs[0],alpha.inputs[1])
 transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(alpha.outputs[0],mix.inputs[0]);l.new(transparent.outputs[0],mix.inputs[1]);l.new(emission.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0]);m.surface_render_method='DITHERED'
 m['189b correction']='Bounded actual-light oxide + native emission; fine alpha porosity; retained vertex palette, physical geometry and quotas'
 filters=ensure_film_ink_exclusion(scene)
 return dict(ink_filters=filters,material=m.name,geometry_changed=False,vertex_alpha_preserved=True,light_response=[.48,1.2],porosity_scale=210,porosity_alpha_range=[.28,1],reason='Pure diffuse pigment appeared near black under existing stylized foreground illumination')

if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-188/scene.blend'));print(json.dumps({k:v for k,v in apply(bpy.context.scene).items()if k not in ('bolts','heavy_plates')},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'candidate.blend'))
