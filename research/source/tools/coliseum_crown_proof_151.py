import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_crown_thickness_151 import apply,TARGETS
O=R/'art/studies/coliseum-151/geometry';O.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-149/scene.blend'));s=bpy.context.scene;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.resolution_percentage=100;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1425/3840;s.render.border_max_x=1640/3840;s.render.border_min_y=1-635/2885;s.render.border_max_y=1-440/2885;s.render.threads_mode='FIXED';s.render.threads=3;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library)
clay=bpy.data.materials.new('151 proof neutral');clay.diffuse_color=(.35,.35,.35,1);clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.35,.35,.35,1)
def render(name,isclay=False):
 slots=[]
 if isclay:
  for ob in C.all_objects:
   if ob.type=='MESH':
    for sl in ob.material_slots:slots.append((sl,sl.link,sl.material));sl.link='OBJECT';sl.material=clay
 s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
 for sl,link,mat in slots:sl.material=mat;sl.link=link
d=apply(C);(O/'audit.json').write_text(json.dumps(d,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'study.blend'));render('after-painted');render('after-clay',True)
