"""Append168kit into an empty native scene; full main camera plus bay/tower/crown/flat-wall proofs."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];study=args[0];O=R/'art/studies'/study/'kit-proof';O.mkdir(parents=True,exist_ok=True);source=O.parent/'scene.blend';kit=O.parent/'kit.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;C=next(c for c in s.collection.children_recursive if c.name=='110 Coliseum detailed front ruin' and not c.library)
cam=s.camera.name;lights=[o.name for o in s.objects if o.type=='LIGHT'];transforms={o.name:[list(row)for row in o.matrix_world] for o in s.objects if o.name in lights+[cam]};world=s.world.name if s.world else None;engine=s.render.engine;view={k:getattr(s.view_settings,k)for k in ['view_transform','look','exposure','gamma']};resolution=[3840,2885]
def signature(ob,dg):
 d={'type':ob.type,'matrix':[list(row)for row in ob.matrix_world],'materials':[x.material.name if x.material else None for x in ob.material_slots]}
 if ob.type=='MESH':
  ev=ob.evaluated_get(dg);me=ev.to_mesh();a=array.array('f',[0])*(len(me.vertices)*3);me.vertices.foreach_get('co',a);b=array.array('i',[0])*len(me.loops);me.loops.foreach_get('vertex_index',b);d['evaluated_geometry']=hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest();ev.to_mesh_clear()
 return d
dg=bpy.context.evaluated_depsgraph_get();before={o.name:signature(o,dg)for o in C.all_objects};bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
with bpy.data.libraries.load(str(kit),link=False)as(src,dst):
 dst.collections=['110 Coliseum detailed front ruin'];dst.objects=['110 Landmark contact ink']
C=dst.collections[0];s.collection.children.link(C)
for gp in dst.objects:s.collection.objects.link(gp)
with bpy.data.libraries.load(str(source),link=False)as(src,dst):
 dst.objects=[cam]+lights
 if world:dst.worlds=[world]
from mathutils import Matrix
for ob in dst.objects:
 s.collection.objects.link(ob);ob.parent=None;ob.matrix_world=Matrix(transforms[ob.name])
s.camera=bpy.data.objects[cam]
if world:s.world=dst.worlds[0]
s.render.engine=engine
for k,v in view.items():setattr(s.view_settings,k,v)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();after={o.name:signature(o,dg)for o in C.all_objects};changes=[k for k,v in before.items() if v!=after.get(k)];assert not changes,changes
external=[{'name':im.name,'path':im.filepath}for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
audit={'source':str(source.relative_to(R)),'kit':str(kit.relative_to(R)),'appended_objects':len(after),'evaluated_meshes':sum(o.type=='MESH'for o in C.all_objects),'exact_evaluated_geometry_transforms_material_names':not changes,'external_images':external,'libraries':[x.filepath for x in bpy.data.libraries],'note':'Fresh factory scene appended kit. Source main camera/lights/world copied for isolated proof; environment geometry/haze absent. No scene artwork projection.'};(O/'append-audit.json').write_text(json.dumps(audit,indent=2))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
regions={'shoulder':(1660,515,1870,790)}
clay=bpy.data.materials.new('Kit validation neutral stone');clay.diffuse_color=(.46,.46,.46,1);clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.46,.46,.46,1);bs.inputs['Roughness'].default_value=.85
t=time.time()
for mode in ['painted','clay']:
 s.view_layers[0].material_override=clay if mode=='clay' else None
 for name,(x0,y0,x1,y1)in regions.items():
  s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885;s.render.filepath=str(O/f'{name}-{mode}.png');bpy.ops.render.render(write_still=True)
(O/'performance.json').write_text(json.dumps({'proof_render_seconds':time.time()-t,'native_frame_resolution':resolution,'regions':regions},indent=2))
