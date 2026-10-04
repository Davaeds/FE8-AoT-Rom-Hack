"""Battle animation: a common (pure) Titan. Lanky, hunched, a head too big for
its body and a fixed wide grin, the way the show draws them.

Normal attack: lumber forward and snatch at the enemy with one huge hand.
Critical: lunge in jaw first and bite.
Dodge: rear back.

The nape sits at the back of the neck around (158, 40) in this right-hand
frame, which is where the cadet's critical cuts when it is the left combatant.
"""
import math

import rig
from rig import Scene, capsule, ellipse, render, vec, add

ABBR = "aot_titan"
SLOT = 2
PAL = {
    "line": (48, 24, 24), "skin": (228, 168, 140), "skind": (184, 116, 96), "skinl": (248, 204, 180),
    "hair": (92, 60, 40), "haird": (52, 34, 26), "eye": (244, 236, 216), "iris": (88, 60, 44),
    "mouth": (112, 28, 36), "teeth": (246, 242, 228), "gas": (236, 236, 236), "gasd": (172, 172, 180),
    "red": (200, 30, 40),
}
PALETTE = list(PAL.values())

IDLE = dict(x=0.0, y=0.0, lean=18.0, head=0.0, jaw=0.0,
            fs=18.0, fe=22.0, bs=-12.0, be=18.0,      # arms: shoulder, elbow (relative)
            fh=22.0, fk=-34.0, bh=-12.0, bk=-14.0,    # legs: hip, knee (relative)
            hand="open")


class Pose(dict):
    def __getattr__(self, k):
        return self[k] if k in self else IDLE[k]


def joints(p):
    hip = (168 + p.x, 68 + p.y)
    sh = add(hip, vec(180 - p.lean, 26))
    neck = add(sh, vec(180 - p.lean - 25, 5))
    j = dict(hip=hip, sh=sh, neck=neck)
    j["head"] = add(neck, vec(180 - p.lean - 50 - p.head, 11))
    j["nape"] = add(neck, vec(-90 - p.lean, 5))
    for side, off in (("f", -4.0), ("b", 4.0)):
        s0 = add(sh, vec(-90 - p.lean, off))
        el = add(s0, vec(getattr(p, side + "s"), 19))
        hand = add(el, vec(getattr(p, side + "s") + getattr(p, side + "e"), 17))
        j[side + "sh"], j[side + "el"], j[side + "hand"] = s0, el, hand
        j[side + "fore"] = getattr(p, side + "s") + getattr(p, side + "e")
        h, k = getattr(p, side + "h"), getattr(p, side + "k")
        knee = add(hip, vec(h, 17))
        foot = add(knee, vec(h + k, 17))
        j[side + "knee"], j[side + "foot"], j[side + "shin"] = knee, foot, h + k
    # keep the feet on the ground: shift everything so the lower foot stands on y = 104
    drop = 104 - max(j["ffoot"][1], j["bfoot"][1]) if not p.get("air") else 0
    return {k: (v[0], v[1] + drop) if isinstance(v, tuple) else v for k, v in j.items()}


def shade(s, p0, p1, w0, w1, g, off=(2.0, 0.6), key="skind"):
    s.fill(key, capsule(add(p0, off), add(p1, off), w0 * 0.55, w1 * 0.55), group=g, clip=g, raw=True)


def draw_leg(s, j, side):
    g = side + "leg"
    hip, knee, foot = j["hip"], j[side + "knee"], j[side + "foot"]
    s.fill("skin", capsule(hip, knee, 11, 8), group=g, raw=True)
    s.fill("skin", capsule(knee, foot, 8, 6), group=g, raw=True)
    shade(s, hip, knee, 11, 8, g)
    shade(s, knee, foot, 8, 6, g)
    s.fill("skin", capsule(foot, add(foot, vec(j[side + "shin"] + 90, 7)), 6, 5), group=g, raw=True)
    s.stroke("skind", [add(knee, (-2, -1)), add(knee, (2, 1))], w=0.8, clip=g, thr=0.4)


