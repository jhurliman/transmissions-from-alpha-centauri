import bpy,math
from mathutils import Vector

def apply(scene):
 dot=next(n for n in scene.world.node_tree.nodes if n.label=='075 Sun angular distance');ray=Vector(dot.inputs[1].default_value).normalized();sun=bpy.data.objects['Soft warm directional daylight'];old=(sun.matrix_world.to_3x3()@Vector((0,0,-1))).normalized();sun.rotation_euler=ray.to_track_quat('-Z','Y').to_euler();scene.view_layers.update()
 fill=bpy.data.objects['Broad diffuse facade fill'];fill.hide_render=False
 return {'soft_fill_enabled':True,'old_ray':list(old),'new_ray':list(ray),'direction_change_degrees':math.degrees(old.angle(ray)),'visible_world_sun_unchanged':True,'strength_and_color_unchanged':True}
