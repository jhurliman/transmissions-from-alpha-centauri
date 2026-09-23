import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-036';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-035/scene.blend'));s=bpy.context.scene;removed=[]
# Hide complete route and its authored mounts; retain recoverable source files.
for o in list(s.objects):
 if o.hide_render:continue
 kill=False
 if o.instance_collection and abs(o.location.x-7.8)<.02 and abs(o.location.y-23)<.02:kill=True
 if o.name.startswith(('Roof return continuous pipe','Roof penetration flashing','Roof riser wall bracket')):kill=True
 if o.type=='MESH' and o.name.startswith('Riser wall standoff'):
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  if pts and abs(sum(v.y for v in pts)/len(pts)-23)<.02 and sum(v.x for v in pts)/len(pts)>0:kill=True
 if kill:o.hide_render=True;o.hide_viewport=True;removed.append(o.name)
(O/'audit.json').write_text(json.dumps({'removed_rear_pipe_objects':removed,'other_geometry_and_camera':'unchanged'},indent=2))
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
