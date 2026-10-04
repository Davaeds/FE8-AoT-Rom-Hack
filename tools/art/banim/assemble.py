"""Assemble FE8 battle animations from indexed frames.

    python3 tools/art/banim/assemble.py

Every animation module listed in ANIMS (tools/art/banim/<name>.py) provides:
    ABBR     up to 11 characters, shown in debug tools only
    SLOT     0-based index in banim_data that this animation replaces
    PALETTE  list of up to 15 RGB tuples (index 0 is transparent)
    frames() dict name -> uint8 array (160 x 240): the right-hand combatant as
             it appears on screen, palette indices, anchored at (148, 88) like
             the game's close-range position
    MODES    12 lists of tokens: ("f", frame_name, delay) or ("c", command)

Output: AoT/Graphics/Banim/banim.bin, placed at the fixed ROM address BASE
(scripts are LZ77-compressed and hold absolute sheet pointers, so the address
must be known here), and AoT/Graphics/Banim/Banim.event, which installs the
table entries.

Format notes (from the fireemblem8u decomp, anime.h and banim-ekrmain.c):
  script frame  = 0x86000000 | id << 16 | delay, sheet pointer, OAM offset
  command       = 0x85000000 | id;   mode end = 0x80000000
  OAM entry     = u32 attr0 | attr1 << 16, u16 oam2 (tile), s16 x, s16 y, u16 pad;
                  a frame's list ends with a header of 1
  sheet         = 32 x 8 tiles, 4bpp, tiles addressed as row * 32 + column
  modes         = 24 words: byte offset of each of the 12 modes in the script
  palette       = 4 x 16 colours (one per faction), LZ77-compressed
"""
import importlib
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lz77  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "AoT", "Graphics", "Banim")
BASE = 0x1800000          # ROM offset of banim.bin
ANCHOR = (148, 88)
ANIMS = ["cadet", "dummy", "pure_titan", "titan_smiling"]

# (shape, size) for each object size in tiles, largest first
OBJ = {(4, 4): (0, 2), (8, 4): (1, 3), (4, 8): (2, 3), (4, 2): (1, 2), (2, 4): (2, 2), (2, 2): (0, 1),
       (4, 1): (1, 1), (1, 4): (2, 1), (2, 1): (1, 0), (1, 2): (2, 0), (1, 1): (0, 0)}
ORDER = [(4, 4), (4, 2), (2, 4), (2, 2), (4, 1), (1, 4), (2, 1), (1, 2), (1, 1)]


def gba_color(c):
    r, g, b = (v >> 3 for v in c)
    return r | g << 5 | b << 10


def objects(frame):
    """Cover the opaque 8x8 cells of a frame with OBJ rectangles.
    Returns [(tx, ty, w, h, pixels)] with tx/ty in tiles from the canvas origin."""
    H, W = frame.shape
    ys, xs = np.nonzero(frame)
    if len(xs) == 0:
        return []
    # align the tile grid to the anchor so frames share tiles when they line up;
    # cell (cx, cy) covers canvas pixels from (cx * 8 + ox, cy * 8 + oy)
    ox, oy = ANCHOR[0] % 8, ANCHOR[1] % 8
    gx0 = (xs.min() - ox) // 8
    gx1 = (xs.max() - ox) // 8
    gy0 = (ys.min() - oy) // 8
    gy1 = (ys.max() - oy) // 8

    def cell(cx, cy):
        x, y = cx * 8 + ox, cy * 8 + oy
        out = np.zeros((8, 8), np.uint8)
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + 8, W), min(y + 8, H)
        if x1 > x0 and y1 > y0:
            out[y0 - y:y1 - y, x0 - x:x1 - x] = frame[y0:y1, x0:x1]
        return out

    cells = {}
    for cy in range(gy0, gy1 + 1):
        for cx in range(gx0, gx1 + 1):
            c = cell(cx, cy)
            if c.any():
                cells[(cx, cy)] = c
    covered = set()
    objs = []
    for cy in range(gy0, gy1 + 1):
        for cx in range(gx0, gx1 + 1):
            if (cx, cy) not in cells or (cx, cy) in covered:
                continue
            for w, h in ORDER:
                rect = [(cx + i, cy + j) for j in range(h) for i in range(w)]
                if any(r in covered for r in rect):
                    continue
                filled = sum(r in cells for r in rect)
                if filled * 4 >= len(rect) * 3 or (w, h) == (1, 1):
                    break
            pix = np.zeros((h * 8, w * 8), np.uint8)
            for j in range(h):
                for i in range(w):
                    c = cells.get((cx + i, cy + j))
                    if c is not None:
                        pix[j * 8:j * 8 + 8, i * 8:i * 8 + 8] = c
                    covered.add((cx + i, cy + j))
            objs.append((cx * 8 + ox, cy * 8 + oy, w, h, pix))
    return objs


