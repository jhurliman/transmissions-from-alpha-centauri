"""Broad scene-readable runoff and ragged light-catching stains on distant openings."""
import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from entrance_weathering_227 import Paint

def finish(base,role):
 m=base.copy();m.name='234 Broad stains '+role+' | '+base.name;p=Paint(m);op=p.op;l=p.l
 em=next(n for n in p.n if n.type=='EMISSION');old=em.inputs['Color'].links[0].from_socket if em.inputs['Color'].is_linked else tuple(em.inputs['Color'].default_value)
 tc=p.node('ShaderNodeTexCoord','panel bounds');ax=p.node('ShaderNodeSeparateXYZ','panel axes');l.new(tc.outputs['Generated'],ax.inputs[0]);u,z=ax.outputs['Y'],ax.outputs['Z']
 geo=p.node('ShaderNodeNewGeometry','world variation');inst=p.node('ShaderNodeObjectInfo','unequal component variation');seed=inst.outputs['Random']
 fine=p.noise(geo.outputs['Position'],13,3)
 # Three wide unequal trails taper down from upper rebates, with translucent shoulders.
 trails=0
 for c,w,length in ((.19,.075,.88),(.61,.115,.64),(.84,.045,.96)):
  center=op('ADD',c,op('MULTIPLY',op('SUBTRACT',seed,.5),.14));down=op('SUBTRACT',1,z);t=op('DIVIDE',down,length)
  width=op('MULTIPLY',w,p.remap(t,0,1,1,.12));distance=op('ABSOLUTE',op('SUBTRACT',u,center))
  core=p.remap(op('DIVIDE',distance,width),.24,1,1,0);fade=p.remap(t,.35,1,1,0)
  trails=op('MAXIMUM',trails,op('MULTIPLY',core,fade))
 trails=op('MULTIPLY',trails,p.remap(fine,.15,.8,.70,1))
 # A large connected stain, with small ragged edge detail, modulates existing lighting.
 broad=p.noise(p.vec(op('MULTIPLY',u,2.2),op('MULTIPLY',z,2.8),seed),1,2)
 field=op('ADD',broad,op('MULTIPLY',fine,.10));mask=p.remap(field,.48,.64)
 basal=p.remap(z,.05,.50,1,0);mask=op('MAXIMUM',mask,op('MULTIPLY',basal,p.remap(fine,.38,.65)))
 if role=='glass':
  body=p.mix(op('MULTIPLY',mask,.52),old,p.mix(1,old,(1.75,1.62,1.42,1),'warm stained glass response','MULTIPLY'),'broad diffuse mineral residue')
  body=p.mix(op('MULTIPLY',trails,.72),body,p.mix(1,old,(.40,.43,.49,1),'dark rain channel','MULTIPLY'),'long translucent runoff')
  # A wider low-opacity border keeps the streak readable without hard graphic stripes.
  body=p.mix(op('MULTIPLY',op('MULTIPLY',basal,mask),.20),body,(.15,.133,.108,1),'lower mineral bloom')
 else:
  body=p.mix(op('MULTIPLY',mask,.48),old,p.mix(1,old,(1.40,1.29,1.15,1),'sun-warmed stain response','MULTIPLY'),'ragged broad light stain')
  body=p.mix(op('MULTIPLY',trails,.66),body,p.mix(1,old,(.44,.39,.35,1),'oxide runoff value','MULTIPLY'),'wide fading rain stain')
 l.new(body,em.inputs['Color']);m['234 broad stain role']=role;return m

def apply(scene):
 leaves=set()
 def walk(c):
  for o in c.objects:
   if o.instance_collection:walk(o.instance_collection)
   elif o.type=='MESH':leaves.add(o)
 for root in bpy.data.collections['215 Short alley composition'].objects:walk(root.instance_collection)
 cache={};rows=[]
 for ob in leaves:
  for sl in ob.material_slots:
   old=sl.material
   if not old:continue
   role=old.get('233 role')
   if not role and 'receiver' in ob.name.lower() and ('230 ' in ob.name or '234 ' in ob.name):role='facade receiver'
   if not role:continue
   key=(old,role)
   if key not in cache:cache[key]=finish(old,role)
   sl.link='OBJECT';sl.material=cache[key];rows.append({'object':ob.name,'role':role,'source':old.name,'material':sl.material.name})
 return {'study':234,'assignments':rows,'materials':len(cache),'technique':'Three broad unequal tapered gravity trails; translucent runoff over a large ragged warm-light stain, with bottom-weighted fine breakup. Existing233 dark base retained.','geometry_unchanged':True}
