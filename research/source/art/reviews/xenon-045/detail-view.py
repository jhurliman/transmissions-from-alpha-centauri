import bpy,os
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-045');label=os.environ.get('DAMAGE_LABEL','medium');O=R if label=='medium' else R/label
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.use_freestyle=False;s.camera.location=(4,3.2,3);s.camera.rotation_euler=(Vector((8.3,7.15,1.25))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=62;s.render.resolution_x=1000;s.render.resolution_y=900;s.cycles.samples=32;s.render.filepath=str(O/'support-detail.png');bpy.ops.render.render(write_still=True)
