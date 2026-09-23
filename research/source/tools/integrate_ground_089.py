import bpy,numpy as np,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/ground-089'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-088/scene.blend'));s=bpy.context.scene
ob=bpy.data.objects['Street foundation'];mats=list(ob.data.materials);d=np.load(O/'ground.npz');vs=d['vertices'];fs=d['faces'];n=len(fs)
me=bpy.data.meshes.new('089 continuous packed earth');me.vertices.add(len(vs));me.vertices.foreach_set('co',vs.astype(np.float32).ravel());me.loops.add(fs.size);me.loops.foreach_set('vertex_index',fs.ravel());me.polygons.add(n);me.polygons.foreach_set('loop_start',np.arange(n,dtype=np.int32)*3);me.polygons.foreach_set('loop_total',np.full(n,3,dtype=np.int32));me.polygons.foreach_set('material_index',d['materials'].astype(np.int32));me.polygons.foreach_set('use_smooth',d['smooth']);me.update()
for mat in mats:me.materials.append(mat)
ob.data=me
# Let real terrain normals supply relief lighting; preserve the accepted pigment field.
mat=me.materials[0].copy();mat.name='089 packed soil: native relief and retained pigment';me.materials[0]=mat
for nd in mat.node_tree.nodes:
 if nd.type=='MIX_RGB' and nd.blend_type=='MULTIPLY' and abs(nd.inputs[0].default_value-.16)<.001:nd.inputs[0].default_value=0
s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'main.png')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
# Same image-plane detail, twice resolution, to inspect material/geometry transfer.
s.render.use_freestyle=False;s.render.resolution_percentage=200;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.16;s.render.border_max_x=.80;s.render.border_min_y=.16;s.render.border_max_y=.45;s.render.filepath=str(O/'road-detail.png');bpy.ops.render.render(write_still=True)
