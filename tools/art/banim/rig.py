"""Pose rig for battle-animation frames: a character is drawn from joint angles
as outlined pixel-art shapes (via the portrait kit's Scene), so every frame of
an animation shares the same proportions and colours.

Screen coordinates. The right-hand combatant faces left; its anchor is at
(148, 88) and its feet stand on y = 104. Angles are in degrees: 0 points
straight down, +90 points forward (left, toward the enemy), 180 points up.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "portraits"))
import pkit  # noqa: E402
from pkit import Scene, ellipse  # noqa: E402

pkit.SS = 4
AX, AY = 148, 88
GROUND = 104


def vec(a, length):
    r = math.radians(a)
    return (-math.sin(r) * length, math.cos(r) * length)


def add(p, v):
    return (p[0] + v[0], p[1] + v[1])


def capsule(p0, p1, w0, w1=None):
    """Tapered limb from p0 to p1 with round ends."""
    w1 = w0 if w1 is None else w1
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / L, dx / L
    a0 = math.atan2(ny, nx)
    pts = []
    for k in range(7):
        t = a0 - math.pi * k / 6
        pts.append((p1[0] + math.cos(t) * w1 / 2, p1[1] + math.sin(t) * w1 / 2))
    for k in range(7):
        t = a0 - math.pi - math.pi * k / 6
        pts.append((p0[0] + math.cos(t) * w0 / 2, p0[1] + math.sin(t) * w0 / 2))
    return pts


class Pose(dict):
    """Joint angles and the hip position. Missing keys fall back to IDLE."""

    def __getattr__(self, k):
        return self[k] if k in self else IDLE[k]


IDLE = dict(x=0.0, y=0.0,          # hip offset from the standing hip
            lean=12.0,              # torso, + leans forward
            head=0.0,
            fs=40.0, fe=40.0,       # front arm: shoulder, elbow (relative)
            bs=-20.0, be=30.0,      # back arm
            fb=110.0, bb=-130.0,    # blade angles (absolute)
            fh=18.0, fk=-30.0,      # front leg: hip, knee (relative, - bends back)
            bh=-14.0, bk=-24.0,
            blades=True)


def joints(p):
    hip = (AX + 4 + p.get("x", 0.0), GROUND - 22 + p.get("y", 0.0))
    lean = p.get("lean", IDLE["lean"])
    neck = add(hip, vec(180 - lean, 14))
    head = add(neck, vec(180 - lean - p.get("head", 0.0), 5.0))
    sh = add(hip, vec(180 - lean, 12))
    j = dict(hip=hip, neck=neck, head=head, sh=sh)
    for side in "fb":
        s = p.get(side + "s", IDLE[side + "s"])
        e = p.get(side + "e", IDLE[side + "e"])
        elbow = add(sh, vec(s, 8.0))
        hand = add(elbow, vec(s + e, 7.5))
        j[side + "elbow"], j[side + "hand"] = elbow, hand
        j[side + "fore"] = s + e
        h = p.get(side + "h", IDLE[side + "h"])
        k = p.get(side + "k", IDLE[side + "k"])
        knee = add(hip, vec(h, 11.0))
        foot = add(knee, vec(h + k, 11.0))
        j[side + "knee"], j[side + "foot"], j[side + "shin"] = knee, foot, h + k
    return j


def shade(s, key, p0, p1, w0, w1, g, off=(1.4, 0.4)):
    """Darker band along the back (+x) edge of a limb, kept inside its group."""
    s.fill(key, capsule(add(p0, off), add(p1, off), w0 * 0.55, w1 * 0.55), group=g, clip=g, raw=True)


def draw_blade(s, hand, angle, length=18):
    tip = add(hand, vec(angle, length))
    base = add(hand, vec(angle, 2.5))
    s.fill("metal", capsule(base, tip, 2.6, 1.2), group="blade", line="metald", raw=True)
    s.stroke("white", [add(base, vec(angle, 3)), add(tip, vec(angle, -3))], w=0.6, thr=0.5)
    # grip with its trigger guard
    s.fill("metald", capsule(add(hand, vec(angle, -3.0)), add(hand, vec(angle, 2.0)), 3.4), group="grip", raw=True)


def draw_leg(s, j, side, g):
    hip, knee, foot = j["hip"], j[side + "knee"], j[side + "foot"]
    s.fill("white", capsule(hip, knee, 7.4, 6.0), group=g, raw=True)
    shade(s, "whited", hip, knee, 7.4, 6.0, g)
    boot_top = add(knee, ((foot[0] - knee[0]) * 0.2, (foot[1] - knee[1]) * 0.2))
    s.fill("white", capsule(knee, boot_top, 6.0, 5.6), group=g, raw=True)
    s.fill("brown", capsule(boot_top, foot, 5.8, 5.0), group=g, raw=True)
    s.fill("haird", capsule(add(boot_top, (1.4, 0)), add(foot, (1.2, 0)), 2.6, 2.2), group=g, clip=g, raw=True)
    toe = add(foot, vec(j[side + "shin"] + 90, 3.4))
    s.fill("brown", capsule(foot, toe, 4.6, 3.4), group=g, raw=True)
    # ODM harness: straps round the thigh
    for f in (0.35, 0.7):
        a = (hip[0] * (1 - f) + knee[0] * f, hip[1] * (1 - f) + knee[1] * f)
        s.stroke("brown", [add(a, (-3.4, 0.4)), add(a, (3.4, -0.4))], w=0.9, clip=g, thr=0.4)


def draw_arm(s, j, side, g, blades, blade_angle):
    """blade_angle is absolute (same convention as the joints)."""
    sh, el, hand = j["sh"], j[side + "elbow"], j[side + "hand"]
    if blades:
        draw_blade(s, hand, blade_angle)
    s.fill("jacket", capsule(sh, el, 5.6, 4.8), group=g, raw=True)
    s.fill("jacket", capsule(el, hand, 4.8, 4.0), group=g, raw=True)
    shade(s, "jacketd", sh, el, 5.6, 4.8, g)
    shade(s, "jacketd", el, hand, 4.8, 4.0, g)
    s.fill("skin", ellipse(hand[0], hand[1], 2.2, 2.2), group=g + "h", raw=True)


def draw_head(s, j, lean):
    hd, neck = j["head"], j["neck"]
    s.fill("skin", capsule(neck, add(neck, vec(180 - lean, 2.5)), 3.8), group="neck", raw=True)
    x, y = hd
    # back hair mass, face, then the fringe falling forward
    s.fill("hair", ellipse(x + 0.8, y - 0.8, 5.8, 5.6), group="head", raw=True)
    for tip in ((x + 6.6, y + 3.6), (x + 5.4, y - 5.4), (x + 1.0, y - 7.0), (x - 4.0, y - 5.8)):
        s.fill("hair", [(x, y - 1), (tip[0] + 1.2, tip[1]), (tip[0], tip[1]), (x + 1, y + 1)], group="head", smooth=False)
    face = [(x - 4.4, y - 2.0), (x - 4.8, y + 1.6), (x - 3.4, y + 4.8), (x - 0.4, y + 5.6), (x + 2.0, y + 3.0),
            (x + 1.6, y - 2.0)]
    s.fill("skin", face, group="head", clip="head")
    s.fill("hair", [(x - 5.4, y - 1.2), (x - 3.6, y - 0.4), (x - 1.6, y - 2.4), (x + 0.4, y - 0.4),
                    (x + 2.6, y - 1.8), (x + 2.4, y - 6.2), (x - 3.4, y - 6.4)], group="head", clip="head", smooth=False)
    s.fill("haird", [(x + 2.0, y - 4.0), (x + 6.0, y - 1.0), (x + 5.4, y + 3.2), (x + 2.6, y + 2.0)],
           group="head", clip="head", smooth=False)
    s.dot("line", x - 3.0, y + 0.6, clip="head")
    s.dot("line", x - 3.0, y + 0.0, clip="head")
    s.stroke("skin", [(x - 1.8, y + 3.6), (x - 0.6, y + 3.8)], w=0.6, clip="head", thr=0.6)


def draw_cadet(s, p, cape=False):
    j = joints(p)
    blades = p.get("blades", True)
    lean = p.get("lean", IDLE["lean"])
    hip, sh = j["hip"], j["sh"]
    if p.get("wire"):
        for tgt in p["wire"]:
            s.stroke("gasd", [add(hip, (-1, -1)), tgt], w=0.8, thr=0.4, free=True)
    draw_arm(s, j, "b", "barm", blades, p.get("bb", IDLE["bb"]))
    draw_leg(s, j, "b", "bleg")
    # gas canisters strapped across the lower back
    back = add(hip, vec(-90 - lean, 5.0))
    for k, d in enumerate((0.0, 2.4)):
        c0 = add(add(back, vec(180 - lean, 1.0 + d)), vec(-90 - lean, -1))
        c1 = add(c0, vec(-90 - lean, 6.5))
        s.fill("metald" if k else "metal", capsule(c0, c1, 3.0, 3.0), group="gas%d" % k, line="line", raw=True)
    # torso: shirt at the waist, cropped jacket above, chest straps
    s.fill("white", capsule(hip, add(hip, vec(180 - lean, 4.5)), 9.6, 9.2), group="torso", raw=True)
    s.fill("jacket", capsule(add(hip, vec(180 - lean, 4.5)), sh, 10.4, 11.0), group="torso", raw=True)
    shade(s, "jacketd", add(hip, vec(180 - lean, 4.5)), sh, 10.4, 11.0, "torso", off=(2.6, 0.4))
    s.stroke("brown", [add(sh, vec(90 - lean, 4)), add(hip, vec(180 - lean, 3.0))], w=1.0, clip="torso", thr=0.4)
    s.stroke("brown", [add(hip, vec(90 - lean, 4.6)), add(hip, vec(-90 - lean, 4.6))], w=1.1, clip="torso", thr=0.4)
    # blade box on the hip
    box0 = add(hip, vec(-80 - lean, 7.5))
    box1 = add(hip, vec(80 - lean, 2.0))
    s.fill("metal", capsule(box0, box1, 5.0, 4.4), group="box", line="line", raw=True)
    s.stroke("metald", [add(box0, (0, 1.2)), add(box1, (0, 1.2))], w=0.9, clip="box", thr=0.45)
    draw_leg(s, j, "f", "fleg")
    draw_head(s, j, lean)
    draw_arm(s, j, "f", "farm", blades, p.get("fb", IDLE["fb"]))
    return j


def puff(s, x, y, r, key="gas"):
    s.fill(key, ellipse(x, y, r, r * 0.85, n=14), group="puff%d_%d" % (int(x), int(y)), line="gasd", raw=True)


def slash(s, cx, cy, r, a0, a1, w=1.6, key="glow"):
    pts = [add((cx, cy), vec(a0 + (a1 - a0) * t / 10, r)) for t in range(11)]
    s.stroke(key, pts, w=w, thr=0.4, free=True)
    s.stroke("white", pts[2:-2], w=w * 0.45, thr=0.5, free=True)


def render(scene, palette, flip_x=None):
    """Indexed 240x160 frame. flip_x mirrors the frame around that column
    (to turn a figure around when it swings behind its target)."""
    im = scene.render(palette, size=(240, 160))
    if flip_x is not None:
        out = np.zeros_like(im)
        xs = np.arange(240)
        src = 2 * int(round(flip_x)) - xs
        ok = (src >= 0) & (src < 240)
        out[:, xs[ok]] = im[:, src[ok]]
        im = out
    return im
