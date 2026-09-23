"""Package fixed-camera matte finish and independent geometry audit in one Blender file."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-006'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-005/geometry.blend'));geo=bpy.context.scene;geo.name='GEOMETRY AUDIT - no painted finish'
# Keep geometry/materials unchanged in the audit scene. A separate view-layer override provides projection.
s=bpy.data.scenes.new('PAINTED CAMERA - fixed view only')
for c in geo.collection.children:s.collection.children.link(c)
for ob in geo.collection.objects:s.collection.objects.link(ob)
s.camera=geo.camera;s.world=geo.world;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False
s.render.resolution_x=1448;s.render.resolution_y=1086;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard';s.view_settings.look='None';s.render.film_transparent=False
im=bpy.data.images.load(str(O/'painted.png'));im.pack()
m=bpy.data.materials.new('New painted finish - screen projection, not reference texture');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
out=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');tex=n.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear';tc=n.new('ShaderNodeTexCoord');l.new(tc.outputs['Window'],tex.inputs['Vector']);l.new(tex.outputs['Color'],e.inputs[0]);l.new(e.outputs[0],out.inputs[0]);s.view_layers[0].material_override=m
# Camera-aligned backing geometry handles sky pixels and gaps in the modeled environment.
c=bpy.data.collections.new('PAINTED ONLY - projection backing');s.collection.children.link(c);cam=s.camera;rot=cam.rotation_euler.to_matrix();center=cam.location+rot@Vector((0,0,-220));vs=[center+rot@Vector((x,y,0)) for x,y in [(-220,-180),(220,-180),(220,180),(-220,180)]];me=bpy.data.meshes.new('Projection backing');me.from_pydata(vs,[],[(0,1,2,3)]);me.update();ob=bpy.data.objects.new('Projection backing - hide in geometry audit',me);c.objects.link(ob);ob.data.materials.append(m)
s['LIMITATION']='Camera-dependent painted finish. Figure and lighting are baked into plate. Not an animated actor or freely relightable scene.'
s['SOURCE']='New painted interpretation of geometry.png; selected reference is not used as the projected texture.'
geo['LIMITATION']='This is the actual editable geometric foundation. Its visual scores remain below 80; finishing details are not yet modeled.'
bpy.context.window.scene=s
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='RENDERED';a.spaces.active.overlay.show_overlays=False
s.render.filepath=str(O/'blender-finished.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'xenon-camera-finish.blend'));bpy.ops.render.render(write_still=True)
