"""Integrate detailed native ruin, painted masonry and local linework."""
import bpy,json,sys,os,time
from mathutils import Matrix
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_materials_110 import apply_materials
O=R/'art/studies/coliseum-110';started=time.time();bpy.ops.wm.open_mainfile(filepath=str(O/'geometry.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];campos=s.camera.matrix_world.translation;xf=Matrix.Translation(campos)@Matrix.Diagonal((.715,.715,.715,1))@Matrix.Translation(-campos)
for ob in C.objects:ob.matrix_world=xf@ob.matrix_world
from coliseum_damage_detail_110 import add_damage_details
damage_audit=add_damage_details(C)
counts=apply_materials(C)
# Restrict existing line styles to the previously inked scene. New ruin gets finer ink.
ex=bpy.data.collections.new('110 Existing ink exclusions');s.collection.children.link(ex);soil=bpy.data.collections.get('077 Soil fractures and mineral scatter')
if soil:ex.children.link(soil)
ex.children.link(C)
for vl in s.view_layers:
 fs=vl.freestyle_settings
 for ls in list(fs.linesets):
  if ls.select_by_collection and ls.collection==soil and ls.collection_negation=='EXCLUSIVE':ls.collection=ex
 for title,thick,col,crease in [('110 Landmark contours',2.0,(.035,.025,.04),False),('110 Landmark fine creases',1.0,(.07,.05,.065),True)]:
  ls=fs.linesets.new(title);ls.select_by_collection=True;ls.collection=C;ls.collection_negation='INCLUSIVE';ls.select_by_edge_types=True;ls.select_silhouette=not crease;ls.select_border=not crease;ls.select_crease=crease;ls.select_contour=not crease;ls.select_external_contour=not crease;ls.select_material_boundary=False;ls.select_edge_mark=False;ls.linestyle.thickness=thick;ls.linestyle.color=col
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
contacts=bpy.data.collections.new('110 Contact ink source');s.collection.children.link(contacts)
for ob in C.objects:
 if ob.get('coliseum_role') in ['wall','band','tower','pier','fracture']:contacts.objects.link(ob)
usage_before={}
for ob in s.objects:
 if ob.type=='MESH':usage_before[ob.name]=ob.lineart.usage;ob.lineart.usage='INCLUDE' if ob in set(C.objects) else 'EXCLUDE'
ink=add_intersection_ink(contacts,'110 Landmark contact ink',radius=.09)
try:ink_count=bake_intersection_ink(ink)
except RuntimeError:ink_count=0
for name,usage in usage_before.items():
 if bpy.data.objects.get(name):bpy.data.objects[name].lineart.usage=usage
(O/'contact-ink.json').write_text(json.dumps({'strokes':ink_count,'source':'landmark structural parts only'}))
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
(O/'finish-audit.json').write_text(json.dumps({'role_counts':counts,'camera_centered_scale':.715,'projection_preserved':True,'reason':'Reduce excessive physical haze path while staying behind far city','painted_reference':'UCL-01','texture_images_used':False,'generation_seconds':time.time()-started,'new_styles':['110 Landmark contours','110 Landmark fine creases'],'existing_styles':'same settings; new landmark excluded from old style coverage'},indent=2))
if os.environ.get('COLISEUM_PREVIEW')=='1':
 s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=450/1440;s.render.border_max_x=1000/1440;s.render.border_min_y=1-470/1082;s.render.border_max_y=1-80/1082;s.render.filepath=str(O/'paint-preview.png')
bpy.ops.render.render(write_still=True)
