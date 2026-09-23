"""Deliver the reviewed187 left-course break plus certified native contact cleanup."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
O=R/'art/studies/coliseum-188';O.mkdir(parents=True,exist_ok=True)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from coliseum_contact_clip_169 import snapshot,digest
def guards(s,embed):return {'149':g149(s,embed=embed),'156':g156(s,embed=embed),'161':g161(s,embed=embed)}
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;guards(s,False)
 s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True)
 (O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]},indent=2)+'\n')
 import parameter_editor
 for flag,name in [('_guard_149','native-ink-visibility'),('_guard156','foreground-ink-visibility'),('_guard161','fascia-ink-visibility161')]:
  (O/(name+'.json')).write_text(json.dumps([getattr(f,flag+'_audit')for f in parameter_editor.callbacks_modifiers_post if getattr(f,flag,False)],indent=2)+'\n')
 raise SystemExit
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));s=bpy.context.scene
before=fingerprint(s);mats=material_snapshot();oldgp=digest(snapshot(bpy.data.objects['110 Landmark contact ink']))
contact=json.loads((R/'art/studies/coliseum-187/contact/audit.json').read_text())
assert oldgp==contact['source_digest']
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-187/contact/corrected-study.blend'));s=bpy.context.scene
after=fingerprint(s);ma=material_snapshot();gp=bpy.data.objects['110 Landmark contact ink']
assert digest(snapshot(gp))==contact['after_digest']
allowed={'COL110 T2 band10 profile'+str(i)for i in range(5)}|{'COL110 U10 sill wall'}
assert set(before)==set(after),'Unexpected scene object inventory change'
changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]}
assert all(name in allowed and set(fields)<={'geometry','normals','materials'}for name,fields in changes.items()),changes
old_graph_changes=[k for k,v in mats.items()if ma.get(k)!=v];assert not old_graph_changes,old_graph_changes
preservation={'source':'retained173','recursive_scene_and_instance_objects':len(before),'changes':changes,'only_six_reviewed_masonry_meshes_changed':True,'camera_lights_transforms_hidden_flags_and_all_other_meshes_unchanged':True,'all_existing_material_graphs_unchanged':True,'contact_ink':contact,'limits':'Scoped technical187 audits supply face attributes, support and numerical residual evidence. Existing inherited crossings elsewhere remain; this is not a globally clean topology claim.'}
(O/'preservation.json').write_text(json.dumps(preservation,indent=2)+'\n')
visibility=guards(s,True)
C=bpy.data.collections['110 Coliseum detailed front ruin']
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440
s.render.use_freestyle=True;s.render.use_compositing=False;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath='//main-4k.png'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
bpy.data.libraries.write(str(O/'kit.blend'),{C,gp},fake_user=True)
(O/'generation.json').write_text(json.dumps({'source':'187/contact/corrected-study.blend','baseline':'173','geometry':'187 fixed-shape left course/sill endpoint cut','contact':'187 continuously certified unsupported contact intervals only','preserved_latest_user_edit':'147 threefold bottom splatter','visibility':visibility,'user_approved':False},indent=2)+'\n')
