import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_contact_clip_169 import O,snapshot,digest,tree
from coliseum_contact_certificate_169 import certify
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-166/scene.blend'));gp=bpy.data.objects['110 Landmark contact ink'];old=snapshot(gp);M=gp.matrix_world.copy();payload=json.load(open(O/'clip-payload.json'));assert digest(old)==payload['source_digest'];transform={'source':'166','object':gp.name,'matrix_world':[list(row)for row in M],'attribute_digest':digest(old),'comparison':'Exact matrix element equality required before applying169'}
(O/'source-transform.json').write_text(json.dumps(transform,indent=2));bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-168/scene.blend'));surf=tree(bpy.data.collections['110 Coliseum detailed front ruin']);a=certify(payload,old,M,surf);a['support_source']='Actual168 geometry';a['clip_payload_sha256']=hashlib.sha256((O/'clip-payload.json').read_bytes()).hexdigest();a['source_transform']=transform;a['no_geometry_or_clip_interval_change']=True;(O/'continuous-support-certificate.json').write_text(json.dumps(a,indent=2));print({k:v for k,v in a.items()if k!='intervals'},flush=True)
