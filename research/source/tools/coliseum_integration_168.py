"""Integrate a reviewed167 geometry delta onto retained166, keeping core shading."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-168';O.mkdir(parents=True,exist_ok=True)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
def guards(s,embed):return {'149':g149(s,embed=embed),'156':g156(s,embed=embed),'161':g161(s,embed=embed)}
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;guards(s,False);s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True)
 (O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]}))
 import parameter_editor
 for flag,name in [('_guard_149','native-ink-visibility'),('_guard156','foreground-ink-visibility'),('_guard161','fascia-ink-visibility161')]:
  (O/(name+'.json')).write_text(json.dumps([getattr(f,flag+'_audit')for f in parameter_editor.callbacks_modifiers_post if getattr(f,flag,False)],indent=2))
 raise SystemExit
# Run only after independent167 geometry review; this file is a prepared recipe.
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-166/scene.blend'));s=bpy.context.scene;before=fingerprint(s);mats=material_snapshot()
from coliseum_shoulder_failure_167 import apply
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
d=apply(C);assert d['accepted_cpu'],d
d['source']='retained166'
from coliseum_contact_clip_169 import apply as clip_contacts
contact_audit=clip_contacts(C);d['contact_ink']=contact_audit
(O/'contact-ink-preservation.json').write_text(json.dumps(contact_audit,indent=2))
d['visibility']=guards(s,True);after=fingerprint(s);ma=material_snapshot();allowed={r['object']for r in d['targets']};removed={r['object']for r in d['targets']if r.get('removed_entire')}
assert set(before)-set(after)==removed
assert not set(after)-set(before)
changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if k in after and v!=after[k]}
assert all(name in allowed and set(fields)<={'geometry','normals','materials'} for name,fields in changes.items()),changes
assert all(v==ma[k]for k,v in mats.items())
(O/'preservation.json').write_text(json.dumps({'source':'retained166','source_objects':len(before),'result_objects':len(after),'removed_inside_same_negative_volume':sorted(removed),'changes':changes,'all_non_target_geometry_normals_materials_transforms_and_all_old_material_graphs_unchanged':True,'target_normal_serialization_limit':'See167 target audits; preserved target normals have a disclosed small serialization delta.'},indent=2))
(O/'generation.json').write_text(json.dumps(d,indent=2))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_freestyle=True;s.render.use_compositing=False;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath='//main-4k.png'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'kit.blend'),{C,bpy.data.objects['110 Landmark contact ink']},fake_user=True)
