"""Apply the validated isolated U10L return payload without adopting a temporary transform."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
NAME='COL110 U10 fractured upper wall L'
def apply(C):
 ob=C.objects[NAME];M=ob.matrix_world.copy();slots=[(s.link,s.material) for s in ob.material_slots]
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-160/repair/candidate.blend'),link=False) as(src,dst):
  dst.meshes=['160 ruled return candidate']
 mesh=dst.meshes[0]
 ob.data=mesh
 for s,(link,mat) in zip(ob.material_slots,slots):s.link=link;s.material=mat
 for mod in list(ob.modifiers):ob.modifiers.remove(mod)
 assert tuple(map(tuple,M))==tuple(map(tuple,ob.matrix_world))
 return {'targets':[{'object':NAME,'replaced':'folded cap and upper angular-end return; protected source faces retained','world_matrix_exact':True}], 'proof':json.loads((R/'art/studies/coliseum-160/repair/preservation-audit.json').read_text()), 'scope':'Source156 evaluated payload. U15R unchanged. Local visual review required before integration.'}
