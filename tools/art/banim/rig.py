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
    hip = (AX + 4 + p.get("x", 0.0), GROUND - 21 + p.get("y", 0.0))
    lean = p.get("lean", IDLE["lean"])
    neck = add(hip, vec(180 - lean, 13))
    head = add(neck, vec(180 - lean - p.get("head", 0.0), 4.5))
    sh = add(hip, vec(180 - lean, 11))
    j = dict(hip=hip, neck=neck, head=head, sh=sh)
    for side in "fb":
        s = p.get(side + "s", IDLE[side + "s"])
        e = p.get(side + "e", IDLE[side + "e"])
        elbow = add(sh, vec(s, 7.5))
        hand = add(elbow, vec(s + e, 7.0))
        j[side + "elbow"], j[side + "hand"] = elbow, hand
        j[side + "fore"] = s + e
        h = p.get(side + "h", IDLE[side + "h"])
        k = p.get(side + "k", IDLE[side + "k"])
        knee = add(hip, vec(h, 10.5))
        foot = add(knee, vec(h + k, 10.5))
        j[side + "knee"], j[side + "foot"], j[side + "shin"] = knee, foot, h + k
    return j


def draw_blade(s, hand, angle, length=17):
    tip = add(hand, vec(angle, length))
    base = add(hand, vec(angle, 2))
    s.fill("metal", capsule(base, tip, 2.2, 1.2), group="blade", line="metald", raw=True)
    s.stroke("glow", [add(base, vec(angle, 3)), add(tip, vec(angle, -2))], w=0.6, thr=0.5)
    # grip and trigger box
    s.fill("metald", capsule(add(hand, vec(angle, -2.5)), add(hand, vec(angle, 1.5)), 3.0), group="grip", raw=True)


def draw_leg(s, j, side, g):
    hip, knee, foot = j["hip"], j[side + "knee"], j[side + "foot"]
    s.fill("white", capsule(hip, knee, 6.0, 5.0), group=g, raw=True)
    mid = ((knee[0] * 0.15 + foot[0] * 0.85), (knee[1] * 0.15 + foot[1] * 0.85))
    s.fill("white", capsule(knee, mid, 5.0, 4.4), group=g, raw=True)
    s.fill("brown", capsule(add(knee, ((foot[0] - knee[0]) * 0.25, (foot[1] - knee[1]) * 0.25)), foot, 4.6, 4.2),
           group=g, raw=True)
    toe = add(foot, vec(j[side + "shin"] + 90, 3.0))
    s.fill("brown", capsule(foot, toe, 3.6, 3.0), group=g, raw=True)
    # thigh strap
    a = ((hip[0] * 0.45 + knee[0] * 0.55), (hip[1] * 0.45 + knee[1] * 0.55))
    s.stroke("brown", [add(a, (-2.6, 0)), add(a, (2.6, 0))], w=0.9, clip=g, thr=0.4)


def draw_arm(s, j, side, g, blades, blade_angle):
    """blade_angle is absolute (same convention as the joints)."""
    sh, el, hand = j["sh"], j[side + "elbow"], j[side + "hand"]
    if blades:
        draw_blade(s, hand, blade_angle)
    s.fill("jacket", capsule(sh, el, 4.6, 4.0), group=g, raw=True)
    s.fill("jacket", capsule(el, hand, 4.0, 3.4), group=g, raw=True)
    s.fill("skin", ellipse(hand[0], hand[1], 1.9, 1.9), group=g + "h", raw=True)


def draw_cadet(s, p, cape=False):
    j = joints(p)
    blades = p.get("blades", True)
    if p.get("wire"):
        for tgt in p["wire"]:
            s.stroke("gas", [add(j["hip"], (-1, 0)), tgt], w=0.7, thr=0.4, free=True)
    draw_arm(s, j, "b", "barm", blades, p.get("bb", IDLE["bb"]))
    draw_leg(s, j, "b", "bleg")
    # torso: white shirt, tan cropped jacket, gear at the hips
    hip, sh, neck = j["hip"], j["sh"], j["neck"]
    lean = p.get("lean", IDLE["lean"])
    s.fill("white", capsule(hip, add(hip, vec(180 - lean, 4)), 8.4, 8.0), group="torso", raw=True)
    s.fill("jacket", capsule(add(hip, vec(180 - lean, 4)), sh, 9.0, 9.6), group="torso", raw=True)
    s.fill("jacketd", capsule(add(hip, vec(180 - lean, 4.5)), add(sh, vec(-90 - lean, 1.5)), 3.0, 3.0),
           group="torso", clip="torso", raw=True)
    s.stroke("brown", [add(sh, vec(90 - lean, 3)), add(hip, vec(180 - lean, 3.5))], w=0.9, clip="torso", thr=0.4)
    # ODM gear: gas canister on the back, blade box at the hip
    back = add(hip, vec(-90 - lean, 4.5))
    s.fill("metald", capsule(add(back, vec(180 - lean, 7)), add(back, vec(-110 - lean, 3)), 3.2, 3.2), group="gear", raw=True)
    box0 = add(hip, vec(-80 - lean, 6))
    box1 = add(hip, vec(70 - lean, 1))
    s.fill("metal", capsule(box0, box1, 4.2, 3.8), group="box", line="metald", raw=True)
    s.stroke("metald", [box0, box1], w=0.6, clip="box", thr=0.5)
    draw_leg(s, j, "f", "fleg")
    # head
    hd = j["head"]
    s.fill("skin", capsule(neck, add(neck, vec(180 - lean, 2)), 3.2), group="neck", raw=True)
    s.fill("hair", ellipse(hd[0] + 0.6, hd[1] - 0.6, 4.9, 4.7), group="head", raw=True)
    face = [(hd[0] - 3.6, hd[1] - 1.5), (hd[0] - 4.0, hd[1] + 1.5), (hd[0] - 2.6, hd[1] + 4.2),
            (hd[0] + 0.2, hd[1] + 4.6), (hd[0] + 1.8, hd[1] + 2.0), (hd[0] + 1.0, hd[1] - 1.8)]
    s.fill("skin", face, group="head", clip="head")
    s.fill("hair", [(hd[0] - 4.4, hd[1] - 1.0), (hd[0] - 1.0, hd[1] - 2.6), (hd[0] + 2.0, hd[1] - 0.6),
                    (hd[0] + 1.6, hd[1] - 5.0), (hd[0] - 3.0, hd[1] - 5.2)], group="head", clip="head")
    s.dot("line", hd[0] - 2.6, hd[1] + 0.4, clip="head")
    s.fill("hair", [(hd[0] + 2.4, hd[1] - 1.0), (hd[0] + 5.6, hd[1] + 1.0), (hd[0] + 3.6, hd[1] + 3.2)],
           group="head")
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
