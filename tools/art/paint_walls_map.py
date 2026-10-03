"""Paint the main menu backdrop (original art): an old Survey Corps map of the three Walls.

    python3 tools/art/paint_walls_map.py OUT.png      (240x160)

Converted by tools/menubgconv.py. Needs numpy and Pillow (not part of the normal build).
"""
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paint_menu_bg import wings_mask  # noqa: E402  (same emblem as the menu frieze)
import paint_menu_bg  # noqa: E402

S = 4
W, H = 240 * S, 160 * S
CX, CY = 120, 79
RINGS = (('MARIA', 72, 9), ('ROSE', 55, 8), ('SINA', 37, 6))   # name, radius, district radius
INK = (34, 20, 12)


def noise(h, w, scale, octaves=4, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gh, gw = max(2, int(h / scale) + 2), max(2, int(w / scale) + 2)
        g = r.random((gh, gw))
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += np.asarray(img, float) / 255 * amp
        tot += amp
        amp *= 0.5
        scale /= 2
    return out / tot


def comp(base, color, alpha):
    a = alpha[..., None]
    return base * (1 - a) + np.asarray(color, float) * a


def layer(fn):
    m = Image.new('L', (W, H), 0)
    fn(ImageDraw.Draw(m))
    return np.asarray(m, float) / 255


FONT5 = {
    'A': ['.##.', '#..#', '####', '#..#', '#..#'], 'E': ['####', '#...', '###.', '#...', '####'],
    'G': ['.###', '#...', '#.##', '#..#', '.###'], 'H': ['#..#', '#..#', '####', '#..#', '#..#'],
    'I': ['###', '.#.', '.#.', '.#.', '###'], 'L': ['#...', '#...', '#...', '#...', '####'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'], 'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'O': ['.##.', '#..#', '#..#', '#..#', '.##.'], 'R': ['###.', '#..#', '###.', '#.#.', '#..#'],
    'S': ['.###', '#...', '.##.', '...#', '###.'], 'W': ['#...#', '#...#', '#.#.#', '##.##', '#...#'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'], 'U': ['#..#', '#..#', '#..#', '#..#', '.##.'],
    'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'], 'P': ['###.', '#..#', '###.', '#...', '#...'],
    'C': ['.###', '#...', '#...', '#...', '.###'], 'D': ['###.', '#..#', '#..#', '#..#', '###.'],
    ' ': ['..', '..', '..', '..', '..'],
}


def text_px(s):
    cols = []
    for ch in s:
        g = FONT5[ch]
        cols.append(np.array([[c == '#' for c in row] for row in g]))
        cols.append(np.zeros((5, 1), bool))
    return np.hstack(cols[:-1])


def paint():
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    # ---------------------------------------------------------------- parchment
    n1 = noise(H, W, 60 * S, 4, 1)
    n2 = noise(H, W, 6 * S, 3, 2)
    img = np.zeros((H, W, 3)) + [196, 164, 112]
    img = img * (0.86 + 0.18 * n1[..., None] + 0.06 * n2[..., None])
    stains = np.clip((noise(H, W, 30 * S, 3, 3) - 0.58) * 3, 0, 1)
    img = comp(img, [168, 132, 92], stains * 0.45)
    # ---------------------------------------------------------------- land inside and outside the Walls
    r = np.hypot(xx - CX * S, yy - CY * S) / S
    forest = np.clip((noise(H, W, 9 * S, 3, 4) - 0.56) * 4, 0, 1) * (r > 40) * (r < 70)
    forest = forest * (np.abs(r - 56) > 3)
    trees = (noise(H, W, 1.6 * S, 2, 5) > 0.55) * forest
    img = comp(img, [112, 118, 76], forest * 0.35)
    img = comp(img, [78, 84, 52], trees * 0.6)
    # roads from the centre out through each district
    def roads(dr):
        for a in range(4):
            ang = a * math.pi / 2 + math.pi / 2
            x1, y1 = CX + math.cos(ang) * 82, CY + math.sin(ang) * 82
            dr.line([(CX * S, CY * S), (x1 * S, y1 * S)], fill=255, width=int(1.0 * S))
    rd = layer(roads)
    dash = ((np.floor(r / 3) % 2) == 0)
    img = comp(img, [140, 104, 72], rd * dash * 0.8 * (r > 10))
    # ---------------------------------------------------------------- the three Walls and their districts
    for name, rad, dist in RINGS:
        def wall(dr, rad=rad, dist=dist):
            w = 2.8 * S
            dr.ellipse([(CX - rad) * S, (CY - rad) * S, (CX + rad) * S, (CY + rad) * S], outline=255, width=int(w))
            for a in range(4):
                ang = a * math.pi / 2 + math.pi / 2
                dx, dy = math.cos(ang) * rad, math.sin(ang) * rad
                bx, by = CX + dx, CY + dy
                deg = math.degrees(ang)
                # districts bulge outward from the Wall as walled half-circles
                dr.arc([(bx - dist) * S, (by - dist) * S, (bx + dist) * S, (by + dist) * S], deg - 90, deg + 90, fill=255, width=int(w * 0.8))
        wm = layer(wall)
        img = comp(img, INK, wm * 0.9)
        def inner(dr, rad=rad):
            dr.ellipse([(CX - rad + 1.6) * S, (CY - rad + 1.6) * S, (CX + rad - 1.6) * S, (CY + rad - 1.6) * S], outline=255, width=int(0.6 * S))
        img = comp(img, [120, 92, 66], layer(inner) * 0.7)
        # rooftops inside each district
        def houses(dr, rad=rad, dist=dist):
            rng = np.random.default_rng(rad)
            for a in range(4):
                ang = a * math.pi / 2 + math.pi / 2
                bx, by = CX + math.cos(ang) * rad, CY + math.sin(ang) * rad
                for _ in range(10):
                    hx = bx + rng.uniform(-dist * 0.6, dist * 0.6)
                    hy = by + rng.uniform(-dist * 0.6, dist * 0.6)
                    if math.hypot(hx - CX, hy - CY) > rad + 1.5:
                        dr.rectangle([hx * S, hy * S, (hx + 1.2) * S, (hy + 1.0) * S], fill=255)
        img = comp(img, [124, 70, 52], layer(houses) * 0.9)
    # the inner capital
    def capital(dr):
        rng = np.random.default_rng(7)
        for _ in range(60):
            a = rng.uniform(0, 2 * math.pi); d = rng.uniform(0, 30)
            hx, hy = CX + math.cos(a) * d, CY + math.sin(a) * d
            dr.rectangle([hx * S, hy * S, (hx + 1.2) * S, (hy + 1.0) * S], fill=255)
    img = comp(img, [124, 70, 52], layer(capital) * 0.6)
    # ---------------------------------------------------------------- labels
    def stamp(img, s, x0, y0, col):
        t = text_px(s)
        m = np.zeros((H, W))
        halo = np.zeros((H, W))
        for y in range(t.shape[0]):
            for x in range(t.shape[1]):
                if t[y, x]:
                    m[(y0 + y) * S:(y0 + y + 1) * S, (x0 + x) * S:(x0 + x + 1) * S] = 1
                    halo[(y0 + y - 1) * S:(y0 + y + 2) * S, (x0 + x - 1) * S:(x0 + x + 2) * S] = 1
        img = comp(img, [222, 204, 164], halo * 0.8)
        return comp(img, col, m)
    for name, rad, dist in RINGS:
        s = 'WALL ' + name
        tw = text_px(s).shape[1]
        img = stamp(img, s, CX - tw // 2, CY - rad + 6, INK)
    s = 'SHIGANSHINA'
    tw = text_px(s).shape[1]
    img = stamp(img, s, CX + 12, CY + 72 + 2, INK)
    # ---------------------------------------------------------------- Survey Corps wings in the corner, inked
    paint_menu_bg.W, paint_menu_bg.H = W, H
    front, back, feathers = wings_mask(214 * S, 138 * S, 11 * S)
    img = comp(img, [236, 226, 204], front)
    img = comp(img, [64, 86, 120], back)
    def ring(dr):
        dr.ellipse([(214 - 15) * S, (138 - 15) * S, (214 + 15) * S, (138 + 15) * S], outline=255, width=int(1.2 * S))
    img = comp(img, INK, layer(ring) * 0.9)
    img = comp(img, INK, (feathers * (front + back)) * 0.8)
    # compass rose, top left
    def compass(dr):
        cx, cy, rr = 22 * S, 22 * S, 12 * S
        dr.polygon([(cx, cy - rr), (cx + 2.5 * S, cy), (cx, cy + rr), (cx - 2.5 * S, cy)], fill=255)
        dr.polygon([(cx - rr, cy), (cx, cy - 2.5 * S), (cx + rr, cy), (cx, cy + 2.5 * S)], fill=255)
        dr.ellipse([cx - 7 * S, cy - 7 * S, cx + 7 * S, cy + 7 * S], outline=255, width=int(0.8 * S))
    img = comp(img, INK, layer(compass) * 0.85)
    # burnt, darkened edges
    edge = np.clip(np.maximum(np.abs(xx / W - 0.5) * 2, np.abs(yy / H - 0.5) * 2) - 0.78 + 0.12 * noise(H, W, 20 * S, 3, 9), 0, 1) / 0.22
    img = comp(img, [96, 62, 38], np.clip(edge, 0, 1) ** 1.5 * 0.85)
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    return out.resize((240, 160), Image.LANCZOS)


if __name__ == '__main__':
    paint().save(sys.argv[1] if len(sys.argv) > 1 else 'walls_map.png')
