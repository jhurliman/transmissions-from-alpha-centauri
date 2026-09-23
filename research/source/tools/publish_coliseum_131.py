"""Publish native rendered arch-ink comparisons."""
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[1]
O = R / 'art/studies/coliseum-131'
P = '/art/studies/coliseum-131/'
regions = {
    'arches': (1750, 560, 2190, 970),
    'detail': (1350, 320, 2690, 1230),
    'inner': (1850, 590, 1995, 760),
    'frame': (2015, 340, 2225, 680),
}
for label, path in [('before', R/'art/studies/coliseum-130/main-4k.png'), ('after', O/'main-4k.png')]:
    im = Image.open(path).convert('RGB')
    im.resize((1440, 1082), Image.Resampling.LANCZOS).save(O/f'{label}-main.png')
    for name, box in regions.items():
        im.crop(box).save(O/f'{label}-{name}.png')
    im.crop(regions['detail']).convert('L').save(O/f'{label}-gray.png')
    if label == 'after':
        im.resize((1440, 1082), Image.Resampling.LANCZOS).save(O/'main.png')

style = '''*{box-sizing:border-box}body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;max-width:1500px;margin:32px auto;padding:0 22px}a{color:#efbc91}img{width:100%;display:block}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:18px 0}figcaption{color:#c5bbc4;margin-top:7px}button{background:#30292d;border:1px solid #78616a;color:#eee7df;border-radius:5px;padding:9px 18px;cursor:pointer;font:inherit}button[aria-pressed=true]{background:#76534c;border-color:#bd8b79}.controls{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}h1{font-size:32px;line-height:1.2}h2{font-size:24px;margin-top:44px}details{margin:32px 0}summary{cursor:pointer}@media(max-width:800px){.pair{grid-template-columns:1fr}}'''
h = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>131 · Arch joints and raised framing</title><style>{style}</style><h1>131 · Arch joints and raised framing</h1><p>Narrow masonry joints rise from the arch crowns to the ledges above. The exposed bent framing now extends upward and anchors just below the intact left wall’s cap.</p><p><a href="#frame">Raised framing</a> · <a href="#arches">Arch comparison</a> · <a href="#detail">Whole coliseum</a> · <a href="{P}main-4k.png">4K render</a> · <a href="{P}scene.blend">Editable scene</a> · <a href="{P}kit.blend">Reusable kit</a></p><div class="controls"><button id="after" aria-pressed="true" onclick="choose('after')">131 · Current</button><button id="before" aria-pressed="false" onclick="choose('before')">130 · Previous</button></div><img id="main" src="{P}after-main.png">'''
for name, title in [('arches', 'Centered stone joints'), ('frame', 'Higher connection to the surviving wall'), ('detail', 'Whole coliseum')]:
    h += f'<section id="{name}"><h2>{title}</h2><div class="pair"><figure><img src="{P}before-{name}.png"><figcaption>130</figcaption></figure><figure><img src="{P}after-{name}.png"><figcaption>131</figcaption></figure></div></section>'
h += f'''<details><summary>Grayscale comparison</summary><div class="pair"><img src="{P}before-gray.png"><img src="{P}after-gray.png"></div></details><p>UCL-01 is your original artwork, created with ChatGPT Images 2.5. Its <a href="/art/original/coliseum/coliseum.png">original master</a> is stored with the project artwork.</p><p>The centerpiece remains in review.</p><script>function choose(v){{document.getElementById('main').src='{P}'+v+'-main.png';for(const x of ['after','before'])document.getElementById(x).setAttribute('aria-pressed',x===v?'true':'false')}}</script></html>'''
(R/'prototype/review-131.html').write_text(h)
