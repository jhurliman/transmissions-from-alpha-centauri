import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-206/anime';sys.path.insert(0,str(R/'tools'));src=R/'art/studies/scene-completion-209/scene.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
ink=bpy.data.objects['096 contacts ink'];old=ink.data
def capture(data):
 return {(l.name,f.frame_number,i):[(tuple(p.position),float(p.opacity),float(p.radius))for p in st.points]for l in data.layers for f in l.frames for i,st in enumerate(f.drawing.strokes)}
before=capture(old);soil=bpy.data.objects['097 Broken soil ink'].data
from anime_proxy_hide_206 import apply
report=apply(s);after=capture(ink.data);changes=[];pointchanges=0
assert before.keys()==after.keys()
for key,ps in before.items():
 qs=after[key];assert len(ps)==len(qs)
 for p,q in zip(ps,qs):assert p[0]==q[0]and p[2]==q[2]
 if ps!=qs:
  changes.append(key);pointchanges+=sum(p[1]!=q[1]for p,q in zip(ps,qs));assert all(q[1]==0 for q in qs)
assert sorted(k[2]for k in changes)==[767,772,2614,2615,2616,2617,2618,4675]
assert soil==bpy.data.objects['097 Broken soil ink'].data
assert old!=ink.data and capture(old)==before
report.update({'source':str(src.relative_to(R)),'actual_changed_strokes':changes,'changed_point_opacities':pointchanges,'all_contact_point_positions_and_radii_unchanged':True,'all_noncharacter_stroke_opacities_unchanged':True,'original_contact_datablock_unmodified':True,'soil_datablock_identity_preserved':True,'visual_status':'Third native plate pending; structural audit isnot actualvisibilityproof'})
(O/'proxy-preservation.json').write_text(json.dumps(report,indent=2));print('206_PRESERVATION_PASS',len(changes),pointchanges,flush=True)
