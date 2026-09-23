"""First current-scene integration proof: reviewed Colosseum190 + beam connector."""
import bpy,sys,json,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/scene-completion-201';O.mkdir(parents=True,exist_ok=True)
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192

def guards(s,embed):
 for g in (g149,g156,g161,g192):g(s,embed=embed)
def write(n,x):(O/n).write_text(json.dumps(x,indent=2,default=str)+'\n')
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;guards(s,False);s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);write('performance.json',{'seconds':time.time()-t})
else:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/beam-rust-197/scene.blend'));s=bpy.context.scene
 source=(R/'tools/scene_integration_138.py').read_text();exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")]);before=fingerprint(s);old=material_snapshot()
 from colosseum_crumbling_190 import replay
 from beam_connector_201 import apply
 result={'colosseum':replay(bpy.data.collections['110 Coliseum detailed front ruin']),'beam':apply(s)}
 after=fingerprint(s);changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};allowed=set(result['colosseum']['targets'])|{result['beam']['object']}
 assert all(k.split('|')[-1] in allowed or any(x in k for x in allowed)for k in changes),changes
 new=material_snapshot();assert all(new[k]==v for k,v in old.items())
 write('generation.json',result);write('preservation.json',{'changed_entries':changes,'missing_entries':sorted(set(before)-set(after)),'old_material_graphs_unchanged':True,'scope':'190 frozen native recessed wall meshes plus one private beam material'})
 guards(s,True);s.render.filepath='//main-4k.png';s.render.use_compositing=True;s.render.use_border=False;s.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
