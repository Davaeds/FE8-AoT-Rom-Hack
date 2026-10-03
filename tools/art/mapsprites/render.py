"""Palettes and quick previews for the map sprite generators.

The five FE8 map sprite palettes (blue, red, green, grey, purple) are read from
the clean ROM in the repo root, so the indexed PNGs carry the in-game colours.
"""
import os
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
MAP_PAL = 0x59EE20  # file offset of the 5 map sprite palettes (32 bytes each)


def map_palettes(path=os.path.join(ROOT, 'FE8_clean.gba')):
    raw = open(path, 'rb').read()[MAP_PAL:MAP_PAL + 5 * 32]
    pals = []
    for k in range(5):
        cols = []
        for i in range(16):
            v = raw[k * 32 + 2 * i] | (raw[k * 32 + 2 * i + 1] << 8)
            r, g, b = v & 31, (v >> 5) & 31, (v >> 10) & 31
            cols.append((r * 255 // 31, g * 255 // 31, b * 255 // 31))
        pals.append(cols)
    return pals


PALS = map_palettes()  # 0 blue, 1 red, 2 green, 3 grey, 4 purple


def to_idx(rows, cmap):
    h, w = len(rows), max(len(r) for r in rows)
    a = np.zeros((h, w), np.uint8)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            a[y, x] = cmap[c]
    return a


def colorize(idx, pal, bg=(40, 40, 60)):
    h, w = idx.shape
    img = np.zeros((h, w, 3), np.uint8)
    for y in range(h):
        for x in range(w):
            v = idx[y, x]
            img[y, x] = bg if v == 0 else PALS[pal][v]
    return Image.fromarray(img)


def sheet(items, scale=8, pal=0, cols=None, label=True):
    """items: list of (name, idx array)."""
    cols = cols or len(items)
    cw = max(a.shape[1] for _, a in items) * scale + 6
    chh = max(a.shape[0] for _, a in items) * scale + 16
    rows = (len(items) + cols - 1) // cols
    out = Image.new('RGB', (cols * cw, rows * chh), (20, 20, 20))
    d = ImageDraw.Draw(out)
    for k, (name, a) in enumerate(items):
        x, y = (k % cols) * cw, (k // cols) * chh
        im = colorize(a, pal).resize((a.shape[1] * scale, a.shape[0] * scale), Image.NEAREST)
        out.paste(im, (x, y + 14))
        if label:
            d.text((x + 2, y + 1), name, fill=(255, 255, 0))
    return out
