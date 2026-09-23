"""Build or render130 in separate Blender processes for a reproducible saved scene."""
import bpy, json, sys, time
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R/'art/studies/coliseum-130'
sys.path.insert(0, str(R/'tools'))
O.mkdir(parents=True, exist_ok=True)

if '--render' in sys.argv:
    bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'))
    s = bpy.context.scene
    s.render.resolution_x = 3840
    s.render.resolution_y = 2885
    s.render.resolution_percentage = 100
    s.render.line_thickness = 3840/1440
    s.render.use_border = False
    s.render.use_crop_to_border = False
    s.render.filepath = str(O/'main-4k.png')
    from coliseum_ink_reference_scene_130 import sync
    sync(s)
    start = time.time()
    bpy.ops.render.render(write_still=True)
    (O/'render-performance.json').write_text(json.dumps({'seconds':time.time()-start,'resolution':[3840,2885],'source':'Fresh-process render of saved130 scene'},indent=2)+'\n')
else:
    from coliseum_arch_ink_130 import apply as arch_ink
    from coliseum_tunnels_130 import apply as tunnels
    from coliseum_ink_reference_scene_130 import apply as preserve_ink
    bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-129/scene.blend'))
    s = bpy.context.scene
    C = bpy.data.collections['110 Coliseum detailed front ruin']
    start = time.time()
    audit = {'source':'129','arch_ink':arch_ink(C, radius=.035)}
    audit['tunnels'] = tunnels(C, length=30., bend_radius=6., outlet_length=5., roof_extra=.65)
    audit['foreground_ink'] = preserve_ink(s, C)
    audit['generation_seconds'] = time.time()-start
    audit['held_studies'] = ['Separate Freestyle view map: did not reproduce archived128 line output; not integrated.']
    s.render.use_freestyle = True
    s.render.use_border = False
    s.render.use_crop_to_border = False
    s.render.resolution_x = 1440
    s.render.resolution_y = 1082
    s.render.resolution_percentage = 100
    s.render.line_thickness = 1
    s.render.filepath = str(O/'main.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
    (O/'generation.json').write_text(json.dumps(audit,indent=2,default=str)+'\n')
    print('130 built in',audit['generation_seconds'],'seconds')
