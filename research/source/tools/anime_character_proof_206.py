"""Separate 2D artwork relighting feasibility study; never changes the integrated source."""
import bpy,json,sys,time,os
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-206/anime';sys.path.insert(0,str(R/'tools'))
BASE=Path(os.environ.get('CHARACTER_SOURCE_SCENE',str(R/'art/studies/scene-completion-209/scene.blend')))
bpy.ops.wm.open_mainfile(filepath=str(BASE));s=bpy.context.scene
from anime_proxy_hide_206 import apply as hide_proxy
proxy_audit=hide_proxy(s);(O/'proxy-hide-audit.json').write_text(json.dumps(proxy_audit,indent=2));print('206_PROXY_AND_INK_HIDDEN',len(proxy_audit['proxy_objects_hidden']),len(proxy_audit['complete_character_contact_strokes_hidden']),flush=True)
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192
from architecture_ink_visibility_205 import apply as g205
from architecture_ink_visibility_207 import apply as g207
for g in(g149,g156,g161,g192,g205,g207):g(s,embed=False)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.filepath=str(O/'clean-background-4k.png')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'clean-background.blend'));t=time.time();bpy.ops.render.render(write_still=True);print('206_CLEAN_PLATE_DONE',time.time()-t,flush=True)
# Fully separate native scene with copied camera and actual lights. No background pixels drive light.
bpy.app.handlers.render_pre.clear();cs=bpy.data.scenes.new('206 Anime native light feasibility');cs.render.engine=s.render.engine;cs.world=s.world.copy();cs.render.resolution_x=3840;cs.render.resolution_y=2885;cs.render.resolution_percentage=100;cs.render.film_transparent=True;cs.render.image_settings.file_format='PNG';cs.render.image_settings.color_mode='RGBA';cs.view_settings.view_transform=s.view_settings.view_transform;cs.view_settings.look=s.view_settings.look;cs.view_settings.exposure=s.view_settings.exposure;cs.view_settings.gamma=s.view_settings.gamma
for ob in [s.camera]+[q for q in s.objects if q.type=='LIGHT']:
 cp=ob.copy();cp.data=ob.data.copy();cs.collection.objects.link(cp)
 if ob==s.camera:cs.camera=cp
