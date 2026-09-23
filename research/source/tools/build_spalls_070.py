import bpy,bmesh,json,random,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-070';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-069/scene.blend'));s=bpy.context.scene;placements=json.loads((R/'art/reviews/xenon-069/placements.json').read_text());col=bpy.data.collections.new('070 editable endpoint spalls');s.collection.children.link(col);audit=[];skipped=[]
for a in placements:
 rng=random.Random(a['seed']+70000)
 if rng.random()>.7:continue
 target=bpy.data.objects[a['part']];host=bpy.data.objects.get(a['host']);world=(host.matrix_world if host else Matrix.Identity(4)) @ target.matrix_world
 center=Vector(a['center']);normal=Vector(a['normal']);f=min(target.data.polygons,key=lambda f:(world@f.center-center).length);n=f.normal.copy();origin=f.center.copy();v=Vector((0,0,1));v-=n*v.dot(n);v.normalize();u=v.cross(n).normalized();vs=[target.data.vertices[i].co for i in f.vertices];umin=min((p-origin).dot(u) for p in vs);umax=max((p-origin).dot(u) for p in vs);vmin=min((p-origin).dot(v) for p in vs);vmax=max((p-origin).dot(v) for p in vs);W=umax-umin;H=vmax-vmin
 paths=json.loads(next((R/'art/reviews/xenon-069').glob('*-'+str(a['seed'])+'-paths.json')).read_text())['paths'];ends=[]
 for path in paths:
  for x,y in [path['points'][0],path['points'][-1]]:
   if min(x,W-x,y,H-y)<.003 and not any(math.dist((x,y),p)<.02 for p in ends):ends.append((x,y))
 rng.shuffle(ends)
 thickness=max(p.co.dot(n) for p in target.data.vertices)-min(p.co.dot(n) for p in target.data.vertices)
 for x,y in ends[:2 if rng.random()<.3 else 1]:
  position=origin+u*(umin+x)+v*(vmin+y)
  radius=min(rng.uniform(.045,.12),min(W,H)*.19);depth=min(rng.uniform(.018,.047),thickness*.30);angle=rng.uniform(0,math.pi);axis=u*math.cos(angle)+v*math.sin(angle);side=n.cross(axis).normalized()
  points=[]
  # A closed convex irregular wedge intersects the existing crack at its actual endpoint.
  for i in range(9):
   theta=2*math.pi*i/9;rr=radius*rng.uniform(.65,1.15);p=position+axis*(math.cos(theta)*rr)+side*(math.sin(theta)*rr*rng.uniform(.5,.8));points.append(p+n*.023);points.append(position+(p-position)*rng.uniform(.25,.65)-n*(depth*rng.uniform(.45,1)))
  me=bpy.data.meshes.new('070 fractured wedge');bm=bmesh.new()
  for p in points:bm.verts.new(p)
  bmesh.ops.convex_hull(bm,input=list(bm.verts));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();c=bpy.data.objects.new('070 endpoint loss | '+target.name,me);col.objects.link(c);c.matrix_world=target.matrix_world.copy();c.hide_render=True;c.hide_set(True)
  idx=next(i for i,m in enumerate(target.data.materials) if m and m.name.startswith('069 Projected fracture'))
  for m in target.data.materials:c.data.materials.append(m)
  for face in c.data.polygons:face.material_index=idx
  mod=target.modifiers.new('070 localized endpoint spall','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.context.view_layer.update();ev=target.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bad=sum(not e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume());bm.free();ev.to_mesh_clear()
  if bad or volume<=0:target.modifiers.remove(mod);skipped.append({'part':target.name,'nonmanifold':bad});continue
  audit.append({'part':target.name,'host':a['host'],'radius_m':radius,'depth_m':depth,'world_position':list(world@position),'nonmanifold':bad})
(O/'spalls.json').write_text(json.dumps(audit,indent=2));(O/'skipped.json').write_text(json.dumps(skipped,indent=2));print('SPALLS',len(audit),flush=True);s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=2880;s.render.resolution_y=2160;s.render.use_border=True;s.render.use_crop_to_border=True
for label,x0,x1,y0,y1 in [('left',0,.36,.27,.91),('right',.62,1,.22,.95)]:
 s.render.border_min_x=x0;s.render.border_max_x=x1;s.render.border_min_y=y0;s.render.border_max_y=y1;s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True)
