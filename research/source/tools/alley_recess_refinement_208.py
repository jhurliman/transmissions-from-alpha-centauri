"""Lighter exposed aggregate and true inner-edge ink for the 198 recessed pit family."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def finish(old):
 m=old.copy();m.name='208 Light exposed aggregate | '+old.name;old.use_fake_user=True
 nt=m.node_tree;n=nt.nodes;l=nt.links
 em=next(x for x in n if x.type=='EMISSION');src=em.inputs[0].links[0].from_socket
 # Remove only198's final dark substrate multiplier, preserving host lighting and finish.
 if src.node.type=='MIX_RGB' and src.node.blend_type=='MULTIPLY':src=src.node.inputs[1].links[0].from_socket
 def node(t,label):
  z=n.new(t);z.label=label;return z
 geo=node('ShaderNodeNewGeometry','208 Native surface coordinates')
 tr=node('ShaderNodeVectorTransform','208 Local inward floor / wall normal');tr.vector_type='NORMAL';tr.convert_from='WORLD';tr.convert_to='OBJECT';l.new(geo.outputs['Normal'],tr.inputs[0])
 dot=node('ShaderNodeVectorMath','208 Floor-to-sidewall depth response');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(0,-1,0);l.new(tr.outputs[0],dot.inputs[0])
 ramp=node('ShaderNodeValToRGB','208 Lighter floor, shaded existing sidewalls');ramp.color_ramp.elements[0].position=.55;ramp.color_ramp.elements[0].color=(.56,.55,.53,1);ramp.color_ramp.elements[1].position=.98;ramp.color_ramp.elements[1].color=(.97,.94,.88,1);l.new(dot.outputs['Value'],ramp.inputs[0])
 mult=node('ShaderNodeMixRGB','208 Restrained warm mineral exposure');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;l.new(src,mult.inputs[1]);l.new(ramp.outputs[0],mult.inputs[2]);out=mult.outputs[0]
 for scale,threshold,color,amount,label in [(130,.30,(.32,.34,.36,1),.76,'Dense fractured mineral flecks'),(62,.23,(1.28,1.26,1.20,1),.65,'Irregular pale aggregate')]:
  vor=node('ShaderNodeTexVoronoi','208 '+label);vor.inputs['Scale'].default_value=scale; l.new(geo.outputs['Position'],vor.inputs['Vector'])
  r=node('ShaderNodeMapRange','208 Soft granular margins');r.clamp=True;r.inputs['From Min'].default_value=threshold*.65;r.inputs['From Max'].default_value=threshold;r.inputs['To Min'].default_value=amount;r.inputs['To Max'].default_value=0;l.new(vor.outputs['Distance'],r.inputs['Value'])
  mix=node('ShaderNodeMixRGB','208 '+label);mix.blend_type='MULTIPLY';mix.inputs[2].default_value=color;l.new(r.outputs[0],mix.inputs[0]);l.new(out,mix.inputs[1]);out=mix.outputs[0]
 l.new(out,em.inputs[0]);return m

def apply(scene):
 targets=[o for o in bpy.data.objects if o.type=='MESH' and o.get('198 native damage')=='recess'];assert len(targets)==14,len(targets)
 coll=bpy.data.collections.new('208 Recess inner edge selection');coll.use_fake_user=True
 mats={};rows=[]
 for o in targets:
  old=o.data;old.use_fake_user=True;o.data=old.copy();o.data.name='208 Inner-edge-marked '+old.name
  cut=set()
  for i,s in enumerate(o.material_slots):
   if s.material and s.material.name.startswith('198 Dark exposed substrate'):
    orig=s.material
    if orig.name not in mats:mats[orig.name]=finish(orig)
    s.link='OBJECT';s.material=mats[orig.name];cut.add(i)
  assert cut,o.name
  adj={}
  for p in o.data.polygons:
   for key in p.edge_keys:adj.setdefault(tuple(sorted(key)),[]).append(p)
  marked=[]
  attr=o.data.attributes.get('freestyle_edge') or o.data.attributes.new('freestyle_edge','BOOLEAN','EDGE')
  for e in o.data.edges:
   ps=adj.get(tuple(sorted(e.vertices)),[])
   if len(ps)==2 and all(p.material_index in cut for p in ps):
    vals=[-p.normal.y for p in ps]
    if max(vals)>.97 and min(vals)<.94:attr.data[e.index].value=True;marked.append(e.index)
  coll.objects.link(o);rows.append({'object':o.name,'cut_material_slots':sorted(cut),'inner_edges_marked':len(marked),'mesh_vertices_unchanged':all(a.co==b.co for a,b in zip(old.vertices,o.data.vertices)),'polygon_topology_unchanged':all(tuple(a.vertices)==tuple(b.vertices) for a,b in zip(old.polygons,o.data.polygons))})
 for vl in scene.view_layers:
  if not vl.use_freestyle:continue
  ls=vl.freestyle_settings.linesets.new('208 Fine recessed floor / wall joins');ls.select_by_collection=True;ls.collection=coll;ls.collection_negation='INCLUSIVE';ls.select_by_edge_types=True
  for prop in ('select_silhouette','select_border','select_crease','select_ridge_valley','select_suggestive_contour','select_material_boundary','select_contour','select_external_contour'):setattr(ls,prop,False)
  ls.select_edge_mark=True;ls.linestyle.thickness=.25;ls.linestyle.color=(.026,.023,.026);ls.linestyle.alpha=.86
 audit={'scope':'198 recess only; impacts and cracks excluded','target_count':len(targets),'materials':{k:v.name for k,v in mats.items()},'objects':rows,'new_geometry':False,'inner_edge_count':sum(x['inner_edges_marked']for x in rows),'new_line_width_base':.25,'status':'candidate; native proof required'}
 return audit
