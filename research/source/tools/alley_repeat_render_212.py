import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-repeat-212';sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene
# Freeze RNA collection iteration before changing render visibility.
audit=json.loads((O/'audit.json').read_text())
city=list(bpy.data.collections['101 Original city layout study'].all_objects)
remaining=[o for o in city if o.get('reference_mass') and not o.hide_render]
for o in remaining:o.hide_render=True
hidden=sorted(set(audit['original_city_hidden'])|{o.name for o in remaining})
typed=[{'name':name,'type':bpy.data.objects[name].type,'reference_mass':bpy.data.objects[name].get('reference_mass')}for name in hidden]
print('212 CITY SOURCE TYPES',json.dumps(typed),flush=True)
(O/'old-city-visibility.json').write_text(json.dumps(typed,indent=2))
assert len([r for r in typed if r['type']=='MESH'])==106,typed
extras=[r for r in typed if r['type']!='MESH']
assert sorted(r['name']for r in extras)==['CITY101 L01 FAR075 closed service riser.040', 'CITY101 R02 FAR075 closed service riser.040', 'CITY101 R08 FAR075 closed service riser.040', 'CITY106 N_L1 CITY101 L01 FAR075 closed service riser.040', 'CITY108 N_L6 CITY101 L01 FAR075 closed service riser.040'] and all(r['type']=='CURVE'for r in extras),extras
audit['old_city_nonmesh_helpers_hidden']=extras
assert all(o.hide_render for o in city if o.get('reference_mass'))
audit['original_city_hidden']=hidden
audit['preservation']['render_visibility_changes_only_old_city']=len(hidden)
audit['visibility_iteration_fix']='Frozen object references before changing hide_render; 106 mesh objects plus5 verified native service-riser CURVEs hidden.'
(O/'audit.json').write_text(json.dumps(audit,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'))
print('212 CITY VISIBILITY VERIFIED',len(hidden),flush=True)
from alley_repeat_212 import repeat_guard_pairs
repeat_guard_pairs(s)
from coliseum_ink_regression_149 import apply as a149
from coliseum_foreground_visibility_156 import apply as a156
from coliseum_foreground_visibility_161 import apply as a161
from architecture_ink_visibility_192 import apply as a192
from architecture_ink_visibility_205 import apply as a205
for fn in(a149,a156,a161,a192,a205):fn(s,embed=False)
def g207(scene,*args):
 from architecture_ink_visibility_207 import install
 install(scene,str(O/'207-guard-proof.json'))
 from alley_repeat_212 import install_far_guard_callbacks
 report=install_far_guard_callbacks(scene)
 (O/'far-guard-callback-audit.json').write_text(json.dumps(report,indent=2))
bpy.app.handlers.render_pre.append(g207)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.use_compositing=True;s.render.filepath=str(O/'main-4k.png')
t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'width':3840,'guards':[149,156,161,192,205,207]}));print('212_PROOF_DONE',flush=True)
