#!/usr/bin/env python3
"""Take the Sacred Stones dragons off the menu buttons (build step).

    python3 tools/menuplates.py CLEAN_ROM OUTDIR

The button plates of the title menu, the difficulty select and the save files
carry dragon decals. Their sprite sheets also hold the vanilla button labels,
so instead of committing edited copies this reads the sheets from the clean ROM
at build time, repaints the inside of every plate as a clean dithered version of
its own colour ramp, stamps the Survey Corps wings where the dragons were, and
writes the sheets to OUTDIR (AoT/Graphics/MenuPlates.event includes them from
build/gen).

Pure Python, so it runs in the normal build.
"""
import pathlib
import sys

# Sheet address -> plates.
#   rows, x: the inside of the plate (x None: found per row inside the
#            ornamented ends of the save file plate)
#   wings:   x centres of the Survey Corps emblems
#   keep:    rectangles (y0, y1, x0, x1) left as they are: the clasps on the frames
SHEETS = {
    0x8A26A74: [  # title menu
        dict(rows=(7, 24), x=(7, 71), wings=[20]),          # half a button, drawn twice (mirrored)
        dict(rows=(7, 24), x=(74, 157), wings=[96, 136]),
        dict(rows=(90, 104), x=(178, 253)),                 # play time box
    ],
    0x8A28A0C: [  # difficulty select
        dict(rows=(5, 26), x=(2, 125), wings=[20, 107], keep=[(5, 5, 52, 75), (26, 26, 52, 75)]),
    ],
    0x8A09E4C: [  # save file slots
        dict(rows=(5, 26), x=None, wings=[30, 168], keep=[(5, 7, 82, 110), (24, 26, 82, 110)]),
    ],
    0x8A2D32C: [  # save files: the same slot plate, the header plate and the play time box
        dict(rows=(5, 26), x=None, wings=[30, 168], keep=[(5, 7, 82, 110), (24, 26, 82, 110)]),
        dict(rows=(37, 58), x=(2, 125), wings=[20, 107], keep=[(37, 37, 52, 75), (58, 58, 52, 75)]),
        dict(rows=(42, 56), x=(131, 206)),                  # play time box
    ],
}
RAMP = {4, 5, 6, 7, 8}
DECAL = {2, 3, 10}
FRAME = {1, 11, 12, 13, 14, 15}
WING_COLOUR = 10

# Survey Corps wings, 23x16, drawn in the decal colour; '.' lets the plate show
WINGS = [
    'WW...................WW',
    'WWWWW.............WWWWW',
    '.WWWWWW.........WWWWWW.',
    '...WWWWW.......WWWWW...',
    '.WW...WWWW...WWWW...WW.',
    '.WWWWW..WWW.WWW..WWWWW.',
    '..WWWWWW..W.W..WWWWWW..',
    '.....WWWWWW.WWWWWW.....',
    '..WWW....WW.WW....WWW..',
    '...WWWWWW.....WWWWWW...',
    '...WWWWWWWW.WWWWWWWW...',
    '........WWW.WWW........',
    '....WWWW.......WWWW....',
    '.....WWWWWW.WWWWWW.....',
    '.......WWWW.WWWW.......',
    '.........WW.WW.........',
]

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
SMOOTH = 5  # columns either side averaged into the ramp level


def lz77_decompress(data, pos):
    assert data[pos] == 0x10, f'no LZ77 data at {pos:#x}'
    size = data[pos + 1] | (data[pos + 2] << 8) | (data[pos + 3] << 16)
    pos += 4
    out = bytearray()
    while len(out) < size:
        flags = data[pos]
        pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                ln = (data[pos] >> 4) + 3
                disp = (((data[pos] & 0xF) << 8) | data[pos + 1]) + 1
                pos += 2
                for _ in range(ln):
                    out.append(out[-disp])
            else:
                out.append(data[pos])
                pos += 1
    return bytes(out)


