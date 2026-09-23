import bpy,math,random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-009';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-008/scene.blend'));s=bpy.context.scene;random.seed(909)
# Ambient comparison used a float-equality mistake in pass8; correct it explicitly.
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND' and n.inputs[1].default_value<.9:n.inputs[1].default_value=1.7
# Broad neutral fill gives readable wall planes without gloss.
bpy.ops.object.light_add(type='AREA',location=(0,-7,10));o=bpy.context.object;o.name='Broad diffuse facade fill';o.data.energy=4200;o.data.shape='DISK';o.data.size=16;o.rotation_euler=(Vector((0,12,6))-o.location).to_track_quat('-Z','Y').to_euler()
for o in bpy.data.objects:
 if o.name.startswith('Distant dust volume'):
  for n in o.data.materials[0].node_tree.nodes:
   if n.type=='VOLUME_SCATTER':n.inputs['Density'].default_value=.0045
# Native procedural sparse flaking: clustered color masks, no bitmap or screen coordinates.
for name in ['Painted lavender steel','Sun-worn warm cladding','Exposed weathered steel']:
 m=bpy.data.materials[name];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');old=p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].is_linked else None
 base=m.diffuse_color
 tex=n.new('ShaderNodeTexCoord');macro=n.new('ShaderNodeTexNoise');macro.inputs['Scale'].default_value=2.6;micro=n.new('ShaderNodeTexNoise');micro.inputs['Scale'].default_value=37;micro.inputs['Detail'].default_value=3
 l.new(tex.outputs['Object'],macro.inputs['Vector']);l.new(tex.outputs['Object'],micro.inputs['Vector'])
 mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY';l.new(macro.outputs['Fac'],mult.inputs[0]);l.new(micro.outputs['Fac'],mult.inputs[1]);th=n.new('ShaderNodeMath');th.operation='GREATER_THAN';th.inputs[1].default_value=.42;l.new(mult.outputs[0],th.inputs[0])
 mix=n.new('ShaderNodeMixRGB');l.new(th.outputs[0],mix.inputs[0]);mix.inputs[1].default_value=base;mix.inputs[2].default_value=(.12,.077,.048,1)
 if old:l.new(old,mix.inputs[1])
 l.new(mix.outputs[0],p.inputs['Base Color'])
# Reproportion far ruins: reduce each mesh around its own center, not toward world origin.
for o in bpy.data.objects:
 if o.name.startswith('Fractured city remnant'):
  pts=o.data.vertices;cx=sum(v.co.x for v in pts)/len(pts);cy=sum(v.co.y for v in pts)/len(pts)
  for v in pts:v.co.x=cx+(v.co.x-cx)*.6;v.co.z*=.65
 if o.name.startswith('Exposed remnant spine'):o.hide_render=True
C=bpy.data.collections.new('009 Designed foreground girders');s.collection.children.link(C)
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);C.objects.link(ob);ob.data.materials.append(m);return ob
metal=bpy.data.materials['Exposed weathered steel'];rust=bpy.data.materials['Oxidized edges'];dark=bpy.data.materials['Foreground dark steel']
def bar(name,a,b,w,d,m):
 delta=Vector(b)-Vector(a);vs=[(i*w/2,j*d/2,k*delta.length/2) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];o=mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m);o.location=(Vector(a)+Vector(b))/2;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();return o
# Flat torn metal pieces give foreground overlap; unlike simple faceted stones they have thickness and folds.
for i,(x,y,z,sz,angle) in enumerate([(-3.7,-8.9,.35,1.2,.4),(-2.2,-9.2,.25,1.3,-.3),(-.7,-9.5,.12,1.2,.5),(.8,-9.6,.18,1.1,-.2),(2.3,-9.2,.25,1.5,.4),(4.0,-8.9,.4,1.2,-.4)]):
 vs=[(-.6,-.4,0),(.6,-.4,0),(.6,.35,0),(.2,.5,.12),(-.1,.27,.15),(-.5,.45,.03)]
 ob=mesh('Torn foreground cladding',[(a*sz,b*sz,c*sz) for a,b,c in vs],[tuple(range(6))],metal if i%2 else rust);ob.location=(x,y,z);ob.rotation_euler=(.25,angle,angle);mod=ob.modifiers.new('Real torn plate thickness','SOLIDIFY');mod.thickness=.045
for i in range(18):
 x=random.uniform(-5,5);y=random.uniform(-9.6,-8.8);a=Vector((x,y,.1));b=a+Vector((random.uniform(-.8,.8),random.uniform(-.2,.3),random.uniform(.35,.85)))
 web=bar('Broken thin steel web',a,b,.04,.21,metal);side=(b-a).cross(Vector((0,0,1))).normalized()*.11
 for sign in [-1,1]:bar('Girder parallel flange',a+side*sign,b+side*sign,.07,.035,rust)
# Extra rubble overlaps the middle-distance bases, never the actor area.
for i in range(90):
 x=random.uniform(-6,6);y=random.uniform(28,34);a=random.uniform(.22,.6);vs=[(x-a,y-a,0),(x+a,y-a,0),(x+a,y+a,0),(x-a,y+a,0),(x-.3*a,y-.4*a,a),(x+.6*a,y-.3*a,.7*a),(x+.4*a,y+.7*a,.5*a)]
 mesh('Midground overlapping rubble',vs,[(0,1,5,4),(1,2,6,5),(2,3,4,6),(3,0,4),(4,5,6)],metal if i%2 else rust)
s.render.filepath=str(O/'render.png');s.cycles.samples=48;s['stage']='Geometry-only round009'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
