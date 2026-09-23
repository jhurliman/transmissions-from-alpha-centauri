"""Controlled145 weathering placement in a copy of preserved143 scene."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-weathering-145/actual';O.mkdir(exist_ok=True)
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]},indent=2));raise SystemExit
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/alley-rust-143/scene.blend'));s=bpy.context.scene
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")]);before=fingerprint(s);mats=material_snapshot()
from alley_weathering_placement_145 import apply
from alley_panel_material_145 import make_panel_material
from alley_surface_details_145 import apply_panels
result=apply(s);specs=result['panels'];u=Vector(specs[0]['u']);v=Vector(specs[0]['v']);normal=Vector(specs[0]['normal']);corners=[]
for p in specs:
 origin=Vector(p['origin'])
 for a,b in [(0,0),(p['width'],0),(0,p['height']),(p['width'],p['height'])]:corners.append(origin+Vector(p['u'])*a+Vector(p['v'])*b)
umin=min(q.dot(u)for q in corners);umax=max(q.dot(u)for q in corners);vmin=min(q.dot(v)for q in corners);vmax=max(q.dot(v)for q in corners);origin=u*umin+v*vmin+normal*Vector(specs[0]['origin']).dot(normal)
material=make_panel_material('145 Actual facade light response',origin=tuple(origin),across=tuple(u),up=tuple(v),span=(umax-umin,vmax-vmin))
for q in result['objects']:
 if q.type=='MESH'and q.material_slots:q.data.materials[0]=material
overrides_path=O/'rust-descriptor-overrides.json'
if overrides_path.exists():
 overrides=json.loads(overrides_path.read_text())
 for p in specs:p.update(overrides.get(p['id'],{}))
bpy.context.view_layer.update();details=apply_panels(specs,seed=145,occupancy=.7,add_nicks=False)
# Microink already renders as dark surface geometry. Structural Freestyle would inflate tiny dots.
exclusions=bpy.data.collections.get('110 Existing ink exclusions');micro=bpy.data.collections.get(details['disable_layers']['microink'])
if exclusions and micro:
 for q in micro.objects:
  if q.name not in exclusions.objects:exclusions.objects.link(q)

for p in specs:p['object']['145 requested_feature']=p.get('145 variant',p.get('id'))
after=fingerprint(s);ma=material_snapshot();changed={k:[f for f in val if val[f]!=after.get(k,{}).get(f)]for k,val in before.items()if val!=after.get(k)};hosts={a['host']for a in result['audit']};removed_allowed={n for a in result['audit']for n in a['removed_only_from_private_instance']}
for name,fields in changed.items():
 assert(name in hosts and fields==['instance'])or(name in removed_allowed and name not in after),(name,fields)
assert all(v==ma[k]for k,v in mats.items()),'An existing material graph changed'
fs=[]
for ls in s.view_layers[0].freestyle_settings.linesets:
 fs.append({'name':ls.name,'collection':ls.collection.name if ls.collection else None,'by_collection':ls.select_by_collection,'negation':ls.collection_negation})
boxes=[a['projected_bounds_4k']for a in result['audit']];crop=[max(0,min(a[0]for a in boxes)-70),max(0,min(a[1]for a in boxes)-40),min(3840,max(a[2]for a in boxes)+100),min(2885,max(a[3]for a in boxes)+100)]
report={'targets':result['audit'],'crop_bounds':crop,'material_origin':list(origin),'material_span':[umax-umin,vmax-vmin],'details':details,'ink_refresh':result.get('ink_cleanup',result.get('ink_audit')),'native_freestyle':fs,'microink_structural_outline_excluded':bool(exclusions and micro),'preservation':{'old_material_graphs_unchanged':True,'source_meshes_and_non_target_instances_unchanged':True,'changes':changed},'status':'First actual-camera proof; no95 claim or user approval'}
(O/'placement-audit.json').write_text(json.dumps(report,indent=2,default=str));s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_freestyle=True;s.render.use_compositing=False;s.render.use_border=False;s.render.use_crop_to_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('145 scene candidate saved',flush=True)
