"""Rigid four-degree landmark rotation; preserve approved E architecture and framing."""
import bpy,math,json,sys,os
from pathlib import Path
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1]
def rotate_landmark(collection,degrees=4,pivot=None,recenter=True):
 members=list(collection.objects);mesh=[o for o in members if o.type=='MESH'];world=[o.matrix_world@v.co for o in mesh for v in o.data.vertices]
 if pivot is None:
  # Measured by applying E affine to source114 ring center (0,347,0).
  pivot=Vector((4.239481449127197,460.57666015625,.9695461392402649))
 pivot=Vector(pivot);scene=bpy.context.scene;cam=scene.camera;rotation=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(degrees),4,'Z')@Matrix.Translation(-pivot)
 # Hold central front band reference point in screen X; keep elevation untouched.
 front=min(world,key=lambda p:p.y);anchor=Vector((4.239481449127197,192.45166015625,29.133399963378906));old=world_to_camera_view(scene,cam,anchor);q=rotation@anchor;new=world_to_camera_view(scene,cam,q);jx=world_to_camera_view(scene,cam,q+Vector((1,0,0))).x-new.x;dx=(old.x-new.x)/jx if recenter else 0;rotation=Matrix.Translation(Vector((dx,0,0)))@rotation
 roots=[o for o in members if o.parent not in members];original={o:o.matrix_world.copy()for o in roots};parent=bpy.data.objects.new('116 Whole coliseum rotation',None);collection.objects.link(parent);parent.matrix_world=rotation
 for o in roots:o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=original[o]
 bpy.context.view_layer.update()
 return {'degrees_world_z':degrees,'pivot_world':list(pivot),'horizontal_recenter_m':dx,'delta_matrix':[list(row)for row in rotation],'nearest_world_y':min((rotation@p).y for p in world),'original_nearest_world_y':min(p.y for p in world),'mesh_geometry_unchanged':True,'root_objects':[o.name for o in roots]}
if __name__=='__main__':
 for sign in [4,-4]:
  bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-115/E/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];s=bpy.context.scene;camera=s.camera.matrix_world.copy();audit=rotate_landmark(C,sign)
  for o in bpy.data.objects:
   if 'Landmark contact ink'in o.name:o.hide_render=True
  for o in C.objects:
   if o.type not in ['MESH','EMPTY','LIGHT']:o.hide_render=True
  assert s.camera.matrix_world==camera
  O=R/'art/studies/coliseum-116/rotation'/('plus4'if sign>0 else'minus4');O.mkdir(parents=True,exist_ok=True);(O/'audit.json').write_text(json.dumps(audit,indent=2));s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=False;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
  if os.environ.get('ROTATION_RENDER')=='1':bpy.ops.render.render(write_still=True)
