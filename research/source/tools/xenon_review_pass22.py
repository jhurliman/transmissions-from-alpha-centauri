import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-022';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-021/scene.blend'));s=bpy.context.scene
# Reposition the composed assembly in the next bay so it is readable from the locked camera.
for o in bpy.data.collections['021 Collapsed service doorway'].objects:o.location.y+=6
for o in list(s.objects):
 if not o.name.startswith(('Right facade plate','Torn cladding sheet')):continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];c=sum(pts,Vector())/8
 if c.x>0 and 1<c.y<5 and c.z<4:bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
def bounds(prefix):
 pts=[o.matrix_world@Vector(v) for o in s.objects if o.name.startswith(prefix) for v in o.bound_box]
 return [[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
a=bounds(('Left deep wall core','Right shadow core'));d=bounds(('Dome ','Fine secondary dome','Crown broken spar'))
images=[m.name for m in bpy.data.materials if m.use_nodes and any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes)]
assert not images
ratio=(d[1][0]-a[1][1])/(a[1][1]-a[1][0]);assert abs(ratio-6)<.001
s.use_nodes=False
(O/'audit.json').write_text(json.dumps({'gap_in_alley_lengths':ratio,'dome_nearest_edge':d[1][0],'camera':list(s.camera.location),'image_texture_materials':images,'material_overrides':[vl.name for vl in s.view_layers if vl.material_override],'compositor_enabled':s.use_nodes,'native_objects':len(s.objects)},indent=2)+'\n')
s.cycles.samples=48;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
