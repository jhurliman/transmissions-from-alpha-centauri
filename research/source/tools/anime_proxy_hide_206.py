"""Hide only native scale-proxy meshes and its eight proven contact-ink strokes."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-206/anime'
def apply(scene):
 proxy=bpy.data.collections['07 Human scale proxy'];objects=list(proxy.all_objects)
 for ob in objects:ob.hide_render=True
 proxy.hide_render=True
 excluded=[]
 def walk(lc,layer):
  if lc.collection==proxy:lc.exclude=True;excluded.append(layer)
  for ch in lc.children:walk(ch,layer)
 for vl in scene.view_layers:walk(vl.layer_collection,vl.name)
 assert len(objects)==15 and all(o.hide_render for o in objects)
 evidence=json.loads((O/'proxy-ink-ownership.json').read_text());selected=[r for r in evidence if r['object']=='096 contacts ink'and r['bounds'][0][2]>.20]
 assert len(selected)==8
 ink=bpy.data.objects['096 contacts ink'];ink.data=ink.data.copy();changed=[]
 for row in selected:
  layer=ink.data.layers[row['layer']];frame=next(f for f in layer.frames if f.frame_number==row['frame']);stroke=frame.drawing.strokes[row['stroke']]
  assert len(stroke.points)==row['count']
  for p,reference in zip(stroke.points,row['points']):
   world=ink.matrix_world@p.position
   assert max(abs(world[k]-reference[k])for k in range(3))<.00001,('Proxy ink sourcechanged',row['stroke'])
   p.opacity=0
  changed.append({'stroke':row['stroke'],'points':row['count'],'bounds':row['bounds']})
 return {'proxy_objects_hidden':[o.name for o in objects],'collection_excluded_in_layers':excluded,'private_contact_ink_copy':True,'complete_character_contact_strokes_hidden':changed,'soil_ink_unchanged':True,'near_ground_strokes_below_z_point20_preserved':True,'source_photo_assets_unchanged':True}
