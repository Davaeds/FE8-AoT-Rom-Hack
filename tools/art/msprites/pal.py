"""AoT map sprite palettes.

FE8 keeps five 16-colour map sprite palettes (one per faction, plus grey for
units that have moved) at 0x59EE20. Every map sprite indexes the same slots in
all of them, so a slot means the same thing in every faction and only the
faction-specific ramps change:

  0 transparent        6 brown mid           12 accent dark
  1 outline            7 brown dark          13 ground shadow
  2 skin light         8 white               14 red
  3 skin mid           9 white shade         15 blond
  4 skin shade        10 steel
  5 brown light       11 accent light

Accent is the Survey Corps cloak green for soldiers (blue faction), raw muscle
red for Titans (red faction) and plain cloth for civilians (green faction).
"""

LEGEND = {
    '.': 0, 'o': 1, 'S': 2, 's': 3, 'k': 4, 'B': 5, 'b': 6, 'd': 7,
    'W': 8, 'w': 9, 'g': 10, 'G': 11, 'n': 12, '_': 13, 'R': 14, 'Y': 15,
}

BASE = [
    (0, 0, 0),
    (44, 30, 46),     # outline: dark purple-brown, never pure black
    (252, 222, 184),  # skin light
    (230, 166, 128),  # skin mid
    (170, 100, 96),   # skin shade, shifted toward red-violet
    (204, 152, 98),   # brown light
    (150, 98, 66),    # brown mid
    (94, 58, 54),     # brown dark
    (250, 248, 232),  # white
    (172, 178, 202),  # white shade, cool
    (114, 124, 152),  # steel
    (104, 148, 80),   # accent light
    (54, 90, 66),     # accent dark
    (96, 106, 88),    # ground shadow
    (216, 46, 40),    # red
    (248, 214, 108),  # blond
]


def faction(accent_light, accent_dark, skin=None):
    p = list(BASE)
    p[11], p[12] = accent_light, accent_dark
    if skin:
        p[2], p[3], p[4] = skin
    return p


BLUE = faction((104, 148, 80), (54, 90, 66))                      # soldiers: Survey Corps green
RED = faction((210, 92, 84), (138, 40, 44),                     # Titans: exposed muscle
              skin=((246, 206, 172), (214, 156, 120), (156, 98, 82)))
GREEN = faction((120, 132, 168), (72, 82, 116))                 # civilians: worn blue cloth
GREY = [(0, 0, 0)] + [((r * 30 + g * 59 + b * 11) // 100,) * 3 for r, g, b in BASE[1:]]
PURPLE = BLUE

PALETTES = [BLUE, RED, GREEN, GREY, PURPLE]


def gba_bytes(pals=PALETTES):
    out = bytearray()
    for p in pals:
        for r, g, b in p:
            v = (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)
            out += bytes((v & 255, v >> 8))
    return bytes(out)
