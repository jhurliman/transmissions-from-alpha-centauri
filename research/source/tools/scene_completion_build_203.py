"""Seven-work-item integration over the current201 native scene."""
import bpy,sys,json,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/scene-completion-203';O.mkdir(parents=True,exist_ok=True)
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192

def guards(s,embed):
 for g in (g149,g156,g161):g(s,embed=embed)
 g192(s,embed=embed,audit_path=None if embed else str(O/'side-return-ink-audit.json'))
def write(n,x):(O/n).write_text(json.dumps(x,indent=2,default=str)+'\n')
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;guards(s,False);s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);write('performance.json',{'seconds':time.time()-t})
else:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-completion-201/scene.blend'));s=bpy.context.scene
 source=(R/'tools/scene_integration_138.py').read_text();exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")]);before=fingerprint(s);old=material_snapshot()
 for m in bpy.data.materials:m.use_fake_user=True
 for ob in objects(s):ob.use_fake_user=True
 from alley_weathering_rollout_198 import apply as facade
 from cloud_refinement_199 import apply as clouds
 from city_transition_refinement_200 import apply as ruins
 from haze_ground_transition_202 import apply as haze
 from middle_rubble_palette_204 import apply as palette
 result={}
 for name,fn in [('facades',facade),('clouds',clouds),('ruins',ruins),('middle_palette',palette),('haze',haze)]:
  print('203 APPLY',name,flush=True);result[name]=fn(s);write('generation-in-progress.json',result)
 after=fingerprint(s);changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if k in after and v!=after[k]};missing=sorted(set(before)-set(after));new=material_snapshot();assert all(new[k]==v for k,v in old.items()),'Old material graph changed'
 assert all(not(set(v)&{'matrix','hidden','camera','light'})for v in changes.values()),'Camera/light/transform changed'
 write('source-fingerprint.json',before);write('candidate-fingerprint.json',after);write('source-materials.json',old);write('candidate-materials.json',new)
 write('generation.json',result);write('preservation.json',{'source':'scene-completion-201','original_entries':len(before),'changed':changes,'missing':missing,'new':sorted(set(after)-set(before)),'original_camera_lights_transforms_preserved':True,'old_material_graphs_unchanged':True,'missing_entries_require_review':'Private instance substitutions may remove old source entries from active traversal; archived data retained.'})
 guards(s,True);s.render.filepath='//main-4k.png';s.render.use_compositing=True;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100
 for vl in s.view_layers:vl.use=True
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
