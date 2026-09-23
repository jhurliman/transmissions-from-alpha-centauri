from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[1];O=R/'art/studies/midground-230';a=json.loads((O/'layout-audit.json').read_text())
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1050" viewBox="0 0 1200 1050"><rect width="1200" height="1050" fill="#20232b"/><style>text{font-family:Arial,sans-serif;fill:#eee7dc} .small{font-size:12px}.title{font-size:24px;font-weight:bold}</style>']
for col,key,title in [(0,'before','229 · 12 buildings'),(1,'after','230 · 18 buildings')]:
 cx=300+col*600
 svg.append(f'<text x="{cx}" y="40" text-anchor="middle" class="title">{title}</text><text x="{cx}" y="66" text-anchor="middle" class="small">Measured top-down footprints · height labels in metres</text>')
 for y in range(40,161,10):
  py=940-(y-40)*6.8;svg.append(f'<line x1="{cx-205}" x2="{cx+205}" y1="{py}" y2="{py}" stroke="#42464d"/><text x="{cx-216}" y="{py+4}" text-anchor="end" class="small">{y}m</text>')
 svg.append(f'<path d="M{cx},955 L{cx},90" stroke="#756647" stroke-width="2" stroke-dasharray="8 7"/><text x="{cx}" y="100" text-anchor="middle" class="small">Toward Colosseum</text><text x="{cx}" y="993" text-anchor="middle" class="small">Toward camera / foreground alley</text>')
 for r in a[key]:
  lo,hi=r['bounds'];x=cx+lo[0]*7;py=940-(hi[1]-40)*6.8;w=(hi[0]-lo[0])*7;h=(hi[1]-lo[1])*6.8;new=r['name'].startswith('230');color='#b28b60'if new else '#65768b';svg.append(f'<rect x="{x:.1f}" y="{py:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{color}" stroke="#e4d8c4"/><text x="{x+w/2:.1f}" y="{py+h/2+4:.1f}" text-anchor="middle" class="small">{hi[2]:.1f}</text>')
svg.append('<text x="600" y="1030" text-anchor="middle" class="small">Blue = existing · ochre = added. Structural footprint bounds exclude projecting pipes; existing buildings remain in place.</text></svg>');(O/'top-down-plan.svg').write_text(''.join(svg))
