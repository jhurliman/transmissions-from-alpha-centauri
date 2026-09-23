"""Native restrained window/entry weathering, retaining all232 meshes and layout."""
import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from entrance_weathering_227 import Paint

def finish(base,role):
 m=base.copy();m.name='233 '+role+' | '+base.name;p=Paint(m);op=p.op;l=p.l
 em=next(n for n in p.n if n.type=='EMISSION');old=em.inputs['Color'].links[0].from_socket if em.inputs['Color'].is_linked else tuple(em.inputs['Color'].default_value)
 tc=p.node('ShaderNodeTexCoord','member-local bounds');sep=p.node('ShaderNodeSeparateXYZ','member axes');l.new(tc.outputs['Generated'],sep.inputs[0]);u,z=sep.outputs['Y'],sep.outputs['Z']
 geo=p.node('ShaderNodeNewGeometry','world variation');fine=p.noise(geo.outputs['Position'],38,2);mid=p.noise(geo.outputs['Position'],7,2)
 edge=p.remap(op('MINIMUM',op('MINIMUM',u,op('SUBTRACT',1,u)),op('MINIMUM',z,op('SUBTRACT',1,z))),.015,.11,1,0)
 basal=p.remap(z,.01,.24,1,0)
 streak=p.remap(p.noise(p.vec(op('MULTIPLY',u,20),op('MULTIPLY',z,.9),0),1,2),.56,.69)
 streak=op('MULTIPLY',streak,p.remap(z,.10,1,.05,.7))
 light=next((n.outputs[0] for n in p.n if n.type=='MAP_RANGE' and abs(n.inputs['To Min'].default_value-.46)<.001),None)
 def lit(c):return p.mix(1,(*c,1),light,'existing native light','MULTIPLY') if light else (*c,1)
 if role=='glass':
  if 'Broken pane' in base.name:old=lit((.10,.13,.15))
  elif light:old=p.mix(1,old,light,'bounded actual glass light','MULTIPLY')
  # No reflection plane: sheltered upper glass, diffuse dirt below the rebate.
  body=p.mix(p.remap(z,.1,.95,.05,.27),old,(.020,.028,.044,1),'upper shelter')
  dust=op('MULTIPLY',basal,p.remap(mid,.30,.67,.25,.70))
  body=p.mix(dust,body,(.105,.096,.087,1),'uneven sill dust')
  body=p.mix(op('MULTIPLY',streak,.25),body,(.12,.135,.145,1),'fine rain residue')
 else:
  old=p.mix(1,old,(.85,.85,.85,1),'weathered frame value','MULTIPLY')
  chip=op('MULTIPLY',edge,p.remap(op('ADD',op('MULTIPLY',mid,.65),op('MULTIPLY',fine,.35)),.49,.65))
  body=p.mix(op('MULTIPLY',chip,.65),old,lit((.10,.059,.035)),'small rooted oxide loss')
  body=p.mix(op('MULTIPLY',op('MULTIPLY',chip,p.remap(fine,.50,.7)),.55),body,lit((.26,.13,.062)),'warm oxide grains')
  body=p.mix(op('MULTIPLY',streak,.15),body,lit((.18,.10,.055)),'thin rain discoloration')
  body=p.mix(op('MULTIPLY',basal,.12),body,lit((.25,.24,.21)),'settled sill dust')
 l.new(body,em.inputs['Color']);m['233 role']=role;return m

def apply(scene):
 roots=bpy.data.collections['215 Short alley composition'].objects
 leaves=set()
 def walk(c):
  for o in c.objects:
   if o.instance_collection:walk(o.instance_collection)
   elif o.type=='MESH':leaves.add(o)
 for root in roots:walk(root.instance_collection)
 cache={};rows=[]
 for o in leaves:
  if not o.name.startswith(('230 ','232 ')):continue
  if any(t in o.name for t in ('glass pane','intact sibling pane','pane remnant')):role='glass'
  elif any(t in o.name for t in ('deep frame','deep sill','deep head','picture frame','sliding sash','sliding lower','closed recessed entry')):role='frame and door'
  else:continue
  for sl in o.material_slots:
   old=sl.material
   if not old:continue
   key=(old.name,role)
   if key not in cache:cache[key]=finish(old,role)
   sl.link='OBJECT';sl.material=cache[key]
   rows.append({'object':o.name,'role':role,'source':old.name,'new':sl.material.name})
 assert rows
 return {'study':233,'method':'Private native material graphs; existing light response, gravity-aligned residue, edge-rooted oxide and sill dirt. No reflection or image overlays.','geometry_changed':False,'assignments':rows,'private_material_count':len(cache),'references':['UCL-01','RS-01','RS-02']}
if __name__=='__main__':
 O=R/'art/studies/facade-finish-233';O.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/midground-damage-232/scene.blend'))
 a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('233 material pass saved',len(a['assignments']),flush=True)
