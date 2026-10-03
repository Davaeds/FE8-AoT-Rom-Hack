"""Portrait kit: draw a character as layered shapes and strokes, rasterise it as
clean pixel art, and lay out an FE8 128x112 portrait sheet (hackbox format).

Coordinates are portrait pixels (the main portrait is 96x80). Shapes are
rendered at SS times the target size and reduced by majority vote, so edges
stay crisp with flat colours. Outlines are added automatically where a shape
meets something behind it, then strokes (eyelids, brows, strands, folds) and
single pixels are laid on top in draw order.

A character module defines PALETTE (key -> RGB, at most 15 entries) and
build(scene, mouth, eyes). mouth is one of MOUTHS, eyes one of open/half/closed.
"""
import numpy as np
from PIL import Image, ImageDraw

SS = 8
BG = (160, 200, 160)
MOUTHS = ["open", "half", "closed_talk", "smile_open", "smile_half", "smile_closed"]


def spline(points, closed=True, n=10):
    """Hermite spline through points. A point (x, y, 1) is a sharp corner."""
    pts = [(float(p[0]), float(p[1]), len(p) > 2 and p[2]) for p in points]
    N = len(pts)
    if N < 3:
        return [(p[0], p[1]) for p in pts]

    def tangent(i):
        if pts[i][2]:
            return (0.0, 0.0)
        if not closed and (i == 0 or i == N - 1):
            j0, j1 = max(i - 1, 0), min(i + 1, N - 1)
            return ((pts[j1][0] - pts[j0][0]) * 0.5, (pts[j1][1] - pts[j0][1]) * 0.5)
        a, b = pts[(i - 1) % N], pts[(i + 1) % N]
        return ((b[0] - a[0]) * 0.5, (b[1] - a[1]) * 0.5)

    out = []
    segs = range(N) if closed else range(N - 1)
    for i in segs:
        p1, p2 = pts[i], pts[(i + 1) % N]
        m1, m2 = tangent(i), tangent((i + 1) % N)
        for t in np.linspace(0, 1, n, endpoint=False):
            h00 = 2 * t**3 - 3 * t**2 + 1
            h10 = t**3 - 2 * t**2 + t
            h01 = -2 * t**3 + 3 * t**2
            h11 = t**3 - t**2
            out.append((h00 * p1[0] + h10 * m1[0] + h01 * p2[0] + h11 * m2[0],
                        h00 * p1[1] + h10 * m1[1] + h01 * p2[1] + h11 * m2[1]))
    if not closed:
        out.append((pts[-1][0], pts[-1][1]))
    return out


def ellipse(cx, cy, rx, ry, n=24, rot=0.0):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    c, s = np.cos(rot), np.sin(rot)
    return [(cx + rx * np.cos(t) * c - ry * np.sin(t) * s,
             cy + rx * np.cos(t) * s + ry * np.sin(t) * c) for t in a]


