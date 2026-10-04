"""Battle animation: 104th cadet with ODM gear and twin blades.

Normal attack: grapple in, spin-slash, kick back off the target.
Critical: grapple high over the Titan, swing round behind it and cut the nape.
Dodge: reel back on the wire with a burst of gas.
"""
import rig
from rig import Pose, Scene, draw_cadet, puff, slash, render

ABBR = "aot_cadet"
SLOT = 0
PAL = {
    "line": (32, 24, 24), "skin": (248, 208, 168), "hair": (84, 56, 42), "haird": (48, 32, 28),
    "jacket": (184, 140, 92), "jacketd": (128, 92, 60), "white": (240, 240, 232), "whited": (176, 176, 184),
    "brown": (88, 56, 40), "metal": (208, 216, 224), "metald": (104, 112, 128), "glow": (176, 232, 255),
    "red": (208, 32, 40), "gas": (236, 236, 236), "gasd": (172, 172, 180),
}
PALETTE = list(PAL.values())

# The target (left combatant) stands at x = 92; its head is around y = 56.
WIRE_HIGH = (60, 6)
WIRE_LOW = (88, 40)

POSES = {
    "idle": Pose(),
    "crouch": Pose(y=5, lean=30, fh=55, fk=-95, bh=-5, bk=-70, fs=-30, fe=20, fb=-120, bs=-50, be=30, bb=-150),
    "launch": Pose(x=-12, y=-14, lean=45, fh=70, fk=-120, bh=20, bk=-100, fs=-60, fe=10, fb=-100,
                   bs=-80, be=10, bb=-110, wire=[WIRE_LOW]),
    "zip": Pose(x=-30, y=-20, lean=65, fh=-30, fk=-20, bh=-50, bk=-30, fs=-150, fe=-20, fb=-170,
                bs=-120, be=10, bb=-150, wire=[WIRE_LOW]),
    "slash_a": Pose(x=-40, y=-16, lean=40, fh=40, fk=-60, bh=-20, bk=-60, fs=150, fe=20, fb=170,
                    bs=120, be=20, bb=150),
    "slash_b": Pose(x=-44, y=-14, lean=35, fh=50, fk=-70, bh=-10, bk=-50, fs=70, fe=10, fb=40,
                    bs=95, be=0, bb=70),
    "recoil": Pose(x=-24, y=-16, lean=-5, fh=60, fk=-20, bh=30, bk=-30, fs=110, fe=0, fb=130,
                   bs=-60, be=10, bb=-90),
    "land": Pose(x=-4, y=4, lean=25, fh=50, fk=-85, bh=-8, bk=-60, fs=60, fe=30, fb=110, bs=-30, be=30, bb=-140),
    # critical
    "glint": Pose(y=6, lean=34, fh=58, fk=-100, bh=-5, bk=-75, fs=-40, fe=15, fb=-110, bs=-60, be=25, bb=-150),
    "rise": Pose(x=-10, y=-34, lean=20, fh=40, fk=-110, bh=10, bk=-90, fs=170, fe=0, fb=175, bs=-90, be=0,
                 bb=-120, wire=[WIRE_HIGH]),
    "over": Pose(x=-52, y=-58, lean=85, fh=-40, fk=-30, bh=-60, bk=-20, fs=-160, fe=-10, fb=-170,
                 bs=-130, be=0, bb=-160, wire=[WIRE_HIGH]),
    # behind the Titan, turned round to face its nape (drawn facing right)
    "behind": Pose(x=-100, y=-40, lean=30, fh=60, fk=-100, bh=10, bk=-90, fs=-150, fe=-20, fb=-175,
                   bs=-120, be=0, bb=-150, flip=True),
    "nape_a": Pose(x=-96, y=-38, lean=45, fh=45, fk=-70, bh=-10, bk=-60, fs=100, fe=10, fb=100,
                   bs=120, be=0, bb=110, flip=True),
    "nape_b": Pose(x=-94, y=-36, lean=40, fh=50, fk=-80, bh=-10, bk=-60, fs=40, fe=10, fb=20,
                   bs=60, be=0, bb=40, flip=True),
    # after the cut: yanked up and back over the Titan's head on the wire
    "away": Pose(x=-92, y=-46, lean=-25, fh=50, fk=-70, bh=15, bk=-60, fs=150, fe=0, fb=160,
                 bs=-100, be=0, bb=-140, flip=True, wire=[(200, 8)]),
    "arc": Pose(x=-24, y=-46, lean=-20, fh=60, fk=-90, bh=20, bk=-80, fs=120, fe=10, fb=150,
                bs=-90, be=0, bb=-130, wire=[(220, 4)]),
    # dodge
    "hop": Pose(x=10, y=-8, lean=-10, fh=40, fk=-60, bh=-20, bk=-40, fs=80, fe=20, fb=120, bs=-60, be=20, bb=-120),
    "hop2": Pose(x=16, y=-3, lean=0, fh=35, fk=-50, bh=-15, bk=-40, fs=70, fe=25, fb=115, bs=-50, be=25, bb=-130),
}


