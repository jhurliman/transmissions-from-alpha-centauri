"""Keep original light pigment; independently increase dark facade strokes."""
import bpy,json,random,hashlib,ast
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-107';O.mkdir(parents=True,exist_ok=True)
source=(R/'tools/city_facades_102.py').read_text()
source=source.replace('centers=[]','centers=[];light_mask=0')
source=source.replace("shape=mathnode('ADD',shape,warp);mask=mathnode('LESS_THAN',shape,1)","shape=mathnode('ADD',shape,warp);mask=mathnode('LESS_THAN',shape,1);feather=mathnode('MINIMUM',mathnode('MAXIMUM',mathnode('DIVIDE',mathnode('SUBTRACT',1,dz),.32),0),1);mask=mathnode('MULTIPLY',mask,feather)")
source=source.replace('   color=mix(mask,color,rgba(c))', '''   if k < BASE_COUNT:
    if k%3!=1:light_mask=mathnode('MAXIMUM',light_mask,mask)
    color=mix(mask,color,rgba(c))
   else:
    # New dark pigment cannot brighten shadow faces or cover original light marks.
    mask=mathnode('MULTIPLY',mask,mathnode('SUBTRACT',1,light_mask))
    color=mix(mask,color,multiply_color(color,.72))''')
# Add a native RGB multiplier local helper, no new geometry or projected art.
source=source.replace(" out=node('ShaderNodeOutputMaterial')", " def multiply_color(c,f):\n  q=node('ShaderNodeMixRGB','Dark pigment over underlying paint');q.blend_type='MULTIPLY';q.inputs[0].default_value=1;l.new(c,q.inputs[1]);q.inputs[2].default_value=(f,f,f,1);return q.outputs[0]\n out=node('ShaderNodeOutputMaterial')")
module=ast.parse(source);defs=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['lin','rgb','rgba','scale','blend','material']];exec(compile(ast.Module(body=defs,type_ignores=[]),'107_dark_stamps','exec'),globals())
records={r['id']:r for r in json.loads((R/'art/studies/city-101/A/reconstruction.json').read_text())['masses']}
counts={r['id']:r['paint_stamps'] for r in json.loads((R/'art/studies/city-102/changes.json').read_text())['masses']}
for variant,factor in [('A',2),('B',4),('C',8)]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/city-106/placement.blend'));s=bpy.context.scene;folder=O/variant;folder.mkdir(exist_ok=True);audit=[]
 for ob in bpy.data.collections['101 Original city layout study'].objects:
  if ob.hide_render or 'measured crown mass' not in ob.name:continue
  mid=ob['reference_mass'];src=ob.get('source_mass',mid);seed=int(hashlib.sha256(mid.encode()).hexdigest()[:8],16);BASE_COUNT=counts[src];dark=sum(k%3==1 for k in range(BASE_COUNT));light=BASE_COUNT-dark;total=BASE_COUNT+dark*(factor-1)
  mat=material(mid,'107 fixed light dark '+variant,rgb(records[src]['color_hex']),seed,marks=total);ob.data=ob.data.copy();ob.data.materials[0]=mat
  audit.append({'id':mid,'light_strokes':light,'dark_strokes':dark*factor,'original_dark_strokes':dark,'light_multiplier':1,'dark_multiplier':factor})
 (folder/'marks.json').write_text(json.dumps(audit,indent=2));s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(folder/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'));bpy.ops.render.render(write_still=True)
