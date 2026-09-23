"""Integrate reviewed foreground families over the ink-safe192 scene."""
import bpy,json,sys,time,array,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/scene-weathering-195';O.mkdir(parents=True,exist_ok=True)
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
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/plate-runoff-192/scene.blend'));s=bpy.context.scene
 source=(R/'tools/scene_integration_138.py').read_text();exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")]);before=fingerprint(s);mats=material_snapshot()
 from first_building_weathering_193 import apply as building
 from beam_feather_194 import apply as beams
 from service_contrast_193 import apply as service
 from plate_runoff_readability_195 import apply as runoff
 result={'building':building(s),'beams':beams(s),'service_and_right_rust':service(s),'readable_runoff':runoff(s)}
 def exclude_new_films(lc):
  if lc.collection.name=='195 Plate rusty water':lc.exclude=True
  for child in lc.children:exclude_new_films(child)
 exclude_new_films(s.view_layers['192 Architecture ink without pigment films'].layer_collection)
 bpy.context.view_layer.update();after=fingerprint(s);changed={k:[f for f in v if v[f]!=after[k][f]] for k,v in before.items() if k in after and v!=after[k]};missing=sorted(set(before)-set(after));assert not missing
 assert all(set(v)<={'materials'} for v in changed.values()),changed
 ma=material_snapshot();assert not [k for k,v in mats.items() if ma.get(k)!=v], 'Original material graph changed'
 write('preservation.json',{'source':'plate-runoff-192','original_entries':len(before),'changed':changed,'new':sorted(set(after)-set(before)),'original_geometry_normals_transforms_unchanged':True,'old_material_graphs_unchanged':True})
 write('generation.json',result);guards(s,True);s.render.filepath='//main-4k.png';s.render.use_compositing=True;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100
 frames={k:[] for k in ['service-panel','left-beam','right-beam']}
 for inst in bpy.context.evaluated_depsgraph_get().object_instances:
  ob=inst.object;parent=inst.parent.name if inst.parent else ''
  key='service-panel' if parent=='133 Exposed utility panel instance' else ('left-beam' if parent=='Architecture | gangway_single_Y_8m' and ob.name.startswith(('Y arm','Y stem','Y splice')) else 'right-beam' if parent=='Architecture | gangway_single_Y_8m.001' and ob.name.startswith(('Y arm','Y stem','Y splice')) else None)
  if key and ob.type=='MESH':
   for p in ob.bound_box:
    v=world_to_camera_view(s,s.camera,inst.matrix_world@Vector(p));frames[key].append((v.x*3840,(1-v.y)*2885))
 boxes={k:[max(0,int(min(v[0]for v in pts))-30),max(0,int(min(v[1]for v in pts))-30),min(3840,int(max(v[0]for v in pts))+30),min(2885,int(max(v[1]for v in pts))+30)]for k,pts in frames.items()if pts}
 write('framing.json',boxes);bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
