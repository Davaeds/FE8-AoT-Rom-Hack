"""Paint the AoT title screen backdrop (original art): the Colossal Titan peering over Wall Maria.

    python3 tools/art/paint_title.py OUTDIR      writes title_bg.png (sky, steam and Wall) and
                                               title_fg.png (the Colossal's head; RGBA)

The two layers become BG1 and BG0 of the title screen (tools/titleconv.py). The logo, the
subtitle and "Press START" are sprites drawn over the Wall, between y=48 and y=156.
Needs numpy and Pillow (not part of the normal build).
"""
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 3                      # paint at 3x, then reduce
W, H = 240 * S, 160 * S
WALL_TOP = 47              # screen row where the Wall's parapet starts
K = 0.80                   # head scale relative to the narration painting
HEAD_CX = 120
HEAD_TOP = WALL_TOP + 1 - 78 * K   # teeth meet the parapet


def lerp(a, b, t):
    return a + (b - a) * t


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


def mask_from(draw_fn):
    m = Image.new('L', (W, H), 0)
    draw_fn(ImageDraw.Draw(m))
    return np.asarray(m, float) / 255


def blur_mask(fn, r):
    mm = mask_from(fn)
    return np.asarray(Image.fromarray((mm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), float) / 255


def comp(base, color, alpha):
    a = alpha[..., None]
    return base * (1 - a) + np.asarray(color, float) * a


yy, xx = np.mgrid[0:H, 0:W].astype(float)
wall_top = WALL_TOP * S


def paint_bg():
    # ------------------------------------------------------------ sky: dusk over a burning district
    t = np.clip(yy / wall_top, 0, 1)
    top = np.array([22, 12, 20]); mid = np.array([104, 34, 30]); low = np.array([228, 116, 56])
    sky = np.where(t[..., None] < 0.5, lerp(top, mid, (t / 0.5)[..., None]), lerp(mid, low, ((t - 0.5) / 0.5)[..., None]))
    n = noise(H, W, 90, 4, 1)
    smoke = np.clip((n - 0.45) * 2.4, 0, 1) * np.clip(1.15 - t, 0, 1)
    img = comp(sky, [48, 26, 32], smoke * 0.75)
    cx, cy = HEAD_CX * S, (HEAD_TOP + 34 * K) * S
    d = np.hypot((xx - cx) / 1.6, (yy - cy) * 1.2) / (80 * S)
    img = comp(img, [255, 178, 96], np.clip(1 - d, 0, 1) ** 2 * 0.6)
    # steam boiling off the Colossal, billowing up and out behind the head
    st = noise(H, W, 26, 4, 7)
    plume = np.zeros((H, W))
    for (px, py, rx, ry) in ((HEAD_CX - 46, 14, 34, 26), (HEAD_CX + 48, 12, 34, 28), (HEAD_CX, -4, 70, 22),
                             (HEAD_CX - 80, 38, 40, 12), (HEAD_CX + 82, 38, 40, 12)):
        plume = np.maximum(plume, np.clip(1 - np.hypot((xx - px * S) / (rx * S), (yy - py * S) / (ry * S)), 0, 1))
    sa = np.clip((st - 0.38) * 2.4, 0, 1) * np.clip(plume * 1.6, 0, 1)
    img = comp(img, [214, 176, 160], sa * 0.55)
    img = comp(img, [248, 236, 226], np.clip((st - 0.52) * 3.0, 0, 1) * np.clip(plume * 1.6, 0, 1) * 0.8)

    # ------------------------------------------------------------ Wall Maria
    wy = yy - wall_top
    tex = noise(H, W, 9, 3, 11)
    stain = noise(H, W, 40, 3, 13)
    wall = np.zeros((H, W, 3)) + [128, 116, 104]
    wall = wall * (0.80 + 0.32 * tex[..., None])
    # vertical weathering streaks
    streak = noise(1, W, 6, 3, 17)[0]
    wall = comp(wall, [70, 62, 60], (np.clip((streak - 0.55) * 3, 0, 1)[None, :] * np.clip(wy / (90 * S), 0, 1) * 0.5) * np.ones((H, 1)))
    wall = comp(wall, [86, 74, 66], np.clip((stain - 0.5) * 2, 0, 1) * 0.35)
    # courses of huge stone blocks
    course = 12 * S
    row_i = np.floor(wy / course)
    rows = (wy % course < 1.0 * S).astype(float)
    off = (row_i % 2) * 19 * S
    cols = (((xx + off) % (38 * S)) < 1.0 * S).astype(float)
    wall = comp(wall, [62, 54, 50], np.clip(rows + cols, 0, 1) * 0.75)
    # light catching the top edge of each block
    wall = comp(wall, [170, 156, 136], ((wy % course >= 1.0 * S) & (wy % course < 2.0 * S)).astype(float) * 0.35)
    # warm dusk light on the upper Wall, falling off into shadow
    grad = np.clip(wy / (110 * S), 0, 1)
    wall = comp(wall, [255, 168, 104], np.clip(1 - wy / (40 * S), 0, 1) * 0.28)
    wall = comp(wall, [34, 28, 34], grad ** 1.3 * 0.62)
    # parapet: a lip of lighter stone with a shadow under it
    para = ((wy >= 0) & (wy < 3 * S)).astype(float)
    wall = comp(wall, [196, 150, 112], para * 0.8)
    wall = comp(wall, [40, 30, 32], ((wy >= 3 * S) & (wy < 4.5 * S)).astype(float) * 0.8)
    img = comp(img, wall, (yy >= wall_top).astype(float))

    # vignette
    vg = np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)), 0, 1) ** 2.2
    img = comp(img, [8, 6, 10], vg * 0.6)
    return img


