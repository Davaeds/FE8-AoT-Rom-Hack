#!/usr/bin/env python3
"""Convert binary PPM (P6) screenshots to PNG using only the standard library."""
import struct
import sys
import zlib


def read_ppm(path):
    with open(path, "rb") as f:
        data = f.read()
    parts = data.split(maxsplit=4)
    if parts[0] != b"P6" or parts[3] != b"255":
        raise ValueError(f"{path}: not an 8-bit binary PPM")
    return int(parts[1]), int(parts[2]), parts[4]


def write_png(path, width, height, rgb, scale=1):
    rows = []
    stride = width * 3
    for y in range(height):
        row = rgb[y * stride:(y + 1) * stride]
        if scale > 1:
            row = b"".join(row[x * 3:x * 3 + 3] * scale for x in range(width))
        rows.extend([b"\x00" + row] * scale)
    raw = b"".join(rows)

    def chunk(tag, payload):
        body = tag + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))

    ihdr = struct.pack(">IIBBBBB", width * scale, height * scale, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    scale = 2
    for src in sys.argv[1:]:
        w, h, rgb = read_ppm(src)
        dst = src[:-4] + ".png" if src.endswith(".ppm") else src + ".png"
        write_png(dst, w, h, rgb, scale)
        print(dst)
