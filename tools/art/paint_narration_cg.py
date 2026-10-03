"""Paint 'The Colossal Titan over Wall Maria' (original art), 240x160, rendered at 2x then reduced.

    python3 tools/art/paint_narration_cg.py AoT/Graphics/Backgrounds/NarrationCG.png
    python3 tools/cgconv.py AoT/Graphics/Backgrounds/NarrationCG.png

Needs numpy and Pillow (not part of the normal build).
"""
import math
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 2
W, H = 240 * S, 160 * S
rng = np.random.default_rng(845)


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


def comp(base, color, alpha):
    a = alpha[..., None]
    return base * (1 - a) + np.asarray(color, float) * a


def paint():
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    # ---------------------------------------------------------------- sky
    t = yy / H
    top = np.array([28, 30, 48]); mid = np.array([120, 58, 46]); low = np.array([214, 120, 62])
    sky = np.where(t[..., None] < 0.45, lerp(top, mid, (t / 0.45)[..., None]), lerp(mid, low, ((t - 0.45) / 0.55)[..., None]))
    n = noise(H, W, 120, 4, 1)
    bands = np.clip((n - 0.45) * 2.2, 0, 1) * (0.35 + 0.65 * np.clip(1 - t * 1.4, 0, 1))
    img = comp(sky, [70, 52, 66], bands * 0.6)
    # glow behind the Colossal
    cx, cy = 120 * S, 62 * S
    d = np.hypot((xx - cx) / 1.3, yy - cy) / (90 * S)
    img = comp(img, [255, 170, 90], np.clip(1 - d, 0, 1) ** 2 * 0.55)

    # ---------------------------------------------------------------- steam behind
    steam = noise(H, W, 40, 4, 7)
    sb = np.clip(1 - np.hypot((xx - cx) / (110 * S), (yy - 70 * S) / (70 * S)), 0, 1)
    img = comp(img, [236, 222, 214], np.clip((steam - 0.42) * 2.4, 0, 1) * sb * 0.85)

    # ---------------------------------------------------------------- Colossal head
    head_cx, head_top = 120 * S, 14 * S
    HH = 88 * S
    prof = [(0.00, 0.0), (0.04, 16), (0.10, 25), (0.22, 33), (0.36, 37), (0.44, 37.5), (0.52, 35),
            (0.64, 31), (0.76, 26), (0.86, 19), (0.94, 11), (1.00, 0.0)]
    vy = (yy - head_top) / HH
    ys = np.array([p[0] for p in prof]); ws = np.array([p[1] for p in prof]) * S
    hw = np.interp(np.clip(vy, 0, 1), ys, ws)
    u = (xx - head_cx) / np.maximum(hw, 1e-3)
    inside = (vy >= 0) & (vy <= 1) & (np.abs(u) <= 1)
    hm = np.asarray(Image.fromarray((inside * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), float) / 255
    # pseudo-3D shading: rounder across, darker toward the jaw and the right side
    across = np.sqrt(np.clip(1 - u * u, 0, 1))
    light = 0.30 + 0.70 * across * (1 - 0.30 * np.clip(u, 0, 1)) * (1 - 0.25 * np.clip(vy - 0.55, 0, 1))
    # striations: vertical on the cranium, sweeping down-and-in over the cheeks and jaw
    bend = np.clip((vy - 0.30) / 0.5, 0, 1)
    phase = u * 22 + np.sign(u) * bend * (np.abs(u) ** 1.5) * -6 + np.sin(vy * 7) * 0.4
    warp = noise(H, W, 14, 2, 17)
    stri = 0.5 + 0.5 * np.sin((phase + (warp - 0.5) * 3.0) * math.pi)
    stri = stri ** 1.6
    grain = noise(H, W, 5, 2, 3)
    m = np.clip(light * (0.70 + 0.22 * stri + 0.16 * grain), 0, 1)
    dark, base, lite, hi = np.array([58, 10, 12]), np.array([132, 28, 26]), np.array([196, 70, 58]), np.array([238, 150, 128])
    mus = np.where(m[..., None] < 0.45, lerp(dark, base, (m / 0.45)[..., None]),
          np.where(m[..., None] < 0.78, lerp(base, lite, ((m - 0.45) / 0.33)[..., None]), lerp(lite, hi, ((m - 0.78) / 0.22)[..., None])))
    img = comp(img, mus, hm)

    def blur_mask(fn, r):
        mm = mask_from(fn)
        return np.asarray(Image.fromarray((mm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), float) / 255

    # cheekbone ridges (pale fibrous bands from nose to temple)
    def cheeks(dr):
        for sd in (-1, 1):
            dr.line([(head_cx + sd * 8 * S, head_top + 50 * S), (head_cx + sd * 22 * S, head_top + 46 * S), (head_cx + sd * 34 * S, head_top + 38 * S)], fill=255, width=int(4 * S))
    img = comp(img, [222, 120, 102], blur_mask(cheeks, 1.6 * S) * hm * 0.55)
    # temple hollows and jaw-muscle shadow
    def hollows(dr):
        for sd in (-1, 1):
            dr.ellipse([head_cx + sd * 27 * S - 6 * S, head_top + 18 * S, head_cx + sd * 27 * S + 6 * S, head_top + 34 * S], fill=255)
            dr.ellipse([head_cx + sd * 26 * S - 6 * S, head_top + 56 * S, head_cx + sd * 26 * S + 6 * S, head_top + 74 * S], fill=255)
    img = comp(img, [60, 12, 14], blur_mask(hollows, 2.5 * S) * hm * 0.55)
    # brow ridge
    def brow(dr):
        for sd in (-1, 1):
            ex = head_cx + sd * 15 * S
            dr.ellipse([ex - 13 * S, head_top + 28 * S, ex + 13 * S, head_top + 36 * S], fill=255)
    img = comp(img, [210, 96, 80], blur_mask(brow, 1.2 * S) * 0.75)
    # deep eye sockets, slanted
    def sockets(dr):
        for sd in (-1, 1):
            ex = head_cx + sd * 15 * S
            dr.polygon([(ex - sd * 10 * S, head_top + 37 * S), (ex + sd * 11 * S, head_top + 33 * S),
                        (ex + sd * 9 * S, head_top + 41 * S), (ex - sd * 6 * S, head_top + 43 * S)], fill=255)
    img = comp(img, [20, 4, 8], blur_mask(sockets, 1.4 * S) * 0.97)
    def pupils(dr):
        for sd in (-1, 1):
            ex = head_cx + sd * 14 * S
            dr.ellipse([ex - 2.0 * S, head_top + 36.2 * S, ex + 2.0 * S, head_top + 40.0 * S], fill=255)
    img = comp(img, [255, 240, 200], mask_from(pupils))
    img = comp(img, [255, 200, 140], blur_mask(pupils, 2.0 * S) * 0.5)
    # nasal cavity
    def nose(dr):
        dr.polygon([(head_cx, head_top + 46 * S), (head_cx - 5 * S, head_top + 53 * S), (head_cx - 2 * S, head_top + 56 * S), (head_cx, head_top + 54 * S),
                    (head_cx + 2 * S, head_top + 56 * S), (head_cx + 5 * S, head_top + 53 * S)], fill=255)
    img = comp(img, [26, 4, 6], blur_mask(nose, 0.6 * S))
    # gums, then teeth: a wide lipless grin
    mx0, mx1, my0, my1 = head_cx - 29 * S, head_cx + 29 * S, head_top + 60 * S, head_top + 78 * S
    def gums(dr):
        dr.rounded_rectangle([mx0 - 2 * S, my0 - 2 * S, mx1 + 2 * S, my1 + 2 * S], radius=8 * S, fill=255)
    img = comp(img, [170, 60, 66], blur_mask(gums, 1.0 * S) * 0.9)
    def mouth_dark(dr):
        dr.rounded_rectangle([mx0, my0, mx1, my1], radius=7 * S, fill=255)
    img = comp(img, [34, 8, 10], mask_from(mouth_dark))
    def teeth(dr):
        n = 13
        for row in (0, 1):
            ya, yb = (my0 + 0.5 * S, (my0 + my1) / 2 - 0.5 * S) if row == 0 else ((my0 + my1) / 2 + 0.5 * S, my1 - 0.5 * S)
            for k in range(n):
                xa = lerp(mx0, mx1, k / n) + 0.7 * S
                xb = lerp(mx0, mx1, (k + 1) / n) - 0.7 * S
                edge = abs((k + 0.5) / n - 0.5) * 2
                inset = edge ** 2 * 4 * S
                if row == 0:
                    dr.rounded_rectangle([xa, ya + inset, xb, yb], radius=1.2 * S, fill=255)
                else:
                    dr.rounded_rectangle([xa, ya, xb, yb - inset], radius=1.2 * S, fill=255)
    tm = mask_from(teeth)
    tshade = np.clip(np.abs((xx - head_cx) / (29 * S)), 0, 1)
    tooth_col = lerp(np.array([240, 232, 214]), np.array([150, 128, 112]), (tshade ** 2 * 0.8)[..., None])
    img = comp(img, tooth_col, tm)
    # rim light from the glow on the left edge of the head
    rim = np.clip(1 - np.abs(u + 0.92) / 0.10, 0, 1) * inside
    img = comp(img, [255, 186, 140], rim * 0.45)

    # ---------------------------------------------------------------- the Wall
    wall_top = 100 * S
    wall = np.zeros((H, W, 3)) + [150, 140, 122]
    tex = noise(H, W, 10, 3, 11)
    rows = ((yy - wall_top) % (13 * S) < 1.0 * S).astype(float)
    off = ((np.floor((yy - wall_top) / (13 * S)) % 2) * 17 * S)
    cols = (((xx + off) % (34 * S)) < 1.0 * S).astype(float)
    wall = wall * (0.82 + 0.3 * tex[..., None])
    wall = comp(wall, [86, 76, 66], np.clip(rows + cols, 0, 1) * 0.7)
    grad = np.clip((yy - wall_top) / (60 * S), 0, 1)
    wall = comp(wall, [60, 50, 50], grad * 0.55)
    wall = comp(wall, [255, 186, 120], np.clip(1 - (yy - wall_top) / (6 * S), 0, 1) * 0.45)   # lit top edge
    wm = (yy >= wall_top).astype(float)
    img = comp(img, wall, wm)
    # parapet line
    img = comp(img, [70, 56, 52], ((yy >= wall_top) & (yy < wall_top + 1.5 * S)).astype(float) * 0.9)

    # ---------------------------------------------------------------- hands gripping the wall top
    def hand(dr, x0, flip):
        # palm/knuckles on top of the wall, four fingers hanging over the edge
        dr.rounded_rectangle([x0 - 14 * S, wall_top - 9 * S, x0 + 14 * S, wall_top + 2 * S], radius=5 * S, fill=255)
        for k in range(4):
            fx = x0 - 11 * S + k * 7.2 * S
            ln = (13, 16, 15, 11)[k if not flip else 3 - k] * S
            dr.rounded_rectangle([fx, wall_top - 2 * S, fx + 5.6 * S, wall_top + ln], radius=2.6 * S, fill=255)
    hands = mask_from(lambda dr: (hand(dr, 66 * S, False), hand(dr, 174 * S, True)))
    hu = noise(H, W, 4, 2, 21)
    hcol = lerp(np.array([110, 26, 22]), np.array([196, 70, 58]), np.clip(0.3 + 0.7 * hu - np.clip((yy - wall_top) / (18 * S), 0, 1) * 0.5, 0, 1)[..., None])
    img = comp(img, hcol, hands)
    # finger separations
    def fseps(dr):
        for x0 in (66 * S, 174 * S):
            for k in range(1, 4):
                fx = x0 - 11 * S + k * 7.2 * S - 0.8 * S
                dr.line([(fx, wall_top - 1 * S), (fx, wall_top + 14 * S)], fill=255, width=int(1 * S))
    img = comp(img, [50, 10, 10], mask_from(fseps) * hands)

    # ---------------------------------------------------------------- town rooftops (foreground silhouettes)
    def roofs(dr):
        x = -10 * S
        r = np.random.default_rng(5)
        while x < W:
            w = r.integers(22, 40) * S
            h = r.integers(14, 26) * S
            base = 160 * S
            top = base - h
            dr.rectangle([x, top + 8 * S, x + w, base], fill=255)
            dr.polygon([(x - 2 * S, top + 9 * S), (x + w / 2, top - 6 * S), (x + w + 2 * S, top + 9 * S)], fill=255)
            if r.random() < 0.5:
                cxh = x + w * 0.7
                dr.rectangle([cxh, top - 6 * S, cxh + 4 * S, top + 4 * S], fill=255)
            x += w - 4 * S
        # church spire
        dr.polygon([(186 * S, 160 * S), (186 * S, 128 * S), (192 * S, 108 * S), (198 * S, 128 * S), (198 * S, 160 * S)], fill=255)
    rm = mask_from(roofs)
    roofcol = np.zeros((H, W, 3)) + [40, 28, 30]
    roofcol = comp(roofcol, [96, 56, 40], np.clip(noise(H, W, 8, 2, 31) - 0.4, 0, 1))
    img = comp(img, roofcol, rm)
    def windows(dr):
        r = np.random.default_rng(9)
        for k in range(16):
            x = r.integers(4, 236) * S
            y = r.integers(140, 156) * S
            dr.rectangle([x, y, x + 2 * S, y + 3 * S], fill=255)
    img = comp(img, [255, 196, 96], mask_from(windows) * rm * 0.9)

    # ---------------------------------------------------------------- steam pouring off the Titan
    st3 = noise(H, W, 18, 4, 51)
    plume = np.zeros((H, W))
    for (px, py, rx, ry) in ((120, 10, 70, 26), (46, 70, 30, 40), (194, 70, 30, 40), (66, 92, 24, 14), (174, 92, 24, 14)):
        plume = np.maximum(plume, np.clip(1 - np.hypot((xx - px * S) / (rx * S), (yy - py * S) / (ry * S)), 0, 1))
    img = comp(img, [248, 240, 232], np.clip((st3 - 0.40) * 2.6, 0, 1) * plume * 0.75)

    # ---------------------------------------------------------------- foreground steam wisps
    st2 = noise(H, W, 26, 4, 41)
    reg = np.clip(1 - np.hypot((xx - cx) / (130 * S), (yy - 96 * S) / (34 * S)), 0, 1)
    img = comp(img, [244, 236, 228], np.clip((st2 - 0.55) * 3, 0, 1) * reg * 0.7)

    # vignette
    vg = np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)), 0, 1) ** 2.2
    img = comp(img, [10, 6, 10], vg * 0.65)

    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    return out.resize((240, 160), Image.LANCZOS)


if __name__ == '__main__':
    im = paint()
    im.save(sys.argv[1] if len(sys.argv) > 1 else 'NarrationCG.png')
