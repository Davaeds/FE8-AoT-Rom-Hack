#!/usr/bin/env python3
"""Build the AoT title screen graphics for the FE8U title screen.

    python3 tools/titleconv.py

Paints the backdrop (tools/art/paint_title.py), letters the logo, the subtitle,
"Press START" and the credit line, and writes into AoT/Graphics/Title/:

  bg1_tiles_a.dmp, bg1_tiles_b.dmp, bg1_map.dmp, bg1_pal.dmp   sky and Wall (BG1, palette 14)
  bg0_tiles.dmp, bg0_map.dmp, bg0_pal.dmp                     the Colossal's head (BG0, palette 15)
  logo.dmp      sprite sheet 256x64: logo (top half) and its drop shadow (bottom half)
  sub.dmp       sprite sheet 256x40: credit line, subtitle banner, "Press START"
  objpal.dmp    four sprite palettes: Press START, credit, logo, subtitle
  glow.dmp      sixteen colours the game cycles through for "Press START"
  title_bg.png, title_fg.png   the painted layers (inputs)
  title_preview.png            the screen as the GBA draws it

The build includes the .dmp files, so this only needs to run after the art
changes. Needs numpy and Pillow (not part of the normal build) and the
Liberation Serif and IPAGothic fonts (Debian packages fonts-liberation and
fonts-ipafont-gothic) for the lettering.

Layout (from the FE8U title code, Title_SetupMainGraphics and
DrawTitleSprites_Loop): BG1 tiles load to VRAM 0x0000 (first 384) and 0x3000
(next 256); BG0 tiles to 0x5000 (192 at most, the map follows at 0x6800). Both
maps are raw 32x20 tilemaps; the game adds the palette (and BG0's tile offset
0x280) itself. Sprites use 2D mapping: the logo at (4,48) with its shadow
half-transparent at (4,53), the subtitle at (16,85), "Press START" at (72,124)
built from two 48x16 halves, the credit line at (4,148).
"""
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools' / 'art'))
from cgconv import lz77_compress, kmeans  # noqa: E402
import paint_title  # noqa: E402

OUT = ROOT / 'AoT' / 'Graphics' / 'Title'
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
KANJI = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5


# ---------------------------------------------------------------- helpers
def to5(rgb):
    return tuple(int(round(c * 31 / 255)) for c in rgb)


def pal_bytes(cols5):
    out = bytearray()
    for r, g, b in cols5:
        v = r | (g << 5) | (b << 10)
        out += bytes([v & 0xFF, v >> 8])
    return bytes(out)


def tile_bytes(t):
    out = bytearray()
    for row in t:
        for x in range(0, 8, 2):
            out.append(int(row[x]) | (int(row[x + 1]) << 4))
    return bytes(out)


def sheet_bytes(idx):
    """2D-mapped sprite sheet (width 256): tiles row by row."""
    h, w = idx.shape
    assert w == 256 and h % 8 == 0
    out = bytearray()
    for ty in range(h // 8):
        for tx in range(32):
            out += tile_bytes(idx[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8])
    return bytes(out)


def quantize(rgb, mask, ncol, seed):
    """Fit ncol colours (5-bit) to the masked pixels, then map with ordered dithering.
    Returns (palette list of 5-bit tuples, index image with 1..ncol, 0 outside mask)."""
    c5 = np.asarray(rgb, float)[..., :3] * 31 / 255
    pts = c5[mask]
    rng = np.random.default_rng(seed)
    if len(pts) > 12000:
        pts = pts[rng.choice(len(pts), 12000, replace=False)]
    pal = np.clip(np.round(kmeans(pts, ncol, 16, rng)), 0, 31)
    # sort dark to light so the palette reads sensibly
    pal = pal[np.argsort(pal.sum(1))]
    h, w = mask.shape
    dith = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w][..., None] * 0.9
    d = ((c5 + dith)[:, :, None, :] - pal[None, None]) ** 2
    idx = d.sum(-1).argmin(-1) + 1
    idx[~mask] = 0
    return [tuple(int(v) for v in p) for p in pal], idx


def build_bg(idx, max_tiles, first_blank):
    """Deduplicate 8x8 tiles of a 240x160 index image; return (tiles, 32x20 map)."""
    tiles, lookup = [], {}
    if first_blank:
        blank = np.zeros((8, 8), int)
        tiles.append(blank)
        lookup[tile_bytes(blank)] = 0
    tmap = np.zeros((20, 32), int)
    for ty in range(20):
        for tx in range(30):
            t = idx[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8]
            key = tile_bytes(t)
            if key not in lookup:
                lookup[key] = len(tiles)
                tiles.append(t)
            tmap[ty, tx] = lookup[key]
    assert len(tiles) <= max_tiles, f'{len(tiles)} tiles, the title screen has room for {max_tiles}'
    return tiles, tmap