def lz77_compress(src):
    """GBA LZ77 (type 0x10) without displacement 1, so it can unpack straight into VRAM."""
    n = len(src)
    out = bytearray([0x10, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    heads = {}
    pos = 0
    while pos < n:
        flag_at = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if pos >= n:
                break
            best_len, best_disp = 0, 0
            for cand in reversed(heads.get(src[pos:pos + 3], [])):
                disp = pos - cand
                if disp > 0x1000:
                    break
                if disp < 2:
                    continue
                ln = 0
                while ln < 18 and pos + ln < n and src[pos + ln] == src[cand + ln]:
                    ln += 1
                if ln > best_len:
                    best_len, best_disp = ln, disp
                    if ln == 18:
                        break
            step = best_len if best_len >= 3 else 1
            if best_len >= 3:
                flags |= 0x80 >> bit
                d = best_disp - 1
                out += bytes([((best_len - 3) << 4) | (d >> 8), d & 0xFF])
            else:
                out.append(src[pos])
            for p in range(pos, pos + step):
                heads.setdefault(src[p:p + 3], []).append(p)
            pos += step
        out[flag_at] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def decode(raw):
    """4bpp sprite sheet, 32 tiles to a row (2D mapping) -> rows of pixel indices."""
    rows = len(raw) // (32 * 32) * 8
    px = [[0] * 256 for _ in range(rows)]
    for t in range(len(raw) // 32):
        ty, tx = divmod(t, 32)
        for i in range(32):
            b = raw[t * 32 + i]
            y, x = ty * 8 + i // 4, tx * 8 + (i % 4) * 2
            px[y][x] = b & 0xF
            px[y][x + 1] = b >> 4
    return px


def encode(px):
    out = bytearray()
    for ty in range(len(px) // 8):
        for tx in range(32):
            for y in range(ty * 8, ty * 8 + 8):
                for x in range(tx * 8, tx * 8 + 8, 2):
                    out.append(px[y][x] | (px[y][x + 1] << 4))
    return bytes(out)


def inner_span(row):
    """Inside of the save file plate on one row: between the ornamented ends and their dark rims."""
    left = max(x for x in range(0, 14) if row[x] in FRAME) + 1
    if row[left] == 10:
        left += 1
    right = min(x for x in range(185, 200) if row[x] in FRAME) - 1
    if row[right] == 10:
        right -= 1
    # the right ornament also has a light edge pixel inside its rim
    if row[right] == 8:
        right -= 1
    return left, right


def regrade(px, plate):
    """Repaint a plate's inside as a smooth, dithered version of its own ramp."""
    y0, y1 = plate['rows']
    keep = plate.get('keep', [])
    spans = {}
    for y in range(y0, y1 + 1):
        spans[y] = inner_span(px[y]) if plate['x'] is None else plate['x']

    def kept(y, x):
        return any(a <= y <= b and c <= x <= d for a, b, c, d in keep)

    def near_decal(y, x):
        return any(px[j][i] in DECAL for j in (y - 1, y, y + 1) for i in (x - 1, x, x + 1))

    # ramp level of each column, from the pixels the decals do not shade
    total, count = {}, {}
    for y, (a, b) in spans.items():
        for x in range(a, b + 1):
            if px[y][x] in RAMP and not kept(y, x) and not near_decal(y, x):
                total[x] = total.get(x, 0) + px[y][x]
                count[x] = count.get(x, 0) + 1
    used = [v for y, (a, b) in spans.items() for v in px[y][a:b + 1] if v in RAMP]
    lo, hi = min(used), max(used)
    level = {}
    xs = sorted({x for a, b in spans.values() for x in range(a, b + 1)})
    for x in xs:
        s = sum(total.get(k, 0) for k in range(x - SMOOTH, x + SMOOTH + 1))
        n = sum(count.get(k, 0) for k in range(x - SMOOTH, x + SMOOTH + 1))
        level[x] = s / n if n else None
    for x in xs:  # columns with no clean pixels nearby take the closest level
        if level[x] is None:
            level[x] = level[min((k for k in xs if level[k] is not None), key=lambda k: abs(k - x))]
    for y, (a, b) in spans.items():
        for x in range(a, b + 1):
            if (px[y][x] in RAMP or px[y][x] in DECAL) and not kept(y, x):
                t = (BAYER[y % 4][x % 4] + 0.5) / 16
                px[y][x] = min(hi, max(lo, int(level[x] + t)))


def stamp_wings(px, cy, cx):
    h, w = len(WINGS), len(WINGS[0])
    for j, line in enumerate(WINGS):
        for i, c in enumerate(line):
            if c == 'W':
                px[cy - h // 2 + j][cx - w // 2 + i] = WING_COLOUR


def main():
    rom = pathlib.Path(sys.argv[1]).read_bytes()
    out = pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for addr, plates in SHEETS.items():
        raw = lz77_decompress(rom, addr - 0x8000000)
        px = decode(raw)
        for plate in plates:
            regrade(px, plate)
            y0, y1 = plate['rows']
            for cx in plate.get('wings', []):
                stamp_wings(px, (y0 + y1 + 1) // 2, cx)
        data = encode(px)
        assert len(data) == len(raw)
        packed = lz77_compress(data)
        assert lz77_decompress(packed, 0) == data
        (out / f'plates_{addr:07X}.dmp').write_bytes(packed)


if __name__ == '__main__':
    main()
