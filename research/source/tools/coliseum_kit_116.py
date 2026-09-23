"""Editable bay4/crown/tower export from approved assembled116, no affine decomposition."""
import bpy,json,os,time,hashlib,collections
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-116';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];meshes=[o for o in C.objects if o.type=='MESH'];source_count=len(meshes);source_unique=len({o.data.as_pointer()for o in meshes});groups=collections.defaultdict(list)
# Exact full-datablock duplicate sharing requires both shape and source-position attribute equality.
for ob in meshes:
 me=ob.data;h=hashlib.sha256();h.update(str(tuple(tuple(round(x,6)for x in v.co)for v in me.vertices)).encode());h.update(str(tuple(tuple(p.vertices)for p in me.polygons)).encode());attr=me.attributes.get('115 Original world position')
 if attr:h.update(str(tuple(tuple(round(x,6)for x in d.vector)for d in attr.data)).encode())
 h.update(str(tuple(m.name if m else''for m in me.materials)).encode());groups[h.hexdigest()].append(ob.name)
exact_groups=[g for g in groups.values()if len(g)>1]
selected=[o for o in meshes if o.get('bay')==4];keep=set(selected)
for o in selected:
 while o.parent:o=o.parent;keep.add(o)
keep.update(o for o in s.objects if o.type in ['CAMERA','LIGHT'])
world_before={o.name:[o.matrix_world@v.co for v in o.data.vertices]for o in selected}
bpy.data.batch_remove(ids=[o for o in list(s.objects)if o not in keep]);bpy.context.view_layer.update();error=max((o.matrix_world@v.co-world_before[o.name][v.index]).length for o in selected for v in o.data.vertices);assert error<1e-6
points=[p for values in world_before.values()for p in values];lo=Vector(tuple(min(p[k]for p in points)for k in range(3)));hi=Vector(tuple(max(p[k]for p in points)for k in range(3)));target=(lo+hi)/2
cam=s.camera;direction=Vector((-.12,-1,.12)).normalized();cam.location=target+direction*120;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';bpy.context.view_layer.update();inv=cam.matrix_world.inverted();cp=[inv@p for p in points];spanx=max(p.x for p in cp)-min(p.x for p in cp);spany=max(p.y for p in cp)-min(p.y for p in cp);cam.data.ortho_scale=max(spany,spanx*1.3)*1.15
s.world=bpy.data.worlds.new('116 Kit neutral world');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.16,.17,.20,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
s.render.resolution_x=1100;s.render.resolution_y=1430;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=False;s.render.filepath=str(O/'kit.png');inventory={'bay':4,'objects':len(selected),'vertices':sum(len(o.data.vertices)for o in selected),'roles':dict(collections.Counter(o.get('coliseum_role','none')for o in selected)),'world_bounds':[list(lo),list(hi)],'export_world_position_max_error_m':error,'parent_hierarchy_preserved':True,'source_mesh_objects':source_count,'source_unique_meshes':source_unique,'exact_duplicate_groups_including_weather_attribute':exact_groups,'sharing_note':'Angular compression plus anisotropic assembly shape and original-world paint coordinates make each warped bay unique. Reusing source110 intact master before procedural warp is viable; direct linked mesh sharing after warp would move painted weathering or alter geometry. No integrated refactor performed.'}
(O/'kit-inventory.json').write_text(json.dumps(inventory,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'kit.blend'));print(json.dumps(inventory))
if os.environ.get('KIT_RENDER')=='1':bpy.ops.render.render(write_still=True)
