import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-059'
bpy.ops.wm.open_mainfile(filepath=str(O/'network.blend'))
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('059 junction breakout'):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
for host in bpy.context.scene.objects:
 if host.instance_collection and host.instance_collection.name.startswith('059 '):
  for o in host.instance_collection.objects:
   if any(m.type=='BOOLEAN' and m.name.startswith('059') for m in o.modifiers):
    mod=o.modifiers.new('059 weld fracture junctions','WELD');mod.merge_threshold=.00001
s=bpy.context.scene;bpy.ops.wm.save_as_mainfile(filepath=str(O/'network.blend'))
# Audit before rendering.
for host in s.objects:
 if host.instance_collection and host.instance_collection.name.startswith('059 '):
  for o in host.instance_collection.objects:
   if any(m.type=='WELD' for m in o.modifiers):
    bm=bmesh.new();bm.from_mesh(o.evaluated_get(bpy.context.evaluated_depsgraph_get()).data);print('AUDIT',o.name,sum(not e.is_manifold for e in bm.edges),flush=True);bm.free()
s.render.filepath=str(O/'network.png');bpy.ops.render.render(write_still=True)
for j,a in enumerate(json.loads((O/'network-audit.json').read_text())):
 center=Vector(a['center']);normal=Vector(a['normal']);size=max(a['face_dimensions']);s.camera.location=center+normal*4+Vector((0,-.4,.25));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=size*1.25;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(O/('network'+('-support.png' if j==0 else '-panel.png')));bpy.ops.render.render(write_still=True)