def map_bytes(tmap):
    out = bytearray()
    for v in tmap.flatten():
        out += bytes([int(v) & 0xFF, int(v) >> 8])
    return bytes(out)


# ---------------------------------------------------------------- lettering
def text_coverage(text, font_path, cap_px, width_px=None, embolden=0, ss=8):
    """Anti-aliased coverage (0..1) of text whose ink is cap_px tall (and width_px wide)."""
    f = ImageFont.truetype(font_path, int(cap_px * ss * 1.42))
    l, t, r, b = f.getbbox(text)
    im = Image.new('L', (r - l + 8 * ss, b - t + 8 * ss), 0)
    ImageDraw.Draw(im).text((4 * ss - l, 4 * ss - t), text, font=f, fill=255)
    if embolden:
        im = im.filter(ImageFilter.MaxFilter(embolden))
    a = np.asarray(im) > 127
    ys, xs = np.where(a)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    tw = width_px or int(round(a.shape[1] * cap_px / a.shape[0]))
    small = Image.fromarray((a * 255).astype(np.uint8)).resize((tw, cap_px), Image.BOX)
    return np.asarray(small) / 255.0


def dilate(m):
    out = m.copy()
    out[1:] |= m[:-1]; out[:-1] |= m[1:]
    out[:, 1:] |= m[:, :-1]; out[:, :-1] |= m[:, 1:]
    return out


def dilate8(m):
    out = dilate(m)
    out[1:, 1:] |= m[:-1, :-1]; out[1:, :-1] |= m[:-1, 1:]
    out[:-1, 1:] |= m[1:, :-1]; out[:-1, :-1] |= m[1:, 1:]
    return out


def shade_rows(mask, top, ramp):
    """Index image filling mask with ramp entries chosen by row (top row of the letters = top)."""
    out = np.zeros(mask.shape, int)
    h = mask.shape[0]
    for y in range(h):
        k = min(len(ramp) - 1, max(0, y - top))
        out[y][mask[y]] = ramp[k]
    return out


