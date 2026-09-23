"""Refined native-derived cloud fields, private materials; sky and scene untouched."""
import bpy,numpy as np,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/clouds-199'
def apply(scene):
 C=bpy.data.collections['082 Derived flat clouds'];rows=[];images={};materials={}
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  for slot in ob.material_slots:
   old=slot.material;tex0=next(n for n in old.node_tree.nodes if n.type=='TEX_IMAGE');family=Path(tex0.image.filepath).stem
   if family not in images:
    a=np.load(O/'assets'/f'{family}.npz')['rgba'];h,w=a.shape[:2];im=bpy.data.images.new('199 Native subtle cloud '+family,width=w,height=h,alpha=True,float_buffer=True);im.colorspace_settings.name='Linear Rec.709';im.pixels.foreach_set(np.flipud(a).ravel());im.filepath_raw=str(O/'assets'/f'{family}.exr');im.file_format='OPEN_EXR';im.save();im.pack();images[family]=im
   if old not in materials:
    m=old.copy();m.name='199 Subtle layered '+old.name;m['199 native cloud refinement']=True;n=m.node_tree.nodes;l=m.node_tree.links;tex=next(x for x in n if x.type=='TEX_IMAGE');tex.image=images[family];tex.interpolation='Linear';em=next(x for x in n if x.type=='EMISSION');l.new(tex.outputs['Color'],em.inputs['Color']);materials[old]=m
   slot.link='OBJECT';slot.material=materials[old];rows.append({'object':ob.name,'old_material':old.name,'new_material':slot.material.name,'family':family})
 return {'assignments':rows,'materials':len(materials),'packed_native_derived_images':len(images),'world_unchanged':True,'geometry_camera_layout_unchanged':True,'reference_pixels_used':False,'source':'Owned082 native cloud render alpha and pigment values','asset_audit':json.loads((O/'asset-audit.json').read_text())}
if __name__=='__main__':
 audit=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));print('199_READY')
