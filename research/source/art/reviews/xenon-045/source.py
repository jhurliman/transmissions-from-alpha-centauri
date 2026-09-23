import bpy,math,json,random,os
from mathutils import Vector
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-045';severity=float(os.environ.get('DAMAGE_SEVERITY','1'));label=os.environ.get('DAMAGE_LABEL','medium');O=O if label=='medium' else O/label;O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-043/scene.blend'));s=bpy.context.scene
host=bpy.data.objects['Architecture | buttress_45'];orig=host.instance_collection;kit=bpy.data.collections.new('DAMAGE | concrete_support_01');kit['part_id']='buttress_45_damage_01';kit['clean_source']=orig.name;kit.asset_mark()
for ob in orig.objects:
 q=ob.copy();kit.objects.link(q)
 if ob.type=='MESH':q.data=ob.data.copy()
host.instance_collection=kit
beam=next(o for o in kit.objects if o.name.startswith('Solid concrete'))
mat=bpy.data.materials.new('045 Exposed concrete aggregate');mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=48;noise.inputs['Detail'].default_value=2
geo=nt.nodes.new('ShaderNodeNewGeometry');nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.07,.045,.034,1);ramp.color_ramp.elements[1].color=(.25,.20,.145,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.009;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
beam.data.materials.append(mat)
dark=bpy.data.materials.new('045 Crack interior');dark.diffuse_color=(.022,.017,.016,1);dark.use_nodes=True;dark.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.022,.017,.016,1)
cutters=bpy.data.collections.new('045 Hidden damage cutters');s.collection.children.link(cutters)
def cut(ob):
 for col in list(ob.users_collection):col.objects.unlink(ob)
 cutters.objects.link(ob);ob.hide_render=True;ob.hide_set(True)
 mod=beam.modifiers.new('Editable spall | '+ob.name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=ob
# Local cutters reference the prefab geometry; host instance transforms all generated damage together.
random.seed(44)
for i,(pos,scale) in enumerate([((.11,1.48-2.65+.045,1.48),(.17,.10,.23)),((-.12,.48-2.65+.025,.48),(.11,.07,.13)),((.22,2.04-2.4,2.04),(.08,.11,.12))]):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=pos);c=bpy.context.object;c.name='Spall cutter '+str(i);c.scale=tuple(v*max(.01,severity) for v in scale)
 for v in c.data.vertices:v.co*=random.uniform(.70,1.23)
 c.data.materials.append(beam.data.materials[0]);c.data.materials.append(mat)
 for f in c.data.polygons:f.material_index=1
 cut(c)
# Tapered crack voids, with dark narrow interiors; actual boolean recesses, not a projected decal.
def curve(name,pts,radius,col,material=None):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=1;d.use_fill_caps=True;d.bevel_depth=radius;d.bevel_resolution=0;p=d.splines.new('POLY');p.points.add(len(pts)-1)
 for i,(v,xyz) in enumerate(zip(p.points,pts)):v.co=(*xyz,1);v.radius=max(.2,1-i/(len(pts)*1.15))
 ob=bpy.data.objects.new(name,d);col.objects.link(ob)
 if material:d.materials.append(material)
 return ob
# Short conditioned random walks, with explicit edge/spall destinations.
# x +/- .20 are the actual side edges of the alley-facing plane.
paths=[]
for seed,a,b in [(451,(-.205,1.24),(.10,1.46)),(452,(.11,1.49),(.205,1.72)),(453,(-.205,.81),(.205,1.01))]:
 rng=random.Random(seed);N=24;walk=0;raw=[0]
 for j in range(1,N):walk=.52*walk+rng.uniform(-.027,.027);raw.append(walk)
 raw.append(0);pts=[]
 for j in range(N+1):
  t=j/N;x=a[0]*(1-t)+b[0]*t;z=a[1]*(1-t)+b[1]*t+raw[j]*math.sin(math.pi*t)
  pts.append((x,z-2.65-.001,z))
 paths.append(pts)
for i,pts in enumerate(paths):
 if severity==0 or (severity<.8 and i>0):continue
 # Monotonic-X ribbon volume avoids self-intersections at tight random-walk bends.
 vs=[];N=len(pts);w=.0045*severity
 for depth in [-.016,.018]:
  for x,y,z in pts:
   for sign in [-1,1]:
    zz=z+sign*w;vs.append((x,zz-2.65+depth,zz))
 fs=[]
 for j in range(N-1):
  a=2*j;b=a+2
  fs.extend([(a,b,b+1,a+1),(a+2*N+1,b+2*N+1,b+2*N,a+2*N),(a,a+2*N,b+2*N,b),(a+1,b+1,b+2*N+1,a+2*N+1)])
 fs.extend([(0,1,2*N+1,2*N),(2*N-2,4*N-2,4*N-1,2*N-1)])
 me=bpy.data.meshes.new('Closed jagged groove');me.from_pydata(vs,[],fs);me.materials.append(beam.data.materials[0]);me.materials.append(mat)
 for f in me.polygons:f.material_index=1
 c=bpy.data.objects.new('Anchored jagged crack cutter '+str(i),me);cutters.objects.link(c);cut(c)
 curve('Recessed anchored fracture '+str(i),[(x,y+.004,z) for x,y,z in pts],.0028*severity,kit,dark)
# An additional corner-wrapping chip intersects both visible planes near a side edge.
if severity>=.8:
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(.195,1.9-2.65+.015,1.9));c=bpy.context.object;c.name='Corner wrap cutter';c.scale=(.085*severity,.065*severity,.12*severity)
 rng=random.Random(455)
 for v in c.data.vertices:v.co*=rng.uniform(.8,1.15)
 c.data.materials.append(beam.data.materials[0]);c.data.materials.append(mat)
 for f in c.data.polygons:f.material_index=1
 cut(c)
for mod in beam.modifiers:mod.show_viewport=False
for mod in beam.modifiers:
 mod.show_viewport=True;bpy.context.view_layer.update()
 assert len(beam.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.polygons)>0,mod.name
kit['damage_rules']=json.dumps({'seed':44,'severity':severity,'variant':label,'cracks':'Three short jagged conditioned walks with edge or spall destinations','spalls':'Three localized faceted Boolean losses','aggregate':'World-space exposed-surface shader','preserve':'Bearing head, footing and primary section remain intact','clean_source':orig.name})
(O/'audit.json').write_text(kit['damage_rules'])
if severity==0:host.instance_collection=orig
s.render.use_freestyle=False;s.render.filepath=str(O/'color-only.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
