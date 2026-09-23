import bpy,bmesh,json,math
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-072';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-071/scene.blend'));s=bpy.context.scene;changes={}
# Use the actual nearby duct material, including its independent service weathering.
duct=bpy.data.materials.get('DUCT | muted blue-gray sheet');h=bpy.data.objects['right_horizontal_utility'];kit=h.instance_collection
slats=[]
for ob in kit.objects:
 if ob.type=='MESH' and ob.name.startswith('Vent horizontal vane'):
  ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(duct);slats.append(ob.name)
changes['duct_metal_slats']=slats
mat=next(o for o in kit.objects if o.name.startswith('Utility broad plate')).data.materials[0]
def prism(name,u0,u1,profile,bevel):
 N=len(profile);vs=[(u,d,z) for u in [u0,u1] for d,z in profile];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mat);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);kit.objects.link(ob);mod=ob.modifiers.new('072 45-degree edge chamfer','BEVEL');mod.width=bevel;mod.segments=1;return ob
# 0.69 m horizontal return matches 0.69 m fall: a true 45 degree soffit.
prism('072 45 degree cantilever return',-7.39,7.39,[(.44,10.15),(1.14,9.45),(1.24,9.45),(1.24,10.15)],.025)
for lo,hi in [(-7.44,-7.25),(7.25,7.44)]:
 prism('072 shoulder chamfered end cap',lo,hi,[(-.29,2.67),(-.29,3.02),(1.15,5.48),(1.33,5.48),(1.33,5.27),(-.09,2.84),(-.09,2.67)],.065)
for ob in kit.objects:
 if ob.type=='MESH' and ob.name.startswith('Utility broad rake'):
  for mod in ob.modifiers:
   if mod.type=='BEVEL':mod.width=.028;mod.segments=1
changes['architecture']=['45 degree underhang return','Thick shoulder end caps with single-segment chamfers','Single-segment rake panel bevels']
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)
# Marked middle-right blue family now follows the adjacent warm side-wall family.
selected=set()
for ob in bpy.data.objects:
 if ob.type=='MESH' and len(ob.data.materials) and ob.data.materials[0] and 'right_middle' in ob.data.materials[0].name:
  selected.update(m for m in ob.data.materials if m and (m.name.startswith(('069 Projected','064 Projected')) or 'right_middle' in m.name))
for m in list(bpy.data.materials):
 if 'right_middle' in m.name:selected.add(m)
for m in selected:
 if not m.use_nodes:continue
 nt=m.node_tree
 for em in [n for n in nt.nodes if n.type=='EMISSION' and n.outputs[0].is_linked and n.inputs['Color'].is_linked]:
  old=em.inputs['Color'].links[0].from_socket;q=nt.nodes.new('ShaderNodeMixRGB');q.label='072 warm gallery palette';q.blend_type='MULTIPLY';q.inputs[0].default_value=1;nt.links.new(old,q.inputs[1]);q.inputs[2].default_value=tuple(a/b for a,b in zip(rgb('#9f6a58'),rgb('#4c5d7b')))+(1,);nt.links.new(q.outputs[0],em.inputs['Color'])
changes['warm_gallery_materials']=len(selected)
# Physical reflection stays outside the diffuse-to-cel conversion.
m=bpy.data.materials['Infill | smoked blue opaque study'];nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(.20,.25,.32,1);bs.inputs['Metallic'].default_value=.82;bs.inputs['Roughness'].default_value=.13;bs.inputs['IOR'].default_value=1.5;nt.links.new(bs.outputs[0],out.inputs['Surface']);s.eevee.use_raytracing=True;s.eevee.ray_tracing_method='SCREEN'
changes['glass']='Native EEVEE screen-traced reflections, tinted reflective glazing, roughness 0.13; open panes remain open'
# Planar captures include opposite architecture outside the main camera frame.
from mathutils import Vector
planes={}
for ins in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=ins.object
 if ob.type!='MESH' or ob.hide_render or not any(slot.material and slot.material.name==m.name for slot in ob.material_slots):continue
 center=ins.matrix_world @ Vector(tuple(sum(v[i] for v in ob.bound_box)/8 for i in range(3)))
 if abs(center.x)<4 or abs(center.x)>15 or center.y>40:continue
 key=round(center.x,1);planes.setdefault(key,[]).append(center)
for x,pts in sorted(planes.items(),key=lambda kv:len(kv[1]),reverse=True)[:8]:
 n=Vector((-1 if x>0 else 1,0,0));p=bpy.data.lightprobes.new('072 window plane '+str(x),'PLANE');p.influence_distance=.6;p.clip_start=.02
 ob=bpy.data.objects.new(p.name,p);s.collection.objects.link(ob);ob.location=(x+n.x*.025,sum(v.y for v in pts)/len(pts),sum(v.z for v in pts)/len(pts));ob.rotation_euler=n.to_track_quat('Z','Y').to_euler();ob.scale=(20,18,1)
changes['planar_reflection_groups']={str(k):len(v) for k,v in planes.items()}
(O/'changes.json').write_text(json.dumps(changes,indent=2));s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=2880;s.render.resolution_y=2160;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.62;s.render.border_max_x=1;s.render.border_min_y=.22;s.render.border_max_y=.95;s.render.filepath=str(O/'right.png');bpy.ops.render.render(write_still=True)
