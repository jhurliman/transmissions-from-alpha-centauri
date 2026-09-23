"""Native camera comparison of156,157 geometry, and157+158 composition."""
import bpy,sys,json,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
O=R/'art/studies/coliseum-159/pairing';O.mkdir(parents=True,exist_ok=True)
def setup():
    s=bpy.context.scene
    s.render.use_compositing=False;s.render.use_freestyle=False
    s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
    s.render.threads_mode='FIXED';s.render.threads=4
    s.render.use_border=True;s.render.use_crop_to_border=True
    x0,y0,x1,y1=2025,535,2350,875
    s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840
    s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
    return s
def render(s,name):
    s.render.filepath=str(O/(name+'.png'));t=time.time();bpy.ops.render.render(write_still=True)
    return time.time()-t
timing={}
if '--paired-only' not in sys.argv:
    bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'))
    s=setup();timing['baseline']=render(s,'baseline156')
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-157/geometry/scene.blend'))
s=setup()
if '--paired-only' not in sys.argv:timing['geometry']=render(s,'geometry157')
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
before=fingerprint(s);mats=material_snapshot()
from coliseum_course_age_158 import apply
d=apply(C);after=fingerprint(s);ma=material_snapshot()
changes={k:[f for f in v if v[f]!=after[k][f]] for k,v in before.items() if v!=after[k]}
targets={r['object'] for r in d['assignments']}
assert set(before)==set(after)
assert all(fields==['materials'] and name in targets for name,fields in changes.items())
assert all(v==ma[k] for k,v in mats.items())
d['preservation']={'changes':changes,'compared_objects':len(before),'existing_material_graphs_unchanged':True,'geometry_normals_camera_lights_transforms_unchanged':True}
d['source']='157 V3 plus158 material; comparison156 retained scene'
d['crop']=[2025,535,2350,875];d['render_note']='Native4K camera crop, Freestyle disabled equally; geometry-driven GP ink retained'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
timing['paired']=render(s,'paired157-158')
d['render_seconds']=timing
(O/'audit.json').write_text(json.dumps(d,indent=2))
