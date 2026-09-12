"""Reproducible, non-generative inspection of the supplied screenshot.

Run: .venv/bin/python analysis/inspect_manuscript.py
All crop coordinates are source pixels, with origin at top left.
No OCR, external text, font template, or learned image restoration is used.
"""

from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from scipy.ndimage import gaussian_filter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = next(ROOT.glob('Screenshot*.png'))
OUT = ROOT / 'site' / 'evidence'
OUT.mkdir(parents=True, exist_ok=True)
source = Image.open(SOURCE).convert('RGB')
source.save(OUT / 'source.png')

# Bounding boxes are (left, top, right, bottom); right and bottom are exclusive.
REGIONS = {
    'A_upper_right': (1030, 345, 1180, 418),
    'B_day_word': (416, 530, 560, 598),
    'C_lower_left': (245, 1162, 365, 1248),
    'D_beneath_skies': (205, 999, 558, 1100),
    'E_first_word': (835, 280, 1010, 389),
    'F_called': (1035, 574, 1200, 645),
    'G_day_one': (992, 658, 1200, 728),
    'H_day_two': (953, 943, 1157, 1023),
    'I_between': (559, 761, 802, 854),
    'J_lower_called': (572, 1065, 737, 1153),
    'K_light': (577, 509, 700, 595),
    'L_top_line': (275, 285, 1012, 385),
    'M_top_block': (160, 280, 1210, 645),
    'N_middle_block': (162, 651, 1205, 936),
    'O_bottom_block': (197, 944, 1191, 1255),
    'P_surface_clear': (352, 397, 429, 449),
    'Q_said_clear': (1032, 725, 1188, 780),
    'R_god_clear': (710, 510, 874, 610),
    'S_waters_clear': (358, 702, 510, 787),
    'T_and_be_clear': (239, 725, 351, 778),
    'U_good_bottom': (554, 1167, 708, 1231),
    'V_day_context': (410, 510, 700, 602),
    'W_second_line': (170, 354, 1030, 472),
    'X_third_line': (165, 435, 1100, 535),
    'Y_fourth_line': (170, 504, 875, 609),
    'Z_middle_left_edge': (162, 769, 291, 854),
}


def wiener(gray, sigma, regularization):
    """Illustrative inverse-filter hypotheses; neither PSF nor noise is known."""
    a = np.pad(np.asarray(gray, dtype=np.float64) / 255, 24, mode='reflect')
    fy, fx = np.fft.fftfreq(a.shape[0])[:, None], np.fft.fftfreq(a.shape[1])[None, :]
    transfer = np.exp(-2 * np.pi**2 * sigma**2 * (fx**2 + fy**2))
    inverse = transfer / (transfer**2 + regularization)
    restored = np.fft.ifft2(np.fft.fft2(a) * inverse).real
    # Restore DC gain only; do not threshold or paint inferred ink.
    restored *= 1 + regularization
    return Image.fromarray(np.clip(restored[24:-24, 24:-24]*255, 0, 255).astype('uint8'))


def variants(crop):
    gray = crop.convert('L')
    a = np.asarray(gray, dtype=np.float64)
    # A broad Gaussian estimates slow illumination variation. It is not an
    # estimate of missing strokes. Subtracting it can accentuate cracks too.
    background = gaussian_filter(a, sigma=10)
    flat = np.clip((a - background) * 2 + 180, 0, 255).astype('uint8')
    yield 'original', crop
    yield 'contrast', ImageOps.autocontrast(gray, cutoff=1)
    yield 'background', Image.fromarray(flat)
    yield 'unsharp', gray.filter(ImageFilter.UnsharpMask(radius=1, percent=100, threshold=3))
    for threshold in (65, 85, 105):
        yield f'threshold_{threshold}', Image.fromarray(np.where(a < threshold, 0, 255).astype('uint8'))
    yield 'wiener_mild', wiener(gray, .65, .06)
    yield 'wiener_medium', wiener(gray, 1.0, .06)
    yield 'wiener_strong', wiener(gray, 1.0, .02)


manifest = {
    'source': SOURCE.name,
    'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'size': list(source.size),
    'coordinate_system': 'top-left origin, [left, top, right-exclusive, bottom-exclusive]',
    'regions': {},
    'processing': {
        'original': 'unchanged pixels; displayed with nearest-neighbor enlargement',
        'contrast': 'grayscale autocontrast, 1 percent cutoff at each end',
        'background': 'clip(2 * (grayscale - Gaussian(sigma=10 px)) + 180, 0, 255)',
        'unsharp': 'Pillow UnsharpMask radius=1, percent=100, threshold=3',
        'threshold_65': 'black where original grayscale < 65, white elsewhere',
        'threshold_85': 'black where original grayscale < 85, white elsewhere',
        'threshold_105': 'black where original grayscale < 105, white elsewhere',
        'wiener_mild': 'Wiener inverse filter, assumed Gaussian sigma=.65 px, K=.06; reflection pad 24 px; DC normalized; unvalidated PSF hypothesis',
        'wiener_medium': 'Wiener inverse filter, assumed Gaussian sigma=1 px, K=.06; reflection pad 24 px; DC normalized; unvalidated PSF hypothesis',
        'wiener_strong': 'Wiener inverse filter, assumed Gaussian sigma=1 px, K=.02; reflection pad 24 px; DC normalized; unvalidated PSF hypothesis',
    },
}

for key, box in REGIONS.items():
    crop = source.crop(box)
    files = {}
    for mode, result in variants(crop):
        filename = f'{key}_{mode}.png'
        result.save(OUT / filename)
        files[mode] = filename
    manifest['regions'][key] = {'box': box, 'files': files}
    if key.startswith(('M_', 'N_', 'O_')):
        continue
    scale = 4 if crop.width < 250 else 3
    width, height = crop.size
    selected = list(variants(crop))
    sheet = Image.new('RGB', (width * scale * 2, (height * scale + 32) * ((len(selected)+1)//2)), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, (mode, result) in enumerate(selected):
        x = (i % 2) * width * scale
        y = (i // 2) * (height * scale + 32)
        draw.text((x + 5, y + 8), f'{key}: {mode}', fill='black')
        sheet.paste(result.resize((width * scale, height * scale), Image.Resampling.NEAREST), (x, y + 32))
    sheet.save(OUT / f'{key}_sheet.png')

overview = source.copy()
draw = ImageDraw.Draw(overview)
for key, box in REGIONS.items():
    if key.startswith(('M_', 'N_', 'O_')):
        continue
    draw.rectangle(box, outline='#fa5757', width=2)
    draw.rectangle((box[0], box[1]-20, box[0]+len(key)*7, box[1]), fill='white')
    draw.text((box[0]+2, box[1]-16), key, fill='black')
overview.save(OUT / 'region-map.png')
deblur_sheet = Image.new('RGB', (1800, 1060), 'white')
draw = ImageDraw.Draw(deblur_sheet)
for row, key in enumerate(('A_upper_right', 'B_day_word', 'C_lower_left')):
    for column, mode in enumerate(('original', 'wiener_mild', 'wiener_medium', 'wiener_strong')):
        crop = Image.open(OUT / f'{key}_{mode}.png')
        enlarged = crop.resize((crop.width*3, crop.height*3), Image.Resampling.NEAREST)
        draw.text((column*450+4, row*350+5), f'{key} / {mode}', fill='black')
        deblur_sheet.paste(enlarged, (column*450, row*350+30))
deblur_sheet.save(OUT / 'deconvolution-comparison.png')
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'source_sha256': manifest['sha256'], 'regions': len(REGIONS), 'output': str(OUT)}))
