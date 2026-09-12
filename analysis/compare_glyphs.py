"""Small within-image shape comparison, not OCR or a probability model.

Manual reference labels are provisional readings of clearer local forms.
Comparison is restricted to explicitly listed alternatives and can be wrong.
Coordinates and processing settings are exported for audit.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import shift

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site' / 'evidence'
im = Image.open(OUT / 'source.png').convert('L')
REFS = {
    'aleph_said': ('aleph', (1088, 739, 1126, 773)),
    'aleph_god': ('aleph', (829, 551, 864, 592)),
    'aleph_light': ('aleph', (637, 550, 668, 591)),
    'resh_light': ('resh', (577, 548, 613, 593)),
    'he_god': ('he', (772, 550, 801, 591)),
    'he_and_be': ('he', (265, 735, 306, 775)),
    'yod_said': ('yod', (1128, 740, 1153, 773)),
    'yod_god': ('yod', (751, 549, 772, 590)),
    'vav_said': ('vav', (1152, 738, 1180, 779)),
    'vav_day': ('vav', (509, 548, 529, 590)),
    'mem_waters': ('mem', (431, 718, 465, 768)),
    'final_mem_god': ('final_mem', (710, 546, 752, 604)),
    'final_mem_day2': ('final_mem', (1045, 960, 1090, 1015)),
    'bet_good': ('bet', (440, 461, 483, 505)),
    'bet_good_bottom': ('bet', (561, 1183, 602, 1222)),
    'pe_surface': ('pe', (399, 398, 429, 443)),
    'nun_surface': ('nun', (384, 402, 401, 444)),
}
TARGETS = {
    'C_third_letter': {'box': (285, 1185, 314, 1219), 'alternatives': ['aleph', 'resh', 'he', 'yod'],
        'exclude': [(0, 24, 5, 34)]},
    'A_left_letter': {'box': (1062, 365, 1091, 399), 'alternatives': ['aleph', 'yod', 'he'],
        'exclude': [(0, 17, 8, 34), (8, 28, 12, 34)]},
    'A_right_letter': {'box': (1126, 361, 1164, 402), 'alternatives': ['bet', 'pe', 'resh'], 'exclude': []},
    'A_middle_letter': {'box': (1090, 361, 1125, 402), 'alternatives': ['resh', 'nun', 'yod'], 'exclude': []},
    'B_extra_form': {'box': (474, 541, 503, 586), 'alternatives': ['mem', 'yod', 'vav', 'final_mem'], 'exclude': []},
}


def normalize(box, level, exclude=()):
    a = np.asarray(im.crop(box), dtype=float)
    valid = np.ones(a.shape, dtype=bool)
    for x0, y0, x1, y1 in exclude:
        valid[y0:y1, x0:x1] = False
    # A soft foreground estimate, threshold swept below. No inferred strokes.
    ink = np.clip((level + 30 - a) / 60, 0, 1) * valid
    ys, xs = np.where((ink > .5) & valid)
    if len(xs) == 0:
        raise ValueError(f'No foreground in {box}')
    x0, x1, y0, y1 = max(0, xs.min()-2), min(a.shape[1], xs.max()+3), max(0, ys.min()-2), min(a.shape[0], ys.max()+3)
    ink, valid = ink[y0:y1, x0:x1], valid[y0:y1, x0:x1]
    # Common canvas, aspect preserved; shape rankings are not probabilities.
    ratio = 40 / max(ink.shape)
    size = (max(1, round(ink.shape[1]*ratio)), max(1, round(ink.shape[0]*ratio)))
    resized = np.asarray(Image.fromarray(ink.astype('float32')).resize(size, Image.Resampling.BILINEAR))
    vm = np.asarray(Image.fromarray(valid.astype('uint8')*255).resize(size, Image.Resampling.NEAREST)) > 0
    result, mask = np.zeros((48, 48)), np.ones((48, 48), dtype=bool)
    x, y = (48-size[0])//2, (48-size[1])//2
    result[y:y+size[1], x:x+size[0]] = resized
    mask[y:y+size[1], x:x+size[0]] = vm
    return result, mask


def similarity(target, ref):
    a, mask = target
    best = 0.0
    for dy in (-2, 0, 2):
        for dx in (-2, 0, 2):
            b = shift(ref[0], (dy, dx), order=1, mode='constant', cval=0)
            # Soft Dice overlap on observable target pixels.
            score = 2 * np.sum(a[mask] * b[mask]) / (np.sum(a[mask]**2) + np.sum(b[mask]**2) + 1e-9)
            best = max(best, float(score))
    return best


results = {}
for name, target in TARGETS.items():
    settings = []
    for level in (65, 75, 85, 95, 105):
        vector = normalize(target['box'], level, target['exclude'])
        ranked = []
        for ref_name, (letter, box) in REFS.items():
            if letter in target['alternatives']:
                ranked.append({'reference': ref_name, 'letter': letter,
                               'score': round(similarity(vector, normalize(box, level)), 4)})
        settings.append({'level': level, 'ranking': sorted(ranked, key=lambda r: -r['score'])})
    results[name] = {**target, 'settings': settings}

# Hold out one manually labelled reference at a time where a second example
# of its class exists. This measures only consistency inside this tiny sample.
controls = []
for name, (letter, box) in REFS.items():
    if sum(other_letter == letter for other_letter, _ in REFS.values()) < 2:
        continue
    ranked = [(similarity(normalize(box, 85), normalize(other_box, 85)), other_name, other_letter)
              for other_name, (other_letter, other_box) in REFS.items() if other_name != name]
    score, nearest, predicted = max(ranked)
    controls.append({'reference': name, 'label': letter, 'nearest': nearest, 'predicted': predicted,
                     'score': round(score, 4), 'match': predicted == letter})

metadata = {'method': __doc__, 'references': {name: {'letter': letter, 'box': box} for name, (letter, box) in REFS.items()},
            'targets': results, 'leave_one_out_at_level_85': controls,
            'warning': 'Manual labels, tiny convenience sample, some classes have one reference. Scores are shape overlaps, NOT calibrated reading confidence. Masks exclude specified damaged-edge rectangles only.'}
(OUT / 'glyph-comparison.json').write_text(json.dumps(metadata, indent=2)+'\n')

entries = [(name, box) for name, (_, box) in REFS.items()] + [(name, t['box']) for name, t in TARGETS.items()]
atlas = Image.new('RGB', (1000, ((len(entries)+4)//5)*230), 'white')
draw = ImageDraw.Draw(atlas)
for i, (name, box) in enumerate(entries):
    x, y = (i%5)*200, (i//5)*230
    draw.text((x+8, y+8), name, fill='black')
    crop = im.crop(box)
    crop.thumbnail((176, 195))
    scale = min(176/crop.width, 195/crop.height)
    crop = crop.resize((round(crop.width*scale), round(crop.height*scale)), Image.Resampling.NEAREST)
    atlas.paste(crop, (x+8, y+30))
atlas.save(OUT / 'glyph-atlas.png')
print(json.dumps({'controls_correct': sum(c['match'] for c in controls), 'controls_total': len(controls),
                  'winners': {name: [s['ranking'][0]['letter'] for s in value['settings']] for name, value in results.items()}}))
