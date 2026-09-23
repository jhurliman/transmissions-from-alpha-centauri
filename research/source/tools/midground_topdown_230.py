"""Actual native geometry overhead diagnostic. Run only after root releases render slot.
No scene source is saved or mutated on disk; clay view is not beauty acceptance.
"""
import bpy,sys,json,math,argparse,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1]

def main():
 args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
 ap=argparse.ArgumentParser();ap.add_argument('--source',default=str(R/'art/studies/midground-230/scene.blend'));ap.add_argument('--output',default=str(R/'art/studies/midground-230/topdown-native.png'));opts=ap.parse_args(args)
 time.sleep(5)
 previous=Path(opts.source).stat().st_size
 while True:
  time.sleep(3);current=Path(opts.source).stat().st_size
  if current==previous:break
  previous=current
 bpy.ops.wm.open_mainfile(filepath=opts.source);source=bpy.context.scene
 roots=[o for o in bpy.data.collections['215 Short alley composition'].objects if o.instance_collection];assert len(roots)==18,len(roots)
 s=bpy.data.scenes.new('230 Native overhead diagnostic');s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.device='CPU';s.render.resolution_x=1024;s.render.resolution_y=1536;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.render.use_freestyle=False;s.render.use_compositing=False
 s.world=bpy.data.worlds.new('230 Diagnostic neutral world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.35,.40,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 for root in roots:
  ob=root.copy();ob.name='Diagnostic '+root.name;s.collection.objects.link(ob);ob.matrix_world=root.matrix_world.copy()
 clay=bpy.data.materials.new('230 Diagnostic pale clay');clay.diffuse_color=(.53,.58,.64,1);clay.use_nodes=True;p=clay.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.53,.58,.64,1);p.inputs['Roughness'].default_value=.8;s.view_layers[0].material_override=clay;s.view_layers[0].use_freestyle=False
 # 128m vertical span: y36..164. Width85.33m preserves geometry aspect; x±25 is centered with margins.
 ca=bpy.data.cameras.new('230 Overhead orthographic');cam=bpy.data.objects.new('230 Overhead orthographic',ca);s.collection.objects.link(cam);cam.location=(0,100,180);cam.rotation_euler=(0,0,0);ca.type='ORTHO';ca.ortho_scale=128;ca.clip_end=350;s.camera=cam
 q0=world_to_camera_view(s,cam,Vector((0,36,0)));q1=world_to_camera_view(s,cam,Vector((0,164,0)));ca.ortho_scale*=abs(q1.y-q0.y)
 ld=bpy.data.lights.new('230 Diagnostic broad key','AREA');light=bpy.data.objects.new('230 Diagnostic broad key',ld);s.collection.objects.link(light);light.location=(-35,70,100);light.rotation_euler=(Vector((0,100,0))-light.location).to_track_quat('-Z','Y').to_euler();ld.energy=70000;ld.shape='DISK';ld.size=70
 s.view_settings.view_transform='AgX';s.render.filepath=opts.output
 bpy.ops.render.render(write_still=True,scene=s.name)
 Path(opts.output).with_suffix('.json').write_text(json.dumps({'type':'Native existing-geometry orthographic diagnostic; clay override only','source':opts.source,'root_instances':len(roots),'render_size':[1024,1536],'world_footprint':{'x':[-128/3,128/3],'y':[36,164]},'preserve_aspect':True,'source_saved':False,'fog_characters_compositor_and_ink':'Not linked into diagnostic scene','not_beauty_acceptance':True},indent=2))
if __name__=='__main__':main()