class Sheets:
    """Packs tile blocks into 32x8-tile sheets. A frame's blocks share one sheet."""

    def __init__(self):
        self.sheets = []

    def new(self):
        self.sheets.append({"tiles": np.zeros((64, 256), np.uint8), "used": np.zeros((8, 32), bool), "blocks": {}})
        return len(self.sheets) - 1

    def _place(self, sh, w, h):
        used = sh["used"]
        for y in range(0, 9 - h):
            for x in range(0, 33 - w):
                if not used[y:y + h, x:x + w].any():
                    return x, y
        return None

    def add_frame(self, objs):
        """Returns (sheet index, [tile index per obj])."""
        order = sorted(range(len(objs)), key=lambda i: -objs[i][2] * objs[i][3])
        for attempt in range(2):
            if not self.sheets or attempt == 1:
                self.new()
            sh = self.sheets[-1]
            snapshot = (sh["used"].copy(), sh["tiles"].copy(), dict(sh["blocks"]))
            tiles = [None] * len(objs)
            ok = True
            for i in order:
                _, _, w, h, pix = objs[i]
                key = (w, h, pix.tobytes())
                if key in sh["blocks"]:
                    tiles[i] = sh["blocks"][key]
                    continue
                pos = self._place(sh, w, h)
                if pos is None:
                    ok = False
                    break
                x, y = pos
                sh["used"][y:y + h, x:x + w] = True
                sh["tiles"][y * 8:(y + h) * 8, x * 8:(x + w) * 8] = pix
                sh["blocks"][key] = y * 32 + x
                tiles[i] = y * 32 + x
            if ok:
                return len(self.sheets) - 1, tiles
            sh["used"], sh["tiles"], sh["blocks"] = snapshot
        raise ValueError("frame does not fit in one sheet")


def sheet_bytes(tiles):
    out = bytearray()
    for ty in range(8):
        for tx in range(32):
            t = tiles[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8]
            for row in t:
                for k in range(0, 8, 2):
                    out.append(int(row[k]) | int(row[k + 1]) << 4)
    return bytes(out)


def oam_bytes(objs, tiles, left):
    out = bytearray()
    for (x, y, w, h, _), t in zip(objs, tiles):
        shape, size = OBJ[(w, h)]
        ox, oy = x - ANCHOR[0], y - ANCHOR[1]
        hflip = 0
        if left:
            ox = -ox - w * 8
            hflip = 1
        attr0 = shape << 14
        attr1 = size << 14 | hflip << 12
        out += struct.pack("<IHhhH", attr0 | attr1 << 16, t, ox, oy, 0)
    out += struct.pack("<IHhhH", 1, 0, 0, 0, 0)
    return bytes(out)


def build(mod, base):
    frames = mod.frames()
    sheets = Sheets()
    frame_info = {}
    oam_r, oam_l = bytearray(), bytearray()
    names = []
    for m in mod.MODES:
        for tok in m:
            if tok[0] == "f" and tok[1] not in names:
                names.append(tok[1])
    for name in names:
        objs = objects(frames[name])
        s, tiles = sheets.add_frame(objs)
        frame_info[name] = (s, len(oam_r), len(frame_info))
        oam_r += oam_bytes(objs, tiles, False)
        oam_l += oam_bytes(objs, tiles, True)

    blob = bytearray()

    def put(data):
        while len(blob) % 4:
            blob.append(0)
        at = base + len(blob)
        blob.extend(data)
        return at

    sheet_addr = [put(lz77.compress(sheet_bytes(sh["tiles"]))) for sh in sheets.sheets]
    script = bytearray()
    offsets = []
    for m in mod.MODES:
        offsets.append(len(script))
        for tok in m:
            if tok[0] == "f":
                s, off, fid = frame_info[tok[1]]
                script += struct.pack("<III", 0x86000000 | (fid & 0xFF) << 16 | tok[2], 0x08000000 + sheet_addr[s], off)
            else:
                script += struct.pack("<I", 0x85000000 | tok[1])
        script += struct.pack("<I", 0x80000000)
    pal = [gba_color(c) for c in mod.PALETTE]
    pal16 = [0] + pal + [0] * (15 - len(pal))
    pal_bytes = struct.pack("<16H", *pal16) * 4
    a = {
        "script": put(lz77.compress(bytes(script))),
        "oam_r": put(lz77.compress(bytes(oam_r))),
        "oam_l": put(lz77.compress(bytes(oam_l))),
        "pal": put(lz77.compress(pal_bytes)),
        "modes": put(struct.pack("<24I", *(offsets + [0] * (24 - len(offsets))))),
    }
    return bytes(blob), a, len(sheets.sheets), len(names)


def main():
    os.makedirs(OUT, exist_ok=True)
    blob = bytearray()
    ev = ["// Battle animations, generated by tools/art/banim/assemble.py. Do not edit.",
          f"// banim.bin sits at the fixed ROM offset 0x{BASE:X}: scripts hold absolute pointers.",
          "PUSH", f"ORG 0x{BASE:X}", '#incbin "banim.bin"']
    for name in ANIMS:
        mod = importlib.import_module(name)
        while len(blob) % 4:
            blob.append(0)
        data, a, nsheets, nframes = build(mod, BASE + len(blob))
        blob += data
        abbr = mod.ABBR.encode()[:11]
        ev += [f"// {name}: {nframes} frames on {nsheets} sheet(s)",
               f"ORG 0xC00008 + {mod.SLOT} * 32",
               "BYTE " + " ".join(str(b) for b in abbr + bytes(12 - len(abbr))),
               "WORD " + " ".join(f"0x{0x08000000 + a[k]:X}" for k in ("modes", "script", "oam_r", "oam_l", "pal"))]
        print(f"{name}: {nframes} frames, {nsheets} sheets")
    ev.append("POP")
    with open(os.path.join(OUT, "banim.bin"), "wb") as f:
        f.write(blob)
    with open(os.path.join(OUT, "Banim.event"), "w") as f:
        f.write("\n".join(ev) + "\n")
    print(f"banim.bin: {len(blob)} bytes at 0x{BASE:X}")


if __name__ == "__main__":
    main()
