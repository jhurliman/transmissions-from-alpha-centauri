"""Integrate207 upper-course visibility and208 mineral recess treatment into accepted205."""
import bpy,sys,json,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/scene-completion-209';O.mkdir(parents=True,exist_ok=True)
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192
from architecture_ink_visibility_205 import apply as g205
from architecture_ink_visibility_207 import apply as g207

def guards(s,embed):
 for g in(g149,g156,g161):g(s,embed=embed)
 for n,g in[(192,g192),(205,g205),(207,g207)]:g(s,embed=embed,audit_path=None if embed else str(O/f'ink-{n}-audit.json'))
def write(n,x):(O/n).write_text(json.dumps(x,indent=2,default=str)+'\n')
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;guards(s,False);s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);write('performance.json',{'seconds':time.time()-t})
else:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-completion-205/scene.blend'));s=bpy.context.scene
 source=(R/'tools/scene_integration_138.py').read_text();exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")]);before=fingerprint(s);mats=material_snapshot()
 from alley_recess_refinement_208 import apply as recess
 report=recess(s);guards(s,True);after=fingerprint(s);ma=material_snapshot();changes=[]
 assert before.keys()==after.keys(),'Unexpected object added/removed'
 for name,old in before.items():
  diff=[k for k in old if old[k]!=after[name][k]]
  assert not(set(diff)-{'materials'}),(name,diff)
  if diff:changes.append({'object':name,'fields':diff,'before':old['materials'],'after':after[name]['materials']})
 assert all(ma.get(k)==v for k,v in mats.items()),'An old material graph changed'
 write('generation.json',report);write('source-fingerprint.json',before);write('candidate-fingerprint.json',after);write('source-materials.json',mats)
 write('preservation.json',{'source':'205','native_objects':len(before),'all_geometry_normals_transforms_instances_lights_camera_preserved':True,'all_original_material_graphs_preserved':len(mats),'material_bindings_changed':changes,'additional_change':'207 source-specific native visibility guard;208 selected concave edge marks/line style on existing geometry.'})
 s.render.filepath='//main-4k.png';bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
