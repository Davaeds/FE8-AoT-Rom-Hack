"""Tiny 2D rig for big map sprites: shaded capsules and torsos at 1x, head stamps, contours.

Coordinates are pixel centres in a 32x32 frame; y grows downward; feet rest on row FEET.
"""
import math
import numpy as np
from tkit import art, OUTLINE, SHADOW

FW = FH = 32
FEET = 30          # last row of the feet; outline on 31; shadow on 31
LIGHT = np.array([-0.55, -0.45, 0.70])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


class Ramp:
    """Palette indices from dark to light, with brightness thresholds."""
    def __init__(self, cols, cuts):
        self.cols, self.cuts = cols, cuts   # len(cuts) == len(cols) - 1, ascending

    def pick(self, b):
        for c, t in zip(self.cols, self.cuts):
            if b < t:
                return c
        return self.cols[-1]


class Layer:
    def __init__(self):
        self.idx = np.zeros((FH, FW), np.uint8)

    @property
    def mask(self):
        return self.idx != 0


def _shade(nx, ny):
    nz2 = max(0.0, 1.0 - nx * nx - ny * ny)
    n = np.array([nx, ny, math.sqrt(nz2)])
    return float(n @ LIGHT)


def capsule(layer, p0, p1, r0, r1, ramp, dark=0.0):
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy or 1e-9
    for y in range(FH):
        for x in range(FW):
            px, py = x + 0.5, y + 0.5
            t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / L2))
            cx, cy = x0 + t * dx, y0 + t * dy
            r = r0 + (r1 - r0) * t
            ex, ey = px - cx, py - cy
            d = math.hypot(ex, ey)
            if d <= r:
                b = _shade(ex / r, ey / r * 0.6) - dark
                layer.idx[y, x] = ramp.pick(b)


def torso(layer, cx, top, rows, ramp, dark=0.0, xs=None):
    """rows: list of (half_width_left, half_width_right) per row from `top` down."""
    for i, (hl, hr) in enumerate(rows):
        y = top + i
        if not 0 <= y < FH:
            continue
        for x in range(FW):
            px = x + 0.5
            if cx - hl <= px <= cx + hr:
                hw = hl if px < cx else hr
                nx = (px - cx) / max(hw, 0.5)
                b = _shade(max(-1, min(1, nx)) * 0.95, -0.15) - dark
                layer.idx[y, x] = ramp.pick(b)


def ellipse(layer, cx, cy, rx, ry, ramp, dark=0.0):
    for y in range(FH):
        for x in range(FW):
            nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if nx * nx + ny * ny <= 1.0:
                layer.idx[y, x] = ramp.pick(_shade(nx, ny) - dark)


def stamp(layer, rows, cmap, x0, y0):
    a = art(rows, cmap)
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            v = a[y, x]
            if v and 0 <= y0 + y < FH and 0 <= x0 + x < FW:
                layer.idx[y0 + y, x0 + x] = v


def plot(layer, pts, color):
    for x, y in pts:
        if 0 <= y < FH and 0 <= x < FW:
            layer.idx[y, x] = color


def _border(mask):
    near = np.zeros_like(mask)
    near[1:, :] |= mask[:-1, :]
    near[:-1, :] |= mask[1:, :]
    near[:, 1:] |= mask[:, :-1]
    near[:, :-1] |= mask[:, 1:]
    return near & ~mask


def composite(layers, contour=OUTLINE, shadow_w=15, shadow_cx=16):
    out = np.zeros((FH, FW), np.uint8)
    for lay in layers:
        if lay is None:
            continue
        m = lay.mask
        c = getattr(lay, 'contour', contour)
        if c is not None:
            edge = _border(m) & (out != 0)
            out[edge] = c
        out[m] = lay.idx[m]
    # external outline
    solid = out != 0
    out[_border(solid)] = OUTLINE
    # ground shadow on the last row, only where empty
    y = FH - 1
    for x in range(shadow_cx - shadow_w // 2, shadow_cx - shadow_w // 2 + shadow_w):
        if 0 <= x < FW and out[y, x] == 0:
            out[y, x] = SHADOW
    return out
