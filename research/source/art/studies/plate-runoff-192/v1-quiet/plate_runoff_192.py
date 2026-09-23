"""192: two-layer rusty-water ribbons on every already-treated anchor plate head.
Source189 source geometry, materials, film/wash geometry and head quota are preserved.
"""
import bpy,json,math,random,time,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import bolt_rust_189 as base
OUT=R/'art/studies/plate-runoff-192'

def exclude_ink(scene,films):
 rows=[]
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   old=ls.collection if ls.select_by_collection else None
   if ls.select_by_collection and ls.collection_negation=='INCLUSIVE':
    assert not films & set(old.all_objects);rows.append(dict(line_set=ls.name,mode='INCLUSIVE',film_excluded=True,filter=old.name));continue
   existing=set(old.all_objects)if old else set()
   name='192 Ink exclusion union | '+(old.name if old else vl.name)
   if films<=existing:new=old
   else:
    new=bpy.data.collections.get(name)or bpy.data.collections.new(name);new.use_fake_user=True
    for ob in existing|films:
     if ob.name not in new.objects:new.objects.link(ob)
    ls.select_by_collection=True;ls.collection=new;ls.collection_negation='EXCLUSIVE'
   assert existing<=set(new.all_objects) and films<=set(new.all_objects)
   rows.append(dict(line_set=ls.name,mode='EXCLUSIVE',film_excluded=True,filter=new.name,old_count=len(existing),new_count=len(new.all_objects),fake_user=new.use_fake_user))
 return rows

