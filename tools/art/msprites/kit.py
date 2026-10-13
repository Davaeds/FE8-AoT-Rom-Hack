"""Helpers for the ASCII map sprite frames: parse, mirror, shift, preview."""
import numpy as np
from PIL import Image, ImageDraw
from pal import LEGEND, PALETTES


def grid(text, w=None, h=None):
    rows = [r for r in text.strip('\n').split('\n')]
    rows = [r.rstrip() for r in rows]
    w = w or max(len(r) for r in rows)
    h = h or len(rows)
    a = np.zeros((h, w), np.uint8)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == ' ':
                c = '.'
            a[y, x] = LEGEND[c]
    return a


def mirror(a):
    return a[:, ::-1].copy()


def shift(a, dx=0, dy=0):
    out = np.zeros_like(a)
    h, w = a.shape
    ys, xs = slice(max(0, dy), min(h, h + dy)), slice(max(0, dx), min(w, w + dx))
    ys0, xs0 = slice(max(0, -dy), min(h, h - dy)), slice(max(0, -dx), min(w, w - dx))
    out[ys, xs] = a[ys0, xs0]
    return out


def over(dst, src, x0=0, y0=0):
    out = dst.copy()
    h, w = src.shape
    for y in range(h):
        for x in range(w):
            if src[y, x] and 0 <= y + y0 < out.shape[0] and 0 <= x + x0 < out.shape[1]:
                out[y + y0, x + x0] = src[y, x]
    return out


def place(a, fw, fh, cx=None):
    """Bottom-align a onto an fw x fh canvas, centred on cx."""
    f = np.zeros((fh, fw), np.uint8)
    h, w = a.shape
    cx = fw // 2 if cx is None else cx
    return over(f, a, cx - w // 2, fh - h)


def rgb(a, pal=0, bg=(60, 60, 80)):
    p = PALETTES[pal]
    out = np.array([[bg if v == 0 else p[v] for v in row] for row in a], np.uint8)
    return Image.fromarray(out)


def preview(items, path, scale=8, bg=(60, 60, 80), cols=None):
    """items: list of (label, array, pal)."""
    cols = cols or len(items)
    cw = max(a.shape[1] for _, a, _ in items) * scale + 8
    ch = max(a.shape[0] for _, a, _ in items) * scale + 14
    rows = (len(items) + cols - 1) // cols
    img = Image.new('RGB', (cols * cw, rows * ch), (24, 24, 30))
    d = ImageDraw.Draw(img)
    for k, (lab, a, p) in enumerate(items):
        x, y = (k % cols) * cw, (k // cols) * ch
        img.paste(rgb(a, p, bg).resize((a.shape[1] * scale, a.shape[0] * scale), Image.NEAREST), (x, y + 12))
        d.text((x + 2, y), lab, fill=(255, 255, 0))
    img.save(path)
    return img


GRASS = (136, 176, 96)


def proof(frames, path, pal=0, big=8):
    """Frames side by side: big scale on dark, then 1x/2x/3x on grass (how it reads in game)."""
    n = len(frames)
    h = max(a.shape[0] for a in frames)
    w = max(a.shape[1] for a in frames)
    top = Image.new('RGB', (n * (w * big + 6), h * big), (24, 24, 30))
    for k, a in enumerate(frames):
        top.paste(rgb(a, pal).resize((a.shape[1] * big, a.shape[0] * big), Image.NEAREST), (k * (w * big + 6), 0))
    row = Image.new('RGB', (top.width, h * 3 + 8), GRASS)
    x = 4
    for s in (1, 2, 3):
        for a in frames:
            row.paste(rgb(a, pal, GRASS).resize((a.shape[1] * s, a.shape[0] * s), Image.NEAREST), (x, 4))
            x += a.shape[1] * s + 4
        x += 10
    out = Image.new('RGB', (top.width, top.height + row.height), (0, 0, 0))
    out.paste(top, (0, 0)); out.paste(row, (0, top.height))
    out.save(path)
    return out
