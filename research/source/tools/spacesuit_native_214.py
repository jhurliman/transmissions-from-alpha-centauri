"""Lightweight isolated native cards, using the actual saved206 light study only."""
import bpy,json,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-spacesuit-214/anime'
source=R/'art/studies/characters-206/anime/proof.blend'
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
    dst.scenes=['206 Anime native light feasibility']
s=dst.scenes[0];s.name='214 Spacesuit native light feasibility';bpy.context.window.scene=s
for old in list(bpy.data.scenes):
    if old!=s:bpy.data.scenes.remove(old)
s.render.use_freestyle=False;s.render.use_compositing=False;s.render.use_border=False
assets=json.loads((O/'asset-audit.json').read_text());rows=[]
for name,x,h in [('traveler-a',-.30,1.72),('traveler-b',.55,1.65)]:
    ob=next(o for o in s.objects if o.type=='MESH' and name in o.name)
    ob.name='214 '+name+' illustrated spacesuit card'
    iw,ih=assets[name]['size'];x0,y0,x1,y1=assets[name]['body_bounds_alpha_gt8'];w=h*(x1-x0)/(y1-y0)
    foot=Vector((x,-6.5,.005));verts=[foot+Vector((-w/2,0,0)),foot+Vector((w/2,0,0)),foot+Vector((w/2,0,h)),foot+Vector((-w/2,0,h))]
    for v,co in zip(ob.data.vertices,verts):v.co=co
    uv=[(x0/iw,1-y1/ih),(x1/iw,1-y1/ih),(x1/iw,1-y0/ih),(x0/iw,1-y0/ih)]
    for loop in ob.data.loops:ob.data.uv_layers.active.data[loop.index].uv=uv[loop.vertex_index]
    im=bpy.data.images.load(str(O/f'{name}-anime.png'));im.pack()
    mat=ob.data.materials[0];mat.name='214 '+name+' 35percent native diffuse'
    next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE').image=im
    pp=[world_to_camera_view(s,s.camera,v)for v in verts];fv=world_to_camera_view(s,s.camera,foot)
    rows.append(dict(name=name,world_foot=list(foot),height_m=h,card_width_m=w,body_bounds_4k=[min(v.x for v in pp)*3840,(1-max(v.y for v in pp))*2885,max(v.x for v in pp)*3840,(1-min(v.y for v in pp))*2885],foot_pixel_4k=[fv.x*3840,(1-fv.y)*2885]))
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True
s.render.filepath=str(O/'native-lit-characters-4k.png');bpy.ops.render.render(write_still=True)
energies=[(o,o.data.energy)for o in s.objects if o.type=='LIGHT']
for ob,e in energies:ob.data.energy=.15*e
s.render.filepath=str(O/'native-lowlight-characters-4k.png');bpy.ops.render.render(write_still=True)
for ob,e in energies:ob.data.energy=e
s.render.filepath=str(O/'native-lit-characters-4k.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'))
(O/'placement.json').write_text(json.dumps(rows,indent=2))
(O/'native-proof-audit.json').write_text(json.dumps({'study':214,'source_light_scene':str(source.relative_to(R)),'actual_lighting_origin':'209 camera/world/directional/fill lights preserved in206 isolated native scene','source_preserved':True,'environment_rerendered':False,'mesh_objects':len([o for o in s.objects if o.type=='MESH']),'rows':rows,'base_art_weight':.65,'native_diffuse_weight':.35,'controlled_lowlight_energy_fraction':.15,'limits':['Generated illustration includes fixed cel shading.','Flat cards have one normal: no per-limb relighting, hair self-shadow or volumetric depth.','No character contact shadow is claimed.','Separate artwork feasibility study, not3Dgeometry acceptance.'],'user_approved':False},indent=2))
print('214_NATIVE_DONE',flush=True)
