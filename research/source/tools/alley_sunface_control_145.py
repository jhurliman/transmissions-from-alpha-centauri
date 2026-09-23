"""Material-only sun-facing control at the unchanged production camera and lighting."""
import bpy,sys,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-weathering-145/actual/sunface';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/alley-rust-143/scene.blend'));s=bpy.context.scene
inventory=json.loads((O.parent/'visible-panel-inventory.json').read_text());q=next(q for q in inventory if q['name']=='Folded sheet face.108' and q['parent']=='right_vertical_galleries');h=bpy.data.objects[q['parent']];target=bpy.data.objects[q['name']]
# Clone the instance tree and override this surface alone. Parent transforms stay fixed.
clones={}
def duplicate(c):
 new=bpy.data.collections.new('145 Sunface diagnostic '+c.name)
 for ob in c.objects:
  if ob==target:
   original=ob;ob=ob.copy();ob.name=original.name+" | 145 sunface control";clones[original]=ob
  elif ob.instance_collection:
   original=ob;ob=ob.copy();ob.instance_collection=duplicate(original.instance_collection)
  new.objects.link(ob)
 for ch in c.children:new.children.link(duplicate(ch))
 return new
private=duplicate(h.instance_collection);h.instance_collection=private;target_new=clones[target]
M=Matrix(q['matrix']);origin=M@Vector(q['local_bounds'][0]);u=M.to_3x3()@Vector((1,0,0));v=M.to_3x3()@Vector((0,0,1))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True
box=[max(0,int(q['bounds'][0])-40),max(0,int(q['bounds'][1])-60),min(3840,int(q['bounds'][2])+80),min(2885,int(q['bounds'][3])+50)];s.render.border_min_x=box[0]/3840;s.render.border_max_x=box[2]/3840;s.render.border_min_y=1-box[3]/2885;s.render.border_max_y=1-box[1]/2885
s.render.filepath=str(O/'before.png');bpy.ops.render.render(write_still=True)
from alley_panel_material_145 import make_panel_material
material=make_panel_material('145 Sunface coating diagnostic',origin=tuple(origin),across=tuple(u),up=tuple(v),span=(q['dim'][0],q['dim'][2]))
for slot in target_new.material_slots:slot.link='OBJECT';slot.material=material
s.render.filepath=str(O/'after.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
(O/'audit.json').write_text(json.dumps({'target':q,'crop_bounds':box,'camera_and_lights_unchanged':True,'only_material_override':True,'freestyle_disabled_for_both_material_controls':True,'production_scene_unchanged':True},indent=2))
