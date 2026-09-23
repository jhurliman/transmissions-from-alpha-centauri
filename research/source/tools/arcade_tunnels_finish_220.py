import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/arcade-tunnels-220'
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
from mathutils import Vector
audit=json.loads((O/'audit.json').read_text());checks=[]
for row in audit['objects']:
 ob=s.objects[row['object']];D=Vector(row['inward_horizontal_direction']);n=row['section_points']*2
 advances=[(ob.data.vertices[2*n+i].co-ob.data.vertices[n+i].co).dot(D)for i in range(n)]
 assert min(advances)>0,(ob.name,min(advances))
 checks.append({'bay':row['bay'],'all_inner_outer_vertices_checked':n,'minimum_forward_advance_m':min(advances),'maximum_forward_advance_m':max(advances)})
(O/'entry-monotonicity.json').write_text(json.dumps({'all_pass':True,'checks':checks},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'smooth-haze-scene.blend'))
from haze_texture_219 import apply
a=apply(s);(O/'haze-219-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('220 HAZE V2 READY',flush=True)
