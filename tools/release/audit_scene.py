"""Read-only packed scene inventory, run with Blender --disable-autoexec."""
import argparse, bpy, json, sys, platform
from pathlib import Path
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser()
p.add_argument('--scene',default=str(R/'releases/v1.0.0/scene.blend'))
p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(Path(a.scene).resolve()))
s=bpy.context.scene
images=[{'name':i.name,'source':i.source,'users':i.users,'size':list(i.size),'path':i.filepath,'packed':bool(i.packed_file or i.packed_files)} for i in bpy.data.images]
report={
 'blender_version':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),
 'platform':platform.platform(),'python':sys.version,'images':images,
 'libraries':[l.filepath for l in bpy.data.libraries],
 'fonts':[{'name':f.name,'path':f.filepath,'packed':bool(f.packed_file)}for f in bpy.data.fonts],
 'texts':[{'name':t.name,'autoexec':t.use_module,'path':t.filepath}for t in bpy.data.texts],
 'external_categories':{k:[{'name':d.name,'path':getattr(d,'filepath','')}for d in getattr(bpy.data,k)] for k in ('cache_files','movieclips','sounds','volumes')},
 'simulation_modifiers':[{'object':o.name,'type':m.type}for o in bpy.data.objects for m in o.modifiers if m.type in {'FLUID','CLOTH','SOFT_BODY','PARTICLE_SYSTEM'}],
 'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],
 'border':[s.render.use_border,s.render.use_crop_to_border],
 'color_management':{'display':s.display_settings.display_device,'view':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},
 'compositor_nodes':[{'name':n.name,'type':n.bl_idname}for n in s.compositing_node_group.nodes]if s.compositing_node_group else []}
Path(a.output).write_text(json.dumps(report,indent=2)+'\n')
print('SCENE_AUDIT_COMPLETE')
