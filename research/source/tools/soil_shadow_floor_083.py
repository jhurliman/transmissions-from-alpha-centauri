import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-083';sys.path.insert(0,str(R/'tools'));from soil_relief_083 import lin
bpy.ops.wm.open_mainfile(filepath=str(O/'main-scene.blend'));s=bpy.context.scene;m=bpy.data.objects['Street foundation'].data.materials[0];r=next(q for q in reversed(list(m.node_tree.nodes)) if q.type=='VALTORGB')
for e in r.color_ramp.elements:e.color=tuple(max(e.color[i],lin(v)) for i,v in enumerate((68,48,41)))+(1,)
s.render.threads_mode='FIXED';s.render.threads=4;bpy.ops.wm.save_as_mainfile(filepath=str(O/'main-scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
