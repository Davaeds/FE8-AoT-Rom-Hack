#!/usr/bin/env python3
"""Tile several PPM screenshots into one PNG contact sheet (stdlib only)."""
import sys
from ppm2png import read_ppm, write_png

cols = 3
out = sys.argv[1]
imgs = [read_ppm(p) for p in sys.argv[2:]]
w, h = imgs[0][0], imgs[0][1]
gap = 4
rows = (len(imgs) + cols - 1) // cols
W, H = cols * w + (cols - 1) * gap, rows * h + (rows - 1) * gap
canvas = bytearray(b"\x40\x40\x40" * W * H)
for i, (_, _, rgb) in enumerate(imgs):
    ox, oy = (i % cols) * (w + gap), (i // cols) * (h + gap)
    for y in range(h):
        start = ((oy + y) * W + ox) * 3
        canvas[start:start + w * 3] = rgb[y * w * 3:(y + 1) * w * 3]
write_png(out, W, H, bytes(canvas), 1)
print(out)
