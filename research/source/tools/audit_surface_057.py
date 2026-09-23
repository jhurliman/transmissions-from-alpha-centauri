import bpy,json,hashlib
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-057'
def signature(path):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 h=hashlib.sha256()
 for o in sorted(bpy.data.objects,key=lambda x:x.name):
  if o.type in {'LIGHT'}:continue
  h.update(str((o.name,o.type,tuple(tuple(r) for r in o.matrix_basis),o.hide_render)).encode())
  if o.type=='MESH':
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 s=bpy.context.scene
 return {'geometry_digest':h.hexdigest(),'camera':tuple(s.camera.location),'rotation':tuple(s.camera.rotation_euler),'lens':s.camera.data.lens,'resolution':(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage)}

b=signature(R/'art/reviews/xenon-055/scene.blend');c=signature(O/'scene.blend');assert b==c;(O/'preservation-audit.json').write_text(json.dumps({'baseline':b,'candidate':c,'identical':True},indent=2))
