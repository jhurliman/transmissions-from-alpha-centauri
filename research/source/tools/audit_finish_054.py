import bpy,json,hashlib
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-050'
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

b=signature(R/'art/reviews/xenon-053/C.blend');a=signature(R/'art/reviews/xenon-054/scene.blend');assert a==b;(R/'art/reviews/xenon-054/preservation-audit.json').write_text(json.dumps({'matches_053_C':True,'signature':a},indent=2));print('PASS')
