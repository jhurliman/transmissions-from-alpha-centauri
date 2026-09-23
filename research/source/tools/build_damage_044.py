import bpy,math,json,random
from mathutils import Vector
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-044';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-043/scene.blend'));s=bpy.context.scene
host=bpy.data.objects['Architecture | buttress_45'];orig=host.instance_collection;kit=bpy.data.collections.new('DAMAGE | concrete_support_01');kit['part_id']='buttress_45_damage_01';kit['clean_source']=orig.name;kit.asset_mark()
for ob in orig.objects:
 q=ob.copy();kit.objects.link(q)
 if ob.type=='MESH':q.data=ob.data.copy()
host.instance_collection=kit
beam=next(o for o in kit.objects if o.name.startswith('Solid concrete'))
mat=bpy.data.materials.new('044 Exposed concrete aggregate');mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=48;noise.inputs['Detail'].default_value=2
geo=nt.nodes.new('ShaderNodeNewGeometry');nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.07,.045,.034,1);ramp.color_ramp.elements[1].color=(.25,.20,.145,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.009;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
beam.data.materials.append(mat)
dark=bpy.data.materials.new('044 Crack interior');dark.diffuse_color=(.022,.017,.016,1);dark.use_nodes=True;dark.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.022,.017,.016,1)
cutters=bpy.data.collections.new('044 Hidden damage cutters');s.collection.children.link(cutters)
def cut(ob):
 for col in list(ob.users_collection):col.objects.unlink(ob)
 cutters.objects.link(ob);ob.hide_render=True;ob.hide_set(True)
 mod=beam.modifiers.new('Editable spall | '+ob.name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=ob
# Local cutters reference the prefab geometry; host instance transforms all generated damage together.
random.seed(44)
for i,(pos,scale) in enumerate([((.11,1.48-2.65+.045,1.48),(.17,.10,.23)),((-.12,.48-2.65+.025,.48),(.11,.07,.13)),((.22,2.04-2.4,2.04),(.08,.11,.12))]):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=pos);c=bpy.context.object;c.name='Spall cutter '+str(i);c.scale=scale
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
paths=[[(.69,-.05),(.84,.03),(.99,-.035),(1.10,.025),(1.23,.005),(1.38,.10),(1.50,.12)],[(1.10,.025),(1.15,-.06),(1.23,-.15)],[(1.38,.10),(1.45,.015),(1.57,-.08)]]
for i,path in enumerate(paths):
 path=list(reversed(path));dense=[]
 for a,b in zip(path,path[1:]):
  for j in range(3):
   t=j/3;zz=a[0]*(1-t)+b[0]*t;off=a[1]*(1-t)+b[1]*t+(random.uniform(-.008,.008) if j else 0);dense.append((zz,off))
 dense.append(path[-1]);pts=[(off,z-2.65-.001,z) for z,off in dense]
 c=curve('Crack cutter '+str(i),pts,.011,cutters)
 bpy.context.view_layer.objects.active=c;c.select_set(True)
 for ob in list(bpy.context.selected_objects):
  if ob!=c:ob.select_set(False)
 bpy.ops.object.convert(target='MESH');c=bpy.context.object;c.data.materials.append(mat);cut(c)
 curve('Recessed fracture interior '+str(i),[(x,y+.005,z) for x,y,z in pts],.0035,kit,dark)
kit['damage_rules']=json.dumps({'seed':44,'cracks':'Tapered branching boolean grooves','spalls':'Three localized faceted Boolean losses','aggregate':'World-space exposed-surface shader','preserve':'Bearing head, footing and primary section remain intact','clean_source':orig.name})
(O/'audit.json').write_text(kit['damage_rules'])
s.render.use_freestyle=False;s.render.filepath=str(O/'color-only.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))

exec(compile((R/"art/reviews/xenon-044/detail-view.py").read_text(),"detail-view.py","exec"))
exec(compile((R/"art/reviews/xenon-044/line-pass.py").read_text(),"line-pass.py","exec"))
