"""Light native weathering on the four nearest-right visible blue window panes only."""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from entrance_weathering_227 import Paint
TARGET_ROOTS=['Architecture | window_bay.005','Architecture | window_open.003']
TARGET_PANES={'Full-height blue glass.005','Full-height blue glass.006','Full-height blue glass.008','Full-height blue glass.009'}

def finish(base,axis):
 m=base.copy();m.name='235 Light near glass | '+base.name;p=Paint(m);op=p.op;l=p.l
 em=next(n for n in p.n if n.type=='EMISSION');old=em.inputs['Color'].links[0].from_socket if em.inputs['Color'].is_linked else tuple(em.inputs['Color'].default_value)
 tex=p.node('ShaderNodeTexCoord','near pane-local coordinates');a=p.node('ShaderNodeSeparateXYZ','near glass axes');l.new(tex.outputs['Generated'],a.inputs[0]);u,z=a.outputs[axis],a.outputs['Z']
 ob=p.node('ShaderNodeObjectInfo','unequal pane variation');seed=ob.outputs['Random'];geo=p.node('ShaderNodeNewGeometry','world surface variation');fine=p.noise(geo.outputs['Position'],21,2)
 # A few unequal rain trails taper gradually, with soft translucent shoulders.
 trails=0
 for center,width,length in[(.16,.055,.86),(.47,.036,.64),(.74,.065,.96),(.91,.024,.48)]:
  c=op('ADD',center,op('MULTIPLY',op('SUBTRACT',seed,.5),.075));down=op('SUBTRACT',1,z);t=op('DIVIDE',down,length);w=op('MULTIPLY',width,p.remap(t,0,1,1,.28));distance=op('ABSOLUTE',op('SUBTRACT',u,c));body=p.remap(op('DIVIDE',distance,w),.12,1,1,0);fade=p.remap(t,.28,1,1,0);trails=op('MAXIMUM',trails,op('MULTIPLY',body,fade))
 trails=op('MULTIPLY',trails,p.remap(fine,.12,.85,.76,1))
 field=p.noise(p.vec(op('MULTIPLY',u,2.1),op('MULTIPLY',z,2.6),seed),1,2);mask=p.remap(op('ADD',field,op('MULTIPLY',fine,.045)),.48,.67)
 lightstain=p.mix(1,old,(1.65,1.52,1.27,1),'subtle preserved-light warmer stain','MULTIPLY');body=p.mix(op('MULTIPLY',mask,.40),old,lightstain,'low-opacity broad stain')
 dark=p.mix(1,old,(.40,.47,.60,1),'quiet rain channel','MULTIPLY');body=p.mix(op('MULTIPLY',trails,.56),body,dark,'four unequal soft rain traces')
 # Irregular translucent residue rises into the visible pane above the frame rebate.
 basal=p.remap(z,.035,op('ADD',.17,op('MULTIPLY',field,.16)),1,0);dust=op('MULTIPLY',basal,p.remap(fine,.25,.72,.24,.52));body=p.mix(dust,body,(.15,.145,.16,1),'restrained lower mineral deposit')
 l.new(body,em.inputs['Color']);m['235 near window light weathering']=True;m['235 role']='Nearest right glass only';return m

def apply(scene):
 if scene.get('near_windows235_applied'):raise RuntimeError('235 near windows already applied')
 copies={};cols={};materials={};rows=[];roots=[]
 # Copy only the collection path and target pane object IDs; every frame and other leaf stays shared unchanged.
 def copy_path(c):
  if c in cols:return cols[c]
  new=bpy.data.collections.new('235 Near glass private '+c.name);new.use_fake_user=True;new.instance_offset=c.instance_offset;cols[c]=new
  for ob in c.objects:
   if ob.name in TARGET_PANES:
    q=ob.copy();q.name='235 Near right '+ob.name;copies[ob]=q;new.objects.link(q)
    xyz=[max(v.co[k]for v in ob.data.vertices)-min(v.co[k]for v in ob.data.vertices)for k in range(3)];axis='X'if xyz[0]>xyz[1]else'Y'
    for slot in q.material_slots:
     old=slot.material;key=(old,axis)
     if key not in materials:materials[key]=finish(old,axis)
     slot.link='OBJECT';slot.material=materials[key];rows.append({'source_object':ob.name,'private_object':q.name,'source_material':old.name,'new_material':slot.material.name,'horizontal_axis':axis,'mesh_data_shared_exact':q.data==ob.data})
   elif ob.instance_collection and any(x.name in TARGET_PANES for x in ob.instance_collection.all_objects):
    q=ob.copy();q.name='235 Near glass path '+ob.name;q.instance_collection=copy_path(ob.instance_collection);new.objects.link(q)
   else:new.objects.link(ob)
  for child in c.children:
   if any(o.name in TARGET_PANES for o in child.all_objects):new.children.link(copy_path(child))
   else:new.children.link(child)
  return new
 for name in TARGET_ROOTS:
  root=scene.objects[name];old=root.instance_collection;root.instance_collection=copy_path(old);roots.append({'object':name,'old_collection':old.name,'new_collection':root.instance_collection.name})
 assert {o.name for o in copies}==TARGET_PANES,[o.name for o in copies]
 # Preserve exactly the previous Freestyle inclusion/exclusion memberships for each pane ID.
 ink=[]
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if not(ls.select_by_collection and ls.collection):continue
   for old,q in copies.items():
    if old.name in ls.collection.all_objects and q.name not in ls.collection.all_objects:ls.collection.objects.link(q);ink.append({'layer':vl.name,'style':ls.name,'pane':q.name})
 scene['near_windows235_applied']=True;bpy.context.view_layer.update()
 return {'study':235,'source':bpy.data.filepath,'scope':'Nearest right blue facade, four visible panes in two original assemblies','root_collection_bindings':roots,'pane_material_bindings':rows,'new_materials':len(materials),'original_geometry_and_materials_unchanged':True,'frames_and_position_unchanged':True,'far234windows_unchanged':True,'ink_membership_copied':ink,'method':'V2: four unequal wider tapered rain traces, irregular lower17–33% translucent mineral fringe, broad warmer stain multiplying original native light. No reflections or image overlay.','review':'CPU scoped candidate; combined native render pending'}
if __name__=='__main__':
 O=R/'art/studies/near-window-weathering-235';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/far-weathering-234/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('235 NEAR WINDOWS READY',flush=True)
