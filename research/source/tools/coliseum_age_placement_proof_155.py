"""Matched native component proof for a single existing age-mask placement change."""
import bpy,sys,json,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
O=R/'art/studies/coliseum-155/material';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-152/scene.blend'))
s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
before=fingerprint(s);mats=material_snapshot()
s.render.use_compositing=False;s.render.use_freestyle=False
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=2
x0,y0,x1,y1=1665,520,1970,800
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840
s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
s.render.filepath=str(O/'before.png');bpy.ops.render.render(write_still=True)
from coliseum_age_placement_155 import apply
t=time.time();d=apply(C);d['generation_seconds']=time.time()-t
after=fingerprint(s);ma=material_snapshot()
changes={k:[f for f in v if v[f]!=after[k][f]] for k,v in before.items() if v!=after[k]}
targets={r['object'] for r in d['assignments']}
assert set(before)==set(after)
assert all(fields==['materials'] and name in targets for name,fields in changes.items())
assert all(v==ma[k] for k,v in mats.items())
d['preservation']={'changes':changes,'compared_objects':len(before),'existing_material_graphs_unchanged':True,'all_geometry_normals_camera_lights_transforms_unchanged':True}
d['source']='152 component comparison, independent of153/154';d['crop']=[x0,y0,x1,y1]
d['render_note']='Native4K crop; matched Freestyle disabled; all geometry-driven GP rim/joint/contact ink retained.'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'study.blend'))
s.render.filepath=str(O/'after.png');t=time.time();bpy.ops.render.render(write_still=True);d['render_seconds']=time.time()-t
(O/'audit.json').write_text(json.dumps(d,indent=2))
