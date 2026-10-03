"""Paint the menu backdrop (original art): Wall Maria's stonework with a carved frieze of
Survey Corps wings. 256x160, seamless left to right (the chapter title card scrolls it).

    python3 tools/art/paint_menu_bg.py OUT.png

Converted by tools/menubgconv.py. Needs numpy and Pillow (not part of the normal build).
"""
import math
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 4
W, H = 256 * S, 160 * S
BAND = (56, 104)             # rows drawn with the darker palette on the chapter title card


def lerp(a, b, t):
    return a + (b - a) * t


def tile_noise(h, w, scale, octaves=4, seed=0):
    """Fractal noise that wraps left to right."""
    r = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gw = max(2, int(round(w / scale)))
        gh = max(2, int(h / scale) + 2)
        g = r.random((gh, gw))
        g = np.hstack([g, g[:, :1]])                      # wrap the last cell onto the first
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((w + w // gw, h), Image.BICUBIC)
        out += np.asarray(img, float)[:, :w] / 255 * amp
        tot += amp
        amp *= 0.5
        scale /= 2
    return out / tot


def comp(base, color, alpha):
    a = alpha[..., None]
    return base * (1 - a) + np.asarray(color, float) * a


def wings_mask(cx, cy, size):
    """Survey Corps emblem: two overlapping wings spread up and out like a shield.
    Returns (front wing, back wing, feather lines) masks."""
    def wing_pts(sign, shift):
        x0 = cx + shift * size
        def P(x, y):
            return (x0 + sign * x * size, cy + y * size)
        # inner edge up from the point, leading edge out to the tip, then three feathers back in
        return [P(0.00, 0.62), P(-0.02, -0.30), P(0.30, -0.55), P(0.62, -0.72), P(0.98, -0.80),
                P(0.86, -0.50), P(0.92, -0.42), P(0.74, -0.14), P(0.80, -0.06), P(0.56, 0.22),
                P(0.60, 0.30), P(0.30, 0.48)]
    def lines(dr, sign, shift):
        x0 = cx + shift * size
        def P(x, y):
            return (x0 + sign * x * size, cy + y * size)
        for a, b in ((P(0.10, -0.26), P(0.86, -0.50)), (P(0.08, 0.02), P(0.74, -0.14)), (P(0.06, 0.30), P(0.56, 0.22))):
            dr.line([a, b], fill=255, width=max(1, int(0.07 * size)))
    m_front = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m_front).polygon(wing_pts(-1, -0.04), fill=255)
    m_back = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m_back).polygon(wing_pts(1, 0.04), fill=255)
    m_lines = Image.new('L', (W, H), 0)
    lines(ImageDraw.Draw(m_lines), -1, -0.04)
    lines(ImageDraw.Draw(m_lines), 1, 0.04)
    f = np.asarray(m_front, float) / 255
    return f, np.asarray(m_back, float) / 255 * (1 - f), np.asarray(m_lines, float) / 255


def paint():
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    tex = tile_noise(H, W, 10 * S, 4, 3)
    blot = tile_noise(H, W, 48 * S, 3, 5)
    wall = np.zeros((H, W, 3)) + [196, 188, 172]
    wall = wall * (0.84 + 0.26 * tex[..., None])
    wall = comp(wall, [150, 138, 122], np.clip((blot - 0.5) * 2.2, 0, 1) * 0.5)
    # stone courses: 16 px tall, 64 px blocks, alternate rows offset by half a block
    course = 16 * S
    row = np.floor(yy / course)
    off = (row % 2) * 32 * S
    seam_h = (yy % course) < 1.2 * S
    seam_v = ((xx + off) % (64 * S)) < 1.2 * S
    wall = comp(wall, [112, 102, 92], (seam_h | seam_v).astype(float) * 0.8)
    wall = comp(wall, [232, 226, 214], (((yy % course) >= 1.2 * S) & ((yy % course) < 2.4 * S)).astype(float) * 0.35)
    # the frieze: a recessed panel framed by two carved mouldings
    b0, b1 = BAND[0] * S, BAND[1] * S
    panel = (yy >= b0) & (yy < b1)
    flat = np.zeros((H, W, 3)) + [176, 166, 150]
    flat = flat * (0.88 + 0.18 * tex[..., None])
    wall = np.where(panel[..., None], flat, wall)
    for edge in (b0, b1):
        wall = comp(wall, [236, 230, 218], ((yy >= edge - 3 * S) & (yy < edge - 2 * S)).astype(float))
        wall = comp(wall, [96, 86, 78], ((yy >= edge - 2 * S) & (yy < edge)).astype(float))
        wall = comp(wall, [70, 62, 58], ((yy >= edge) & (yy < edge + 1 * S)).astype(float) * 0.8)
    for edge in (b0 + 4 * S, b1 - 5 * S):
        wall = comp(wall, [120, 110, 98], ((yy >= edge) & (yy < edge + 1 * S)).astype(float) * 0.7)
        wall = comp(wall, [226, 218, 204], ((yy >= edge + 1 * S) & (yy < edge + 2 * S)).astype(float) * 0.6)
    # carved wings every 64 px, in relief: lit from the top left
    cy = (b0 + b1) / 2
    for k in range(4):
        cx = (32 + 64 * k) * S
        front, back, feathers = wings_mask(cx, cy, 18 * S)
        both = np.clip(front + back, 0, 1)
        sh = np.roll(np.roll(both, 2 * S, 0), 2 * S, 1)
        hi = np.roll(np.roll(both, -1 * S, 0), -1 * S, 1)
        wall = comp(wall, [96, 86, 80], np.clip(sh - both, 0, 1) * 0.9)
        wall = comp(wall, [246, 240, 230], np.clip(hi - both, 0, 1) * 0.8)
        wall = comp(wall, [232, 226, 214], front)
        wall = comp(wall, [120, 112, 108], back)
        wall = comp(wall, [150, 140, 128], feathers * front)
        wall = comp(wall, [84, 78, 76], feathers * back)
    # weathering streaks running down from the frieze
    streak = tile_noise(1, W, 5 * S, 3, 9)[0]
    st = np.clip((streak - 0.6) * 3, 0, 1)[None, :] * np.clip((yy - b1) / (40 * S), 0, 1) * np.clip(1 - (yy - b1) / (56 * S), 0, 1)
    wall = comp(wall, [128, 118, 106], st * 0.45)
    out = Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8))
    return out.resize((256, 160), Image.LANCZOS)


if __name__ == '__main__':
    paint().save(sys.argv[1] if len(sys.argv) > 1 else 'menu_bg.png')
