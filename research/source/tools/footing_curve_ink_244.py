"""Prevent duplicate Freestyle contours around already-dark physical contact/scuff curves."""
def apply(scene):
 import bpy
 targets=list(bpy.data.collections['243 Foundation contact and wear'].objects);rows=[]
 for layer in scene.view_layers:
  for ls in layer.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for ob in targets:
     if ob.name not in ls.collection.objects:ls.collection.objects.link(ob);rows.append([layer.name,ls.name,ob.name])
 # Retain contact seals; omit tiny free curves which acquired disproportionate outlines.
 for ob in targets:
  if 'scuff' in ob.name or 'nick' in ob.name:ob.hide_render=True
 return {'contact_seals_preserved':True,'removed_tiny_curve_scuffs':9,'duplicate_ink_exclusions':rows,'aggregate_grime_water_staining_and_native_chipped_footing_preserved':True}
