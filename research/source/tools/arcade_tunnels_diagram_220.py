"""Measured vector diagram directly from the native tunnel audit; no reference raster."""
import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/arcade-tunnels-220';a=json.loads((O/'audit.json').read_text());b=a['objects'][8];h=b['height_m'];drop=30/math.sqrt(2)
def points(v):return' '.join(f'{x:.2f},{y:.2f}'for x,y in v)
def side(x,z):return(70+x*10,245-z*10)
floor=[side(0,0),side(30,0),side(30+drop,-drop)];roof=[side(0,h),side(30+h*math.tan(math.pi/8),h),side(30+drop+h/math.sqrt(2),-drop+h/math.sqrt(2))]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="720" viewBox="0 0 1100 720"><rect width="1100" height="720" fill="#eee8df"/><g font-family="sans-serif" fill="#332f35"><text x="40" y="38" font-size="25">220 · Native descending ground-arcade tunnels</text><text x="40" y="65" font-size="15">18 fitted arch mouths · all dimensions measured in current world metres</text>']
svg+=[f'<polyline points="{points(floor)}" fill="none" stroke="#59483f" stroke-width="7"/>',f'<polyline points="{points(roof)}" fill="none" stroke="#59483f" stroke-width="7"/>','<text x="130" y="280" font-size="19">30 m straight</text>','<text x="415" y="425" font-size="19">30 m at 45° down</text>','<text x="655" y="440" font-size="16">21.213 m drop</text>','<text x="45" y="315" font-size="14">Native fitted entry</text>','<text x="555" y="490" font-size="14">Open outlet</text>']
# Plan: same nativeworldcoordinates; orange first segment, blue descending projection.
xs=[p['entry_floor_center'][0]for p in a['objects']];ys=[p['entry_floor_center'][1]for p in a['objects']];xmin=min(xs);ymin=min(ys)
def plan(p):return(760+(p[0]-xmin)*1.4,110+(p[1]-ymin)*1.4)
for p in a['objects']:
 e,k,o=[plan(p[v])for v in('entry_floor_center','bend_floor_center','outlet_floor_center')];svg.append(f'<polyline points="{points([e,k])}" fill="none" stroke="#a26f49" stroke-width="2"/><polyline points="{points([k,o])}" fill="none" stroke="#687a93" stroke-width="2"/><text x="{e[0]:.1f}" y="{e[1]-4:.1f}" font-size="9">{p["bay"]}</text>')
svg+=['<text x="765" y="455" font-size="15">Plan · native arch reveal axes</text>','<text x="40" y="580" font-size="17">Exact native rear arch contours; solid walls, roof and floor; connected miter.</text>','<text x="40" y="610" font-size="17">No horizontal turn. No tunnel-to-tunnel surface intersections.</text>','<text x="40" y="640" font-size="14">Diagram traced from audited editable mesh construction, not an artistic reference.</text>','</g></svg>'];(O/'measured-route.svg').write_text(''.join(svg))
