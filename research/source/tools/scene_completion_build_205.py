"""Final seven-item scene plus middle palette, with proven hidden-ink correction only."""
import bpy,sys,json,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/scene-completion-205';O.mkdir(parents=True,exist_ok=True)
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192
from architecture_ink_visibility_205 import apply as g205

def guards(s,embed):
 for g in (g149,g156,g161):g(s,embed=embed)
 g192(s,embed=embed,audit_path=None if embed else str(O/'side-return-192-audit.json'))
 g205(s,embed=embed,audit_path=None if embed else str(O/'side-return-205-audit.json'))
def write(n,x):(O/n).write_text(json.dumps(x,indent=2,default=str)+'\n')
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;guards(s,False);s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);write('performance.json',{'seconds':time.time()-t})
else:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-completion-203/scene.blend'));s=bpy.context.scene
 source=(R/'tools/scene_integration_138.py').read_text();exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")]);before=fingerprint(s);mats=material_snapshot();guards(s,True);after=fingerprint(s);ma=material_snapshot()
 assert before==after,'Geometry or object state changed';assert mats==ma,'Material graph changed'
 write('preservation.json',{'source':'scene-completion-203','all_object_entries_identical':len(before),'all_material_graphs_identical':len(mats),'change':'Only a native source-specific depth visibility guard and its embedded script; no art geometry/material change.'})
 write('candidate-fingerprint.json',after);write('source-materials.json',mats)
 write('component-provenance.json',{'integrated_art':'../scene-completion-203/generation.json','source_fresh_check':'../scene-completion-203/fresh-check.json','source_scope_check':'../scene-completion-203/scope-check.json','native_damage':'../alley-weathering-198/audit.json','clouds':'../clouds-199/review.json','colosseum':'../scene-completion-201/generation.json','ruins':'../city-transition-200/review.json','middle_palette':'../middle-rubble-204/audit.json','haze':'../haze-ground-202/review.json','final_visual_review_required':True})
 s.render.filepath='//main-4k.png';bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
