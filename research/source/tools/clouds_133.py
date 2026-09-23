"""Editable native-source cloud fidelity133; preserve plates, world, camera and scene."""
import bpy,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def apply(scene):
 C=bpy.data.collections.get('082 Derived flat clouds')
 if C is None:raise RuntimeError('Missing accepted cloud plates')
 rows=[];images={};materials={}
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  for slot in ob.material_slots:
   old=slot.material
   if old.get('133 cloud layered field'):continue
   tex0=next(n for n in old.node_tree.nodes if n.type=='TEX_IMAGE');family=Path(tex0.image.filepath).stem
   if family not in images:
    a=np.load(R/'art/studies/clouds-133/assets'/f'{family}.npz')['rgba'];h,w=a.shape[:2];im=bpy.data.images.new('133 Native layered '+family,width=w,height=h,alpha=True,float_buffer=True);im.colorspace_settings.name='Linear Rec.709';im.pixels.foreach_set(np.flipud(a).ravel());im.filepath_raw=str(R/'art/studies/clouds-133/assets'/f'{family}.exr');im.file_format='OPEN_EXR';im.save();im.pack();images[family]=im
   if old not in materials:
    m=old.copy();m.name='133 Fine-contour layered '+old.name;m['133 cloud layered field']=True;n=m.node_tree.nodes;l=m.node_tree.links;tex=next(x for x in n if x.type=='TEX_IMAGE');tex.image=images[family];tex.interpolation='Linear';em=next(x for x in n if x.type=='EMISSION');l.new(tex.outputs['Color'],em.inputs['Color']);materials[old]=m
   slot.link='OBJECT';slot.material=materials[old];rows.append({'object':ob.name,'old_material':old.name,'new_material':slot.material.name,'native_source_family':family})
 return {'cloud_assignments':rows,'new_materials':len(materials),'new_derived_images':len(images),'world_unchanged':True,'cloud_geometry_and_placements_unchanged':True,'source':'Owned082 native-derived pigment assets; procedural distance fields, no reference pixels','config':'config/clouds-133.json'}