def paint_fg(bg):
    """Return (rgb, alpha) of the Colossal's head, composited over bg."""
    img = bg.copy()
    alpha = np.zeros((H, W))
    k = K * S
    head_cx, head_top = HEAD_CX * S, HEAD_TOP * S
    HH = 88 * k
    prof = [(0.00, 0.0), (0.04, 16), (0.10, 25), (0.22, 33), (0.36, 37), (0.44, 37.5), (0.52, 35),
            (0.64, 31), (0.76, 26), (0.86, 19), (0.94, 11), (1.00, 0.0)]
    vy = (yy - head_top) / HH
    ys = np.array([p[0] for p in prof]); ws = np.array([p[1] for p in prof]) * k
    hw = np.interp(np.clip(vy, 0, 1), ys, ws)
    u = (xx - head_cx) / np.maximum(hw, 1e-3)
    inside = (vy >= 0) & (vy <= 1) & (np.abs(u) <= 1) & (yy < wall_top)
    hm = np.asarray(Image.fromarray((inside * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), float) / 255
    across = np.sqrt(np.clip(1 - u * u, 0, 1))
    light = 0.30 + 0.70 * across * (1 - 0.30 * np.clip(u, 0, 1)) * (1 - 0.25 * np.clip(vy - 0.55, 0, 1))
    bend = np.clip((vy - 0.30) / 0.5, 0, 1)
    phase = u * 16 + np.sign(u) * bend * (np.abs(u) ** 1.5) * -5 + np.sin(vy * 7) * 0.4
    warp = noise(H, W, 10, 2, 17)
    stri = (0.5 + 0.5 * np.sin((phase + (warp - 0.5) * 3.0) * math.pi)) ** 1.6
    grain = noise(H, W, 4, 2, 3)
    m = np.clip(light * (0.70 + 0.24 * stri + 0.14 * grain), 0, 1)
    dark, base, lite, hi = np.array([58, 10, 12]), np.array([136, 28, 26]), np.array([200, 72, 58]), np.array([240, 156, 130])
    mus = np.where(m[..., None] < 0.45, lerp(dark, base, (m / 0.45)[..., None]),
          np.where(m[..., None] < 0.78, lerp(base, lite, ((m - 0.45) / 0.33)[..., None]), lerp(lite, hi, ((m - 0.78) / 0.22)[..., None])))
    img = comp(img, mus, hm)
    alpha = np.maximum(alpha, hm)

    def at(x, y):
        return head_cx + x * k, head_top + y * k

    def cheeks(dr):
        for sd in (-1, 1):
            dr.line([at(sd * 8, 50), at(sd * 22, 46), at(sd * 34, 38)], fill=255, width=int(4 * k))
    img = comp(img, [224, 122, 104], blur_mask(cheeks, 1.6 * k) * hm * 0.55)

    def hollows(dr):
        for sd in (-1, 1):
            x0, y0 = at(sd * 27 - 6, 18); x1, y1 = at(sd * 27 + 6, 34)
            dr.ellipse([min(x0, x1), y0, max(x0, x1), y1], fill=255)
    img = comp(img, [60, 12, 14], blur_mask(hollows, 2.5 * k) * hm * 0.55)

    def brow(dr):
        for sd in (-1, 1):
            x0, y0 = at(sd * 15 - 13, 28); x1, y1 = at(sd * 15 + 13, 36)
            dr.ellipse([x0, y0, x1, y1], fill=255)
    img = comp(img, [214, 98, 82], blur_mask(brow, 1.2 * k) * hm * 0.8)

    def sockets(dr):
        for sd in (-1, 1):
            ex = 15 * sd
            dr.polygon([at(ex - sd * 10, 37), at(ex + sd * 11, 33), at(ex + sd * 9, 41), at(ex - sd * 6, 43)], fill=255)
    img = comp(img, [18, 4, 8], blur_mask(sockets, 1.0 * k) * 0.97)

    def pupils(dr):
        for sd in (-1, 1):
            x0, y0 = at(sd * 14 - 2.2, 36.0); x1, y1 = at(sd * 14 + 2.2, 40.2)
            dr.ellipse([x0, y0, x1, y1], fill=255)
    img = comp(img, [255, 244, 210], mask_from(pupils))
    img = comp(img, [255, 200, 140], blur_mask(pupils, 2.0 * k) * 0.55)

    def nose(dr):
        dr.polygon([at(0, 46), at(-5, 53), at(-2, 56), at(0, 54), at(2, 56), at(5, 53)], fill=255)
    img = comp(img, [26, 4, 6], blur_mask(nose, 0.5 * k))

    mx0, my0 = at(-29, 60); mx1, my1 = at(29, 78)

    def gums(dr):
        dr.rounded_rectangle([mx0 - 2 * k, my0 - 2 * k, mx1 + 2 * k, my1 + 2 * k], radius=8 * k, fill=255)
    img = comp(img, [176, 62, 68], blur_mask(gums, 1.0 * k) * hm * 0.9)

    def mouth_dark(dr):
        dr.rounded_rectangle([mx0, my0, mx1, my1], radius=7 * k, fill=255)
    img = comp(img, [34, 8, 10], mask_from(mouth_dark) * hm)

    def teeth(dr):
        n = 11
        for row in (0, 1):
            ya, yb = (my0 + 0.6 * k, (my0 + my1) / 2 - 0.6 * k) if row == 0 else ((my0 + my1) / 2 + 0.6 * k, my1 - 0.6 * k)
            for i in range(n):
                xa = lerp(mx0, mx1, i / n) + 0.8 * k
                xb = lerp(mx0, mx1, (i + 1) / n) - 0.8 * k
                edge = abs((i + 0.5) / n - 0.5) * 2
                inset = edge ** 2 * 4 * k
                if row == 0:
                    dr.rounded_rectangle([xa, ya + inset, xb, yb], radius=1.2 * k, fill=255)
                else:
                    dr.rounded_rectangle([xa, ya, xb, yb - inset], radius=1.2 * k, fill=255)
    tm = mask_from(teeth) * hm
    tshade = np.clip(np.abs((xx - head_cx) / (29 * k)), 0, 1)
    tooth_col = lerp(np.array([244, 236, 218]), np.array([150, 128, 112]), (tshade ** 2 * 0.8)[..., None])
    img = comp(img, tooth_col, tm)
    rim = np.clip(1 - np.abs(u + 0.92) / 0.10, 0, 1) * inside
    img = comp(img, [255, 190, 140], rim * 0.5)

    return img, alpha


def paint():
    bg = paint_bg()
    fg, a = paint_fg(bg)
    bg_im = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).resize((240, 160), Image.LANCZOS)
    fg_im = Image.fromarray(np.clip(fg, 0, 255).astype(np.uint8)).resize((240, 160), Image.LANCZOS)
    a_im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((240, 160), Image.BOX)
    fg_rgba = fg_im.convert('RGBA')
    fg_rgba.putalpha(a_im.point(lambda v: 255 if v >= 128 else 0))
    return bg_im, fg_rgba


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    bg, fg = paint()
    bg.save(os.path.join(out, 'title_bg.png'))
    fg.save(os.path.join(out, 'title_fg.png'))
