#!/usr/bin/env python3
"""Convert a 240x160 RGB picture into an FE8 CG (the picture behind CG-mode text).

    python3 tools/cgconv.py AoT/Graphics/Backgrounds/NarrationCG.png

Writes, next to the PNG: <name>_chunk0.dmp .. <name>_chunk9.dmp (LZ77, 64 tiles
each), <name>_tsa.dmp and <name>_pal.dmp, plus <name>_preview.png showing the
picture exactly as the GBA will draw it. The build includes the .dmp files, so
this only needs to run after the PNG changes. Needs numpy and Pillow (not part
of the normal build).

Format (FE8U gCGDataTable entry): pointer to ten LZ77 chunks of 0x800 bytes of
4bpp tiles, pointer to a TSA (width-1, height-1, then u16 entries from the
bottom row up: tile | palette << 12), pointer to the palettes. The picture
uses six 16-colour palettes; colour 0 is never used so nothing is see-through.
Each 8x8 tile gets one palette, chosen by alternating palette fitting and tile
assignment (k-means), with light ordered dithering for smooth gradients.
"""
import pathlib
import sys

import numpy as np
from PIL import Image

W, H = 240, 160
TW, TH = W // 8, H // 8
NPAL, NCOL = 6, 15
CHUNKS, CHUNK_TILES = 10, 64
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5


def lz77_compress(src):
    """GBA BIOS LZ77 (type 0x10), never using displacement 1 so it is VRAM-safe."""
    src = bytes(src)
    n = len(src)
    out = bytearray([0x10, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    pos = 0
    while pos < n:
        flag_at = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if pos >= n:
                break
            best_len, best_disp = 0, 0
            for disp in range(2, min(pos, 0x1000) + 1):
                ln = 0
                while ln < 18 and pos + ln < n and src[pos + ln] == src[pos + ln - disp]:
                    ln += 1
                if ln > best_len:
                    best_len, best_disp = ln, disp
                    if ln == 18:
                        break
            if best_len >= 3:
                flags |= 0x80 >> bit
                d = best_disp - 1
                out += bytes([((best_len - 3) << 4) | (d >> 8), d & 0xFF])
                pos += best_len
            else:
                out.append(src[pos])
                pos += 1
        out[flag_at] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def kmeans(points, k, iters, rng):
    pts = points.astype(float)
    # k-means++ seeding
    centres = [pts[rng.integers(len(pts))]]
    for _ in range(1, k):
        d = np.min(((pts[:, None, :] - np.array(centres)[None]) ** 2).sum(-1), axis=1)
        if d.sum() == 0:
            centres.append(pts[rng.integers(len(pts))])
        else:
            centres.append(pts[rng.choice(len(pts), p=d / d.sum())])
    c = np.array(centres)
    for _ in range(iters):
        lab = np.argmin(((pts[:, None, :] - c[None]) ** 2).sum(-1), axis=1)
        for j in range(k):
            sel = pts[lab == j]
            if len(sel):
                c[j] = sel.mean(0)
    return c


def convert(png):
    img = np.asarray(Image.open(png).convert('RGB'), float)
    assert img.shape == (H, W, 3), f'{png} must be {W}x{H}'
    c5 = img * 31 / 255
    tiles = c5.reshape(TH, 8, TW, 8, 3).transpose(0, 2, 1, 3, 4).reshape(TH * TW, 64, 3)
    rng = np.random.default_rng(845)
    means = tiles.mean(1)
    assign = np.argmin(((means[:, None] - kmeans(means, NPAL, 20, rng)[None]) ** 2).sum(-1), axis=1)
    for _ in range(6):
        pals = []
        for p in range(NPAL):
            px = tiles[assign == p].reshape(-1, 3)
            if len(px) < NCOL:
                px = tiles.reshape(-1, 3)
            if len(px) > 6000:
                px = px[rng.choice(len(px), 6000, replace=False)]
            pals.append(kmeans(px, NCOL, 12, rng))
        pals = np.array(pals)
        err = np.zeros((len(tiles), NPAL))
        for p in range(NPAL):
            d = ((tiles[:, :, None, :] - pals[p][None, None]) ** 2).sum(-1)
            err[:, p] = d.min(-1).sum(-1)
        assign = np.argmin(err, axis=1)
    pals = np.clip(np.round(pals), 0, 31).astype(int)
    # final mapping with ordered dithering
    idx = np.zeros((H, W), int)
    pal_of = assign.reshape(TH, TW)
    for ty in range(TH):
        for tx in range(TW):
            pal = pals[pal_of[ty, tx]].astype(float)
            blk = c5[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8] + np.tile(BAYER, (2, 2))[..., None] * 0.9
            d = ((blk[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
            idx[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8] = d.argmin(-1) + 1
    return pals, pal_of, idx


def write(png):
    png = pathlib.Path(png)
    pals, pal_of, idx = convert(png)
    stem = png.with_suffix('')
    # tiles in reading order, padded to 640
    data = bytearray()
    for ty in range(TH):
        for tx in range(TW):
            t = idx[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8]
            for row in t:
                for x in range(0, 8, 2):
                    data.append(int(row[x]) | (int(row[x + 1]) << 4))
    data += bytes(CHUNKS * CHUNK_TILES * 32 - len(data))
    for k in range(CHUNKS):
        part = data[k * CHUNK_TILES * 32:(k + 1) * CHUNK_TILES * 32]
        pathlib.Path(f'{stem}_chunk{k}.dmp').write_bytes(lz77_compress(part))
    tsa = bytearray([TW - 1, TH - 1])
    for ty in reversed(range(TH)):
        for tx in range(TW):
            e = (ty * TW + tx) | (int(pal_of[ty, tx]) << 12)
            tsa += bytes([e & 0xFF, e >> 8])
    pathlib.Path(f'{stem}_tsa.dmp').write_bytes(bytes(tsa))
    pal = bytearray()
    for p in range(8):
        for i in range(16):
            r, g, b = (pals[p][i - 1] if (p < NPAL and i > 0) else (0, 0, 0))
            v = int(r) | (int(g) << 5) | (int(b) << 10)
            pal += bytes([v & 0xFF, v >> 8])
    pathlib.Path(f'{stem}_pal.dmp').write_bytes(bytes(pal))
    # preview as the GBA draws it (5-bit colour expanded)
    prev = np.zeros((H, W, 3), np.uint8)
    for ty in range(TH):
        for tx in range(TW):
            pal = pals[pal_of[ty, tx]]
            t = idx[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8] - 1
            prev[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8] = (pal[t] * 255 / 31).round().astype(np.uint8)
    Image.fromarray(prev).save(f'{stem}_preview.png')
    print(f'{png}: {TW * TH} tiles, {NPAL} palettes')


if __name__ == '__main__':
    for a in sys.argv[1:]:
        write(a)