assets=json.loads((O/'asset-audit.json').read_text());rows=[]
for name,x,h in [('airam',-.30,1.72),('miranda',.55,1.65)]:
 im=bpy.data.images.load(str(O/f'{name}-anime.png'));im.pack();iw,ih=assets[name]['size'];x0,y0,x1,y1=assets[name]['body_bounds_alpha_gt8'];w=h*(x1-x0)/(y1-y0)
 # Bounds use actual painted bodyalpha, not the larger transparent canvas.
 foot=Vector((x,-6.5,0.005));verts=[foot+Vector((-w/2,0,0)),foot+Vector((w/2,0,0)),foot+Vector((w/2,0,h)),foot+Vector((-w/2,0,h))]
 me=bpy.data.meshes.new('206 '+name+' upright card');me.from_pydata([list(v)for v in verts],[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new(name='Generated art UV');uvs=[(x0/iw,1-y1/ih),(x1/iw,1-y1/ih),(x1/iw,1-y0/ih),(x0/iw,1-y0/ih)]
 for loop in me.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
 ob=bpy.data.objects.new('206 '+name+' authored2D light-study',me);cs.collection.objects.link(ob);m=bpy.data.materials.new('206 '+name+' bounded native diffuse');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');tex=n.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear';em=n.new('ShaderNodeEmission');l.new(tex.outputs['Color'],em.inputs['Color']);df=n.new('ShaderNodeBsdfDiffuse');l.new(tex.outputs['Color'],df.inputs['Color']);mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.35;mix.label='65percent authored albedo plus35percent actual scene diffuse';l.new(em.outputs[0],mix.inputs[1]);l.new(df.outputs[0],mix.inputs[2]);tr=n.new('ShaderNodeBsdfTransparent');alpha=n.new('ShaderNodeMixShader');l.new(tex.outputs['Alpha'],alpha.inputs[0]);l.new(tr.outputs[0],alpha.inputs[1]);l.new(mix.outputs[0],alpha.inputs[2]);l.new(alpha.outputs[0],out.inputs['Surface']);m.surface_render_method='DITHERED';me.materials.append(m)
 pp=[world_to_camera_view(s,s.camera,v)for v in verts];fv=world_to_camera_view(s,s.camera,foot);rows.append(dict(name=name,world_foot=list(foot),height_m=h,card_width_m=w,body_bounds_4k=[min(v.x for v in pp)*3840,(1-max(v.y for v in pp))*2885,max(v.x for v in pp)*3840,(1-min(v.y for v in pp))*2885],foot_pixel_4k=[fv.x*3840,(1-fv.y)*2885],uv_bounds=[x0/iw,1-y1/ih,x1/iw,1-y0/ih],material=m.name))
cs.render.filepath=str(O/'native-lit-characters-4k.png');bpy.context.window.scene=cs;bpy.ops.render.render(write_still=True,scene=cs.name)
# Small controlled relighting test changes light strengths only in the separate character scene.
energies=[(o,o.data.energy)for o in cs.objects if o.type=='LIGHT']
for ob,e in energies:ob.data.energy=e*.15
cs.render.filepath=str(O/'native-lowlight-characters-4k.png');bpy.ops.render.render(write_still=True,scene=cs.name)
for ob,e in energies:ob.data.energy=e
bpy.context.window.scene=s;bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'))
audit={'study':206,'media':'Generated anime artwork on native textured flat cards; not3Dcharactergeometry acceptance','source_scene':str(BASE.relative_to(R)),'rows':rows,'lighting':'Copiedactual209scene directional+fill lights;35percent diffuse response and65percent base artwork for modest contrast','lighting_test':'lowlight copy uses15percent originallightenergy; source205lights unchanged','limitations':['Flat card normals cannot reproduce hair/limb self-shadow or volumetric rimlight.','No claimed physicallygrounded foot contactshadow in this isolated relightingpass. Ground-shadow proxy rig is futurework.','Sourceart includes restrained cel shading; it is not a neutral PBRtexture.'],'native_scene':cs.name,'alpha':'Generatedalpha retained; bodyfitUV only','source_hidden_only':['07 Human scale proxy,15objects','8proven character-local096contactinkstrokes'],'preserved_source_file':True,'user_approved':False};(O/'native-proof-audit.json').write_text(json.dumps(audit,indent=2));print('206_NATIVE_DONE',json.dumps(rows),flush=True)

# Clearly labelled compositor proof from the freshly rendered native background and card pass.
comp=bpy.data.scenes.new('206 Illustrated character compositing study');comp.render.engine=cs.render.engine;comp.collection.objects.link(cs.camera);comp.camera=cs.camera;comp.render.resolution_x=3840;comp.render.resolution_y=2885;comp.render.resolution_percentage=100;comp.render.film_transparent=True;comp.render.image_settings.file_format='PNG';comp.render.image_settings.color_mode='RGBA';comp.view_settings.view_transform=s.view_settings.view_transform;comp.view_settings.look=s.view_settings.look
nt=bpy.data.node_groups.new('206 Native background and native-lit artwork composite','CompositorNodeTree');comp.compositing_node_group=nt;nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');out=nt.nodes.new('NodeGroupOutput');bg=nt.nodes.new('CompositorNodeImage');bg.image=bpy.data.images.load(str(O/'clean-background-4k.png'));fg=nt.nodes.new('CompositorNodeImage');fg.image=bpy.data.images.load(str(O/'native-lit-characters-4k.png'));over=nt.nodes.new('CompositorNodeAlphaOver');over.inputs['Factor'].default_value=1;nt.links.new(bg.outputs['Image'],over.inputs['Background']);nt.links.new(fg.outputs['Image'],over.inputs['Foreground']);nt.links.new(over.outputs[0],out.inputs['Image']);comp.render.use_compositing=True;comp.render.filepath=str(O/'scene-composite.png');bpy.context.window.scene=comp;bpy.ops.render.render(write_still=True,scene=comp.name);bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'));print('206_COMPOSITE_DONE',flush=True)
