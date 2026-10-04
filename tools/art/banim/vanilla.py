"""Decode a vanilla battle animation from the clean ROM (for calibration only;
nothing decoded here is ever written into the repo)."""
import struct
import sys

import numpy as np

sys.path.insert(0, __import__("os").path.dirname(__file__))
import lz77  # noqa: E402

ROM = open("FE8_clean.gba", "rb").read()
SIZES = {(0, 0): (1, 1), (0, 1): (2, 2), (0, 2): (4, 4), (0, 3): (8, 8), (1, 0): (2, 1), (1, 1): (4, 1),
         (1, 2): (4, 2), (1, 3): (8, 4), (2, 0): (1, 2), (2, 1): (1, 4), (2, 2): (2, 4), (2, 3): (4, 8)}


def u32(b, a):
    return struct.unpack_from("<I", b, a)[0]


def entry(i):
    e = 0xC00008 + i * 32
    return [u32(ROM, e + 12 + 4 * k) & 0x1FFFFFF for k in range(5)]


def tiles(sheet):
    t = np.frombuffer(sheet, np.uint8).reshape(-1, 32)
    out = np.zeros((len(t), 8, 8), np.uint8)
    out[:, :, 0::2] = (t & 15).reshape(-1, 8, 4)
    out[:, :, 1::2] = (t >> 4).reshape(-1, 8, 4)
    return out


def oam_entries(O, off):
    out = []
    while True:
        h = u32(O, off)
        if h == 1:
            return out
        a0, a1 = h & 0xFFFF, h >> 16
        oam2, x, y = struct.unpack_from("<Hhh", O, off + 4)
        out.append((a0, a1, oam2, x, y))
        off += 12


def render(sheet, ents, size=(512, 512), origin=(256, 256)):
    T = tiles(sheet)
    img = np.zeros(size, np.int16) - 1
    for a0, a1, oam2, x, y in ents:
        if a0 & 0x300:  # affine/disabled: skip
            continue
        w, h = SIZES[(a0 >> 14, a1 >> 14)]
        hf, vf = a1 >> 12 & 1, a1 >> 13 & 1
        base = oam2 & 0x3FF
        for ty in range(h):
            for tx in range(w):
                t = T[base + ty * 32 + tx]
                if hf: t = t[:, ::-1]
                if vf: t = t[::-1]
                dx = (w - 1 - tx if hf else tx) * 8 + x + origin[0]
                dy = (h - 1 - ty if vf else ty) * 8 + y + origin[1]
                sub = img[dy:dy + 8, dx:dx + 8]
                m = t > 0
                sub[m] = t[m]
    return img
