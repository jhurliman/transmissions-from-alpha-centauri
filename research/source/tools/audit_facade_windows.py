"""Ray-check the actual instance geometry: closed pane versus open/broken cavity."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/components/facades/v011';checks=[]
for key,x,expected in [('window_bay',.55,'pane'),('window_open',.55,'backing'),('window_broken',-.55,'backing')]:
 bpy.ops.wm.open_mainfile(filepath=str(O/(key+'.blend')))
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 hit,p,n,idx,ob,m=bpy.context.scene.ray_cast(dg,Vector((x,-2,1.60)),Vector((0,1,0)))
 expected_name='Full-height blue glass' if expected=='pane' else 'Interior shadow backing'
 ok=hit and ob.name.startswith(expected_name)
 checks.append({'variant':key,'hit_object':ob.name if hit else None,'depth':p.y if hit else None,'expected':expected_name,'pass':ok})
assert all(c['pass'] for c in checks),checks
col=bpy.data.collections['PROOF | window_broken']
kick=next(o for o in col.objects if o.instance_collection and o.instance_collection.get('part_id')=='kick_sloped_15')
window=next(o for o in col.objects if o.instance_collection and o.instance_collection.get('part_id')=='window_slider_broken')
face=next(o for o in kick.instance_collection.objects if o.name.startswith('Continuous frame-to-frame kick'))
verts=[kick.matrix_world@face.matrix_world@v.co for v in face.data.vertices][:4]
left_frame=next(o for o in col.objects if o.instance_collection and o.instance_collection.get('part_id')=='plate_narrow' and o.location.x<0)
right_frame=next(o for o in col.objects if o.instance_collection and o.instance_collection.get('part_id')=='plate_narrow' and o.location.x>0)
side_half=.5*json.loads(left_frame.instance_collection['interface_json'])['width']
assert abs(verts[0].y)<1e-6 and abs(verts[1].y)<1e-6
assert abs(verts[2].y-window.location.y)<1e-6 and abs(verts[2].z-window.location.z)<1e-6
assert abs(verts[0].x-(left_frame.location.x+side_half))<1e-6
assert abs(verts[1].x-(right_frame.location.x-side_half))<1e-6
hit,point,normal,index,obj,mat=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((0,-2,.28)),Vector((0,1,0)))
assert hit and obj.name.startswith('Continuous frame-to-frame kick'),obj.name if hit else 'No kick hit'
checks.append({'kick_surface_unobstructed':True,'kick_lower_edge_flush':True,'kick_upper_edge_matches_inset_window':True,'kick_spans_side_frame_to_side_frame':True,'measured_inset':verts[2].y})
(O/'opening-audit.json').write_text(json.dumps({'actual_geometry_ray_checks':checks,'scope':'Checks one unobstructed sample through each state; not a general collision audit.'},indent=2))
print(json.dumps(checks))
