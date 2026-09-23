import bpy,json,bmesh
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-055'
for version in ['054','055']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'art/reviews/xenon-{version}/scene.blend'));s=bpy.context.scene
 if version=='055':
  results=[]
  for o in bpy.data.objects:
   if o.type=='MESH' and o.name.startswith('Folded fascia'):
    bm=bmesh.new();bm.from_mesh(o.data);count=sum(not e.is_manifold for e in bm.edges);angles=[tuple(f.normal) for f in bm.faces if .69<f.normal.z<.72];assert count==0 and angles;results.append({'object':o.name,'non_manifold_edges':count,'chamfer_normals':angles});bm.free()
  (O/'geometry-check.json').write_text(json.dumps(results,indent=2))
  cols={c for c in bpy.data.collections if any(o.name.startswith('Folded fascia') for o in c.objects)}
  for c in cols:c['chamfer_055']='90 mm run and rise, 45 degrees, geometry and highlight material'
  bpy.data.libraries.write(str(O/'chamfered-gangway-kit.blend'),cols,fake_user=True)
 s.render.resolution_x=4320;s.render.resolution_y=3240;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1100/1440;s.render.border_max_x=1;s.render.border_min_y=1-830/1080;s.render.border_max_y=1-330/1080;s.render.filepath=str(O/(version+'-surface-detail.png'));bpy.ops.render.render(write_still=True)
