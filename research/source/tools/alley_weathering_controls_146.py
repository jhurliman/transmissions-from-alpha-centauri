"""Native material/geometry controls and editable kit delivery for weathering145."""
import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-weathering-146/combined'
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
from alley_panel_material_146 import make_panel_material
from alley_damage_145 import box,mat
C=bpy.data.collections['145 Alley damage panel study'];D=bpy.data.collections['145 Panel detail layers'];A=bpy.data.collections['145 Clean panel master | asset']
bpy.data.libraries.write(str(O/'panel-kit.blend'),{C,D,A},fake_user=True)
# Native clay demonstrates the physical loss before color and stains are judged.
s.render.resolution_percentage=57
clay=mat('145 Combined clay control',(.42,.42,.42));s.view_layers[0].material_override=clay
s.render.filepath=str(O/'clay.png');bpy.ops.render.render(write_still=True);s.view_layers[0].material_override=None
# Same camera, light and material response, with undamaged facing and no details.
D.hide_render=True;clean=make_panel_material();descriptors=json.loads((R/'art/studies/alley-weathering-145/geometry/audit.json').read_text())['panels']
for p in descriptors:
 o=bpy.data.objects[p['object']];o.hide_render=True;x=p['origin'][0];q=box('145 Baseline clean face '+p['id'],(x,0,0),(x+p['width'],.024,p['height']),C);q.data.materials.append(clean)
s.render.resolution_percentage=100;s.render.filepath=str(O/'before-4k.png');bpy.ops.render.render(write_still=True)
(O/'delivery.json').write_text(json.dumps({'kit':'panel-kit.blend','editable_native_collections':[C.name,D.name,A.name],'reference_images_projected':False,'source_scene_143_unchanged':True,'main_resolution':[3840,1745],'aspect_ratio':3840/1745,'clean_material_matches_candidate':True,'clay_percentage':57,'user_approved':False},indent=2))
