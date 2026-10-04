"""Battle animation: wooden Titan training dummy on a post. Its arm swings on
a pivot (the "attack"), and it rocks when it dodges. The nape is a padded
target block, marked red."""
import rig
from rig import Scene, capsule, ellipse, render, vec, add

ABBR = "aot_dummy"
SLOT = 1
PAL = {
    "line": (40, 26, 20), "wood": (176, 124, 72), "woodd": (120, 80, 48), "woodl": (216, 168, 112),
    "rope": (216, 196, 128), "post": (96, 64, 40), "paint": (236, 232, 216), "red": (184, 40, 40),
    "metal": (150, 150, 160),
}
PALETTE = list(PAL.values())


def draw(s, arm=30.0, rock=0.0, crack=False):
    gx, gy = 150 + rock * 0.3, 104
    # post and base
    s.fill("post", capsule((gx - 1, gy - 2), (gx + rock * 0.2, gy - 34), 5, 4), group="post", raw=True)
    s.fill("post", [(gx - 10, gy), (gx + 9, gy), (gx + 6, gy - 4), (gx - 7, gy - 4)], group="post", smooth=False)
    top = (gx + rock, gy - 34)
    # body: a barrel-shaped torso of planks
    body = [(top[0] - 9, top[1] + 4), (top[0] - 11, top[1] - 8), (top[0] - 8, top[1] - 20), (top[0] + 7, top[1] - 21),
            (top[0] + 11, top[1] - 8), (top[0] + 9, top[1] + 4)]
    s.fill("wood", body, group="body")
    s.fill("woodd", [(top[0] + 3, top[1] - 21), (top[0] + 7, top[1] - 21), (top[0] + 11, top[1] - 8),
                     (top[0] + 9, top[1] + 4), (top[0] + 4, top[1] + 4)], group="body", clip="body", smooth=False)
    for dx in (-5, 0):
        s.stroke("woodd", [(top[0] + dx, top[1] - 20), (top[0] + dx, top[1] + 3)], w=0.7, clip="body", thr=0.45)
    s.stroke("rope", [(top[0] - 11, top[1] - 6), (top[0] + 11, top[1] - 6)], w=1.4, clip="body", thr=0.4)
    # head with painted face, padded nape block behind it (right side)
    hc = (top[0] - 1, top[1] - 29)
    s.fill("red", [(hc[0] + 6, hc[1] - 2), (hc[0] + 11, hc[1] - 1), (hc[0] + 11, hc[1] + 6), (hc[0] + 6, hc[1] + 7)],
           group="nape", smooth=False)
    if crack:
        s.stroke("line", [(hc[0] + 7, hc[1] - 2), (hc[0] + 9, hc[1] + 3), (hc[0] + 8, hc[1] + 7)], w=0.8, clip="nape")
    s.fill("wood", ellipse(hc[0], hc[1], 8, 8.5), group="head", raw=True)
    s.fill("woodd", [(hc[0] + 3, hc[1] - 8), (hc[0] + 8, hc[1] - 2), (hc[0] + 7, hc[1] + 5), (hc[0] + 3, hc[1] + 8),
                     (hc[0] + 5, hc[1])], group="head", clip="head")
    s.fill("woodl", ellipse(hc[0] - 3, hc[1] - 4, 2.5, 1.6), group="head", clip="head", raw=True)
    s.fill("paint", ellipse(hc[0] - 5, hc[1] - 1, 1.6, 1.4), group="head", clip="head", raw=True)
    s.fill("paint", ellipse(hc[0] - 1, hc[1] - 1, 1.6, 1.4), group="head", clip="head", raw=True)
    s.dot("line", hc[0] - 5, hc[1] - 1, clip="head")
    s.dot("line", hc[0] - 1, hc[1] - 1, clip="head")
    s.stroke("line", [(hc[0] - 7, hc[1] + 4), (hc[0] - 4, hc[1] + 5), (hc[0] - 1, hc[1] + 4.5)], w=0.8, clip="head", thr=0.4)
    # swinging arm on a metal pivot at the shoulder
    sh = (top[0] - 6, top[1] - 16)
    el = add(sh, vec(arm, 10))
    hand = add(el, vec(arm + 20, 9))
    s.fill("wood", capsule(sh, el, 5, 4.4), group="arm", raw=True)
    s.fill("wood", capsule(el, hand, 4.4, 5.6), group="arm", raw=True)
    s.fill("woodd", ellipse(hand[0], hand[1], 3, 3), group="arm", clip="arm", raw=True)
    s.fill("metal", ellipse(sh[0], sh[1], 1.8, 1.8), group="pivot", raw=True)


def frame(**kw):
    s = Scene()
    draw(s, **kw)
    return render(s, PAL)


def frames():
    return {
        "idle": frame(),
        "wind": frame(arm=-40),
        "swing": frame(arm=90, rock=-2),
        "swing2": frame(arm=130, rock=-3),
        "rock_l": frame(rock=-3, arm=40),
        "rock_r": frame(rock=3, arm=20),
        "cracked": frame(crack=True),
        "blank": frame() * 0,
    }


def F(name, d):
    return ("f", name, d)


def C(n):
    return ("c", n)


NORMAL = [C(0x03), C(0x07), F("idle", 1), F("wind", 8), C(0x43), F("wind", 2), C(0x24), C(0x04), F("swing", 2),
          C(0x1A), C(0x1F), F("swing2", 4), C(0x01), F("swing", 4), F("idle", 4), C(0x06), F("idle", 2), C(0x0D)]
MISS = [t for t in NORMAL if t not in (C(0x1A), C(0x1F))]
CRIT = [t if t != C(0x1A) else C(0x09) for t in NORMAL]
RANGED = [C(0x03), C(0x07), F("idle", 1), C(0x05), F("idle", 2), C(0x01), C(0x06), F("idle", 1), C(0x0D)]
DODGE = [C(0x02), F("idle", 1), C(0x0E), F("rock_r", 3), F("rock_l", 3), F("rock_r", 1), C(0x01), F("idle", 2), C(0x0D)]
STAND = [F("idle", 1), C(0x01)]


def back(mode):
    return [("f", "blank", t[2]) if t[0] == "f" else t for t in mode]


MODES = [NORMAL, back(NORMAL), CRIT, back(CRIT), RANGED, RANGED, DODGE, DODGE, STAND, STAND, STAND, MISS]
