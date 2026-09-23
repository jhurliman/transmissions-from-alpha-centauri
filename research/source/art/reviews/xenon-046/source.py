import bpy,json,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-046');R.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'xenon-045/scene.blend'));s=bpy.context.scene
source=bpy.data.collections['DAMAGE | concrete_support_01']
hidden=bpy.data.collections.new('046 Hidden damage cutters');s.collection.children.link(hidden)
placements=[]
for suffix,dz,flip,low in [('.001',.25,True,True),('.003',-.23,True,False)]:
 host=bpy.data.objects['Architecture | buttress_45'+suffix]
 kit=bpy.data.collections.new('DAMAGE | individual support '+suffix);kit.asset_mark();kit['clean_source']='FAC | buttress_45'
 T=Matrix.Translation((0,dz,dz)) @ Matrix.Diagonal((-1 if flip else 1,1,1,1))
 for original in source.objects:
  if low and original.type=='CURVE' and not original.name.endswith('0'):continue
  q=original.copy();q.data=original.data.copy() if original.data else None;kit.objects.link(q)
  if q.type=='CURVE':
   q.matrix_world=T @ original.matrix_world
   if low:q.data.bevel_depth*=.55
  for mod in list(q.modifiers):
   if mod.type!='BOOLEAN':continue
   old=mod.object
   if low and ('Corner' in old.name or ('crack cutter' in old.name and not old.name.endswith('0'))):q.modifiers.remove(mod);continue
   c=old.copy();c.data=old.data.copy();hidden.objects.link(c);c.matrix_world=T @ old.matrix_world
   if low and 'Spall cutter' in c.name:c.scale*=.55
   c.hide_render=True;c.hide_set(True);mod.object=c
 host.instance_collection=kit
 placements.append({'host':host.name,'position':list(host.location),'severity':'low' if low else 'medium','damage_shift':dz,'mirrored':flip})
# World-space process masks originate at actual component joints.
def op(nt,kind,a,b=None):
 n=nt.nodes.new('ShaderNodeMath');n.operation=kind
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def setup(m):
 nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');g=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Position'],xyz.inputs[0]);return nt,bs,g,xyz
