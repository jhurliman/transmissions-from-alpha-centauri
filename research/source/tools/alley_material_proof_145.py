import bpy,sys,json,math,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-weathering-145/material';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
# ShaderToRGB uses nativeEevee. Rendering side is identical to scene pipeline.
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.color_mode='RGB';s.view_settings.view_transform='Standard';s.view_settings.look='None'
from alley_panel_material_145 import make_panel_material
mat=make_panel_material(origin=(-1.132,0,0),span=(2.264,2.864));C=bpy.data.collections.new('145 Material test panels');s.collection.children.link(C)
def box(n,c,d,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=c);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);b=o.modifiers.new('Native folded edge','BEVEL');b.width=.008;b.segments=2;o.data.materials.append(m)
 for co in list(o.users_collection):co.objects.unlink(o)
 C.objects.link(o);return o
for row in range(2):
 for col in range(2):box('145 Test panel '+str(row)+str(col),((col-.5)*1.144,0,.71+row*1.444),(1.12,.024,1.42),mat)
back=bpy.data.materials.new('145 Backing');back.diffuse_color=(.035,.04,.05,1);back.use_nodes=True;back.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.035,.04,.05,1);box('Test backing',(0,.10,1.43),(2.36,.16,2.94),back)
w=bpy.data.worlds.new('145 Neutral cool fill');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.09,.12,.19,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
cam=bpy.data.cameras.new('145 Fixed camera');co=bpy.data.objects.new('145 Fixed camera',cam);s.collection.objects.link(co);co.location=(3.4,-6.7,3.3);target=Vector((0,0,1.43));co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=3.6;s.camera=co
sun=bpy.data.lights.new('145 Warm key','AREA');sun.energy=850;sun.color=(1,.65,.38);sun.shape='DISK';sun.size=3;lo=bpy.data.objects.new('145 Warm key',sun);s.collection.objects.link(lo)
def light(pos):lo.location=pos;lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
light((-3,-4,6));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));times={}
for name,pos,energy in [('key-left',(-3,-4,6),850),('key-right',(4,-3,5),850),('cool-fill-only',(-3,-4,6),0)]:
 light(pos);sun.energy=energy;s.render.filepath=str(O/(name+'.png'));t=time.time();bpy.ops.render.render(write_still=True);times[name]=time.time()-t
(O/'proof.json').write_text(json.dumps({'fixed_camera':True,'same_material_for_all_panels_and_lights':True,'dimensions_m':[1.12,1.42,.024],'resolution':[1600,1200],'times':times,'not_production_integrated':True},indent=2))
