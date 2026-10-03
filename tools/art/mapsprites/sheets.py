"""Assemble SMS (standing) and MMS (moving) sheets and write indexed PNGs.

SMS: 3 frames stacked vertically; frame size 16x16, 16x32 or 32x32.
MMS: 15 frames of 32x32 stacked vertically:
  0-3 facing left (walk), 4-7 facing down (walk), 8-11 facing up (walk),
  12-14 selected (facing down).
"""
import os
import numpy as np
from PIL import Image
from render import PALS, ROOT

OUT = os.path.join(ROOT, 'AoT', 'Graphics', 'MapSprites')


def blit(dst, src, x0, y0):
    h, w = src.shape
    for y in range(h):
        for x in range(w):
            v = src[y, x]
            if v:
                yy, xx = y0 + y, x0 + x
                if 0 <= yy < dst.shape[0] and 0 <= xx < dst.shape[1]:
                    dst[yy, xx] = v


def mirror(a):
    return a[:, ::-1].copy()


def bob(a, dy=1, rows=None):
    """Shift the top `rows` rows down by dy (a breathing nod)."""
    out = a.copy()
    rows = rows or a.shape[0]
    top = a[:rows].copy()
    out[:rows] = 0
    out[dy:rows + dy] = np.where(top[:rows] != 0, top[:rows], out[dy:rows + dy])
    # keep lower part pixels that were under the old top
    for y in range(rows + dy, a.shape[0]):
        out[y] = a[y]
    return out


def place_bottom(frame_w, frame_h, art, cx=None, bottom=None):
    """Return a frame with art bottom-aligned (shadow on the last row) and centered."""
    f = np.zeros((frame_h, frame_w), np.uint8)
    h, w = art.shape
    cx = frame_w // 2 if cx is None else cx
    bottom = frame_h if bottom is None else bottom
    blit(f, art, cx - (w + 1) // 2, bottom - h)
    return f


def sms_sheet(frames, fw, fh, cx=None):
    return np.vstack([place_bottom(fw, fh, a, cx) for a in frames])


def mms_sheet(left4, down4, up4, sel3, cx=16):
    fr = [place_bottom(32, 32, a, cx) for a in list(left4) + list(down4) + list(up4) + list(sel3)]
    assert len(fr) == 15
    return np.vstack(fr)


def save_png(idx, name, pal=0):
    im = Image.fromarray(idx.astype(np.uint8), 'P')
    flat = []
    for k, c in enumerate(PALS[pal]):
        flat += list(c) if k else [128, 160, 128]
    im.putpalette(flat)
    im.save(f'{OUT}/{name}.png', transparency=0)
    return im
