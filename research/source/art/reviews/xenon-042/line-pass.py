import bpy
bpy.ops.wm.open_mainfile(filepath='/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-042/scene.blend')
for col in bpy.data.collections:
 if col.name.startswith('042 ') and ' | ' in col.name:
  family,source=col.name[4:].split(' | ',1);orig=bpy.data.collections.get(source)
  if orig:
   for k in orig.keys():col[k]=orig[k]
  col['coating_family']=family
s=bpy.context.scene;s.render.use_freestyle=True
for ls in s.view_layers[0].freestyle_settings.linesets:
 ls.linestyle.alpha=.8;ls.linestyle.thickness=.85
s.render.filepath='/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-042/render.png';bpy.ops.wm.save_as_mainfile(filepath='/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-042/scene.blend');bpy.ops.render.render(write_still=True)
