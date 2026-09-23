"""Compact cool weathered footing and physical contact seals at the two entries."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from entrance_weathering_227 import Paint

def apply(scene):
 ob=bpy.data.objects['242 Single concrete footing for left service cluster'];me=ob.data
 # Restrict the foundation to the two ground entries beyond the return loop.
 x0,x1,y0,y1=-9.35,-7.68,8.49,9.48;z0,z1=-.24,.32
 ring=[(x0+.10,y0),(x1-.09,y0),(x1,y0+.075),(x1,8.73),(x1-.045,8.765),(x1,8.81),(x1,9.17),(x1-.035,9.195),(x1,9.23),(x1,y1-.10),(x1-.11,y1),(x0+.06,y1),(x0,y1-.06),(x0,y0+.095)]
 n=len(ring);verts=[(x,y,z)for z in(z0,z1)for x,y in ring];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 new=bpy.data.meshes.new('243 Compact chipped shared footing');new.from_pydata(verts,[],faces);new.update();ob.data=new
 bm=bmesh.new();bm.from_mesh(new);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(new);bm.free()
 for mod in ob.modifiers:
  if mod.type=='BEVEL':mod.width=.008
 m=bpy.data.materials.new('243 Blue-grey stained concrete');m.use_nodes=True;p=Paint(m);p.n.clear()
 geo=p.node('ShaderNodeNewGeometry','world surface');pos=geo.outputs['Position'];sep=p.node('ShaderNodeSeparateXYZ','world axes');p.l.new(pos,sep.inputs[0]);x,y,z=sep.outputs
 broad=p.noise(pos,5.5,3);fine=p.noise(pos,95,2)
 color=p.mix(p.remap(broad,.32,.67),(.115,.14,.215,1),(.21,.23,.31,1),'cool mineral fracture variation')
 # Stronger irregular weathering; granules, low dirt deposits, and vertical runoff.
 color=p.mix(p.remap(fine,.24,.38,.72,0),color,(.027,.032,.05,1),'dark exposed aggregate')
 color=p.mix(p.remap(fine,.64,.77,0,.38),color,(.30,.32,.39,1),'pale aggregate chips')
 basal=p.op('MULTIPLY',p.remap(z,-.02,.27,.60,.05),p.remap(broad,.2,.65,.5,1))
 color=p.mix(basal,color,(.045,.046,.062,1),'ground grime deposit')
 rainpos=p.vec(p.op('MULTIPLY',x,16),p.op('MULTIPLY',y,19),p.op('MULTIPLY',z,1.3));rain=p.noise(rainpos,1,2)
 color=p.mix(p.op('MULTIPLY',p.remap(rain,.55,.7,0,.55),p.remap(z,.04,.32,.3,1)),color,(.055,.065,.105,1),'unequal vertical water staining')
 diffuse=p.node('ShaderNodeBsdfDiffuse','actual scene light');diffuse.inputs['Color'].default_value=(.8,.8,.8,1);diffuse.inputs['Roughness'].default_value=1
 rgb=p.node('ShaderNodeShaderToRGB','native light response');p.l.new(diffuse.outputs[0],rgb.inputs[0]);bw=p.node('ShaderNodeRGBToBW','light value');p.l.new(rgb.outputs[0],bw.inputs[0]);shade=p.remap(bw.outputs[0],.12,.8,.48,1)
 em=p.node('ShaderNodeEmission','bounded blue mineral shading');p.l.new(p.mix(1,color,shade,'native shading','MULTIPLY'),em.inputs['Color']);out=p.node('ShaderNodeOutputMaterial','surface');p.l.new(em.outputs[0],out.inputs['Surface']);new.materials.append(m)
 # Thin dark seals are actual geometry exactly on the top, not projected ink.
 ink=bpy.data.materials.new('243 Pipe concrete contact and scuffs');ink.use_nodes=True;nt=ink.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(.009,.010,.018,1);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs['Surface'])
 coll=bpy.data.collections.new('243 Foundation contact and wear');scene.collection.children.link(coll);created=[]
 def curve(name,pts,radius):
  c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=0;c.resolution_u=1
  sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
  for a,b in zip(sp.points,pts):a.co=(*b,1)
  q=bpy.data.objects.new(name,c);coll.objects.link(q);c.materials.append(ink);created.append(q.name);return q
 curve('243 Round pipe footing contact',[(-8.1+.205*math.cos(i*math.tau/64),9+.205*math.sin(i*math.tau/64),z1+.006)for i in range(65)],.014)
 curve('243 Rear rectangular entry contact',[(x,y,z1+.006)for x,y in[(-9.174,8.72),(-8.985,8.72),(-8.985,8.88),(-9.174,8.88),(-9.174,8.72)]],.012)
 # Unequal sparse native surface gashes read at final camera scale.
 for i,(xx,yy,ll)in enumerate([(-8.91,8.57,.15),(-8.65,8.89,.10),(-8.53,9.32,.13),(-8.07,8.64,.07),(-9.14,9.16,.10),(-7.78,9.3,.09)]):
  curve('243 Concrete top nick '+str(i),[(xx,yy,z1+.005),(xx+ll*.45,yy+.012,z1+.005),(xx+ll,yy-.008,z1+.005)],.006)
 for i,(yy,zz,ll)in enumerate([(8.59,.21,.14),(8.88,.12,.18),(9.27,.22,.11)]):
  curve('243 Concrete front scuff '+str(i),[(x1+.005,yy,zz),(x1+.005,yy+ll*.55,zz+.012),(x1+.005,yy+ll,zz-.009)],.007)
 # Restore the pre-footing world-space ink, then occlude only the compact pad.
 with bpy.data.libraries.load(str(__import__('pathlib').Path(__file__).resolve().parents[1]/'art/studies/hybrid-finish-241/scene.blend'),link=False)as(a,b):b.objects=['096 contacts ink','097 Broken soil ink']
 restores=[]
 for orig,name in zip(b.objects,['096 contacts ink','097 Broken soil ink']):
  target=bpy.data.objects[name];target.data=orig.data.copy();restores.append(name);bpy.data.objects.remove(orig,do_unlink=True)
 bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles();tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(t.vertices)for t in mesh.loop_triangles],all_triangles=True);ev.to_mesh_clear();origin=scene.camera.matrix_world.translation;hidden={}
 for name in restores:
  gp=bpy.data.objects[name];count=0
  for la in gp.data.layers:
   for fr in la.frames:
    for st in fr.drawing.strokes:
     for pt in st.points:
      v=gp.matrix_world@pt.position;d=v-origin;hit=tree.ray_cast(origin,d.normalized(),d.length)
      if hit[0]is not None and hit[3]<d.length-.015 and pt.opacity>0:pt.opacity=0;count+=1
  hidden[name]=count
 return {'bounds':[x0,x1,y0,y1,z0,z1],'previous_area_m2':1.9*4.6,'new_area_m2':(x1-x0)*(y1-y0),'loop_clearance_y_m':y0-6.9,'contacts':created[:2],'weathering':'cool mineral aggregate, dark basal deposits, vertical water staining, physical edge chips and scuffs','native_ink_restored_before_reclip':restores,'occluded_points':hidden}