class Scene:
    def __init__(self):
        self.ops = []

    def fill(self, key, pts, group=None, outline=True, smooth=True, clip=None, raw=False, line=None):
        """Filled shape. Shapes sharing a group get no outline between them.
        clip limits painting to pixels already belonging to that group."""
        path = pts if raw else (spline(pts) if smooth else [(p[0], p[1]) for p in pts])
        self.ops.append(dict(kind="fill", key=key, path=path, group=group or key,
                             outline=outline, clip=clip, line=line))

    def stroke(self, key, pts, w=1.0, smooth=True, closed=False, clip=None, thr=0.3):
        path = spline(pts, closed=closed) if smooth and len(pts) > 2 else [(p[0], p[1]) for p in pts]
        self.ops.append(dict(kind="stroke", key=key, path=path, w=w, clip=clip, thr=thr,
                             closed=closed))

    def dot(self, key, x, y, clip=None):
        self.ops.append(dict(kind="dot", key=key, x=x, y=y, clip=clip))

    def render(self, palette, size=(96, 80), scale=1.0, ox=0.0, oy=0.0, line="line"):
        keys = list(palette)
        kidx = {k: i + 1 for i, k in enumerate(keys)}
        tw, th = size
        hw, hh = tw * SS, th * SS

        def xf(path):
            return [((x - ox) * scale * SS, (y - oy) * scale * SS) for x, y in path]

        groups = {}
        glines = {}
        op_hi = np.full((hh, hw), -1, np.int32)  # winning fill op per hi-res pixel
        fills = [i for i, o in enumerate(self.ops) if o["kind"] == "fill"]
        for i in fills:
            o = self.ops[i]
            groups.setdefault(o["group"], i)
            if o["line"]:
                glines[groups[o["group"]]] = o["line"]
            m = Image.new("L", (hw, hh), 0)
            ImageDraw.Draw(m).polygon(xf(o["path"]), fill=255)
            mask = np.asarray(m) > 0
            if o["clip"] is not None:
                gmap = np.array([self.ops[j].get("group") == o["clip"]
                                 for j in range(len(self.ops))] + [False])
                mask &= gmap[op_hi]
            op_hi[mask] = i

        # majority vote down to target size
        present = np.unique(op_hi)
        best = np.full((th, tw), -1, np.int32)
        bestc = np.full((th, tw), -1, np.int32)
        for i in present:
            c = (op_hi == i).reshape(th, SS, tw, SS).sum(axis=(1, 3))
            better = c > bestc
            best[better] = i
            bestc[better] = c[better]

        out = np.zeros((th, tw), np.uint8)
        grp = np.full((th, tw), -1, np.int32)  # group order of each pixel
        top = best.copy()                       # op index on top, for stroke ordering
        for i in present:
            if i < 0:
                continue
            o = self.ops[i]
            sel = best == i
            out[sel] = kidx[o["key"]]
            grp[sel] = groups[o["group"]]
        nooutline = {groups[o["group"]] for o in self.ops if o["kind"] == "fill" and not o["outline"]}

        # automatic outlines: a pixel in front of a different group gets a line.
        # Against the background the line is dark; inside, the group's own line colour.
        line_bg = np.zeros_like(out, bool)
        line_in = np.zeros_like(out, bool)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nb = np.full_like(grp, -1)
            ys = slice(max(dy, 0), th + min(dy, 0))
            yd = slice(max(-dy, 0), th + min(-dy, 0))
            xs = slice(max(dx, 0), tw + min(dx, 0))
            xd = slice(max(-dx, 0), tw + min(-dx, 0))
            nb[yd, xd] = grp[ys, xs]
            fg = (grp >= 0) & (nb < grp)
            line_bg |= fg & (nb < 0)
            line_in |= fg & (nb >= 0)
        for g in nooutline:
            line_bg &= grp != g
            line_in &= grp != g
        line_in &= ~line_bg
        out[line_bg] = kidx[line]
        for g in np.unique(grp[line_in]):
            out[line_in & (grp == g)] = kidx[glines.get(int(g), line)]

        def group_of(name):
            return groups.get(name, -2)

        for i, o in enumerate(self.ops):
            if o["kind"] == "stroke":
                m = Image.new("L", (hw, hh), 0)
                w = max(1, int(round(o["w"] * max(scale, 0.75) * SS)))
                p = xf(o["path"])
                if o["closed"]:
                    p = p + p[:1]
                d = ImageDraw.Draw(m)
                d.line(p, fill=255, width=w, joint="curve")
                r = w / 2
                for x, y in (p[0], p[-1]):
                    d.ellipse((x - r, y - r, x + r, y + r), fill=255)
                cov = (np.asarray(m) > 0).reshape(th, SS, tw, SS).mean(axis=(1, 3))
                sel = (cov >= o["thr"]) & (top < i) & (top >= 0)
                if o["clip"] is not None:
                    sel &= grp == group_of(o["clip"])
                out[sel] = kidx[o["key"]]
            elif o["kind"] == "dot":
                x = int(round((o["x"] - ox) * scale))
                y = int(round((o["y"] - oy) * scale))
                if 0 <= x < tw and 0 <= y < th and top[y, x] < i and top[y, x] >= 0:
                    if o["clip"] is None or grp[y, x] == group_of(o["clip"]):
                        out[y, x] = kidx[o["key"]]
        return out


def gba(c):
    return tuple((v >> 3) << 3 for v in c)


def build_sheet(mod, mouth_pos, eye_pos, mini=(0.62, 48, 38)):
    """Return a P-mode 128x112 sheet for a character module.
    mouth_pos/eye_pos are (x, y) in tiles; mini is (scale, face cx, face cy)."""
    pal = mod.PALETTE
    assert len(pal) <= 15, f"{len(pal)} colours"

    def draw(mouth="closed", eyes="open", **kw):
        s = Scene()
        mod.build(s, mouth=mouth, eyes=eyes)
        return s.render(pal, **kw)

    sheet = np.zeros((112, 128), np.uint8)
    sheet[0:80, 0:96] = draw()
    mx, my = mouth_pos[0] * 8, mouth_pos[1] * 8
    for n, m in enumerate(MOUTHS):
        frame = draw(mouth=m)[my:my + 16, mx:mx + 32]
        fx, fy = (n % 3) * 32, 80 + (n // 3) * 16
        sheet[fy:fy + 16, fx:fx + 32] = frame
    ex, ey = eye_pos[0] * 8, eye_pos[1] * 8
    sheet[48:64, 96:128] = draw(eyes="half")[ey:ey + 16, ex:ex + 32]
    sheet[64:80, 96:128] = draw(eyes="closed")[ey:ey + 16, ex:ex + 32]
    s, cx, cy = mini
    sheet[16:48, 96:128] = draw(size=(32, 32), scale=s, ox=cx - 16 / s, oy=cy - 16 / s)

    img = Image.fromarray(sheet, "P")
    flat = list(gba(BG))
    for c in pal.values():
        flat += list(gba(c))
    flat += [0] * (768 - len(flat))
    img.putpalette(flat)
    return img


def preview(img, path, zoom=4):
    img.convert("RGB").resize((img.width * zoom, img.height * zoom), Image.NEAREST).save(path)
