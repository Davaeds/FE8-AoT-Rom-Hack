"""The Smiling Titan, which ate Carla Yeager: chin-length blond hair parted in
the middle, round staring eyes with tiny pupils, plump cheeks, and a huge
closed-lip grin stretched nearly ear to ear."""
from face import eye, clump
from pkit import ellipse

PALETTE = {
    "line":   (44, 30, 26),
    "skin":   (246, 212, 176),
    "skind":  (218, 164, 128),
    "skinx":  (156, 98, 80),
    "white":  (252, 250, 240),
    "hair":   (226, 190, 110),
    "haird":  (164, 124, 64),
    "hairl":  (250, 232, 170),
    "iris":   (120, 92, 70),
    "irisd":  (60, 44, 34),
    "lip":    (196, 112, 98),
    "teeth":  (246, 240, 222),
    "gum":    (96, 30, 30),
}

MOUTH = (4, 6)
EYES = (4, 4)
MINI = (0.58, 48, 37)

HAIR = [((38, 10), (25, 50), 11, 2.5), ((45, 9), (33, 24), 9, 1.5), ((58, 10), (71, 50), 11, -2.5),
        ((51, 9), (63, 24), 9, -1.5)]


def build(s, mouth="closed", eyes="open"):
    hl = dict(group="hair", line="line")
    s.fill("hair", ellipse(48, 25, 24, 20), **hl, raw=True)
    # bare shoulders
    s.fill("skin", [(6, 80, 1), (14, 68), (34, 62), (62, 62), (82, 68), (90, 80, 1)], group="body", line="skinx")
    s.fill("skind", [(62, 62), (82, 68), (90, 80, 1), (70, 80, 1), (66, 70)], group="body", clip="body")
    s.stroke("skinx", [(30, 72), (38, 76), (44, 74)], w=0.7, thr=0.5)
    s.stroke("skinx", [(66, 72), (58, 76), (52, 74)], w=0.7, thr=0.5)
    # wide, plump face
    face = [(26, 30), (25, 40), (27, 50), (32, 58), (40, 64), (48, 66), (56, 64), (64, 58), (69, 50),
            (71, 40), (70, 30), (64, 19), (48, 14), (32, 19)]
    s.fill("skin", face, group="skin", line="skinx")
    s.fill("skind", [(64, 30), (70, 30), (71, 40), (69, 50), (64, 58), (58, 62), (64, 50), (66, 40)],
           group="skin", clip="skin")
    s.fill("skind", ellipse(33, 48, 4, 2.5), group="skin", clip="skin", raw=True)
    s.fill("skind", ellipse(63, 48, 4, 2.5), group="skin", clip="skin", raw=True)
    # round staring eyes, pupils pinned
    eye(s, 0, 38, 37, 8.5, 7.0, -1, eyes, look=0.4, tilt=0.6, lid=1.0, lower=0.9, iris_w=0.16, flick=0)
    eye(s, 1, 58, 37, 8.5, 7.0, +1, eyes, look=-0.4, tilt=0.6, lid=1.0, lower=0.9, iris_w=0.16, flick=0)
    s.stroke("line", [(33, 31), (38, 30), (43, 31.5)], w=0.8, thr=0.45)
    s.stroke("line", [(53, 31.5), (58, 30), (63, 31)], w=0.8, thr=0.45)
    # nose
    s.stroke("skinx", [(48, 40), (46.5, 46), (49.5, 46.6)], w=0.8, thr=0.45)
    grin(s, mouth)
    for root, tip, w, bend in HAIR:
        s.fill("hair", clump(root, tip, w, bend, taper=0.6), **hl)
    s.fill("hairl", [(34, 14), (42, 9), (47, 8), (40, 13), (36, 18)], group="hair", clip="hair")
    s.fill("hairl", [(54, 9), (62, 12), (66, 17), (60, 14)], group="hair", clip="hair")
    for a, b in [((40, 14), (31, 40)), ((56, 14), (65, 40))]:
        s.stroke("haird", [a, b], w=0.9, clip="hair", thr=0.45)


def grin(s, state):
    """A closed grin stretched almost to the ears; speech frames bare the teeth."""
    gap = {"open": 3.5, "half": 1.8, "smile_open": 3.5, "smile_half": 1.8, "closed_talk": 0.8}.get(state, 0.0)
    top = [(30, 49), (38, 53), (48, 54.5), (58, 53), (66, 49)]
    if gap:
        bot = [(x, y + gap * (1 - abs(x - 48) / 22)) for x, y in top]
        s.fill("teeth", top + bot[::-1], group="grin", line="line")
        for x in range(36, 62, 3):
            s.stroke("skind", [(x, 53 - abs(x - 48) * 0.1), (x, 53.5 + gap * 0.5)], w=0.6, clip="grin", thr=0.5)
    s.fill("lip", [(31, 49.5), (38, 52.6), (48, 53.6), (58, 52.6), (65, 49.5), (58, 51.8), (48, 52.6), (38, 51.8)],
           group="lip", outline=False)
    s.stroke("line", top, w=1.2)
    s.stroke("lip", [(36, 56.5 + gap), (48, 58 + gap), (60, 56.5 + gap)], w=1.0, thr=0.45)
    s.stroke("skinx", [(28.5, 47), (30, 49), (29.5, 51)], w=0.8, thr=0.45)
    s.stroke("skinx", [(67.5, 47), (66, 49), (66.5, 51)], w=0.8, thr=0.45)
