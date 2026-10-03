"""Toolkit for big map sprites: fill-only ASCII art, auto outline, ground shadow, previews."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from render import PALS

OUTLINE, SHADOW = 15, 13

# Shared letters (palette indices valid on every faction palette unless noted).
BASE = {
    '.': 0, 'O': 15, 'K': 15,
    'H': 6, 'S': 5, 's': 4,          # skin: highlight, mid, shadow
    'W': 14, 'w': 3,                 # white, light grey (3 is faction-dependent: grey on red)
    'G': 13,                         # ground shadow
    'Y': 12,                         # yellow
    'M': 7, 'm': 8, 'L': 9, 'l': 10, # faction main ramp (reds on enemy units)
    'P': 2, 'p': 1,                  # faction light/dark (lilac/mauve on enemy units)
}


def art(rows, extra=None):
    cmap = dict(BASE)
    if extra:
        cmap.update(extra)
    w = max(len(r) for r in rows)
    for i, r in enumerate(rows):
        assert len(r) == w, f'row {i} has width {len(r)}, expected {w}: {r!r}'
    a = np.zeros((len(rows), w), np.uint8)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            a[y, x] = cmap[c]
    return a


def outline(a, color=OUTLINE):
    """1px outline (4-neighbourhood) around every non-transparent pixel."""
    h, w = a.shape
    p = np.zeros((h + 2, w + 2), np.uint8)
    p[1:-1, 1:-1] = a
    solid = p != 0
    near = np.zeros_like(solid)
    near[1:, :] |= solid[:-1, :]
    near[:-1, :] |= solid[1:, :]
    near[:, 1:] |= solid[:, :-1]
    near[:, :-1] |= solid[:, 1:]
    out = p.copy()
    out[(~solid) & near] = color
    return out


def frame(a, fw=32, fh=32, cx=None, bottom=None, shadow=None):
    """Place outlined art in a frame, centred on cx, feet row at `bottom`-1 then add ground shadow."""
    f = np.zeros((fh, fw), np.uint8)
    h, w = a.shape
    cx = fw // 2 if cx is None else cx
    bottom = fh if bottom is None else bottom
    x0, y0 = cx - w // 2, bottom - h
    for y in range(h):
        for x in range(w):
            v = a[y, x]
            if v and 0 <= y0 + y < fh and 0 <= x0 + x < fw:
                f[y0 + y, x0 + x] = v
    if shadow:
        sw, sy = shadow  # width, row
        for x in range(cx - sw // 2, cx - sw // 2 + sw):
            if 0 <= x < fw and f[sy, x] == 0:
                f[sy, x] = SHADOW
    return f


def mirror(a):
    return a[:, ::-1].copy()


def shift(a, dx=0, dy=0):
    out = np.zeros_like(a)
    h, w = a.shape
    ys = slice(max(0, dy), min(h, h + dy)); yd = slice(max(0, -dy), min(h, h - dy))
    xs = slice(max(0, dx), min(w, w + dx)); xd = slice(max(0, -dx), min(w, w - dx))
    out[ys, xs] = a[yd, xd]
    return out


def colorize(idx, pal=1, bg=(40, 40, 60)):
    rgb = np.array([bg] + [tuple(c) for c in PALS[pal][1:]], np.uint8)
    return Image.fromarray(rgb[idx])


def preview(frames, path, pal=1, scale=6, cols=8, bgtile=None):
    """Big view of frames plus a 2x in-game-scale strip on a map background."""
    fh, fw = frames[0][1].shape
    rows = (len(frames) + cols - 1) // cols
    W = cols * (fw * scale + 8)
    H = rows * (fh * scale + 18)
    img = Image.new('RGB', (W, H + fh * 2 * 2 + 30), (24, 24, 28))
    d = ImageDraw.Draw(img)
    for k, (name, a) in enumerate(frames):
        x, y = (k % cols) * (fw * scale + 8), (k // cols) * (fh * scale + 18)
        img.paste(colorize(a, pal).resize((fw * scale, fh * scale), Image.NEAREST), (x, y + 14))
        d.text((x + 2, y + 1), name, fill=(255, 255, 0))
    # game-scale strip
    strip = Image.new('RGB', (len(frames) * (fw + 4) + 4, fh + 4), (198, 206, 140))
    if bgtile is not None:
        for tx in range(0, strip.width, bgtile.width):
            for ty in range(0, strip.height, bgtile.height):
                strip.paste(bgtile, (tx, ty))
    for k, (name, a) in enumerate(frames):
        im = colorize(a, pal).convert('RGBA')
        px = np.array(im)
        px[..., 3] = np.where(a == 0, 0, 255)
        strip.paste(Image.fromarray(px), (4 + k * (fw + 4), 2), Image.fromarray(px))
    img.paste(strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST), (0, H + 10))
    img.save(path)
    return img
