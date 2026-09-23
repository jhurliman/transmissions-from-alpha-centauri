"""Publish the actual native188 render and matched173 comparisons."""
from pathlib import Path
from PIL import Image
import json,re,urllib.request
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-188';P='/art/studies/coliseum-188/'
for label,path in [('before',R/'art/studies/coliseum-173/main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(path).convert('RGB')
 im.resize((1440,1082),Image.Resampling.LANCZOS).save(O/f'{label}-main.png')
 im.resize((1800,1352),Image.Resampling.LANCZOS).save(O/f'{label}-display1800.png')
 im.crop((1400,350,2460,1240)).save(O/f'{label}-landmark.png')
 im.crop((2080,545,2310,775)).save(O/f'{label}-right.png')
 im.resize((1440,1082),Image.Resampling.LANCZOS).convert('L').save(O/f'{label}-gray.png')
def pair(part):
 return f'<div class="pair"><figure><img src="{P}before-{part}.png"><figcaption>Before</figcaption></figure><figure><img src="{P}after-{part}.png"><figcaption>Updated</figcaption></figure></div>'
scores=''
if (O/'critic.json').exists():
 d=json.loads((O/'critic.json').read_text());sc=d.get('scores',{})
 scores='<p>Independent critic: '+', '.join(k.replace('_',' ')+': '+str(v)for k,v in sc.items())+'. Your approval remains separate.</p>'
kit=''
if (O/'kit-proof/right-break-painted.png').exists():
 kit=f'<details><summary>Editable kit check</summary><div class="pair"><img src="{P}kit-proof/right-break-painted.png"><img src="{P}kit-proof/right-break-clay.png"></div></details>'
h=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>188 · Clearer broken cornice</title>
<style>body{{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;max-width:1500px;margin:28px auto;padding:0 22px}}a{{color:#efbc91}}img{{width:100%;display:block}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}figure{{margin:10px 0}}figcaption{{color:#c5bbc4}}button{{padding:12px;background:#433137;color:#fff;border:1px solid #957e77;cursor:pointer}}section{{margin:42px 0}}.detail{{max-width:980px}}@media(max-width:700px){{.pair{{grid-template-columns:1fr}}}}</style>
<h1>188 · Clearer broken cornice</h1><p>The damaged left end of the right cornice now reads as a larger attached stone break, with fewer competing fragments. The bottom panel splatter remains at three times its earlier coverage.</p>
<button onclick="pick('after')">Updated</button> <button onclick="pick('before')">Before</button><img id="main" src="{P}after-main.png">
<p><a href="{P}main-4k.png">Full 4K render</a> · <a href="{P}scene.blend">Editable scene</a> · <a href="{P}kit.blend">Colosseum kit</a></p>
<section id="splatter"><h2>Bottom splatter ×3</h2><p>The fine bottom splatter has three times its previous coverage, with the same patch size and fade up the panels. This change is preserved in the scene above.</p><div class="pair"><figure><img src="/art/studies/alley-weathering-147/actual/before-crop.png"><figcaption>Previous coverage</figcaption></figure><figure><img src="/art/studies/alley-weathering-147/actual/after-crop.png"><figcaption>3× coverage</figcaption></figure></div><p><a href="/prototype/review-147.html#mask">Inspect the material comparison</a></p></section>
<section id="detail" class="detail"><h2>Broken cornice</h2>{pair('right')}</section>
<section><h2>Whole landmark</h2>{pair('landmark')}</section>{scores}{kit}
<section><h2>Original reference</h2><img src="/art/studies/coliseum-134/analysis/independent/reference-display.png"><p>Your original artwork, created with ChatGPT Images 2.5.</p></section>
<details><summary>Grayscale</summary>{pair('gray')}</details>
<p id="status">Review candidate; not marked user-approved.</p><script>function pick(v){{document.getElementById('main').src='{P}'+v+'-main.png'}}</script></html>'''
(R/'prototype/review-188.html').write_text(h)
paths=re.findall(r'(?:src|href)="(/[^"#]+)"',h);missing=[p for p in paths if not(R/p.lstrip('/')).exists()];assert not missing,missing
(O/'delivery-check.json').write_text(json.dumps({'missing':missing,'resolution':list(Image.open(O/'main-4k.png').size),'http':urllib.request.urlopen('http://127.0.0.1:8765/prototype/review-188.html').status},indent=2)+'\n')
print('Published188')
