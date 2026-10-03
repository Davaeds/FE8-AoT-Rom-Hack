#!/usr/bin/env python3
"""Build the menu backdrops that replace the Sacred Stones rune pictures.

    python3 tools/menubgconv.py

1. Paints AoT/Graphics/Menu/menu_bg.png (tools/art/paint_menu_bg.py) and writes
menu_bg.dmp (640 tiles, LZ77) and menu_bg_pal.dmp (two palettes) next to it,
plus menu_bg_preview.png as the chapter title card colours it.

2. Paints AoT/Graphics/Menu/main_bg.png (tools/art/paint_walls_map.py), the
full-screen picture behind the title menu and the save files, and writes
main_bg.dmp (600 tiles, LZ77), main_bg_tsa.dmp and main_bg_pal.dmp (eight
palettes) in the same layout as a CG (see tools/cgconv.py), plus
main_bg_preview.png.

FE8U draws this picture (Img_CommGameBgScreen) behind the main menu, the save
menus, the preparation screens and the chapter title card. The game lays the
tiles out itself, in order, 32 to a row (so the picture is 256x160 and wraps
left to right), and uses the second palette for rows 7-12 on the chapter title
card. Both palettes share one set of colour slots, the second a darker shade of
the first, so the picture reads correctly whichever one a screen picks.
Needs numpy and Pillow (not part of the normal build).
"""
import pathlib
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools' / 'art'))
from cgconv import lz77_compress  # noqa: E402
import cgconv  # noqa: E402
from titleconv import quantize, tile_bytes, pal_bytes  # noqa: E402
import paint_menu_bg  # noqa: E402
import paint_walls_map  # noqa: E402

OUT = ROOT / 'AoT' / 'Graphics' / 'Menu'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im = paint_menu_bg.paint()
    im.save(OUT / 'menu_bg.png')
    rgb = np.asarray(im.convert('RGB'))
    pal, idx = quantize(rgb, np.ones(rgb.shape[:2], bool), 15, 847)
    dark = [tuple(int(round(v)) for v in (r * 0.42, g * 0.40, b * 0.46)) for r, g, b in pal]
    data = b''.join(tile_bytes(idx[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8]) for ty in range(20) for tx in range(32))
    assert len(data) == 0x5000
    (OUT / 'menu_bg.dmp').write_bytes(lz77_compress(data))
    (OUT / 'menu_bg_pal.dmp').write_bytes(pal_bytes([(0, 0, 0)] + pal) + pal_bytes([(0, 0, 0)] + dark))
    prev = np.zeros((160, 256, 3), np.uint8)
    for y in range(160):
        p = dark if 56 <= y < 104 else pal
        for x in range(256):
            prev[y, x] = [round(c * 255 / 31) for c in p[idx[y, x] - 1]]
    Image.fromarray(prev).save(OUT / 'menu_bg_preview.png')

    # the title menu backdrop: a CG-style picture (six palettes, TSA from the bottom row up)
    png = OUT / 'main_bg.png'
    paint_walls_map.paint().save(png)
    cgconv.write(png)
    stem = OUT / 'main_bg'
    chunks = b''.join(lz77_decompress(pathlib.Path(f'{stem}_chunk{k}.dmp').read_bytes()) for k in range(cgconv.CHUNKS))
    for k in range(cgconv.CHUNKS):
        pathlib.Path(f'{stem}_chunk{k}.dmp').unlink()
    (OUT / 'main_bg.dmp').write_bytes(lz77_compress(chunks[:600 * 32]))
    print(f'wrote {OUT}')


def lz77_decompress(data):
    assert data[0] == 0x10
    size = data[1] | (data[2] << 8) | (data[3] << 16)
    out = bytearray()
    pos = 4
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


if __name__ == '__main__':
    main()
