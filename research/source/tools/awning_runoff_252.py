"""Gravity-projected vent runoff, private to the original utility awning."""
import bpy, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from entrance_weathering_227 import Paint

def apply(scene):
 root=scene.objects['right_horizontal_utility']; src=root.instance_collection
 roofs=[o for o in src.objects if o.name.startswith('Utility broad rake')]
 lips=[o for o in src.objects if o.name.startswith('Vent head and sill') and min((root.matrix_world@o.matrix_world@Vector(v)).z for v in o.bound_box)<7]
 vs=[];fs=[]
 for o in roofs:
  M=root.matrix_world@o.matrix_world; offset=len(vs)
  vs.extend(M@v.co for v in o.data.vertices);fs.extend(tuple(offset+i for i in p.vertices)for p in o.data.polygons)
 bvh=BVHTree.FromPolygons(vs,fs)
 events=[];apertures=[];rng=random.Random(251)
 for j,o in enumerate(sorted(lips,key=lambda o:o.name)):
  pts=[root.matrix_world@o.matrix_world@Vector(v)for v in o.bound_box]
  x=min(v.x for v in pts);za=min(v.z for v in pts);lo=min(v.y for v in pts)+.18;hi=max(v.y for v in pts)-.18
  apertures.append((lo,hi))
  for k in range(6 if j==0 else 9):
   y=lo+(hi-lo)*(k+rng.uniform(.25,.75))/(6 if j==0 else 9)
   hit,normal,_,dist=bvh.ray_cast(Vector((x,y,za)),Vector((0,0,-1)))
   assert hit is not None
   g=Vector((0,0,-1));down=(g-normal*g.dot(normal)).normalized()
   events.append({'vent':o.name,'origin':[x,y,za],'impact':list(hit),'fall_m':dist,'downslope':list(down),'width':rng.uniform(.055,.14),'strength':rng.uniform(.68,.98),'drift':rng.uniform(-.035,.035)})
 private=bpy.data.collections.new('252 Private vent runoff awning');private.use_fake_user=True;private.instance_offset=src.instance_offset
 changes=[]
 for o in src.objects:
  if o not in roofs and not o.name.startswith('Utility projecting edge'):private.objects.link(o);continue
  q=o.copy();private.objects.link(q)
  for sl in q.material_slots:
   base=sl.material;m=base.copy();m.name='252 Vent runoff | '+base.name;p=Paint(m);op=p.op
   em=next(n for n in p.n if n.type=='EMISSION');old=em.inputs['Color'].links[0].from_socket
   geo=p.node('ShaderNodeNewGeometry','World gravity runoff');sep=p.node('ShaderNodeSeparateXYZ','world axes');p.l.new(geo.outputs['Position'],sep.inputs[0]);x,y,z=sep.outputs
   aperture=0
   for lo,hi in apertures:
    aperture=op('MAXIMUM',aperture,op('MULTIPLY',p.remap(y,lo,lo+.04),p.remap(y,hi-.04,hi,1,0)))
   # Gate inherited directional weathering without changing its base pigment.
   for inherited in list(p.n):
    if inherited.type=='GROUP' and inherited.node_tree and 'Chromatic seam-fed runoff' in inherited.node_tree.name:
     strength=inherited.inputs['Strength'];original=strength.links[0].from_socket if strength.is_linked else strength.default_value
     p.put(op('MULTIPLY',original,aperture),strength)
   coarse=p.noise(p.vec(op('MULTIPLY',x,3),op('MULTIPLY',y,7),op('MULTIPLY',z,2)),1,2)
   grit=p.noise(geo.outputs['Position'],39,2.4)
   mask=0;impact=0
   for e in events:
    ix,iy,iz=e['impact'];t=op('MULTIPLY',op('SUBTRACT',ix,x),2)
    center=op('ADD',iy,op('ADD',op('MULTIPLY',t,e['drift']),op('MULTIPLY',op('SUBTRACT',coarse,.5),.065)))
    d=op('ABSOLUTE',op('SUBTRACT',y,center));w=op('MULTIPLY',e['width'],p.remap(t,0,2,1,.48))
    trail=op('MULTIPLY',p.remap(d,op('MULTIPLY',w,.25),w,1,0),p.remap(t,-.03,.10))
    trail=op('MULTIPLY',trail,p.remap(coarse,.20,.72,.72,1))
    mask=op('MAXIMUM',mask,op('MULTIPLY',trail,e['strength']))
    dd=op('ADD',op('DIVIDE',op('MULTIPLY',d,d),e['width']**2*2.8),op('DIVIDE',op('MULTIPLY',t,t),.15**2))
    impact=op('MAXIMUM',impact,p.remap(dd,.1,1.8,1,0))
   mask=op('MAXIMUM',mask,op('MULTIPLY',impact,.52));mask=op('MULTIPLY',mask,p.remap(grit,.2,.8,.7,1))
   mask=op('MULTIPLY',mask,aperture)
   dark=p.mix(1,old,(.07,.08,.11,1),'Cool soot-bearing runoff','MULTIPLY')
   body=p.mix(mask,old,dark,'Vent drips follow physical fall and roof gradient')
   p.l.new(body,em.inputs['Color']);sl.link='OBJECT';sl.material=m
  changes.append(q.name)
 for c in src.children:private.children.link(c)
 root.instance_collection=private
 return {'apertures':apertures,'inherited_runoff_masked':True,'vents':len(lips),'drips':events,'targets':changes,'method':'Vertical ray from outer lower vent sill into actual roof mesh; tangent gravity sets downslope. Narrow irregular material trails from impact to eave. No fluid dynamics claim.','geometry_unchanged':True,'haze_unchanged':True}
