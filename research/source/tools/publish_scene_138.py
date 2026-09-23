from pathlib import Path
from PIL import Image
import json,re
R=Path(__file__).resolve().parents[1]; O=R/'art/studies/scene-details-138'; P='/art/studies/scene-details-138/'
bounds=json.loads((R/'art/studies/alley-rust-137/crop.json').read_text())['bounds']
for label,path in [('before',R/'art/studies/coliseum-134/main-4k.png'),('after',O/'main-4k.png')]:
 im=Image.open(path).convert('RGB');im.resize((1440,1082),Image.Resampling.LANCZOS).save(O/f'{label}-main.png');im.crop(bounds).save(O/f'{label}-rust.png');im.crop((1390,700,2470,1235)).save(O/f'{label}-street.png');im.convert('L').resize((1440,1082)).save(O/f'{label}-gray.png')
def pair(part):return f'<div class="pair"><figure><img src="{P}before-{part}.png"><figcaption>Before · 134</figcaption></figure><figure><img src="{P}after-{part}.png"><figcaption>Updated · 138</figcaption></figure></div>'
h=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>138 · Corrosion and atmosphere</title><style>body{{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;max-width:1500px;margin:28px auto;padding:0 22px}}a{{color:#efbc91}}img{{width:100%;display:block}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}figure{{margin:10px 0}}figcaption{{color:#c5bbc4}}button{{padding:12px;background:#433137;color:#fff;border:1px solid #957e77;cursor:pointer}}section{{margin:42px 0}}@media(max-width:700px){{.pair{{grid-template-columns:1fr}}}}</style><h1>138 · Corrosion and atmosphere</h1><p>Dark corrosion gathers around bolt heads; interrupted rust follows exposed flange edges. Rain trails run downward from attachment points, using maroon, burnt red and ochre over retained steel.</p><button onclick="pick('after')">Updated</button> <button onclick="pick('before')">Before</button><img id="main" src="{P}after-main.png"><p><a href="{P}main-4k.png">Full 4K render</a> · <a href="{P}scene.blend">Editable scene</a></p><section id="rust"><h2>Support and ledge</h2>{pair('rust')}<h3>Reference detail</h3><img style="max-width:420px" src="/references/user-rust-137/target.png"></section><section id="street"><h2>Warm atmosphere across the city depth</h2>{pair('street')}<img src="/art/studies/coliseum-136/haze/reference-street.png"></section><details><summary>Grayscale</summary>{pair('gray')}</details><p>Also includes the inspected crown fracture and local cornice weathering studies. Working candidate; user approval remains pending. Reference artwork is your original work made with ChatGPT Images 2.5.</p><script>function pick(v){{document.getElementById('main').src='{P}'+v+'-main.png'}}</script></html>'''
# Review target is preserved in the project; no temporary clipboard dependency.
assert (R/'art/studies/alley-rust-137/reference-target.png').exists()
h=h.replace('/references/user-rust-137/target.png','/art/studies/alley-rust-137/reference-target.png')
critic=O/'critic.json'
if critic.exists():
 scores=json.loads(critic.read_text())['scores']
 h=h.replace('<details><summary>Grayscale</summary>', '<p>Independent colosseum scores: '+', '.join(k.replace('_',' ')+': '+str(v) for k,v in scores.items())+'. The 95-per-axis target remains open.</p><details><summary>Grayscale</summary>')
(R/'prototype/review-138.html').write_text(h)
paths=re.findall(r'(?:src|href)="(/[^"#]+)"',h); missing=[p for p in paths if not(R/p.lstrip('/')).exists()]
(O/'delivery-check.json').write_text(json.dumps({'missing':missing,'resolution':list(Image.open(O/'main-4k.png').size)},indent=2));assert not missing,missing
print('Published review138')
