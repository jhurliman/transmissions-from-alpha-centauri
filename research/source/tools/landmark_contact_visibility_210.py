"""Reclip only the dedicated baked landmark GP against current external opaque geometry.
Reusable after landmark transforms or new foreground construction; no scale dependency.
"""
import bpy,math,json,sys
from pathlib import Path
from collections import Counter
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_contact_clip_169 import snapshot,digest,run
NAME='110 Landmark contact ink'


def material_occludes(mat):
 if mat is None or not mat.use_nodes:return True
 # Follow only active output dependencies; disconnected legacy nodes do not classify surfaces.
 pending=[];seen=set()
 for n in mat.node_tree.nodes:
  if n.type=='OUTPUT_MATERIAL' and n.is_active_output:
   if n.inputs['Volume'].is_linked:return False
   pending.extend(link.from_node for link in n.inputs['Surface'].links)
 while pending:
  n=pending.pop()
  if n.as_pointer() in seen:continue
  seen.add(n.as_pointer())
  if n.type in {'BSDF_TRANSPARENT','BSDF_GLASS','BSDF_REFRACTION','VOLUME_PRINCIPLED','VOLUME_SCATTER','VOLUME_ABSORPTION'}:return False
  if n.type=='BSDF_PRINCIPLED':
   alpha=n.inputs.get('Alpha');trans=n.inputs.get('Transmission Weight')
   if alpha and (alpha.is_linked or alpha.default_value<.999):return False
   if trans and (trans.is_linked or trans.default_value>.001):return False
  if n.type=='GROUP' and n.node_tree:
   for out in n.node_tree.nodes:
    if out.type=='GROUP_OUTPUT' and out.is_active_output:
     pending.extend(link.from_node for sock in out.inputs for link in sock.links)
  pending.extend(link.from_node for sock in n.inputs for link in sock.links)
 return True


def external_tree(scene):
 visible_objects=set()
 def visit(c):
  if c.hide_render:return
  visible_objects.update(c.objects)
  for child in c.children:visit(child)
 visit(scene.collection)
 instance_matrices={}
 def instance_leaves(c,transform,ancestors):
  if c in ancestors or c.hide_render:return
  ancestors=ancestors|{c}
  for obj in c.objects:
   if obj.hide_render:continue
   world=transform@obj.matrix_world
   instance_matrices.setdefault(obj,[]).append(world)
   if obj.instance_type=='COLLECTION' and obj.instance_collection:
    instance_leaves(obj.instance_collection,world@Matrix.Translation(-obj.instance_collection.instance_offset),ancestors)
  for child in c.children:instance_leaves(child,transform,ancestors)
 for root in visible_objects:
  if not root.hide_render and root.instance_type=='COLLECTION' and root.instance_collection:
   instance_leaves(root.instance_collection,root.matrix_world@Matrix.Translation(-root.instance_collection.instance_offset),set())
 members=set(bpy.data.collections['110 Coliseum detailed front ruin'].all_objects);members.add(bpy.data.objects[NAME]);dg=bpy.context.evaluated_depsgraph_get();vs=[];ts=[];owners=[];counts=Counter();skipped=Counter();mat_cache={}
 for inst in dg.object_instances:
  ob=inst.object;orig=ob.original
  if orig in members or(inst.parent and inst.parent.original in members):continue
  if ob.hide_render or ob.type not in {'MESH','CURVE','SURFACE','FONT','META'}:continue
  if inst.is_instance:
   allowed_paths=instance_matrices.get(orig,[])
   if not any(max(abs(a-b) for row1,row2 in zip(m,inst.matrix_world) for a,b in zip(row1,row2))<.0001 for m in allowed_paths):skipped['no_render_visible_instance_path']+=1;continue
  elif orig not in visible_objects:skipped['no_visible_collection_path']+=1;continue
  low=ob.name.lower()
  if any(t in low for t in ['haze','dust volume','cloud','sky','corrosion film','runoff film']):skipped['atmosphere_or_film']+=1;continue
  mats=[sl.material for sl in ob.material_slots];allowed=[]
  for mat in mats:
   key=mat.as_pointer()if mat else 0
   if key not in mat_cache:mat_cache[key]=material_occludes(mat)
   allowed.append(mat_cache[key])
  if allowed and not any(allowed):skipped['transparent_material']+=1;continue
  me=ob.to_mesh()
  if not me:continue
  me.calc_loop_triangles();tris=[t for t in me.loop_triangles if not allowed or t.material_index>=len(allowed)or allowed[t.material_index]]
  if tris:
   off=len(vs);vs.extend(inst.matrix_world@v.co for v in me.vertices);ts.extend(tuple(off+i for i in t.vertices)for t in tris);owners.extend([orig.name]*len(tris));counts[orig.name]+=len(tris)
  ob.to_mesh_clear()
 assert ts,'No external opaque occluder triangles'
 return BVHTree.FromPolygons(vs,ts,all_triangles=True),owners,{'instances_or_objects':len(counts),'triangles':len(ts),'vertices':len(vs),'skipped':dict(skipped),'occluder_triangle_counts':dict(counts)}