beam=next(o for o in source.objects if o.name.startswith('Solid concrete'))
m=beam.data.materials[0].copy();m.name='046 Bearing-joint concrete runoff';beam.data.materials[0]=m;nt,bs,g,xyz=setup(m)
width=op(nt,'MAXIMUM',op(nt,'SUBTRACT',1,op(nt,'MULTIPLY',op(nt,'ABSOLUTE',op(nt,'SUBTRACT',xyz.outputs['Y'],7.15)),8)),0)
z=op(nt,'MULTIPLY',op(nt,'LESS_THAN',xyz.outputs['Z'],2.46),op(nt,'MAXIMUM',op(nt,'MULTIPLY',op(nt,'SUBTRACT',xyz.outputs['Z'],.5),.50),0))
scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.5,46,.7);nt.links.new(g.outputs['Position'],scale.inputs[0]);noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=2;nt.links.new(scale.outputs[0],noise.inputs['Vector'])
mask=op(nt,'MULTIPLY',op(nt,'MULTIPLY',width,z),op(nt,'MULTIPLY',op(nt,'MAXIMUM',op(nt,'SUBTRACT',noise.outputs['Fac'],.33),0),.85))
mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(mask,mix.inputs[0]);mix.inputs[1].default_value=bs.inputs['Base Color'].default_value;mix.inputs[2].default_value=(.07,.05,.032,1);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
# Independent metal corrosion + localized bright abrasion at housing joints.
changed=[]
for ob in list(s.objects):
 if not ob.instance_collection or abs(ob.location.x-9)>.02 or abs(ob.location.y-8)>.02 or ob.location.z>2.7:continue
 col=bpy.data.collections.new('046 Metal test | '+ob.instance_collection.name)
 for original in ob.instance_collection.objects:
  q=original.copy();col.objects.link(q)
  if q.type!='MESH':continue
  q.data=original.data.copy()
  for slot in q.material_slots:
   if not slot.material or not ('enamel' in slot.material.name or 'steel' in slot.material.name):continue
   m=slot.material.copy();m.name='046 Joint metal wear | '+m.name;slot.material=m;nt,bs,g,xyz=setup(m);base=bs.inputs['Base Color'].default_value[:]
   noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=65;noise.inputs['Detail'].default_value=2;nt.links.new(g.outputs['Position'],noise.inputs['Vector'])
   d=op(nt,'ABSOLUTE',op(nt,'SUBTRACT',xyz.outputs['Z'],1.1));rust=op(nt,'MAXIMUM',op(nt,'SUBTRACT',1,op(nt,'MULTIPLY',d,12)),0)
   rust=op(nt,'MULTIPLY',rust,op(nt,'GREATER_THAN',noise.outputs['Fac'],.54));rust=op(nt,'MULTIPLY',rust,.65)
   blend=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(rust,blend.inputs[0]);blend.inputs[1].default_value=base;blend.inputs[2].default_value=(.22,.075,.025,1)
   d2=op(nt,'MINIMUM',d,op(nt,'ABSOLUTE',op(nt,'SUBTRACT',xyz.outputs['Z'],2.6)));edge=op(nt,'MULTIPLY',op(nt,'LESS_THAN',d2,.025),op(nt,'GREATER_THAN',noise.outputs['Fac'],.52))
   polish=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(edge,polish.inputs[0]);nt.links.new(blend.outputs[0],polish.inputs[1]);polish.inputs[2].default_value=(.34,.32,.29,1);nt.links.new(polish.outputs[0],bs.inputs['Base Color'])
   # Exposed steel is smoother and metallic; porous rust stays matte.
   rough=op(nt,'SUBTRACT',op(nt,'ADD',.57,op(nt,'MULTIPLY',rust,.38)),op(nt,'MULTIPLY',edge,.26));nt.links.new(rough,bs.inputs['Roughness'])
   metallic=op(nt,'MAXIMUM',op(nt,'MULTIPLY',edge,.85),op(nt,'MULTIPLY',op(nt,'SUBTRACT',1,rust),.12));nt.links.new(metallic,bs.inputs['Metallic'])
   bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.0015;nt.links.new(op(nt,'MULTIPLY',rust,noise.outputs['Fac']),bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
 ob.instance_collection=col;changed.append(ob.name)

# Evaluate every changed beam; preserve clean masters and write a reusable baked collection.
audit=[];baked=bpy.data.collections.new('046 Baked support beams')
for host in s.objects:
 if not host.instance_collection or not host.instance_collection.name.startswith('DAMAGE |'):continue
 beam=next(o for o in host.instance_collection.objects if o.name.startswith('Solid concrete'))
 mesh=bpy.data.meshes.new_from_object(beam.evaluated_get(bpy.context.evaluated_depsgraph_get()));bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table()
 unseen=set(bm.verts);components=0
 while unseen:
  stack=[unseen.pop()];components+=1
  while stack:
   for edge in stack.pop().link_edges:
    for v in edge.verts:
     if v in unseen:unseen.remove(v);stack.append(v)
 mesh.calc_loop_triangles();entry={'host':host.name,'triangles':len(mesh.loop_triangles),'components':components,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume()}
 assert entry['components']==1 and entry['non_manifold_edges']==0 and entry['volume']>0,entry
 audit.append(entry);bm.free();ob=bpy.data.objects.new('Baked '+host.name,mesh);baked.objects.link(ob);ob.matrix_world=host.matrix_world
bpy.data.libraries.write(str(R/'baked-beams.blend'),{baked},fake_user=True)
(R/'audit.json').write_text(json.dumps({'beams':audit,'placements':placements,'metal_instances':changed,'clean_supports':2},indent=2))
s.render.use_freestyle=True;s.cycles.samples=32;s.render.filepath=str(R/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(R/'scene.blend'))
bpy.ops.render.render(write_still=True)
# Native camera proofs, no image overlay.
s.render.use_freestyle=False;s.render.resolution_x=1000;s.render.resolution_y=900
for name,loc,target,lens in [('support-detail',(4,3.2,3),(8.3,7.15,1.25),62),('support-pair',(3.6,7.2,3.2),(8.3,12.1,1.2),48),('metal-detail',(5.6,7.8,1.65),(9,8,1.45),60)]:
 s.camera.location=loc;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