def draw_hand(s, j, side, kind, g):
    hand, fore = j[side + "hand"], j[side + "fore"]
    if kind == "fist":
        s.fill("skin", ellipse(hand[0], hand[1], 5.2, 5.2), group=g, raw=True)
        for k in (-2.4, 0, 2.4):
            a = add(hand, vec(fore + 90, k))
            s.stroke("skind", [add(a, vec(fore, 1.0)), add(a, vec(fore, 4.2))], w=0.6, clip=g, thr=0.45)
        return
    palm = add(hand, vec(fore, 2))
    s.fill("skin", ellipse(palm[0], palm[1], 5.2, 5.2), group=g, raw=True)
    spread = 22 if kind == "open" else 9
    for k, d in enumerate((-1.5, -0.5, 0.5, 1.5)):
        a = fore + d * spread
        base = add(palm, vec(a, 3.5))
        s.fill("skin", capsule(base, add(base, vec(a + (8 if kind == "grab" else 0), 6.5)), 2.6, 2.0),
               group=g, raw=True)
    thumb = add(palm, vec(fore - 80, 3.5))
    s.fill("skin", capsule(thumb, add(thumb, vec(fore - 40, 5)), 2.8, 2.2), group=g, raw=True)


def draw_arm(s, j, side, p):
    g = side + "arm"
    s0, el, hand = j[side + "sh"], j[side + "el"], j[side + "hand"]
    s.fill("skin", capsule(s0, el, 9, 7), group=g, raw=True)
    s.fill("skin", capsule(el, hand, 7, 6), group=g, raw=True)
    shade(s, s0, el, 9, 7, g)
    shade(s, el, hand, 7, 6, g)
    draw_hand(s, j, side, p.hand if side == "f" else "open", g)


def draw_head(s, j, p, H=1.4):
    """The head is drawn H times life size: Titans' heads are too big for their bodies."""
    x, y = j["head"]

    def P(dx, dy):
        return (x + dx * H, y + dy * H)

    tilt = -p.lean * 0.3 - p.head
    s.fill("skin", capsule(j["neck"], j["head"], 10, 12), group="neck", raw=True)
    # back hair mass behind the skull
    s.fill("hair", ellipse(*P(2.5, -1.5), 12.5 * H, 12.0 * H, rot=tilt), group="head", raw=True)
    for tip in ((15, 6), (13, -9), (6, -14), (-4, -14)):
        s.fill("hair", [P(2, -2), P(tip[0] + 2, tip[1]), P(*tip), P(3, 2)], group="head", smooth=False)
    # face: wide, a heavy jaw that drops open
    jaw = p.jaw
    face = [P(-11, -4), P(-12, 3), P(-10.5, 9 + jaw), P(-3, 12 + jaw), P(4, 9 + jaw * 0.5), P(5, -3), P(0, -9)]
    s.fill("skin", face, group="head", clip="head")
    s.fill("skind", [P(1, -6), P(6, -3), P(5, 8), P(1, 10 + jaw)], group="head", clip="head")
    # fringe
    s.fill("hair", [P(-12.5, -3), P(-9, -2), P(-6, -5), P(-3, -2.5), P(0.5, -5.5), P(4, -2), P(4, -11), P(-6, -12.5)],
           group="head", clip="head", smooth=False)
    s.fill("haird", [P(3, -9), P(12, -2), P(12, 6), P(5, 2)], group="head", clip="head")
    # big round staring eyes with tiny pupils
    for ex in (-9.0, -3.2):
        c = P(ex, 0.8)
        s.fill("eye", ellipse(c[0], c[1], 2.0 * H, 1.7 * H), group="head", clip="head", raw=True)
        s.dot("line", c[0] - 0.8, c[1], clip="head")
    s.stroke("line", [P(-11.4, -1.4), P(-6.8, -1.6)], w=0.7, clip="head", thr=0.5)
    s.stroke("line", [P(-5.4, -1.6), P(-1.2, -1.2)], w=0.7, clip="head", thr=0.5)
    s.stroke("skind", [P(-7.2, 2.6), P(-7.8, 4.2), P(-6.4, 4.4)], w=0.6, clip="head", thr=0.5)
    # the grin: lips stretched almost ear to ear, teeth bared
    top, bot = 6.2, 8.0 + jaw
    s.fill("mouth", [P(-11.6, top - 0.8), P(-6, top + 0.2), P(2.4, top - 1.0), P(2.0, bot - 0.6), P(-5, bot + 0.6),
                     P(-11.0, bot - 1.2)], group="head", clip="head")
    s.stroke("teeth", [P(-10.8, top + 0.1), P(-5, top + 0.8), P(1.6, top - 0.2)], w=1.3 * H, clip="head", thr=0.4)
    if jaw >= 2:
        s.stroke("teeth", [P(-10.2, bot - 1.2), P(-5, bot - 0.2), P(1.2, bot - 1.2)], w=1.1 * H, clip="head", thr=0.4)
    for k in range(6):
        t0 = P(-10.0 + k * 2.2, top - 0.2)
        s.stroke("line", [t0, (t0[0], t0[1] + 1.4 * H)], w=0.45, clip="head", thr=0.6)
    s.stroke("line", [P(-12.2, top - 1.6), P(-11.2, top + 0.4)], w=0.6, clip="head", thr=0.5)
    s.stroke("line", [P(2.6, top - 2.0), P(2.2, top + 0.2)], w=0.6, clip="head", thr=0.5)


