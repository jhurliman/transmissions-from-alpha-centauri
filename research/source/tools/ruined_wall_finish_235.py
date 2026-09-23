"""Construction-led ruin finish: large light stains, runoff, and localized exposed aggregate."""
import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from entrance_weathering_227 import Paint

def finish(base,role):
 m=base.copy();m.name='235 Layered wall '+role+' | '+base.name;p=Paint(m);op=p.op;l=p.l
 em=next(n for n in p.n if n.type=='EMISSION')
 source=next((n.outputs[0] for n in p.n if n.type=='GROUP' and n.node_tree and n.node_tree.name.startswith('204 Half')),None)
 if source is None:source=em.inputs['Color'].links[0].from_socket if em.inputs['Color'].is_linked else tuple(em.inputs['Color'].default_value)
 # Remove inherited200 cloud multiplication BEFORE the preserved204 hue mapping.
 shade=next((n.outputs['Color'] for n in p.n if n.type=='VALTORGB' and n.label=='133 Broken-building shade families'),None)
 palette=next((n for n in p.n if n.type=='GROUP' and n.node_tree and n.node_tree.name.startswith('204 Half')),None)
 if shade is not None and palette is not None:
  quiet=p.mix(1,shade,(.82,.82,.82,1),'quiet mineral base','MULTIPLY')
  ao=p.node('ShaderNodeAmbientOcclusion','local construction shelter');ao.inputs['Distance'].default_value=1.2
  quiet=p.mix(.30,quiet,ao.outputs['Color'],'retained contact shelter','MULTIPLY');l.new(quiet,palette.inputs[0])
 geo=p.node('ShaderNodeNewGeometry','actual wall surface');ax=p.node('ShaderNodeSeparateXYZ','world axes');l.new(geo.outputs['Position'],ax.inputs[0]);ns=p.node('ShaderNodeSeparateXYZ','world face normal');l.new(geo.outputs['Normal'],ns.inputs[0]);choose=op('GREATER_THAN',op('ABSOLUTE',ns.outputs['X']),.6)
 u=op('ADD',op('MULTIPLY',choose,ax.outputs['Y']),op('MULTIPLY',op('SUBTRACT',1,choose),ax.outputs['X']));z=ax.outputs['Z']
 tex=p.node('ShaderNodeTexCoord','whole wall extent');g=p.node('ShaderNodeSeparateXYZ','height on remnant');l.new(tex.outputs['Generated'],g.inputs[0])
 medium=p.noise(geo.outputs['Position'],2.4,2.6);fine=p.noise(geo.outputs['Position'],18,2)
 field=op('ADD',p.noise(geo.outputs['Position'],.42,2),op('MULTIPLY',medium,.12));mask=p.remap(field,.53,.61)
 def mul(v,c,label):return p.mix(1,v,(*c,1),label,'MULTIPLY')
 body=p.mix(op('MULTIPLY',mask,.25),source,mul(source,(1.42,1.28,1.11),'warm grazing stain'),'large ragged light stain')
 rain=p.noise(p.vec(op('MULTIPLY',u,3.7),op('MULTIPLY',z,.27),0),1,2)
 rain=p.remap(rain,.54,.69);rain=op('MULTIPLY',rain,p.remap(medium,.27,.62,.20,.90))
 origin=p.remap(g.outputs['Z'],.18,.94,.08,.75)
 body=p.mix(op('MULTIPLY',rain,origin),body,mul(source,(.53,.48,.46),'wet sheltered tone'),'long interrupted gravity wash')
 basal=p.remap(z,.10,2.3,1,0)
 if role=='core':
  body=mul(body,(1.12,1.09,1.02),'exposed dry mineral')
  cells=p.node('ShaderNodeTexVoronoi','coarse broken aggregate');cells.inputs['Scale'].default_value=8;l.new(geo.outputs['Position'],cells.inputs['Vector'])
  grains=p.remap(cells.outputs['Distance'],.18,.31,1,0)
  body=p.mix(op('MULTIPLY',grains,.43),body,mul(source,(.49,.48,.50),'aggregate dark flecks'),'uneven aggregate')
  body=p.mix(op('MULTIPLY',p.remap(fine,.59,.72),.28),body,mul(source,(1.58,1.49,1.31),'aggregate pale flecks'),'broken mineral highlights')
 elif role=='lip':body=mul(body,(1.22,1.13,1.02),'warm exposed fracture lip')
 # A few clustered mineral freckles; most surviving facing is kept quiet.
 speck=op('MULTIPLY',p.remap(fine,.65,.74),op('ADD',.07,op('MULTIPLY',basal,.45)))
 body=p.mix(speck,body,mul(source,(.35,.33,.38),'dark scuff'),'base-concentrated fine damage')
 body=p.mix(op('MULTIPLY',op('MULTIPLY',basal,p.remap(medium,.43,.62)),.27),body,mul(source,(1.37,1.25,1.10),'ground dust'),'irregular lower-wall dust')
 l.new(body,em.inputs['Color']);m['235 finish role']=role;return m

