import bpy,math,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-037';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-036/scene.blend'));s=bpy.context.scene
cam=s.camera.matrix_world.copy();lens=s.camera.data.lens
def srgb(h):
 vals=[int(h[i:i+2],16)/255 for i in (1,3,5)]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)+(1,)
palette={'Cladding | slate enamel':'#72769c','Cladding | pale mineral blue':'#8989aa','Cladding | warm neutral insert':'#a58b80','Structure | bare mineral':'#9d8c82','Structure | charcoal steel':'#535064','Recess | dark backing':'#292632','Infill | smoked blue opaque study':'#454d83','DUCT | muted blue-gray sheet':'#74799d'}
for m in bpy.data.materials:
 if not m.use_nodes:continue
 color=palette.get(m.name)
 if m.name.startswith('PIP | blue-gray'):color='#777b9f'
 if m.name.startswith('PIP | dark machined'):color='#515164'
 for n in m.node_tree.nodes:
  if n.type=='BSDF_PRINCIPLED' and color:
   n.inputs['Base Color'].default_value=srgb(color);n.inputs['Roughness'].default_value=.78;n.inputs['Coat Weight'].default_value=0;n.inputs['Specular IOR Level'].default_value=.22
   n.inputs['Metallic'].default_value=.35 if 'steel' in m.name.lower() else 0
# Retain native lighting, avoid a painted or projected finish.
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
for o in s.objects:
 if o.type=='LIGHT' and o.data.type=='SUN':o.data.energy=2.2;o.data.color=(1,.66,.45);o.data.angle=.10
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND':
  if n.name=='Background':n.inputs['Color'].default_value=(.39,.43,.66,1);n.inputs['Strength'].default_value=1.35
  else:n.inputs['Color'].default_value=srgb('#cf543c');n.inputs['Strength'].default_value=1
# A restrained silhouette pass; physical panel seams supply internal detail.
s.render.use_freestyle=True
fs=s.view_layers[0].freestyle_settings
for ls in list(fs.linesets):fs.linesets.remove(ls)
ls=fs.linesets.new('Selective geometry contours');ls.select_silhouette=True;ls.select_border=True;ls.select_crease=False;ls.select_contour=True;ls.select_external_contour=True;ls.select_material_boundary=False
line=ls.linestyle;line.color=(.055,.035,.067);line.alpha=.68;line.thickness=.65
s.render.line_thickness=1;s.cycles.samples=64
assert s.camera.matrix_world==cam and s.camera.data.lens==lens
(O/'settings.json').write_text(json.dumps({'palette_srgb_albedos':palette,'view_transform':'Standard','lines':'Native Freestyle silhouettes/borders; crease lines disabled','geometry':'unchanged','camera':'unchanged'},indent=2))
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