def draw_titan(s, p):
    j = joints(p)
    draw_arm(s, j, "b", p)
    draw_leg(s, j, "b")
    hip, sh = j["hip"], j["sh"]
    # torso: narrow hips, a round belly and a broad, bony chest
    lean = p.lean
    chest = add(hip, vec(180 - lean, 18))
    s.fill("skin", capsule(hip, chest, 17, 22), group="torso", raw=True)
    s.fill("skin", capsule(chest, sh, 22, 19), group="torso", raw=True)
    s.fill("skind", capsule(add(hip, vec(-90 - lean, 5)), add(sh, vec(-90 - lean, 5)), 8, 9), group="torso",
           clip="torso", raw=True)
    belly = add(hip, vec(180 - lean, 8))
    s.stroke("skind", [add(belly, vec(90 - lean, 1)), add(belly, vec(180 - lean, 4))], w=0.6, clip="torso", thr=0.5)
    for k in range(3):   # ribs along the side
        r = add(chest, vec(180 - lean, 1 + k * 3))
        s.stroke("skind", [add(r, vec(90 - lean, 2)), add(r, vec(-90 - lean, 6))], w=0.6, clip="torso", thr=0.5)
    s.stroke("skind", [add(sh, vec(90 - lean, 7)), add(chest, vec(90 - lean, 9))], w=0.7, clip="torso", thr=0.5)
    draw_leg(s, j, "f")
    draw_head(s, j, p)
    draw_arm(s, j, "f", p)
    if p.get("steam"):
        k = p["steam"]
        for i, (dx, dy) in enumerate([(0, -6), (5, -11), (-4, -13), (8, -3)]):
            rig.puff(s, j["nape"][0] + dx * (1 + k), j["nape"][1] + dy * (1 + k * 0.6), 2.5 + k * 1.5)
    return j


