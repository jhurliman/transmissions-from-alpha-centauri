import bpy
bpy.ops.wm.open_mainfile(filepath='/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-044/scene.blend')
s=bpy.context.scene;s.render.use_freestyle=True
for ls in s.view_layers[0].freestyle_settings.linesets:
 ls.linestyle.alpha=.8;ls.linestyle.thickness=.85
s.render.filepath='/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-044/render.png';bpy.ops.wm.save_as_mainfile(filepath='/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-044/scene.blend');bpy.ops.render.render(write_still=True)
