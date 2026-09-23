import bpy, math
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100
s.world.color=(.5,.5,.5)
c=bpy.data.collections.new('Intersection sources');s.collection.children.link(c)
def cube(name, loc, scale,color):
 bpy.ops.mesh.primitive_cube_add(size=2,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o)
 mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1);o.data.materials.append(mat);return o
cube('Terrain', (0,0,-.25),(4,4,.25),(.5,.32,.19));cube('Footing',(0,0,.25),(1,.5,.6),(.7,.3,.22));o=cube('Beam',(0,0,1.2),(.2,.2,1.5),(.2,.3,.5));o.rotation_euler.y=.6
# Occluder blocks part of intersection and checks that line cannot draw through it.
cube('Occluder',(-.8,-1.2,.4),(.3,.3,.6),(.3,.45,.25))
bpy.ops.object.camera_add(location=(5,-8,5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((0,0,.5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=7
bpy.ops.object.light_add(type='AREA',location=(1,-4,6));bpy.context.object.data.energy=1000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4

def add_intersection_ink(collection, name='Intersection ink', radius=.02):
 g=bpy.data.grease_pencils.new(name);o=bpy.data.objects.new(name,g);bpy.context.scene.collection.objects.link(o)
 layer=g.layers.new('Intersection strokes',set_active=True);layer.use_lights=False
 mat=bpy.data.materials.new(name);bpy.data.materials.create_gpencil_data(mat);mat.grease_pencil.color=(.018,.012,.022,1);mat.grease_pencil.show_fill=False;g.materials.append(mat)
 m=o.modifiers.new(name,'LINEART');m.source_type='COLLECTION';m.source_collection=collection;m.target_layer='Intersection strokes';m.target_material=mat
 for attr in ['use_contour','use_loose','use_crease','use_material','use_edge_mark','use_light_contour','use_shadow'] :setattr(m,attr,False)
 m.use_intersection=True;m.radius=radius;m.opacity=1;m.level_start=0;m.level_end=0;m.use_multiple_levels=False;m.stroke_depth_offset=.005
 return o
add_intersection_ink(c)
s.view_settings.view_transform='Standard';s.render.filepath=str(OUT/'probe.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'probe.blend'));bpy.ops.render.render(write_still=True)
