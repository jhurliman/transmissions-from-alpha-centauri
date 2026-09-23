"""Matched full-scene and native-detail review for the distributed rust pass."""
from pathlib import Path
from PIL import Image
import json
import re
import urllib.request
import numpy as np

R = Path(__file__).resolve().parents[1]
O = R / 'art/studies/rust-189'
P = '/art/studies/rust-189/'
regions = {
    'left-beam': (120, 830, 820, 2040),
    'right-beam': (3250, 780, 3840, 2030),
    'left-wall': (100, 100, 1410, 1880),
    'right-wall': (2530, 100, 3840, 1880),
}
images = {}
for label, path in [('before', R / 'art/studies/coliseum-188/main-4k.png'), ('after', O / 'main-4k.png')]:
    im = Image.open(path).convert('RGB')
    images[label] = im
    im.resize((1800, round(im.height * 1800 / im.width)), Image.Resampling.LANCZOS).save(O / f'{label}-display.png')
    im.resize((1440, round(im.height * 1440 / im.width)), Image.Resampling.LANCZOS).convert('L').save(O / f'{label}-gray.png')
    for name, box in regions.items():
        im.crop(box).save(O / f'{label}-{name}.png')

a = np.asarray(images['before']).astype(np.int16)
b = np.asarray(images['after']).astype(np.int16)
d = np.abs(a-b).max(2)
metrics = {'resolution': list(images['after'].size), 'pixels_changed_over4': int((d > 4).sum()), 'regions': {}}
for name, (x0, y0, x1, y1) in regions.items():
    region = d[y0:y1, x0:x1]
    metrics['regions'][name] = {'box': [x0, y0, x1, y1], 'pixels_over4': int((region > 4).sum()), 'fraction_over4': float((region > 4).mean())}
metrics['note'] = 'Change extent, not a quality score. Both sides and whole scene require visual review.'
(O / 'pixel-comparison.json').write_text(json.dumps(metrics, indent=2) + '\n')
Image.fromarray(np.clip(np.abs(a-b) * 5, 0, 255).astype('uint8')).resize((1440,1082)).save(O / 'difference-5x.png')

def pair(name):
    return f'<div class="pair"><figure><img src="{P}before-{name}.png"><figcaption>Before</figcaption></figure><figure><img src="{P}after-{name}.png"><figcaption>Updated</figcaption></figure></div>'

plates = ''
proof = O / 'plate-crops.json'
if proof.exists():
    for i, row in enumerate(json.loads(proof.read_text())):
        box = row['box']
        for label, im in images.items():
            im.crop(box).save(O / f'{label}-plate-{i}.png')
        plates += f'<h3>{row.get("label", "Anchor plate " + str(i+1))}</h3>' + pair(f'plate-{i}')

html = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>189 · Rust across the alley</title>
<style>body{{background:#191a20;color:#eee6dd;font:17px/1.55 system-ui;max-width:1560px;margin:30px auto;padding:0 24px}}a{{color:#edbb98}}img{{display:block;width:100%;height:auto}}figure{{margin:12px 0}}figcaption{{color:#c2b7b1}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}button{{background:#443c42;color:#fff;border:1px solid #80716d;border-radius:5px;padding:10px 18px;font:inherit;cursor:pointer}}section{{margin:44px 0}}.refs{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}@media(max-width:760px){{.pair,.refs{{grid-template-columns:1fr}}}}</style>
<h1>189 · Rust across the alley</h1><p>Small bolt-fed water stains across both sides of the scene, with a few heavily weathered anchor plates. The Y beams now have edge corrosion, granular oxide and fine runoff in place of the flat camouflage patches.</p>
<button onclick="pick('after')">Updated</button> <button onclick="pick('before')">Before</button><img id="main" src="{P}after-display.png">
<p><a href="{P}main-4k.png">Full 4K render</a> · <a href="{P}scene.blend">Editable scene</a> · <a href="/prototype/review-188.html">Previous scene</a></p>
<section id="beams"><h2>Left steel support</h2>{pair('left-beam')}<h2>Right steel support</h2>{pair('right-beam')}</section>
<section id="bolts"><h2>Anchor plates and bolt runoff</h2>{plates}<details><summary>Left wall</summary>{pair('left-wall')}</details><details><summary>Right wall</summary>{pair('right-wall')}</details></section>
<section id="references"><h2>Your steel references</h2><div class="refs"><figure><img src="/references/rusted-steel-189/RS-01-alamy.jpg"><figcaption><a href="https://c8.alamy.com/comp/CXYC2N/rusted-steel-beam-detailed-view-berlin-CXYC2N.jpg">Alamy · edge corrosion</a></figcaption></figure><figure><img src="/references/rusted-steel-189/RS-02-stockcake.jpg"><figcaption><a href="https://images.stockcake.com/public/b/e/7/be7a9476-7475-4c43-9298-a714dcf46fd3_large/rusty-metal-beams-stockcake.jpg">Stockcake · bolt roots and rain stains</a></figcaption></figure><figure><img src="/references/rusted-steel-189/RS-03-bigstock.jpg"><figcaption><a href="https://static1.bigstockphoto.com/5/5/2/large1500/255633313.jpg">Bigstock · granular oxide</a></figcaption></figure></div><p>Reference images only; the scene uses editable native materials and attached weathering.</p></section>
<details><summary>Grayscale comparison</summary>{pair('gray')}</details><script>function pick(v){{document.getElementById('main').src='{P}'+v+'-display.png'}}</script></html>'''
(R / 'prototype/review-189.html').write_text(html)
links = re.findall(r'(?:src|href)="(/[^"#]+)"', html)
missing = [p for p in links if not (R / p.lstrip('/')).exists()]
assert not missing, missing
(O / 'publication-check.json').write_text(json.dumps({'missing': missing, 'http': urllib.request.urlopen('http://127.0.0.1:8765/prototype/review-189.html').status}, indent=2) + '\n')
print('Published189')
