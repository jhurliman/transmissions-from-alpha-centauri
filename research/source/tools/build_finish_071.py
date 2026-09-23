import bpy,bmesh,json,random,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-071';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-069/scene.blend'));s=bpy.context.scene;placements=json.loads((R/'art/reviews/xenon-069/placements.json').read_text());col=bpy.data.collections.new('071 editable endpoint spalls');s.collection.children.link(col);audit=[];skipped=[]
for a in placements:
 rng=random.Random(a['seed']+70000)
 if rng.random()>.7:continue
 if len(audit)>=10:break
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
  radius=min(rng.uniform(.16,.30),min(W,H)*.38);depth=min(rng.uniform(.05,.12),thickness*.75);angle=rng.uniform(0,math.pi);axis=u*math.cos(angle)+v*math.sin(angle);side=n.cross(axis).normalized()
  points=[]
  # A closed convex irregular wedge intersects the existing crack at its actual endpoint.
  for i in range(9):
   theta=2*math.pi*i/9;rr=radius*rng.uniform(.65,1.15);p=position+axis*(math.cos(theta)*rr)+side*(math.sin(theta)*rr*rng.uniform(.5,.8));points.append(p+n*.023);points.append(position+(p-position)*rng.uniform(.25,.65)-n*(depth*rng.uniform(.45,1)))
  me=bpy.data.meshes.new('071 fractured wedge');bm=bmesh.new()
  for p in points:bm.verts.new(p)
  bmesh.ops.convex_hull(bm,input=list(bm.verts));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();c=bpy.data.objects.new('071 endpoint loss | '+target.name,me);col.objects.link(c);c.matrix_world=target.matrix_world.copy();c.hide_render=True;c.hide_set(True)
  idx=next(i for i,m in enumerate(target.data.materials) if m and m.name.startswith('069 Projected fracture'))
  for m in target.data.materials:c.data.materials.append(m)
  for face in c.data.polygons:face.material_index=idx
  mod=target.modifiers.new('071 localized endpoint spall','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.context.view_layer.update();ev=target.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bad=sum(not e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume());bm.free();ev.to_mesh_clear()
  if bad or volume<=0:target.modifiers.remove(mod);skipped.append({'part':target.name,'nonmanifold':bad});continue
  audit.append({'part':target.name,'host':a['host'],'radius_m':radius,'depth_m':depth,'world_position':list(world@position),'nonmanifold':bad})
(O/'spalls.json').write_text(json.dumps(audit,indent=2));(O/'skipped.json').write_text(json.dumps(skipped,indent=2));s.render.filepath=str(O/'damage-only.png');bpy.ops.render.render(write_still=True)
# Palette transforms preserve existing shading, streaks and texture, but narrow the
# former blue/rust division to related pigments on all but the selected split building.
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
palettes={
 'left_middle':{'base':'#565e70','weather1':'#5f6471','weather2':'#444d60','spec':'#b7a18d'},
 'left_rear':{'base':'#66616e','weather1':'#716a72','weather2':'#504d5e','spec':'#b7acb6'},
 'right_front':{'base':'#526575','weather1':'#5c6b78','weather2':'#414f60','spec':'#b5c5cd'},
 'right_middle':{'base':'#4c5d7b','weather1':'#566783','weather2':'#3c4b69','spec':'#bbcce8'},
 'right_rear':{'base':'#655c76','weather1':'#726879','weather2':'#4d465e','spec':'#c1b9d1'},
 'warm_road':{'base':'#9f6a58','weather1':'#986755','weather2':'#76504a','spec':'#d9b598'}
}
def mathnode(nt,op,a,b):
 q=nt.nodes.new('ShaderNodeMath');q.operation=op
 for i,z in enumerate([a,b]):
  if isinstance(z,(int,float)):q.inputs[i].default_value=z
  else:nt.links.new(z,q.inputs[i])
 return q.outputs[0]
def mix(nt,a,b,factor,kind='MIX'):
 q=nt.nodes.new('ShaderNodeMixRGB');q.blend_type=kind
 for i,z in [(0,factor),(1,a),(2,b)]:
  if isinstance(z,tuple):q.inputs[i].default_value=z
  elif isinstance(z,(float,int)):q.inputs[i].default_value=z
  else:nt.links.new(z,q.inputs[i])
 return q.outputs[0]
def ratio(new,old):return tuple(a/b for a,b in zip(rgb(new)[:3],rgb(old)[:3]))+(1,)
# Recover building identity for the copied fracture materials from their original part slots.
fracture_family={}
for ob in bpy.data.objects:
 if ob.type!='MESH' or not len(ob.data.materials):continue
 original=ob.data.materials[0]
 if original:
  for mat in ob.data.materials:
   if mat and mat.name.startswith(('069 Projected fracture','064 Projected surface')):fracture_family[mat.name]=original.name
records=[]
for m in list(bpy.data.materials):
 if not m.use_nodes:continue
 identity=fracture_family.get(m.name,m.name)
 family=next((k for k in palettes if k in identity),None)
 if '043 Side-road' in identity:family='warm_road'
 if family is None:continue
 if any(k in identity for k in ['PIP |','DUCT |','steel','Recess |']):continue
 nt=m.node_tree;ems=[n for n in nt.nodes if n.type=='EMISSION' and n.outputs[0].is_linked]
 if not ems:continue
 pal=palettes[family]
 for em in ems:
  if not em.inputs['Color'].is_linked:continue
  old=em.inputs['Color'].links[0].from_socket;sep=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(old,sep.inputs[0])
  warm=mathnode(nt,'GREATER_THAN',mathnode(nt,'SUBTRACT',sep.outputs[0],sep.outputs[2]),.002)
  # Previously rust-painted areas become a nearby weathered version of the base pigment.
  gain=mix(nt,ratio(pal['base'],'#53556b'),ratio(pal['weather1'],'#a57261'),warm)
  out=mix(nt,old,gain,1,'MULTIPLY')
  # A second tone grades darker stains without generating another broad patch mask.
  lum=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(old,lum.inputs[0]);low=mathnode(nt,'MULTIPLY',mathnode(nt,'LESS_THAN',lum.outputs[0],.055),.16)
  out=mix(nt,out,mix(nt,out,ratio(pal['weather2'],pal['base']),1,'MULTIPLY'),low)
  # Tint existing bright highlights only; no new luminous strips are painted in.
  bright=nt.nodes.new('ShaderNodeMapRange');bright.clamp=True;nt.links.new(lum.outputs[0],bright.inputs[0]);bright.inputs['From Min'].default_value=.23;bright.inputs['From Max'].default_value=.42;bright.inputs['To Max'].default_value=.65
  highlight=mix(nt,old,ratio(pal['spec'],'#c5b5aa'),1,'MULTIPLY');out=mix(nt,out,highlight,bright.outputs[0]);nt.links.new(out,em.inputs['Color'])
 records.append({'material':m.name,'family':family})
(O/'palettes.json').write_text(json.dumps({'palettes':palettes,'retained_split':'039 front-left','materials':records},indent=2));s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=2880;s.render.resolution_y=2160;s.render.use_border=True;s.render.use_crop_to_border=True
for label,x0,x1,y0,y1 in [('left',0,.36,.27,.91),('right',.62,1,.22,.95)]:
 s.render.border_min_x=x0;s.render.border_max_x=x1;s.render.border_min_y=y0;s.render.border_max_y=y1;s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True)
