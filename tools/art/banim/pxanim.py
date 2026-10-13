"""Battle animations built from pixel-art poses (poses/<anim>/<pose>.png).

A frame is a pose pasted on the 240x160 canvas with its feet (bottom centre of
the pose, or `foot` from the layout) at (x, y), optionally mirrored, plus
effects drawn with rig.py (gas puffs, slash arcs, glints, blood, steam).
"""
import json
import os

import numpy as np

import rig
from rig import Scene, puff, slash, render
from poses import load_palette, load_pose

HERE = os.path.dirname(os.path.abspath(__file__))
GROUND = 105  # y of the feet in the standing pose, like the vanilla close-range layout


class PoseSet:
    def __init__(self, anim):
        self.anim = anim
        self.palette, _ = load_palette(anim)
        with open(os.path.join(HERE, "poses", anim, "palette.json")) as f:
            self.names = json.load(f)["names"]
        self.cache = {}

    def pose(self, name):
        if name not in self.cache:
            self.cache[name] = load_pose(self.anim, name)
        return self.cache[name]

    def index(self, key):
        return self.names.index(key) + 1

    def place(self, name, x, y, flip=False, foot=None):
        """Canvas with pose `name` whose foot point lands on (x, y)."""
        a = self.pose(name)
        if flip:
            a = a[:, ::-1]
        h, w = a.shape
        fx, fy = foot if foot else (w // 2, h)
        if flip and foot:
            fx = w - 1 - fx
        out = np.zeros((160, 240), np.uint8)
        x0, y0 = int(round(x - fx)), int(round(y - fy))
        ys0, xs0 = max(0, -y0), max(0, -x0)
        ys1, xs1 = min(h, 160 - y0), min(w, 240 - x0)
        if ys1 > ys0 and xs1 > xs0:
            sub = a[ys0:ys1, xs0:xs1]
            dst = out[y0 + ys0:y0 + ys1, x0 + xs0:x0 + xs1]
            dst[sub > 0] = sub[sub > 0]
        return out

    def fx(self, base, items):
        """Effects on top of a frame; colours are the animation's named slots."""
        named = {k: self.palette[i + 1] for i, k in enumerate(self.names)}
        named.setdefault("gas", named["white"])
        named.setdefault("gasd", named["white2"])
        s = Scene()
        for it in items:
            kind = it[0]
            if kind == "puff":
                puff(s, it[1], it[2], it[3])
            elif kind == "slash":
                slash(s, it[1], it[2], it[3], it[4], it[5], *(it[6:] or ()))
            elif kind == "star":
                x, y = it[1], it[2]
                s.stroke("white", [(x - 4, y), (x + 4, y)], w=1, free=True)
                s.stroke("white", [(x, y - 4), (x, y + 4)], w=1, free=True)
                s.stroke("glow", [(x - 2, y - 2), (x + 2, y + 2)], w=1, free=True)
                s.stroke("glow", [(x - 2, y + 2), (x + 2, y - 2)], w=1, free=True)
            elif kind == "blood":
                x, y, k = it[1], it[2], it[3]
                for i, (dx, dy) in enumerate([(-6, -5), (-9, 1), (-4, 7), (4, -8), (7, 4), (-12, -2)]):
                    r = 1.6 + (i % 3) * 0.5 + k
                    s.fill("red", rig.ellipse(x + dx * (1 + k * 0.6), y + dy * (1 + k * 0.6), r, r, n=10),
                           group="b%d" % i, line="red", raw=True)
            elif kind == "steam":
                x, y, k = it[1], it[2], it[3]
                for i, (dx, dy) in enumerate([(-3, -8), (3, -12), (-7, -14), (6, -6)]):
                    puff(s, x + dx * (1 + k), y + dy * (1 + k * 0.7), 2.5 + k * 1.5)
            elif kind == "wire":  # grapple wire from (x0, y0) to (x1, y1)
                s.stroke("metal", [(it[1], it[2]), (it[3], it[4])], w=0.8, free=True)
        keys = list(named)
        top = render(s, named)
        out = base.copy()
        for i, k in enumerate(keys):
            m = top == i + 1
            out[m] = self.index(k) if k in self.names else self.index({"gas": "white", "gasd": "white2"}[k])
        return out
