"""133: connected partial building shells bridge approved alley blocks to distant city.
Additive deterministic native geometry; leaves all existing systems unchanged.
"""
import bpy,bmesh,math,random
from mathutils import Vector

def apply(scene):
 if bpy.data.collections.get('133 Ruined transition structures'):raise RuntimeError('Use fresh source')
 C=bpy.data.collections.new('133 Ruined transition structures');scene.collection.children.link(C);rng=random.Random(13307);rows=[]
 def rgba(h):
  a=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in a)+(1,)
 def material(name,h):
  m=bpy.data.materials.new('133 '+name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
  def node(t):return n.new(t)
  out=node('ShaderNodeOutputMaterial');em=node('ShaderNodeEmission');geo=node('ShaderNodeNewGeometry');dot=node('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.38,-.67,.64);l.new(geo.outputs['Normal'],dot.inputs[0]);ramp=node('ShaderNodeValToRGB');ramp.label='133 Broken-building shade families';ramp.color_ramp.interpolation='EASE';base=rgba(h);ramp.color_ramp.elements[0].position=-.35;ramp.color_ramp.elements[0].color=tuple(v*.42 for v in base[:3])+(1,);ramp.color_ramp.elements[1].position=.55;ramp.color_ramp.elements[1].color=base;l.new(dot.outputs['Value'],ramp.inputs[0])
  # Native finite patches with quiet interiors, much weaker than structural shades.
  noise=node('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.0;noise.inputs['Detail'].default_value=2.;l.new(geo.outputs['Position'],noise.inputs['Vector']);gr=node('ShaderNodeValToRGB');gr.color_ramp.elements[0].position=.40;gr.color_ramp.elements[0].color=(.56,.53,.62,1);gr.color_ramp.elements[1].position=.62;gr.color_ramp.elements[1].color=(1,1,1,1);l.new(noise.outputs['Fac'],gr.inputs[0]);mul=node('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=.38;l.new(ramp.outputs['Color'],mul.inputs[1]);l.new(gr.outputs[0],mul.inputs[2])
  ao=node('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=1.7;dark=node('ShaderNodeMixRGB');dark.blend_type='MULTIPLY';dark.inputs[0].default_value=.45;l.new(mul.outputs[0],dark.inputs[1]);l.new(ao.outputs['Color'],dark.inputs[2]);l.new(dark.outputs[0],em.inputs['Color']);l.new(em.outputs[0],out.inputs['Surface']);return m
 mats=[material('weathered violet masonry','62586c'),material('cool fractured concrete','595c6c'),material('muted warm masonry','695d68')];core=material('exposed warm-gray aggregate','79675e');metal=material('broken structural iron','34313e')
 def mesh(name,vs,fs,m):
  me=bpy.data.meshes.new('133 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free()
  if bad:raise RuntimeError((name,bad))
  me.materials.append(m);me.materials.append(core);o=bpy.data.objects.new('133 '+name,me);C.objects.link(o);o['133 ruin bridge']=True
  for p in me.polygons:
   if p.normal.z>.25:p.material_index=1
  return o
 def box(name,center,dims,m):
  v=[tuple(center[k]+sg[k]*dims[k]/2 for k in range(3))for sg in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
  return mesh(name,v,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m)
 def wall(name,origin,along,width,height,thickness,m):
  # Quiet surviving courses alternate with clustered broken teeth, never a regular saw.
  top=[(0,height*.61),(.12*width,height*.81),(.19*width,height*.77),(.24*width,height),(.57*width,height),(.62*width,height*.90),(.68*width,height*.92),(.76*width,height*.62),(.82*width,height*.58),(width,height*.36)]
  poly=[(0,-.12),(width,-.12)]+list(reversed(top));u=Vector(along);n=Vector((-u.y,u.x,0));base=Vector(origin);vs=[base+u*a+Vector((0,0,z))+n*d for d in [-thickness/2,thickness/2]for a,z in poly];N=len(poly);fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
  o=mesh(name,vs,fs,m)
  # Real apertures through surviving structure, intentionally irregular/restricted to high bay.
  if height>3.4:
   for j in range(1 if width<4.8 else 2):
    at=width*(.30+j*.22);zz=min(min(2.65,height*.48)-.90,1.45);cc=base+u*at+Vector((0,0,zz));cut=box(name+' temporary aperture',cc,(thickness*4,1.1,1.45)if abs(u.y)>.5 else(1.1,thickness*4,1.45),m)
    mod=o.modifiers.new('True broken window opening','BOOLEAN');mod.object=cut;mod.operation='DIFFERENCE';mod.solver='EXACT';bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
  bevel=o.modifiers.new('Small broken masonry edge','BEVEL');bevel.width=.035;bevel.segments=1
  return o
 def slab(name,points,thick,m):
  vs=[Vector(p)+Vector((0,0,z))for z in [-thick/2,thick/2]for p in points];N=len(points);return mesh(name,vs,[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)],m)
 def beam(name,a,b,width,m):
  a,b=Vector(a),Vector(b);o=box(name,(a+b)*.5,(width,width,(b-a).length),m);center=(a+b)*.5
  # Mesh is world-coordinate; rotate vertices about center.
  rot=(b-a).to_track_quat('Z','Y').to_matrix()
  for v in o.data.vertices:v.co=center+rot@(v.co-center)
  return o
 # Six roofless partial buildings; taller middle remnants conceal distant tower feet.
 specs=[(-1,8.6,33.6,4.5,3.5,4.2),(-1,9.4,38.0,5.0,5.7,3.4),(-1,8.1,44.1,5.5,7.4,4.0),(1,9.2,33.4,4.0,2.7,3.5),(1,10.0,37.4,5.7,6.1,4.4),(1,8.6,44.0,5.2,4.8,3.4)]
 for i,(side,x,y,w,h,depth) in enumerate(specs):
  x*=side;m=mats[i%3];prefix=('L'if side<0 else'R')+str(i)
  front=wall(prefix+' standing street wall',(x,y,0),(0,1,0),w,h,.30,m)
  back=wall(prefix+' attached return',(x,y+w-.16,0),(side,0,0),depth,h*.61,.30,m)
  if i in (0,2,4):
   wall(prefix+' broken camera-facing cross wall',(x,y+1.15,0),(-side,0,0),2.2,h*.75,.36,m)
  # Partial floor shares two supported wall edges, broken out toward the open corner.
  level=min(2.65,h*.48)
  slab(prefix+' surviving floor',[(x,y+w-.25,level),(x+side*depth*.80,y+w-.25,level),(x+side*depth*.68,y+w-2.1,level),(x+side*.9,y+w-2.6,level),(x,y+w-2.3,level)],.24,m)
  # Fallen floor fragment leans back into this same structural remnant; grounded end.
  slab(prefix+' collapsed floor',[(x-side*1.7,y+.3,.12),(x-side*.2,y+.6,.15),(x+side*.7,y+2.5,level),(x-side*.2,y+2.8,level*.84)],.22,m)
  beam(prefix+' surviving floor rib',(x+.02*side,y+w-2.25,level-.15),(x+side*depth*.70,y+w-2.25,level-.15),.18,metal)
  # One broken uprighting pier belongs to the return, not a scatter pebble.
  box(prefix+' remnant return pier',(x+side*depth*.84,y+w-.15,h*.20),( .42,.48,h*.4),m)
  # Three low broad rubble plates gather at the wall base and remain outside central route.
  for j in range(3):
   xx=x-side*rng.uniform(.2,1.25);yy=y+rng.uniform(.1,w);L=rng.uniform(1.1,2.1);W=rng.uniform(.6,1.2);z=rng.uniform(.12,.28)
   slab(prefix+f' grounded broken plate{j}',[(xx-L/2,yy-W/2,z),(xx+L*.45,yy-W*.35,z+.06),(xx+L*.30,yy+W*.52,z+.25),(xx-L*.50,yy+W*.40,z+.12)],.24,m)
  rows.append({'id':prefix,'wall_origin':[x,y,0],'wall_width':w,'height':h,'return_depth':depth,'real_apertures':h>3.4})
 for o in C.objects:
  if o.type=='MESH':
   bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
   if bad:raise RuntimeError('Nonclosed result '+o.name)
 return {'collection':C.name,'buildings':rows,'objects':len(C.objects),'source_geometry_changed':False,'placement_y':[33.4,49.6],'minimum_road_clearance_x':min(abs(v.co.x) for o in C.objects if o.type=='MESH' for v in o.data.vertices),'construction':'Thick connected roofless L-shells with real window voids, attached surviving floor remnants and grounded collapsed slabs; no generic pebble scatter.'}