def apply(scene):
 start=time.time();OUT.mkdir(parents=True,exist_ok=True)
 if bpy.data.collections.get('192 Plate rusty water'):raise RuntimeError('192 already applied')
 retained=json.loads((R/'art/studies/rust-189/fasteners/audit.json').read_text());selected={r['key']for r in retained['bolts']};dg=bpy.context.evaluated_depsgraph_get();plates=[];heads=[]
 for inst in dg.object_instances:
  o=inst.object
  if o.type!='MESH' or o.hide_render or not(base.plate(o.name)or o.name.startswith(('073 hex anchor','Splice bolt'))):continue
  if inst.parent and inst.parent.hide_render:continue
  mat=inst.matrix_world.copy();bb=[Vector(v)for v in o.bound_box];lo=Vector([min(v[k]for v in bb)for k in range(3)]);hi=Vector([max(v[k]for v in bb)for k in range(3)]);p=mat@((lo+hi)/2);axis=min(range(3),key=lambda k:hi[k]-lo[k]);normal=(mat.to_3x3()@Vector([int(k==axis)for k in range(3)])).normalized()
  if normal.dot(scene.camera.matrix_world.translation-p)<0:normal=-normal
  key=o.name+'|'+str(inst.parent.name if inst.parent else '')+'|'+','.join('%.5f'%v for v in p)
  dimensions=[(mat.to_3x3()@Vector([hi[k]-lo[k]if j==k else 0 for j in range(3)])).length for k in range(3)]
  row=dict(key=key,name=o.name,parent=inst.parent.name if inst.parent else None,p=p,n=normal,mat=mat,inv=mat.inverted(),ob=o.original,r=sorted(dimensions)[1]/2,bounds=[mat@v for v in bb])
  (plates if base.plate(o.name)else heads).append(row)
 C=bpy.data.collections.new('192 Plate rusty water');scene.collection.children.link(C)
 verts=[];faces=[];colors=[];records=[];reject=0
 material=bpy.data.materials['189 Fastener oxide translucent pigment']
 for p in plates:
  bolts=[b for b in heads if b['parent']==p['parent']and((p['name'].startswith('Y splice')and b['name'].startswith('Splice bolt'))or(p['name'].startswith('073 anchor')and b['name'].startswith('073 hex anchor')))]
  if len(bolts)!=4:continue
  nn=p['n'];down=Vector((0,0,-1));down-=nn*down.dot(nn);down.normalize();across=down.cross(nn).normalized();vs=[(v-p['p']).dot(down)for v in p['bounds']];bottom=max(vs);top=min(vs);H=bottom-top
  bolt_v=[(b['p']-p['p']).dot(down)for b in bolts];split=(min(bolt_v)+max(bolt_v))/2
  def hit(q,offset):
   origin=q+nn*.20;ld=p['inv'].to_3x3()@(-nn);scale=ld.length;ld.normalize();ok,loc,no,fi=p['ob'].evaluated_get(dg).ray_cast(p['inv']@origin,ld,distance=.45*scale)
   if not ok:return None
   no=(p['inv'].transposed().to_3x3()@no).normalized()
   if no.dot(nn)<.20:return None
   return p['mat']@loc+nn*offset
  for b in bolts:
   if b['key']not in selected:continue
   rng=random.Random(base.rank(b['key'])+192);lower=(b['p']-p['p']).dot(down)>split;count=1 if rng.random()<.56 else 2;entry=dict(key=b['key'],plate=p['key'],plate_height=H,bolt_center=list(b['p']),lower_bolt=lower,line_count=count,lines=[])
   for line in range(count):
    offset=b['r']*(rng.uniform(-.32,.32)if count==1 else [-.38,.35][line]+rng.uniform(-.06,.06));root=b['p']+across*offset+down*(b['r']*.80);start_v=(root-p['p']).dot(down);remaining=bottom-start_v-.0012
    target=.15*H*rng.uniform(.93,1.07)*(1 if line==0 else .80);length=remaining if lower else min(target,remaining)
    if length<=.001:continue
    half=H*rng.uniform(.0105,.0140)*(1 if line==0 else .8);drift=rng.uniform(-.15,.15)*half;ph=rng.uniform(0,math.tau);prior=len(faces);prior_vertex=len(verts)
    # Outer diluted wash and a narrower oxide-rich stream share the same origin.
    for role,width_factor,pigment,peak,zoff in [('soft outer wash',1,(.225,.072,.033),.70,.00135),('narrow oxide core',.34,(.135,.034,.020),.90,.00165)]:
     grid=[];N=16;cross=[-1,-.5,0,.5,1]
     for j in range(N+1):
      t=j/N;taper=.20+.80*(1-t)**.8;fade=(1-t)**.7 if not lower else .18+.82*(1-t)**.7;row=[]
      shift=drift*math.sin(t*math.pi)+half*.055*math.sin(t*7+ph)*t
      for x in cross:
       q=root+down*(length*t)+across*(shift+x*half*width_factor*taper);at=hit(q,zoff)
       edge=(1-abs(x))**.65;alpha=peak*fade*edge
       row.append((at,(*pigment,alpha)))
      grid.append(row)
     for j in range(N):
      for k in range(4):
       values=[grid[j][k],grid[j][k+1],grid[j+1][k+1],grid[j+1][k]]
       if any(v[0]is None for v in values):reject+=1;continue
       ix=len(verts);verts.extend(v[0]for v in values);colors.extend(v[1]for v in values);faces.append(tuple(range(ix,ix+4)))
    entry['lines'].append(dict(root=list(root),end=list(root+down*length),length=length,length_as_plate_height=length/H,nominal_target=.15*H,lower_reaches_bottom=lower and abs(start_v+length-(bottom-.0012))<1e-5,bottom_clearance=bottom-(start_v+length),outer_width=2*half,core_width=2*half*.34,geometry_bottom_clearance=bottom-max((v-p['p']).dot(down)for v in verts[prior_vertex:])if len(verts)>prior_vertex else None,faces=len(faces)-prior))
   records.append(entry)
 mesh=bpy.data.meshes.new('192 Layered plate water ribbons');mesh.from_pydata(verts,[],faces);mesh.materials.append(material);mesh.update();attr=mesh.color_attributes.new(name='Oxide',type='FLOAT_COLOR',domain='POINT')
 for v,c in zip(attr.data,colors):v.color=c
 ob=bpy.data.objects.new('192 Plate bolt rusty-water overlays',mesh);C.objects.link(ob);ob.visible_shadow=False;ob['192 runoff']='Two translucent receiver-bound layers; fine core with fading outer wash; clip to physical plate bottom'
 ink=exclude_ink(scene,{ob});heavy={b['key']for p in retained['heavy_plates']for b in retained['bolts']if b['heavy_plate_bolt']};affected={r['key']for r in records}
 result=dict(version=192,source='art/studies/rust-189/scene.blend',references=['RS-02','UCL-01','UP-03'],technique='145/146 continuous outer rusty-water wash plus narrower overlaid core; native source-derived ribbons',eligible_plates=len(plates),eligible_plate_heads=len(heads),treated_plate_heads=len(records),original_scene_head_quota=retained['applied_bolt_occurrences'],heavy_plate_heads_preserved=len(heavy&affected),all_heavy_plate_heads_covered=heavy<=affected,one_line_heads=sum(r['line_count']==1 for r in records),two_line_heads=sum(r['line_count']==2 for r in records),actual_lines=sum(len(r['lines'])for r in records),rejected_surface_quads=reject,zero_geometry_heads=sum(not any(l['faces'] for l in r['lines'])for r in records),all_lower_runs_reach_plate_bottom=all(l['lower_reaches_bottom'] and l['geometry_bottom_clearance']is not None and l['geometry_bottom_clearance']<=.02*r['plate_height']for r in records if r['lower_bolt']for l in r['lines']),new_objects=[ob.name],new_collections=[C.name],changed_original_objects=[],changed_original_materials=[],original189_films_preserved=True,ink_filters=ink,vertices=len(verts),faces=len(faces),seconds=time.time()-start,plates=records)
 (OUT/'diagnostic.json').write_text(json.dumps(result,indent=2))
 print({k:result[k]for k in ['treated_plate_heads','heavy_plate_heads_preserved','all_heavy_plate_heads_covered','zero_geometry_heads','all_lower_runs_reach_plate_bottom']},flush=True)
 assert result['all_heavy_plate_heads_covered'] and result['all_lower_runs_reach_plate_bottom'] and not result['zero_geometry_heads']
 (OUT/'audit.json').write_text(json.dumps(result,indent=2));return result
def append_payload(scene):
 if bpy.data.collections.get('192 Plate rusty water'):raise RuntimeError('192 already applied')
 with bpy.data.libraries.load(str(OUT/'candidate.blend'),link=False) as (src,dst):dst.collections=['192 Plate rusty water']
 C=dst.collections[0];scene.collection.children.link(C)
 common=bpy.data.materials['189 Fastener oxide translucent pigment']
 for ob in C.all_objects:
  if ob.type=='MESH':ob.data.materials[0]=common
 filters=exclude_ink(scene,set(C.all_objects));result=json.loads((OUT/'audit.json').read_text());result['integration_ink_filters']=filters;return result

if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rust-189/scene.blend'));result=apply(bpy.context.scene);print(json.dumps({k:v for k,v in result.items()if k!='plates'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'candidate.blend'))
