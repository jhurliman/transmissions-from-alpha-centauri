import bpy,sys,json,hashlib,time
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-131/surface'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-130/scene.blend'))
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1350/3840;s.render.border_max_x=2690/3840;s.render.border_min_y=1-1230/2885;s.render.border_max_y=1-320/2885
before={o.name:(o.data.as_pointer(),len(o.data.vertices),len(o.data.polygons)) for o in C.all_objects if o.type=='MESH'}
roles=[]
for o in C.all_objects:
 if o.type!='MESH':continue
 for i,slot in enumerate(o.material_slots):
  m=slot.material
  if m and (m.get('role')=='fracture' or 'Exposed masonry core' in m.name or 'Exposed warm masonry core' in m.name):roles.append({'object':o.name,'slot':i,'material':m.name,'faces':sum(p.material_index==i for p in o.data.polygons)})
(O/'classification.json').write_text(json.dumps(roles,indent=2))
s.render.filepath=str(O/'baseline.png');bpy.ops.render.render(write_still=True)
from coliseum_surface_131 import apply
a=apply(C,1.0);a['geometry_unchanged']=all(before[o.name]==(o.data.as_pointer(),len(o.data.vertices),len(o.data.polygons)) for o in C.all_objects if o.type=='MESH');a['excluded']='130 tunnels and native ink';(O/'audit.json').write_text(json.dumps(a,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'))
s.render.filepath=str(O/'candidate.png');bpy.ops.render.render(write_still=True)
s.render.image_settings.color_mode='BW';bpy.data.images['Render Result'].save_render(str(O/'candidate-gray.png'),scene=s)
