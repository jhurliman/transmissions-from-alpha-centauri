"""Geometry-derived visible-landmark mask for4K image analysis; no source-scene writes."""
import bpy,time,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-120/analysis';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/scene.blend'))
s=bpy.context.scene;C=set(bpy.data.collections['110 Coliseum detailed front ruin'].all_objects)
def emission(name,value):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear()
    e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(value,value,value,1)
    out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],out.inputs['Surface']);return m
white=emission('120 Analysis landmark mask',1);black=emission('120 Analysis occluder mask',0)
for ob in s.objects:
    if ob.type=='GREASEPENCIL':ob.hide_render=True
    if ob.type!='MESH':continue
    volume_only=any(m and m.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked and not n.inputs['Surface'].is_linked for n in m.node_tree.nodes)for m in ob.data.materials)
    if volume_only:ob.hide_render=True;continue
    ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(white if ob in C else black)
    for face in ob.data.polygons:face.material_index=0
s.world=bpy.data.worlds.new('120 Mask black world');s.world.use_nodes=True
s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0,0,0,1)
s.render.use_freestyle=False;s.render.use_compositing=False;s.render.film_transparent=False
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'landmark-mask.png')
t=time.time();bpy.ops.render.render(write_still=True)
(O/'mask-audit.json').write_text(json.dumps({'source':'119/scene.blend','resolution':[3840,2885],'method':'Visible landmark white, opaque occluders black; volume-only geometry and ink excluded. Source scene unchanged.','seconds':time.time()-t},indent=2))