POSES = {
    "idle": Pose(),
    "idle2": Pose(y=1, lean=20, head=-4, fs=14, fe=26, bs=-8, be=20),
    # snatch
    "rear": Pose(x=6, lean=4, head=6, fs=-120, fe=40, bs=-30, be=30, fh=12, fk=-20, bh=-20, bk=-10, jaw=1),
    "step": Pose(x=-6, lean=30, fs=-60, fe=30, bs=-20, be=20, fh=40, fk=-50, bh=-24, bk=-8, jaw=1),
    "snatch": Pose(x=-16, lean=48, head=-14, fs=62, fe=6, bs=10, be=20, fh=50, fk=-60, bh=-30, bk=-6, jaw=2),
    "grab": Pose(x=-18, lean=52, head=-16, fs=64, fe=12, bs=14, be=20, fh=52, fk=-62, bh=-32, bk=-6, jaw=2,
                 hand="grab"),
    "pull": Pose(x=-8, lean=30, head=-6, fs=40, fe=60, bs=0, be=20, fh=34, fk=-44, bh=-20, bk=-10, jaw=1, hand="fist"),
    # bite
    "gape": Pose(x=4, lean=6, head=14, fs=-30, fe=30, bs=-40, be=30, fh=14, fk=-20, bh=-18, bk=-10, jaw=4),
    "lunge": Pose(x=-26, lean=66, head=-30, fs=60, fe=20, bs=40, be=10, fh=60, fk=-70, bh=-36, bk=-4, jaw=5),
    "chomp": Pose(x=-28, lean=68, head=-28, fs=56, fe=24, bs=38, be=12, fh=60, fk=-70, bh=-36, bk=-4, jaw=0),
    # dodge
    "reel": Pose(x=8, lean=0, head=10, fs=-20, fe=60, bs=-50, be=40, fh=10, fk=-14, bh=-24, bk=-12, jaw=1),
}
NUMERIC = ("x", "y", "lean", "head", "jaw", "fs", "fe", "bs", "be", "fh", "fk", "bh", "bk")
TWEENS = []


def tween(a, b, t):
    pa, pb = POSES[a], POSES[b]
    out = Pose(pb if t >= 0.5 else pa)
    for k in NUMERIC:
        out[k] = getattr(pa, k) + (getattr(pb, k) - getattr(pa, k)) * t
    return out


def draw_pose(p):
    s = Scene()
    draw_titan(s, p)
    return render(s, PAL)


def frames():
    out = {name: draw_pose(p) for name, p in POSES.items()}
    for name in TWEENS:
        a, b, t = name.split("~")
        out[name] = draw_pose(tween(a, b, float(t)))
    out["blank"] = out["idle"] * 0
    return out


def F(name, d):
    return ("f", name, d)


def T(a, b, t, d):
    name = "%s~%s~%.2f" % (a, b, t)
    if name not in TWEENS:
        TWEENS.append(name)
    return ("f", name, d)


def C(n):
    return ("c", n)


NORMAL = [C(0x03), C(0x07), F("idle", 1), T("idle", "rear", 0.5, 4), F("rear", 8), C(0x43), T("rear", "step", 0.5, 3),
          F("step", 3), T("step", "snatch", 0.5, 2), C(0x24), C(0x04), F("snatch", 2), C(0x1A), C(0x1F), F("grab", 6),
          C(0x01), F("pull", 5), T("pull", "idle", 0.5, 4), C(0x06), F("idle", 2), C(0x0D)]
MISS = [t for t in NORMAL if t not in (C(0x1A), C(0x1F))]
CRIT = [C(0x03), C(0x07), F("idle", 1), T("idle", "gape", 0.5, 4), F("gape", 10), C(0x34), C(0x1B),
        T("gape", "lunge", 0.5, 3), C(0x24), C(0x04), F("lunge", 2), C(0x09), C(0x1F), F("chomp", 8), C(0x01),
        T("chomp", "idle", 0.5, 5), C(0x06), F("idle", 2), C(0x0D)]
RANGED = [C(0x03), C(0x07), F("idle", 1), F("idle", 2), C(0x05), F("idle", 2), C(0x01), C(0x06), F("idle", 1),
          C(0x0D)]
DODGE = [C(0x02), F("idle", 1), C(0x0E), T("idle", "reel", 0.5, 2), F("reel", 4), F("reel", 1), C(0x01),
         T("reel", "idle", 0.5, 3), F("idle", 2), C(0x0D)]
STAND = [F("idle", 1), C(0x01)]


def back(mode):
    return [("f", "blank", t[2]) if t[0] == "f" else t for t in mode]


MODES = [NORMAL, back(NORMAL), CRIT, back(CRIT), RANGED, RANGED, DODGE, DODGE, STAND, STAND, STAND, MISS]
