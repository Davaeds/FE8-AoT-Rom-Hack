"""The Colossal Titan: a skinless head of red, striated muscle, a full row of
bare teeth from cheek to cheek, small pale eyes sunk under a heavy brow, and
steam pouring off it."""
from face import eye
from pkit import ellipse

PALETTE = {
    "line":   (40, 10, 14),
    "skinx":  (40, 10, 14),
    "red":    (184, 52, 44),
    "redd":   (118, 26, 30),
    "redl":   (226, 106, 84),
    "sinew":  (238, 196, 168),
    "teeth":  (242, 232, 208),
    "teethd": (184, 166, 140),
    "white":  (252, 244, 226),
    "iris":   (226, 214, 190),
    "irisd":  (150, 136, 116),
    "steam":  (236, 236, 232),
    "steamd": (184, 184, 182),
    "gum":    (82, 16, 22),
}

MOUTH = (4, 6)
EYES = (4, 4)
MINI = (0.55, 48, 36)


def build(s, mouth="closed", eyes="open"):
    # steam billowing up behind the head in two banks
    import math
    for side in (-1, 1):
        for i in range(9):
            y = 78 - i * 9
            x = 49 + side * (30 + 6 * math.sin(i * 1.7) + i * 1.2)
            r = 10 - i * 0.5
            s.fill("steam", ellipse(x, y, r, r * 0.85), group="steam", outline=False, raw=True)
            s.stroke("steamd", [(x - r * 0.7, y + r * 0.3), (x, y + r * 0.7), (x + r * 0.7, y + r * 0.3)], w=1.0,
                     clip="steam", thr=0.4)
    # neck and shoulder muscle
    s.fill("red", [(22, 80, 1), (30, 62), (40, 60), (58, 60), (68, 62), (78, 80, 1)], group="neck", line="line")
    for x0, x1 in [(30, 36), (40, 42), (56, 54), (66, 62)]:
        s.stroke("redd", [(x0, 64), (x1, 80)], w=1.1, clip="neck", thr=0.4)
    s.stroke("sinew", [(36, 62), (49, 68), (62, 62)], w=1.0, clip="neck", thr=0.4)
    # long head
    head = [(25, 28), (24, 38), (27, 45), (29, 54), (34, 63), (41, 68), (49, 70), (57, 68), (64, 63), (69, 54),
            (71, 45), (74, 38), (73, 28), (68, 13), (57, 5), (41, 5), (30, 13)]
    s.fill("red", head, group="head", line="line")
    s.fill("redd", [(62, 10), (72, 28), (72, 42), (69, 52), (64, 61), (60, 64), (63, 50), (65, 34), (62, 20)],
           group="head", clip="head")
    # striations: fibres over the skull and cheeks
    for a, b in [((38, 9), (34, 24)), ((44, 7), (42, 22)), ((50, 7), (50, 22)), ((56, 8), (58, 22)),
                 ((30, 34), (32, 52)), ((66, 34), (63, 52)), ((26, 30), (28, 40)), ((72, 30), (70, 40))]:
        s.stroke("redd", [a, b], w=0.9, clip="head", thr=0.4)
    for a, b in [((40, 10), (37, 22)), ((47, 8), (46, 21)), ((53, 9), (54, 21))]:
        s.stroke("redl", [a, b], w=0.8, clip="head", thr=0.45)
    # cheek tendons (no lips)
    s.stroke("sinew", [(28, 40), (30, 47), (33, 58)], w=1.2, clip="head", thr=0.4)
    s.stroke("sinew", [(70, 40), (68, 47), (65, 58)], w=1.2, clip="head", thr=0.4)
    # heavy brow ridge and deep sockets
    s.fill("redd", [(29, 30), (40, 25), (49, 28), (58, 25), (69, 30), (66, 34), (58, 30), (49, 32), (40, 30), (32, 34)],
           group="head", clip="head")
    s.fill("line", ellipse(39, 35, 6.5, 4.4), group="head", clip="head", raw=True)
    s.fill("line", ellipse(59, 35, 6.5, 4.4), group="head", clip="head", raw=True)
    eye(s, 0, 39, 35.5, 8.5, 5.0, -1, eyes, look=0, tilt=0.2, lid=0.8, lower=0.0, iris_w=0.22, flick=0)
    eye(s, 1, 59, 35.5, 8.5, 5.0, +1, eyes, look=0, tilt=0.2, lid=0.8, lower=0.0, iris_w=0.22, flick=0)
    # nose cavity
    s.fill("line", [(46, 40), (49, 37), (52, 40), (51, 45), (47, 45)], group="head", clip="head")
    s.stroke("redl", [(49, 37), (49, 44)], w=0.7, clip="head", thr=0.5)
    jaw(s, mouth)


def jaw(s, state):
    """Bare teeth from cheek to cheek in a fixed grimace; the jaw drops for speech."""
    gap = {"open": 4.0, "half": 2.0, "smile_open": 4.0, "smile_half": 2.0}.get(state, 0.0)
    up = [(30, 47), (38, 49.5), (49, 50.5), (60, 49.5), (68, 47)]
    lo = [(p[0], p[1] + 11 + gap - abs(p[0] - 49) * 0.12) for p in up]
    s.fill("gum", up + lo[::-1], group="jaw", line="line")
    s.fill("teeth", [(31, 48), (38, 50.3), (49, 51.3), (60, 50.3), (67, 48), (66.5, 53.5), (60, 55.3), (49, 56.2),
                     (38, 55.3), (31.5, 53.5)], group="jaw", clip="jaw")
    s.fill("teeth", [(32, 51 + 4.5 + gap), (38, 56.2 + gap), (49, 57 + gap), (60, 56.2 + gap), (66, 55.5 + gap),
                     (65, 60.5 + gap), (49, 61.5 + gap), (33, 60.5 + gap)], group="jaw", clip="jaw")
    for x in range(34, 66, 3):
        bow = abs(x - 49) * 0.18
        s.stroke("teethd", [(x, 49.5 + bow * 0.5), (x, 55.5 - bow * 0.2)], w=0.7, clip="jaw", thr=0.45)
        s.stroke("teethd", [(x + 1.5, 57 + gap - bow * 0.2), (x + 1.5, 61 + gap - bow * 0.3)], w=0.7, clip="jaw", thr=0.45)
