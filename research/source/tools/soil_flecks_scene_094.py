import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-094';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-093/scene-C.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
g=s.objects['Street foundation'];targets=[n for n in g.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'pigment-C' in n.image.name];assert len(targets)==1
for label in ['A','B','C']:
 im=bpy.data.images.load(str(O/f'pigment-{label}.png'),check_existing=False);im.pack();targets[0].image=im
 s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_freestyle=True;s.render.filepath=str(O/f'main-{label}.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/f'scene-{label}.blend'));bpy.ops.render.render(write_still=True)
 s.render.use_freestyle=False;s.render.resolution_percentage=200;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.18;s.render.border_max_x=.44;s.render.border_min_y=.17;s.render.border_max_y=.39;s.render.filepath=str(O/f'detail-{label}.png');bpy.ops.render.render(write_still=True)
