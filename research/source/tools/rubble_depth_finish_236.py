"""Native depth-continuous rubble pigment and graded visible geometry ink."""
import bpy
from mathutils import Vector
from entrance_weathering_227 import Paint

def apply(scene):
 targets=[]
 for ob in scene.objects:
  if ob.type!='MESH':continue
  names=[c.name for c in ob.users_collection]
  if any(n.startswith('236') for n in names) or any(n in ('077 End rubble depth clusters','078 End rubble tangled structural remnants') for n in names):
   y=sum((ob.matrix_world@Vector(c)).y for c in ob.bound_box)/8
   if y>=31:targets.append((ob,y))
 assert targets,'No rubble targets'
 cache={};rows=[];bins=[[] for _ in range(8)]
 for ob,y in targets:
  t=max(0,min(1,(y-31)/18));k=min(7,int(t*8));bins[k].append(ob)
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes:continue
   if old not in cache:
    m=old.copy();m.name='236 Depth-soft rubble | '+old.name;p=Paint(m)
    em=next((n for n in p.n if n.type=='EMISSION'),None)
    if em:
     oldcolor=em.inputs['Color'].links[0].from_socket if em.inputs['Color'].is_linked else tuple(em.inputs['Color'].default_value)
     geo=p.node('ShaderNodeNewGeometry','236 actual fragment depth');ax=p.node('ShaderNodeSeparateXYZ','236 street depth');p.l.new(geo.outputs['Position'],ax.inputs[0])
     fade=p.remap(ax.outputs['Y'],31,49,0,.22,'236 continuous subdued distant pigment')
     # Existing atmospheric volume remains the principal haze; this modest
     # diffuse violet-mineral convergence keeps blue/rust variation visible.
     color=p.mix(fade,oldcolor,(.16,.135,.16,1),'236 depth contrast convergence');p.l.new(color,em.inputs['Color'])
    cache[old]=m
   slot.link='OBJECT';slot.material=cache[old]
  rows.append({'object':ob.name,'depth':y,'band':k})
 # Remove all duplicate stroke ownership while keeping native occlusion.
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if not(ls.select_by_collection and ls.collection):continue
   for ob,y in targets:
    if ls.collection_negation=='EXCLUSIVE':
     if ob.name not in ls.collection.objects:ls.collection.objects.link(ob)
    elif ob.name in ls.collection.objects:ls.collection.objects.unlink(ob)
 vl=scene.view_layers['215 Distant ink without atmospheric boundary'];styles=[]
 for k,objects in enumerate(bins):
  if not objects:continue
  t=k/7;c=bpy.data.collections.new('236 Rubble ink depth '+str(k));c.use_fake_user=True
  for ob in objects:c.objects.link(ob)
  ls=vl.freestyle_settings.linesets.new('236 Rubble transition '+str(k));ls.select_by_collection=True;ls.collection=c;ls.collection_negation='INCLUSIVE';ls.select_by_visibility=True;ls.visibility='VISIBLE';ls.select_by_edge_types=True
  for key in ['silhouette','border','crease','ridge_valley','suggestive_contour','material_boundary','contour','external_contour','edge_mark']:
   if hasattr(ls,'select_'+key):setattr(ls,'select_'+key,key in ['silhouette','border','crease','external_contour'])
  ls.linestyle.thickness=1.35-.65*t;ls.linestyle.alpha=.96-.20*t;ls.linestyle.color=tuple(a+(b-a)*t for a,b in zip((.015,.012,.022),(.075,.061,.080)))
  styles.append({'band':k,'count':len(objects),'thickness':ls.linestyle.thickness,'alpha':ls.linestyle.alpha})
 return {'targets':rows,'private_materials':len(cache),'styles':styles,'global_fog_unchanged':True,'material_fade':'Continuous world Y31–49, maximum22% violet-mineral blend'}