def apply(scene,audit_path=None,max_pixel_step=.5,gap_m=.02):
 gp=bpy.data.objects[NAME];before=snapshot(gp);M=gp.matrix_world.copy();camera=scene.camera.matrix_world.translation.copy();tree,owners,inventory=external_tree(scene);source_digest=digest(before);other_gp={o.name:digest(snapshot(o))for o in scene.objects if o.type=='GREASEPENCIL'and o!=gp}
 audit={'object':NAME,'source_digest':source_digest,'source_points':sum(len(st['point']['position'])for rec in before for st in rec['strokes']),'source_strokes':sum(len(rec['strokes'])for rec in before),'gap_m':gap_m,'max_projected_sample_spacing_full_resolution_pixels':max_pixel_step,'midpoint_checks':True,'transition_bisection_steps':16,'gp_flags':{'show_in_front':gp.show_in_front,'stroke_depth_order':gp.data.stroke_depth_order,'modifiers':[m.type for m in gp.modifiers]},'scope':'Only dedicated110GP; external opaque evaluated instances. Existing landmark self-contact style is retained.','occluder_inventory':inventory,'ray_queries':0,'hidden_queries':0,'hidden_owner_counts':{},'examples':[],'changes':[],'unchanged_strokes':0,'fully_removed_strokes':0,'split_or_trimmed_strokes':0,'cyclic_strokes_checked':0,'replay_requirement':'Start from the unclipped source drawing; retained source datablock has fake user. Reapplying cannot restore newly revealed strokes.','limitation':'Clipping cannot reconstruct newly exposed contact strokes absent from the original camera-dependent bake.'}
 owner_counts=Counter();payload=[];all_expected={};original_matrices={o.name:o.matrix_world.copy()for o in scene.objects}
 def visible(world):
  audit['ray_queries']+=1;d=world-camera;length=d.length
  if length<=gap_m:return True
  hit=tree.ray_cast(camera,d/length,length-gap_m)
  if hit[0]is None:return True
  gap=length-hit[3];owner=owners[hit[2]];audit['hidden_queries']+=1;owner_counts[owner]+=1
  if len(audit['examples'])<100:audit['examples'].append({'world':list(world),'occluder':owner,'gap_m':gap})
  return False
 def pixels(p):
  q=world_to_camera_view(scene,scene.camera,p);return Vector((q.x*scene.render.resolution_x,(1-q.y)*scene.render.resolution_y))
 for rec in before:
  records=[];unchanged=[]
  for si,original in enumerate(rec['strokes']):
   positions=original['point'].get('position',[]);n=len(positions)
   if n<2:unchanged.append(original);audit['unchanged_strokes']+=1;continue
   cyclic=bool(original['curve'].get('cyclic',False));audit['cyclic_strokes_checked']+=int(cyclic)
   st={'point':{k:list(v)+([v[0]]if cyclic else[])for k,v in original['point'].items()},'curve':dict(original['curve'])}
   if cyclic:st['curve']['cyclic']=False
   world=[M@Vector(p)for p in st['point']['position']];screen=[pixels(p)for p in world];intervals=[];max_t=len(world)-1
   for seg,(a,b)in enumerate(zip(world,world[1:])):
    pieces=max(1,int(math.ceil((screen[seg+1]-screen[seg]).length/max_pixel_step)))
    # Midpoints halve the bound and catch islands with equally classified endpoints.
    pieces*=2;previous=visible(a)
    for j in range(pieces):
     ta=j/pieces;tb=(j+1)/pieces;current=visible(a.lerp(b,tb));lo,hi=ta,tb
     if previous!=current:
      for _ in range(16):
       mid=(lo+hi)/2
       if visible(a.lerp(b,mid))==previous:lo=mid
       else:hi=mid
      edge=(lo+hi)/2
      if previous:intervals.append((seg+ta,seg+edge))
      else:intervals.append((seg+edge,seg+tb))
     elif previous:intervals.append((seg+ta,seg+tb))
     previous=current
   merged=[]
   for a,b in intervals:
    if b-a<1e-10:continue
    if merged and a-merged[-1][1]<1e-8:merged[-1]=(merged[-1][0],b)
    else:merged.append((a,b))
   if len(merged)==1 and merged[0][0]<1e-9 and abs(merged[0][1]-max_t)<1e-9:
    unchanged.append(original);audit['unchanged_strokes']+=1;continue
   runs=[run(st,a,b)for a,b in merged]
   if cyclic and len(runs)>1 and merged[0][0]<1e-9 and abs(merged[-1][1]-max_t)<1e-9:
    first,last=runs[0],runs[-1];joined={'point':{k:last['point'][k]+first['point'][k][1:]for k in first['point']},'curve':dict(last['curve'])};runs=[joined]+runs[1:-1]
   if cyclic:
    for r in runs:r['curve']['cyclic']=False
   row={'stroke':si,'visible_intervals':merged,'runs':runs};records.append(row)
   audit['changes'].append({'layer':rec['layer'],'frame':rec['frame'],'stroke':si,'source_points':n,'retained_runs':len(runs),'visible_intervals':merged,'cyclic_source':cyclic})
   if runs:audit['split_or_trimmed_strokes']+=1
   else:audit['fully_removed_strokes']+=1
  if records:payload.append((rec,records));all_expected[(rec['layer'],rec['frame'])]=unchanged
 # Private drawing; all unchanged source strokes and all their attributes remain exact.
 if payload:
  gp.data.use_fake_user=True
  gp.data=gp.data.copy()
  for rec,records in payload:
   dr=gp.data.layers[rec['layer']].frames[rec['frame']].drawing;dr.remove_strokes(indices=[r['stroke']for r in records]);basepoint=sum(len(st.points)for st in dr.strokes);basecurve=len(dr.strokes);runs=[r for row in records for r in row['runs']]
   if runs:
    dr.add_strokes(sizes=[len(r['point']['position'])for r in runs]);off=basepoint
    for j,st in enumerate(runs):
     for k,values in st['point'].items():
      attr=dr.attributes[k];prop=rec['schema'][k]['prop']
      for i,value in enumerate(values):setattr(attr.data[off+i],prop,value)
     for k,value in st['curve'].items():setattr(dr.attributes[k].data[basecurve+j],rec['schema'][k]['prop'],value)
     off+=len(st['point']['position'])
 after=snapshot(gp)
 for rec in after:
  key=(rec['layer'],rec['frame'])
  if key in all_expected:assert rec['strokes'][:len(all_expected[key])]==all_expected[key],'Untouched contact attributes changed'
 assert all(digest(snapshot(bpy.data.objects[n]))==d for n,d in other_gp.items()),'Other GP changed'
 assert all(max(abs(x-y)for a,b in zip(m,bpy.data.objects[n].matrix_world)for x,y in zip(a,b))<1e-6 for n,m in original_matrices.items()),'Object transform changed during visibility clipping'
 audit['result_digest']=digest(after);audit['result_points']=sum(len(st['point']['position'])for rec in after for st in rec['strokes']);audit['result_strokes']=sum(len(rec['strokes'])for rec in after);audit['hidden_owner_counts']=dict(owner_counts);audit['untouched_stroke_attributes_exact']=True;audit['other_GP_owners_unchanged']=list(other_gp);audit['all_object_transforms_unchanged']=True
 if audit_path:Path(audit_path).write_text(json.dumps(audit,indent=2))
 return audit


def restore_unclipped(scene,source_digest):
 """Restore preserved source drawing by digest before changing foreground occluders.
 The GP object's already approved transform is untouched.
 """
 gp=bpy.data.objects[NAME];current=gp.data;matrix=gp.matrix_world.copy();before=digest(snapshot(gp))
 if before==source_digest:return {'already_unclipped':True,'source_digest':source_digest,'drawing':current.name}
 found=None
 try:
  for drawing in bpy.data.grease_pencils:
   if drawing==current or not drawing.use_fake_user:continue
   gp.data=drawing
   if digest(snapshot(gp))==source_digest:found=drawing;break
 finally:gp.data=found if found else current
 if found is None:raise RuntimeError('Unclipped landmark contact source missing; load original saved source before new visibility clipping')
 assert gp.matrix_world==matrix
 return {'restored':True,'source_digest':source_digest,'previous_digest':before,'drawing':found.name,'transform_unchanged':True}