# 4x5 capitals for the credit line ('#' = ink)
FONT5 = {
    'A': ['.##.', '#..#', '####', '#..#', '#..#'], 'B': ['###.', '#..#', '###.', '#..#', '###.'],
    'C': ['.###', '#...', '#...', '#...', '.###'], 'D': ['###.', '#..#', '#..#', '#..#', '###.'],
    'E': ['####', '#...', '###.', '#...', '####'], 'F': ['####', '#...', '###.', '#...', '#...'],
    'G': ['.###', '#...', '#.##', '#..#', '.###'], 'H': ['#..#', '#..#', '####', '#..#', '#..#'],
    'I': ['###', '.#.', '.#.', '.#.', '###'], 'J': ['..##', '...#', '...#', '#..#', '.##.'],
    'K': ['#..#', '#.#.', '##..', '#.#.', '#..#'], 'L': ['#...', '#...', '#...', '#...', '####'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'], 'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'O': ['.##.', '#..#', '#..#', '#..#', '.##.'], 'P': ['###.', '#..#', '###.', '#...', '#...'],
    'R': ['###.', '#..#', '###.', '#.#.', '#..#'], 'S': ['.###', '#...', '.##.', '...#', '###.'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'], 'U': ['#..#', '#..#', '#..#', '#..#', '.##.'],
    'V': ['#...#', '#...#', '.#.#.', '.#.#.', '..#..'], 'W': ['#...#', '#...#', '#.#.#', '##.##', '#...#'],
    'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'], '.': ['.', '.', '.', '.', '#'], ' ': ['..', '..', '..', '..', '..'],
}


def pixel_text(text):
    cols = []
    for ch in text:
        g = FONT5[ch]
        cols.append(np.array([[c == '#' for c in row] for row in g]))
        cols.append(np.zeros((5, 1), bool))
    return np.hstack(cols[:-1])


def letter():
    """Return (logo 256x64, sub 256x40) index images and the four sprite palettes (8-bit RGB)."""
    # ------------------------------------------------ palettes
    ink = (14, 10, 14)
    steel = [(255, 255, 250), (236, 238, 236), (214, 218, 222), (188, 194, 202), (150, 158, 170),
             (112, 120, 134), (170, 176, 186), (204, 208, 214)]
    blood = [(255, 120, 96), (220, 48, 40), (176, 22, 24), (120, 10, 16)]
    pal_press = [(0, 0, 0), ink] + [(0, 0, 0)] * 6 + [(255, 248, 236)] + [(0, 0, 0)] * 7
    pal_credit = [(0, 0, 0), (196, 186, 172), (20, 14, 16)] + [(0, 0, 0)] * 13
    pal_logo = [(0, 0, 0), ink] + steel + blood + [(0, 0, 0)] * 2
    pal_sub = [(0, 0, 0), ink, (255, 150, 120), (226, 52, 44), (184, 24, 26), (132, 12, 18), (86, 6, 12)] + [(0, 0, 0)] * 9
    S0, R0 = 2, 10   # first steel and blood indices in pal_logo

    # ------------------------------------------------ logo: ATTACK on TITAN, 232x32
    cap, small = 25, 12
    gap = 4
    w1, w2, w3 = 159, 28, 120                      # natural widths at this cap height
    k = (229 - 2 * gap) / (w1 + w2 + w3)
    a = text_coverage('ATTACK', SERIF, cap, int(round(w1 * k))) >= 0.45
    o = text_coverage('ON', SERIF, small, int(round(w2 * k * 1.05))) >= 0.45
    t = text_coverage('TITAN', SERIF, cap, int(round(w3 * k))) >= 0.45
    top = 3
    big = np.zeros((32, 232), bool)
    on = np.zeros((32, 232), bool)
    x = 1
    big[top:top + cap, x:x + a.shape[1]] = a
    x += a.shape[1] + gap
    oy = top + (cap - small) // 2 + 1
    on[oy:oy + small, x:x + o.shape[1]] = o
    x += o.shape[1] + gap
    big[top:top + cap, x:x + t.shape[1]] = t
    x += t.shape[1]
    assert x <= 231, x
    # chrome: bright crown, a dark horizon just under the middle, light reflection below
    ramp = [S0 + i for i in (0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 4, 4, 3, 3, 6, 6, 7, 7, 7, 3)]
    logo_main = shade_rows(big, top, ramp)
    ramp_on = [R0 + i for i in (0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)]
    logo_main += shade_rows(on, oy, ramp_on)
    letters = big | on
    outline = dilate8(letters) & ~letters
    logo_main[outline] = 1
    footprint = dilate8(letters)
    logo = np.zeros((64, 256), int)
    logo[0:32, 0:232] = logo_main
    logo[32:64, 0:232][footprint] = 1               # the shadow, drawn half-transparent 5px lower

    # ------------------------------------------------ subtitle: 進撃の巨人, 208x32
    kc = text_coverage('進撃の巨人', KANJI, 24, embolden=5) >= 0.42
    banner = np.zeros((32, 208), int)
    kx = (208 - kc.shape[1]) // 2
    ky = 4
    km = np.zeros((32, 208), bool)
    km[ky:ky + kc.shape[0], kx:kx + kc.shape[1]] = kc
    banner = shade_rows(km, ky, [2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6])
    banner[dilate8(km) & ~km] = 1
    # blade strokes either side of the title
    cy = ky + 12
    for x0, x1 in ((kx - 34, kx - 8), (kx + kc.shape[1] + 8, kx + kc.shape[1] + 34)):
        for xx in range(x0, x1):
            f = (xx - x0) / (x1 - x0)
            taper = f if x0 < kx else 1 - f
            if taper > 0.08:
                banner[cy, xx] = 3
                banner[cy - 1, xx] = 1
                banner[cy + 1, xx] = 1
    # ------------------------------------------------ Press START, 96x16
    pc = text_coverage('Press START', SERIF, 11, 86) >= 0.45
    press = np.zeros((16, 96), int)
    pm = np.zeros((16, 96), bool)
    pm[2:13, 5:91] = pc
    press[pm] = 8
    press[dilate8(pm) & ~pm] = 1
    # ------------------------------------------------ credit line, 232x8
    ct = pixel_text('BASED ON ATTACK ON TITAN BY HAJIME ISAYAMA')
    credit = np.zeros((8, 232), int)
    cx = (232 - ct.shape[1]) // 2
    cm = np.zeros((8, 232), bool)
    cm[1:6, cx:cx + ct.shape[1]] = ct
    sh = np.zeros_like(cm)
    sh[2:7, cx + 1:cx + 1 + ct.shape[1]] = ct
    credit[sh & ~cm] = 2
    credit[cm] = 1

    sub = np.zeros((40, 256), int)
    sub[0:8, 0:232] = credit
    sub[8:40, 0:208] = banner
    sub[8:24, 208:256] = press[:, 0:48]
    sub[24:40, 208:256] = press[:, 48:96]
    return logo, sub, [pal_press, pal_credit, pal_logo, pal_sub]


def glow_ramp():
    """Sixteen colours for "Press START": the game ping-pongs between entry 0 and entry 15."""
    a, b = np.array([255, 248, 236]), np.array([150, 54, 46])
    return [tuple(int(round(v)) for v in a + (b - a) * (i / 15) ** 1.4) for i in range(16)] + [(150, 54, 46)]


# ---------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bg_im, fg_im = paint_title.paint()
    bg_im.save(OUT / 'title_bg.png')
    fg_im.save(OUT / 'title_fg.png')

    # BG1: sky and Wall, colours 1..15 (0 would show the backdrop, which is white in the intro)
    bg = np.asarray(bg_im.convert('RGB'))
    pal1, idx1 = quantize(bg, np.ones(bg.shape[:2], bool), 15, 845)
    tiles1, map1 = build_bg(idx1, 640, first_blank=False)
    data1 = b''.join(tile_bytes(t) for t in tiles1)
    a_part, b_part = data1[:384 * 32], data1[384 * 32:] or bytes(32)
    (OUT / 'bg1_tiles_a.dmp').write_bytes(lz77_compress(a_part))
    (OUT / 'bg1_tiles_b.dmp').write_bytes(lz77_compress(b_part))
    (OUT / 'bg1_map.dmp').write_bytes(lz77_compress(map_bytes(map1)))
    (OUT / 'bg1_pal.dmp').write_bytes(pal_bytes([(0, 0, 0)] + pal1))

    # BG0: the Colossal's head, colour 0 see-through
    fg = np.asarray(fg_im)
    pal0, idx0 = quantize(fg, fg[..., 3] >= 128, 15, 846)
    tiles0, map0 = build_bg(idx0, 192, first_blank=True)
    (OUT / 'bg0_tiles.dmp').write_bytes(lz77_compress(b''.join(tile_bytes(t) for t in tiles0)))
    (OUT / 'bg0_map.dmp').write_bytes(lz77_compress(map_bytes(map0)))
    (OUT / 'bg0_pal.dmp').write_bytes(pal_bytes([(0, 0, 0)] + pal0))

    # sprites
    logo, sub, objpals = letter()
    (OUT / 'logo.dmp').write_bytes(lz77_compress(sheet_bytes(logo)))
    (OUT / 'sub.dmp').write_bytes(lz77_compress(sheet_bytes(sub)))
    objpal5 = [[to5(c) for c in p] for p in objpals]
    (OUT / 'objpal.dmp').write_bytes(b''.join(pal_bytes(p) for p in objpal5))
    glow5 = [to5(c) for c in glow_ramp()]
    (OUT / 'glow.dmp').write_bytes(pal_bytes(glow5))

    # preview, as the GBA draws the idle title screen (Press START at its brightest)
    def c8(c5):
        return np.array([round(v * 255 / 31) for v in c5])
    P1 = [c8((0, 0, 0))] + [c8(c) for c in pal1]
    P0 = [c8((0, 0, 0))] + [c8(c) for c in pal0]
    scr = np.zeros((160, 240, 3))
    for y in range(160):
        for x in range(240):
            scr[y, x] = P1[idx1[y, x]]
            if idx0[y, x]:
                scr[y, x] = P0[idx0[y, x]]
    OP = [[c8(c) for c in p] for p in objpal5]
    OP[0][8] = c8(glow5[0])

    def put(img, pal, x0, y0, blend=False):
        h, w = img.shape
        for y in range(h):
            for x in range(w):
                v = img[y, x]
                X, Y = x0 + x, y0 + y
                if v and 0 <= X < 240 and 0 <= Y < 160:
                    scr[Y, X] = (scr[Y, X] + OP[pal][v]) / 2 if blend else OP[pal][v]
    put(logo[32:64, 0:232], 2, 4, 53, blend=True)
    put(logo[0:32, 0:232], 2, 4, 48)
    put(sub[8:40, 0:208], 3, 16, 85)
    put(sub[8:24, 208:256], 0, 72, 124)
    put(sub[24:40, 208:256], 0, 120, 124)
    put(sub[0:8, 0:232], 1, 4, 148)
    Image.fromarray(scr.astype(np.uint8)).save(OUT / 'title_preview.png')
    print(f'BG1 {len(tiles1)} tiles, BG0 {len(tiles0)} tiles; wrote {OUT}')


if __name__ == '__main__':
    main()
