"""Continuous native angular compression, UCL-01/DP-03/UX-01. Separate C study."""
import bpy,math,json,sys,time,os
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-perspective-115/D';O.mkdir(parents=True,exist_ok=True)
from coliseum_haze_115 import apply_haze
from coliseum_materials_115 import apply_materials
from coliseum_affine_115 import apply_affine
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-114/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];camera=s.camera.matrix_world.copy();started=time.time()
lean=Matrix.Rotation(math.radians(2),4,'X');step=math.tau/36;anchor=next(o for o in C.objects if o.get('bay')==4 and 'fractured upper wall L' in o.name);auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*step,4,'Z');delta=anchor.matrix_world@auth.inverted();auth_to_world=delta@Matrix.Translation(Vector((0,347,0)))@lean;world_to_auth=auth_to_world.inverted()
M=Matrix(json.loads((O.parent/'measurements.json').read_text())['variants'][0]['matrix']);factor=.68
apply_haze(3,19);apply_materials(C)
objects=list(C.objects);count=0;min_y=1e9;max_shift=0;bad=0;baseline_bad=0
for ob in objects:
 if ob.type!='MESH':ob.hide_render=True;continue
 old=ob.data;baseline_bad+=sum(p.area<1e-12 for p in old.polygons);ob.data=old.copy();mesh=ob.data;world=ob.matrix_world.copy();inv=world.inverted();attr=mesh.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
 for v in mesh.vertices:
  w=world@v.co;attr.data[v.index].vector=w
  p=world_to_auth@w;rad=math.hypot(p.x,p.y);theta=math.atan2(p.y,p.x)
  outer=75*(1-.055*p.z/78)
  if rad<outer:rad=outer+.3*(rad-outer)
  if theta>math.pi/2:theta-=math.tau
  theta=-math.pi/2+factor*(theta+math.pi/2);p.x=rad*math.cos(theta);p.y=rad*math.sin(theta);new=auth_to_world@p
  max_shift=max(max_shift,(new-w).length);v.co=inv@new;min_y=min(min_y,(M@new).y);count+=1
 mesh.update()
 for poly in mesh.polygons:
  if poly.area<1e-12:bad+=1
# Attribute interpolates original coordinates across warped faces, keeping all weathering attached.
materials={m for ob in C.objects if ob.type=='MESH' for m in ob.data.materials}
for mat in materials:
 if not mat or not mat.use_nodes:continue
 n=mat.node_tree.nodes;l=mat.node_tree.links;unscale=next((q for q in n if q.label=='Preserve authored weathering scale'),None)
 if unscale:
  a=n.new('ShaderNodeAttribute');a.attribute_name='115 Original world position';a.name='115 Nonlinear attached weathering';l.new(a.outputs['Vector'],unscale.inputs[0])
oldink=bpy.data.objects.get('110 Landmark contact ink')
if oldink:oldink.hide_render=True
clearance_adjustment=max(0,177.55-min_y);M[1][3]+=clearance_adjustment;min_y+=clearance_adjustment
exact=apply_affine(C,M);assert s.camera.matrix_world==camera
s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'main.png')
audit={'angular_compression':factor,'inner_radial_depth_scale':.3,'nominal_bay_density_multiplier':1/factor,'warped_vertices':count,'degenerate_faces':bad,'baseline_degenerate_faces':baseline_bad,'world_y_clearance_adjustment':clearance_adjustment,'nearest_world_y':min_y,'max_pre_affine_shift_m':max_shift,'exact_affine':exact,'seconds_generation':time.time()-started,'weathering':'Original source world position point attribute, interpolated on same topology','topology':'Faces and winding unchanged; angular mapping positive monotonic, radius/Z unchanged; shared meshes copied diagnostically'}
(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print(json.dumps(audit))
if os.environ.get('PERSPECTIVE_RENDER')=='1':bpy.ops.render.render(write_still=True)
