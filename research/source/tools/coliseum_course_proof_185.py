"""Read-only native right-cornice shape/contact diagnosis on retained173."""
import bpy,json,time,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
O=R/'art/studies/coliseum-185/geometry';O.mkdir(parents=True,exist_ok=True)
cfg={
 'source':'art/studies/coliseum-185/geometry/HELD-diagnostic.blend',
 'references':{'UCL-01':'Unequal attached broken courses and readable retained mass','UCL-02':'Exposed core/return plane hierarchy','DP-03':'Detailed structure subordinate to coherent large planes'},
 'hypothesis':'The contested right-cornice knot may result from several genuine short course ends competing in projection; neutral matched views distinguish shape from pigment and explicit ink.',
 'crop':[2080,545,2310,775],
 'fixed':['Camera','Geometry and normals','Actual lights and haze','Saved materials and retained scene','No art mutation'],
 'changed_for_diagnosis':['Temporary explicit-ink visibility','Temporary neutral material on landmark solid surfaces only'],
 'criteria':['Identify meaningful course-end silhouette/interior plane roles before any simplification','Never treat physical dark contacts or mesh edge counts alone as false ink','Preserve true black architectural joints in final art'],
}

bpy.ops.wm.open_mainfile(filepath=str(R/cfg['source']))
s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
x0,y0,x1,y1=cfg['crop'];s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
ink=[o for o in list(C.all_objects)+[bpy.data.objects['110 Landmark contact ink']] if (re.search(r'\bink\b',o.name.lower()) or o.type in {'GREASEPENCIL','GPENCIL'}) and not o.hide_render]
timings={}
def render(name):
 t=time.time();s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);timings[name]=time.time()-t

for o in ink:o.hide_render=True
render('painted-without-ink')
clay=bpy.data.materials.new('184 Diagnostic neutral stone');clay.use_nodes=True
bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.46,.46,.46,1);bs.inputs['Roughness'].default_value=.85
changed=[]
for o in C.all_objects:
 if o.type!='MESH' or re.search(r'\bink\b',o.name.lower()):continue
 for i,slot in enumerate(o.material_slots):
  if slot.material:
   changed.append([o.name,i,slot.material.name]);slot.link='OBJECT';slot.material=clay
render('clay-without-ink')

(O/'proof-audit.json').write_text(json.dumps({'configuration':cfg,'seconds':timings,'explicit_ink_hidden':[o.name for o in ink],'temporary_neutral_assignments':changed,'saved_scene_changed':False,'no_geometry_mutation':True,'limits':'Diagnostic neutral materials retain current light and volume transport. Freestyle disabled equally in every crop; explicit native mesh/curve/GP ink is toggled separately. No finished artwork or scene is saved.'},indent=2)+'\n')
