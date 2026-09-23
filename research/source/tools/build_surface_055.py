import bpy,json,bmesh,math
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-055'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-054/scene.blend'));s=bpy.context.scene
# Reuse only helper definitions, no scene-changing execution.
src=(R/'tools/build_finish_054.py').read_text();exec(src[src.index('def rgb('):src.index('# Sky:')])
changed=[]
# Native long 45-degree nose, replacing the plain folded fascia cross-section.
for o in list(bpy.data.objects):
 if o.type!='MESH' or not o.name.startswith('Folded fascia'):continue
 vs=o.data.vertices;lo=[min(v.co[i] for v in vs) for i in range(3)];hi=[max(v.co[i] for v in vs) for i in range(3)];x0,y0,z0=lo;x1,y1,z1=hi;d=.09
 profile=[(y0,z0),(y0,z1-d),(y0+d,z1),(y1+d,z1),(y1+d,z0)];N=len(profile);verts=[(x,y,z) for x in [x0,x1] for y,z in profile];faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
 me=bpy.data.meshes.new('055 45 degree folded fascia');me.from_pydata(verts,[],faces)
 for mat in o.data.materials:me.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o.data=me
 for mod in o.modifiers:
  if mod.type=='BEVEL':mod.width=.003;mod.segments=1
 changed.append(o.name)
# Finer wear carried as color: broad low-contrast grain plus sparse larger marks.
for g in bpy.data.node_groups:
 if not g.name.startswith('051 Facade'):continue
 nt=g;out=next(n for n in nt.nodes if n.type=='GROUP_OUTPUT');base=out.inputs[0].links[0].from_socket;geo=nt.nodes.new('ShaderNodeNewGeometry')
 def noise(scale):
  n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=3;n.inputs['Roughness'].default_value=.75;nt.links.new(geo.outputs['Position'],n.inputs['Vector']);return n.outputs['Fac']
 grain=op(nt,'ADD',op(nt,'MULTIPLY',noise(72),.22),.87);color=mix(nt,base,(.62,.58,.56,1),op(nt,'MULTIPLY',op(nt,'SUBTRACT',1,grain),.75),'MULTIPLY')
 gate=op(nt,'GREATER_THAN',noise(1.8),.57);chips=op(nt,'MULTIPLY',gate,op(nt,'GREATER_THAN',noise(9),.66));color=mix(nt,color,(.22,.19,.22,1),op(nt,'MULTIPLY',chips,.80),'MULTIPLY')
 # Thin, locally connected scar fragments follow distorted cellular boundaries.
 distort=nt.nodes.new('ShaderNodeTexNoise');distort.inputs['Scale'].default_value=11;distort.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],distort.inputs[0]);v=nt.nodes.new('ShaderNodeVectorMath');v.operation='SCALE';v.inputs['Scale'].default_value=.10;nt.links.new(distort.outputs['Color'],v.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';nt.links.new(geo.outputs['Position'],add.inputs[0]);nt.links.new(v.outputs[0],add.inputs[1]);cell=nt.nodes.new('ShaderNodeTexVoronoi');cell.feature='DISTANCE_TO_EDGE';cell.inputs['Scale'].default_value=5.5;nt.links.new(add.outputs[0],cell.inputs['Vector'])
 scar=op(nt,'MULTIPLY',op(nt,'LESS_THAN',cell.outputs['Distance'],.022),op(nt,'GREATER_THAN',noise(2.6),.65));color=mix(nt,color,(.25,.21,.23,1),op(nt,'MULTIPLY',scar,.70),'MULTIPLY');nt.links.new(color,out.inputs[0])
# Brighter existing pipe highlight bands.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree
 for n in nt.nodes:
  if n.type=='MIX_RGB' and not n.inputs[2].is_linked and tuple(round(x,5) for x in n.inputs[2].default_value)==tuple(round(x,5) for x in rgb('#b8b5ae')):
   if n.inputs[0].is_linked:
    weight=n.inputs[0].links[0].from_node
    if weight.type=='MATH' and weight.operation=='MULTIPLY':weight.inputs[1].default_value=.36
# Copy only the materials on selected architectural features; no global facade glow.
cache={};objects=[]
for o in list(bpy.data.objects):
 if o.type!='MESH':continue
 kind='fascia' if o.name.startswith('Folded fascia') else 'kick' if o.name.startswith('Continuous frame-to-frame kick') else 'corner' if o.name.startswith(('Folded corner cap','Gallery structural blade')) else None
 if not kind:continue
 if kind=='corner' and o.name.startswith('Gallery structural blade'):
  for mod in o.modifiers:
   if mod.type=='BEVEL':mod.width=.035;mod.segments=1
  changed.append(o.name)
 for slot in o.material_slots:
  old=slot.material
  if not old or not old.use_nodes:continue
  key=(old.name,kind)
  if key not in cache:
   m=old.copy();m.name='055 '+kind+' | '+old.name;nt=m.node_tree;em=next((n for n in nt.nodes if n.type=='EMISSION' and n.outputs[0].is_linked),None)
   if not em:continue
   base=em.inputs['Color'].links[0].from_socket;geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Normal'],xyz.inputs[0])
   if kind=='fascia':mask=op(nt,'MULTIPLY',op(nt,'GREATER_THAN',xyz.outputs['Z'],.65),op(nt,'LESS_THAN',xyz.outputs['Z'],.77))
   elif kind=='kick':mask=op(nt,'GREATER_THAN',xyz.outputs['Z'],.16)
   else:
    mask=op(nt,'MULTIPLY',op(nt,'GREATER_THAN',op(nt,'ABSOLUTE',xyz.outputs['X'],0),.35),op(nt,'GREATER_THAN',op(nt,'ABSOLUTE',xyz.outputs['Y'],0),.35))
   noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=13;noise.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],noise.inputs[0]);mask=op(nt,'MULTIPLY',mask,op(nt,'GREATER_THAN',noise.outputs['Fac'],.35))
   # Lift local pigment, retaining warm versus cool material identity.
   pale=mix(nt,base,rgb('#e4c4a5'),.35 if kind=='fascia' else .22)
   nt.links.new(mix(nt,base,pale,mask),em.inputs['Color']);cache[key]=m
  slot.material=cache[key]
 objects.append({'object':o.name,'kind':kind})
# Isolate a useful frame detail in addition to the full game view.
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));(O/'audit.json').write_text(json.dumps({'geometry_changes':changed,'highlight_objects':objects,'fascia_chamfer_m':.09,'fascia_chamfer_degrees':45,'pipe_highlight_mix':.36,'camera':list(s.camera.location)},indent=2));bpy.ops.render.render(write_still=True)
