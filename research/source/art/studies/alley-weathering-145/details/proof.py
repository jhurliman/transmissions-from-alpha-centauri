import bpy,sys,json,hashlib,time
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-weathering-145/details'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/alley-weathering-145/geometry/scene.blend'));s=bpy.context.scene
from alley_panel_material_145 import make_panel_material
from alley_surface_details_145 import apply_panels
m=make_panel_material();d=json.loads((R/'art/studies/alley-weathering-145/geometry/audit.json').read_text());specs=[]
for p in d['panels']:
 q=dict(p);q['object']=bpy.data.objects[p['object']];q['object'].data.materials[0]=m;specs.append(q)
def hashes():return {o.name:hashlib.sha256(repr(([tuple(v.co)for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons])).encode()).hexdigest()for o in s.objects if o.type=='MESH'}
h=hashes();s.render.resolution_x=1920;s.render.resolution_y=873;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_compositing=False;s.render.use_freestyle=False;s.view_layers[0].material_override=None
s.render.filepath=str(O/'before.png');bpy.ops.render.render(write_still=True)
a=apply_panels(specs,seed=145,occupancy=.70,add_nicks=False);a['unchanged_original_meshes']=all(hashes().get(k)==v for k,v in h.items());a['original_mesh_count']=len(h);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'after.png');bpy.ops.render.render(write_still=True)
