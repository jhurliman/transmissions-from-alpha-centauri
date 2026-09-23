import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/components/facades/v014'
bpy.ops.wm.open_mainfile(filepath=str(O/'service_window_bay.blend'))
bpy.context.view_layer.update();col=bpy.data.collections['PROOF | service_window_bay']
cap=next(o for o in col.objects if o.instance_collection and o.instance_collection.get('part_id')=='duct_cap')
points=[cap.matrix_world@ob.matrix_world@Vector(p) for ob in cap.instance_collection.objects if ob.type=='MESH' for p in ob.bound_box]
roof=max((o for o in col.objects if o.name.startswith('Chase end closure')),key=lambda o:max(v.co.z for v in o.data.vertices))
roofbottom=min((roof.matrix_world@v.co).z for v in roof.data.vertices)
clearance=roofbottom-max(p.z for p in points)
assert clearance>.10,clearance
r={'terminal_cap_to_cover_clearance_m':clearance,'pass':True,'scope':'Actual mesh bounds, including cap fasteners; no global collision claim.'}
(O/'clearance-audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
