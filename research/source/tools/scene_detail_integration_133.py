"""Combine separately inspected clouds, ruins and alley damage with selected haze."""
import bpy,json,sys,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scene-details-133';O.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(R/'tools'))
def refine_rust():
 rows=[]
 for m in bpy.data.materials:
  if m.library or m.get('133 weathering')!='oxide steel':continue
  ramp=next(n for n in m.node_tree.nodes if n.label=='133 Connected oxide islands and finite streaks');bias=.465-ramp.color_ramp.elements[0].position
  ramp.color_ramp.elements[0].position=.515-bias;ramp.color_ramp.elements[1].position=.545-bias
  col=next(n for n in m.node_tree.nodes if n.label=='133 Deep oxide, ochre corrosion and fine pits');tone=col.inputs[0].links[0].from_node;tone.inputs[0].default_value=.40
  rows.append({'material':m.name,'retained_edge_bias':bias,'mask':[.515-bias,.545-bias],'fine_tone_weight':.40})
 return rows
def fingerprint(scene):
 out={}
 for o in scene.objects:
  d={'matrix':[list(v)for v in o.matrix_world],'hidden':o.hide_render,'instance_collection':o.instance_collection.name if o.instance_collection else None,'materials':[slot.material.name if slot.material else None for slot in o.material_slots]}
  if o.type=='MESH':
   vs=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',vs);loops=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',loops);d['geometry']=hashlib.sha256(vs.tobytes()+loops.tobytes()).hexdigest()
  if o.type=='CAMERA':d['camera']=[o.data.type,o.data.lens,o.data.ortho_scale,o.data.shift_x,o.data.shift_y]
  if o.type=='LIGHT':d['light']=[o.data.type,o.data.energy,list(o.data.color)]
  out[o.name]=d
 return out
if '--render' not in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-132/selected/scene.blend'));s=bpy.context.scene
 before=fingerprint(s)
 from clouds_133 import apply as clouds
 from city_transition_133 import apply as city
 from alley_damage_133 import apply as alley
 from coliseum_black_joint_133 import apply as blackjoint
 t=time.time();audit={'source':'132 selected full-city5x haze','blackjoint':blackjoint(s),'clouds':clouds(s),'city':city(s),'alley':alley(s)};audit['rust_critic_refinement']=refine_rust();audit['generation_seconds']=time.time()-t
 after=fingerprint(s);changes={k:[field for field in before[k] if before[k].get(field)!=after.get(k,{}).get(field)]for k in before if before[k]!=after.get(k)};preservation={'changed_existing':changes,'added':sorted(set(after)-set(before)),'removed':sorted(set(before)-set(after))};(O/'preservation.json').write_text(json.dumps(preservation,indent=2));assert not preservation['removed'];assert not any('geometry' in fields or 'matrix' in fields or 'camera' in fields or 'light' in fields for fields in changes.values()),changes
 # New alley/transition silhouettes require current-scene ink, not archived128 overlays.
 s.render.use_compositing=False;s.compositing_node_group=None;s.render.use_freestyle=True
 for ls in s.view_layers[0].freestyle_settings.linesets:ls.show_render=True
 s.view_layers[0].freestyle_settings.as_render_pass=False;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.line_thickness=1;s.render.use_border=False;s.render.use_crop_to_border=False
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));(O/'generation.json').write_text(json.dumps(audit,indent=2,default=str)+'\n')
else:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.filepath=str(O/'main-4k.png');assets={c for c in bpy.data.collections if c.name.startswith(('PREFAB133 Missing cladding','133 Rusted Y support')) and c.library is None};bpy.data.libraries.write(str(O/'prefabs.blend'),assets,fake_user=True);t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'render_seconds':time.time()-t,'resolution':[3840,2885],'ink':'Fresh primary native Freestyle for newly changed alley/transition geometry'},indent=2)+'\n')
