"""A common Titan: thin, scraggly brown hair, a bulbous nose, empty bug eyes
and a wide, lipless mouth full of teeth. Naked, man-shaped and wrong."""
from face import eye, clump
from pkit import ellipse

PALETTE = {
    "line":   (40, 28, 24),
    "skin":   (232, 190, 152),
    "skind":  (196, 146, 112),
    "skinx":  (140, 88, 70),
    "white":  (248, 244, 230),
    "hair":   (104, 76, 54),
    "haird":  (66, 46, 34),
    "iris":   (84, 70, 58),
    "irisd":  (44, 34, 28),
    "teeth":  (240, 230, 206),
    "teethd": (188, 170, 144),
    "gum":    (110, 40, 40),
}

MOUTH = (4, 6)
EYES = (4, 4)
MINI = (0.58, 48, 37)


def build(s, mouth="closed", eyes="open"):
    hl = dict(group="hair", line="line")
    s.fill("skin", [(4, 80, 1), (12, 66), (34, 60), (62, 60), (84, 66), (92, 80, 1)], group="body", line="skinx")
    s.fill("skind", [(62, 60), (84, 66), (92, 80, 1), (72, 80, 1), (66, 68)], group="body", clip="body")
    s.stroke("skinx", [(28, 70), (40, 74), (46, 72)], w=0.7, thr=0.5)
    # lumpy, wide head
    head = [(25, 28), (23, 40), (26, 52), (33, 61), (42, 66), (50, 67), (58, 65), (66, 59), (71, 50),
            (73, 38), (71, 26), (64, 14), (49, 9), (34, 13)]
    s.fill("skin", head, group="skin", line="skinx")
    s.fill("skind", [(64, 20), (71, 26), (73, 38), (71, 50), (66, 59), (60, 63), (66, 48), (68, 34)],
           group="skin", clip="skin")
    # scraggly hair on the crown
    for root, tip, w, bend in [((40, 12), (28, 26), 6, 1.5), ((48, 10), (40, 22), 6, 1.0), ((54, 10), (62, 22), 6, -1.0),
                               ((60, 12), (70, 26), 6, -1.5), ((34, 16), (25, 34), 5, 1.5), ((66, 16), (73, 32), 5, -1.5)]:
        s.fill("hair", clump(root, tip, w, bend, taper=0.5), **hl)
    s.fill("hair", ellipse(50, 12, 13, 4.5), **hl, raw=True)
    # bulging, vacant eyes
    s.fill("skind", ellipse(38, 35.5, 7.5, 5.2), group="skin", clip="skin", raw=True)
    s.fill("skind", ellipse(60, 35.5, 7.5, 5.2), group="skin", clip="skin", raw=True)
    eye(s, 0, 38, 36, 10, 7.0, -1, eyes, look=1.0, tilt=0.8, lid=1.1, lower=1.0, iris_w=0.15, flick=0)
    eye(s, 1, 60, 36, 10, 7.0, +1, eyes, look=-1.6, tilt=0.4, lid=1.1, lower=1.0, iris_w=0.15, flick=0)
    # big nose
    s.fill("skind", [(46, 36), (52, 36), (55, 46), (52, 48.5), (46, 48.5), (43, 46)], group="nose", line="skinx")
    s.dot("skinx", 46, 47)
    s.dot("skinx", 52, 47)
    teeth(s, mouth)


def teeth(s, state):
    gap = {"open": 3.5, "half": 1.8, "smile_open": 3.5, "smile_half": 1.8, "closed_talk": 0.8}.get(state, 0.0)
    up = [(31, 50), (40, 53.5), (49, 54.5), (58, 53.5), (67, 50)]
    lo = [(x, y + 5 + gap - abs(x - 49) * 0.08) for x, y in up]
    s.fill("gum", up + lo[::-1], group="mouth", line="line")
    s.fill("teeth", [(32, 50.4), (40, 53.8), (49, 54.8), (58, 53.8), (66, 50.4), (66, 52.2), (58, 55.8),
                     (49, 56.8), (40, 55.8), (32, 52.2)], group="mouth", clip="mouth")
    s.fill("teeth", [(33, 53.4 + gap), (49, 57.6 + gap), (65, 53.4 + gap), (65, 55.5 + gap), (49, 60 + gap),
                     (33, 55.5 + gap)], group="mouth", clip="mouth")
    for x in range(35, 65, 3):
        s.stroke("teethd", [(x, 50), (x, 61 + gap)], w=0.6, clip="mouth", thr=0.5)