FX = {
    "launch": [("puff", 168, 82, 4), ("puff", 175, 86, 3)],
    "zip": [("puff", 140, 66, 4), ("puff", 150, 70, 3), ("puff", 158, 73, 2)],
    "slash_a": [("slash", 106, 64, 16, 175, 120)],
    "glint": [("star", 118, 78)],
    "rise": [("puff", 160, 64, 4), ("puff", 168, 70, 3)],
    "over": [("puff", 128, 34, 4), ("puff", 138, 38, 3), ("puff", 146, 42, 2)],
    "hop": [("puff", 150, 82, 4), ("puff", 158, 86, 3)],
}
# extra frames: (name, base pose, effects)
EXTRA = [
    ("slash_b_fx", "slash_b", [("slash", 106, 64, 17, 175, 20, 2.2)]),
    ("slash_c_fx", "slash_b", [("slash", 106, 64, 18, 120, 10, 1.4)]),
    ("nape_b_fx", "nape_b", [("slash", 62, 48, 14, -170, -20, 2.4)]),
    ("nape_c_fx", "nape_b", [("slash", 62, 48, 13, -150, -40, 1.2), ("blood", 86, 36, 0)]),
    ("nape_d_fx", "away", [("blood", 82, 42, 0.8), ("steam", 82, 40, 0.6)]),
    ("nape_e_fx", "arc", [("steam", 82, 38, 1.2)]),
]
NUMERIC = ("x", "y", "lean", "head", "fs", "fe", "bs", "be", "fb", "bb", "fh", "fk", "bh", "bk")


def tween(a, b, t):
    """Pose between two key poses (t = 0..1); flags and wires come from the nearer one."""
    pa, pb = POSES[a], POSES[b]
    out = Pose(pb if t >= 0.5 else pa)
    for k in NUMERIC:
        va, vb = getattr(pa, k), getattr(pb, k)
        out[k] = va + (vb - va) * t
    return out


def fx(base, items):
    """Draw effects into a copy of a frame (effects go on top)."""
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
    top = render(s, PAL)
    out = base.copy()
    out[top > 0] = top[top > 0]
    return out


def draw_pose(p, effects=()):
    s = Scene()
    j = draw_cadet(s, p)
    im = render(s, PAL, flip_x=j["hip"][0] if p.get("flip") else None)
    return fx(im, effects) if effects else im


def frames():
    out = {}
    for name, p in POSES.items():
        out[name] = draw_pose(p)
        if name in FX:
            out[name + "_fx"] = draw_pose(p, FX[name])
    for name, base, effects in EXTRA:
        out[name] = draw_pose(POSES[base], effects)
    for name in TWEENS:
        a, b, t = name.split("~")
        out[name] = draw_pose(tween(a, b, float(t)))
    out["blank"] = out["idle"] * 0
    return out


TWEENS = []


def T(a, b, t, d):
    """Frame token for an in-between pose."""
    name = "%s~%s~%.2f" % (a, b, t)
    if name not in TWEENS:
        TWEENS.append(name)
    return ("f", name, d)


def F(name, d):
    return ("f", name, d)


def C(n):
    return ("c", n)


NORMAL = [C(0x03), C(0x07), F("idle", 1), T("idle", "crouch", 0.5, 2), F("crouch", 4), C(0x43),
          F("launch_fx", 2), T("launch", "zip", 0.5, 2), F("zip_fx", 2), T("zip", "slash_a", 0.5, 2),
          F("slash_a_fx", 2), C(0x24), C(0x04), F("slash_b_fx", 2), C(0x1A), C(0x1F), F("slash_c_fx", 3),
          F("slash_b", 2), T("slash_b", "recoil", 0.5, 2), F("recoil", 3), C(0x01), T("recoil", "land", 0.5, 3),
          F("land", 4), C(0x06), T("land", "idle", 0.5, 3), C(0x34), F("idle", 2), F("idle", 1), C(0x0D)]
MISS = [t for t in NORMAL if t not in (C(0x1A), C(0x1F))]
CRIT = [C(0x03), C(0x07), F("idle", 1), T("idle", "glint", 0.5, 2), F("glint", 3), C(0x34), F("glint_fx", 8),
        C(0x1B), T("glint", "rise", 0.5, 2), F("rise_fx", 3), T("rise", "over", 0.5, 3), F("over_fx", 4),
        C(0x43), F("behind", 4), F("nape_a", 3), C(0x24), C(0x04), F("nape_b_fx", 2), C(0x09), C(0x1F),
        F("nape_c_fx", 4), F("nape_d_fx", 5), C(0x01), F("nape_e_fx", 3), T("arc", "land", 0.5, 3), F("land", 5), C(0x06),
        T("land", "idle", 0.5, 3), C(0x34), F("idle", 2), F("idle", 1), C(0x0D)]
RANGED = [C(0x03), C(0x07), F("idle", 1), F("idle", 2), F("idle", 2), C(0x05), F("idle", 2), C(0x01), C(0x06),
          F("idle", 2), F("idle", 1), C(0x0D)]
DODGE = [C(0x02), F("idle", 1), C(0x0E), F("hop_fx", 3), F("hop2", 3), F("hop2", 1), C(0x01),
         T("hop2", "idle", 0.5, 2), F("idle", 2), C(0x0D)]
STAND = [F("idle", 1), C(0x01)]


def back(mode):
    return [("f", "blank", t[2]) if t[0] == "f" else t for t in mode]


MODES = [NORMAL, back(NORMAL), CRIT, back(CRIT), RANGED, RANGED, DODGE, DODGE, STAND, STAND, STAND, MISS]
