"""blender -b --python tools/render_iteration.py -- config/bay-v002.json [--final]
Non-destructive, paired review render. Refuses to overwrite an existing iteration.
"""
import bpy,json,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];cfg=json.loads((root/args[0]).read_text());refs=json.loads((root/'references/manifest.json').read_text());byid={x['id']:x for x in refs}
assert all(x in byid for x in cfg['reference_ids'])
assert len({byid[x]['group'] for x in cfg['reference_ids']})>=2
out=root/'art/reviews'/cfg['iteration'];out.mkdir(exist_ok=False,parents=True)
bpy.ops.wm.open_mainfile(filepath=str(root/cfg['scene']));s=bpy.context.scene
s.render.resolution_x,s.render.resolution_y=cfg['final_resolution' if '--final' in args else 'draft_resolution'];s.render.resolution_percentage=100;s.cycles.samples=24
camera=list(s.camera.matrix_world);camera=[[float(v) for v in row] for row in camera]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 p=m.node_tree.nodes.get('Principled BSDF')
 if p:
  p.inputs['Metallic'].default_value=0.05;p.inputs['Roughness'].default_value=.88
  p.inputs['Specular IOR Level'].default_value=.18
s.render.filepath=str(out/'rich.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'rich.blend'));bpy.ops.render.render(write_still=True)
# Graphic study uses the same matte scene and geometry. This is not an EGA conversion.
s.render.engine='CYCLES';s.view_settings.view_transform='Standard';s.view_settings.look='None'
for m in bpy.data.materials:
 if not m.use_nodes:continue
 p=m.node_tree.nodes.get('Principled BSDF')
 if p:p.inputs['Specular IOR Level'].default_value=0;p.inputs['Metallic'].default_value=0
s.render.filepath=str(out/'graphic.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'graphic.blend'));bpy.ops.render.render(write_still=True)
cfg.update(camera_matrix=camera,blender_version=bpy.app.version_string,resolution=[s.render.resolution_x,s.render.resolution_y],scene_sha256=hashlib.sha256((root/cfg['scene']).read_bytes()).hexdigest())
(out/'review.json').write_text(json.dumps(cfg,indent=2)+'\n')
