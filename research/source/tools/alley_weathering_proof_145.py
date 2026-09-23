"""Combined native panel system proof; production143 remains untouched."""
import bpy,sys,json,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-weathering-145/combined';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/alley-weathering-145/geometry/scene.blend'));s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.view_settings.view_transform='Standard';s.view_settings.look='None';s.render.resolution_x=3840;s.render.resolution_y=1745;s.render.resolution_percentage=100;s.view_layers[0].material_override=None
from alley_panel_material_145 import make_panel_material
from alley_surface_details_145 import apply_panels
panelmat=make_panel_material();d=json.loads((R/'art/studies/alley-weathering-145/geometry/audit.json').read_text());specs=[]
for p in d['panels']:
 q=dict(p);q['object']=bpy.data.objects[p['object']];q['object'].data.materials[0]=panelmat;specs.append(q)
a=apply_panels(specs,seed=145,occupancy=.70,add_nicks=False)
for o in s.objects:
 if o.type=='LIGHT':
  o.data.color=(1,.69,.46)if'Warm'in o.name else(.50,.65,1)
world=s.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.13,.20,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.40
s.render.use_compositing=False;s.render.use_freestyle=True;s.render.line_thickness=1
fs=s.view_layers[0].freestyle_settings
for ls in list(fs.linesets):fs.linesets.remove(ls)
ls=fs.linesets.new('145 Visible panel damage contours');ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True;ls.select_material_boundary=False;ls.linestyle.color=(.02,.014,.025);ls.linestyle.thickness=.8
s.render.filepath=str(O/'combined-4k.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));(O/'details-audit.json').write_text(json.dumps(a,indent=2));t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,1745],'scope':'Standalone component proof; actual alleycamera validation pending'}))
