"""Full native scene carrying the independently retained165 core light response."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-166';O.mkdir(parents=True,exist_ok=True)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
def guards(s,embed):return {'149':g149(s,embed=embed),'156':g156(s,embed=embed),'161':g161(s,embed=embed)}
if 'render'in sys.argv:
    bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;guards(s,False);s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True)
    (O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]}))
    import parameter_editor
    for flag,name in [('_guard_149','native-ink-visibility'),('_guard156','foreground-ink-visibility'),('_guard161','fascia-ink-visibility161')]:
        (O/(name+'.json')).write_text(json.dumps([getattr(f,flag+'_audit')for f in parameter_editor.callbacks_modifiers_post if getattr(f,flag,False)],indent=2))
    raise SystemExit
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-163/scene.blend'));s=bpy.context.scene;before=fingerprint(s);mats=material_snapshot()
# Apply only the reviewed core material change to the retained full scene.
from coliseum_core_response_165 import apply
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library)
d=apply(s);d['visibility']=guards(s,True);after=fingerprint(s);ma=material_snapshot();changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};allowed={r['object']for r in d['assignments']}
assert set(before)==set(after)
assert all(fields==['materials']and name in allowed for name,fields in changes.items()),changes
assert all(v==ma[k]for k,v in mats.items())
(O/'preservation.json').write_text(json.dumps({'source':'retained163','objects':len(before),'changes':changes,'geometry_normals_camera_lights_transforms_and_existing_material_graphs_unchanged':True,'new_face_attributes_only':[]},indent=2))
(O/'generation.json').write_text(json.dumps(d,indent=2))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_freestyle=True;s.render.use_compositing=False;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath='//main-4k.png'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'kit.blend'),{C},fake_user=True)