def apply(scene):
 C=bpy.data.collections['133 Ruined transition structures'];cache={};rows=[]
 for ob in C.objects:
  if ob.type!='MESH' or not(ob.get('230 weathered')or ob.get('235 structure')):continue
  for slot in ob.material_slots:
   old=slot.material
   if old is None:continue
   role=old.get('235 wall role','face')
   if role=='face' and any(t in old.name.lower()for t in('core','exposed recessed')):role='core'
   key=(old,role)
   if key not in cache:cache[key]=finish(old,role)
   slot.link='OBJECT';slot.material=cache[key];rows.append({'object':ob.name,'role':role,'source':old.name,'material':slot.material.name})
 return {'material_assignments':rows,'private_materials':len(cache),'method':'Restore204half palette/native light baseline; broad warm stains and gravity wash, quieter facing, rough aggregate localized to cores and basal scuffs.','accepted234far_buildings_untouched':True}

def ink(scene):
 C=bpy.data.collections['133 Ruined transition structures'];targets=[o for o in C.objects if o.type=='MESH' and(o.get('230 weathered')or o.get('235 structure'))]
 # Remove duplicate near-line eligibility without removing opaque occluders.
 generic=bpy.data.collections.get('215 Distant accepted component ink')
 if generic:
  for ob in targets:
   if ob.name in generic.objects:generic.objects.unlink(ob)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for ob in targets:
     if ob.name not in ls.collection.objects:ls.collection.objects.link(ob)
 vl=scene.view_layers['215 Distant ink without atmospheric boundary'];outer=vl.freestyle_settings.linesets['230 Broken wall readable contours'];collection=outer.collection
 for ob in targets:
  if ob.name not in collection.objects:collection.objects.link(ob)
 collection.use_fake_user=True
 outer.linestyle=outer.linestyle.copy();outer.linestyle.name='235 Ruin silhouette';outer.linestyle.thickness=.82;outer.linestyle.color=(.032,.028,.041);outer.linestyle.alpha=.94
 outer.select_crease=False;outer.select_edge_mark=False;outer.select_material_boundary=False;outer.select_silhouette=True;outer.select_border=True;outer.select_external_contour=True
 inner=vl.freestyle_settings.linesets.new('235 Fine ruin interior structure');inner.select_by_collection=True;inner.collection=collection;inner.collection_negation='INCLUSIVE';inner.select_by_visibility=True;inner.visibility='VISIBLE';inner.select_by_edge_types=True;inner.edge_type_combination='AND';inner.edge_type_negation='INCLUSIVE'
 for key in ['silhouette','border','crease','ridge_valley','suggestive_contour','material_boundary','contour','external_contour','edge_mark']:
  if hasattr(inner,'select_'+key):setattr(inner,'select_'+key,False)
 for key in ['silhouette','border','external_contour']:
  setattr(inner,'select_'+key,True);setattr(inner,'exclude_'+key,True)
 inner.select_crease=True;inner.exclude_crease=False
 inner.linestyle.thickness=.65;inner.linestyle.color=(.045,.040,.059);inner.linestyle.alpha=.88
 return {'objects':len(targets),'silhouette_px':.82,'interior_px':.65,'interior_predicate':'crease AND NOT silhouette AND NOT border AND NOT external contour','near_duplicate_eligibility_removed':True,'visibility':'Native hidden geometry retained;215 atmosphere-free ink only'}
