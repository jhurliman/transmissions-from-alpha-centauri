"""Independent editable physical-scale architectural catalog, no scene edits."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-prefabs-211';sys.path.insert(0,str(R/'tools'))
from city_prefabs_211 import kit
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
for f,v,x,stories in [(0,0,-8,3),(1,1,-3,3),(2,2,2,3),(0,2,9,10)]:
 c=kit(f,v,stories);o=bpy.data.objects.new('211 Catalog '+str(f)+' '+str(stories)+'stories',None);o.instance_type='COLLECTION';o.instance_collection=c;s.collection.objects.link(o);o.location=(x,0,0)
 if stories==10:o.scale=(2,2,1)
cam=bpy.data.cameras.new('211 Catalog camera');o=bpy.data.objects.new('211 Catalog camera',cam);s.collection.objects.link(o);o.location=(35,-58,35);o.rotation_euler=(Vector((1,1,18))-o.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=46;s.camera=o
sun=bpy.data.lights.new('211 Catalog sun','SUN');sun.energy=2.5;o=bpy.data.objects.new('211 Catalog sun',sun);s.collection.objects.link(o);o.rotation_euler=(.5,-.5,-.5)
s.world=bpy.data.worlds.new('211 Catalog neutral');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.14,.14,.17,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.6
# Materials use native ShaderToRGB; catalog uses same EEVEE pipeline as scene.
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.resolution_percentage=100
s.view_settings.view_transform='Standard';s.render.use_freestyle=True;bpy.context.view_layer.use_freestyle=True;s.render.line_thickness=.65
ls=bpy.context.view_layer.freestyle_settings.linesets[0];ls.linestyle=bpy.data.linestyles.new('211 Catalog physical contours');ls.linestyle.thickness=1.1;ls.linestyle.color=(.026,.026,.035);ls.select_by_collection=False;ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'catalog.blend'));print('211CATALOG_SAVED')
