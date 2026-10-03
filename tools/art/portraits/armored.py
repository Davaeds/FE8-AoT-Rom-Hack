"""The Armored Titan: pale, cracked armour plates over a muscled head, long
blond hair falling behind, blank glowing eyes, and a jaw of armoured ridges."""
from face import eye, clump
from pkit import ellipse

PALETTE = {
    "line":   (36, 26, 24),
    "skinx":  (36, 26, 24),
    "plate":  (230, 222, 196),
    "plated": (170, 160, 136),
    "platel": (252, 250, 236),
    "seam":   (126, 50, 44),
    "red":    (178, 72, 58),
    "hair":   (222, 186, 108),
    "haird":  (156, 116, 58),
    "hairl":  (248, 228, 164),
    "white":  (250, 250, 236),
    "iris":   (236, 240, 230),
    "irisd":  (190, 206, 210),
    "gum":    (70, 20, 22),
}

MOUTH = (4, 6)
EYES = (4, 4)
MINI = (0.58, 48, 36)

HAIR = [((32, 14), (20, 66), 12, 2.0), ((28, 24), (16, 58), 10, 1.0), ((66, 14), (78, 64), 12, -2.0),
        ((70, 24), (82, 56), 10, -1.0), ((38, 8), (24, 40), 10, 2.0), ((60, 8), (74, 40), 10, -2.0)]


def build(s, mouth="closed", eyes="open"):
    hl = dict(group="hair", line="line")
    s.fill("hair", ellipse(49, 26, 26, 23), **hl, raw=True)
    for root, tip, w, bend in HAIR:
        s.fill("hair", clump(root, tip, w, bend, taper=0.7), **hl)
    s.fill("haird", [(14, 66), (24, 34), (49, 26), (74, 34), (84, 66)], group="hair", clip="hair")
    for a, b in [((30, 20), (22, 50)), ((66, 20), (76, 50)), ((40, 9), (30, 30)), ((58, 9), (68, 30))]:
        s.stroke("hairl", [a, b], w=0.9, clip="hair", thr=0.45)
    # armoured neck and shoulders
    s.fill("red", [(10, 80, 1), (20, 66), (36, 60), (62, 60), (78, 66), (88, 80, 1)], group="body", line="line")
    s.fill("plate", [(10, 80, 1), (18, 68), (32, 64), (36, 80, 1)], group="body", clip="body")
    s.fill("plate", [(88, 80, 1), (80, 68), (66, 64), (62, 80, 1)], group="body", clip="body")
    s.fill("plate", [(40, 62), (58, 62), (56, 80, 1), (42, 80, 1)], group="body", clip="body")
    for pts in ([(32, 64), (36, 80)], [(66, 64), (62, 80)], [(40, 62), (42, 80)], [(58, 62), (56, 80)],
                [(18, 72), (33, 70)], [(80, 72), (65, 70)]):
        s.stroke("seam", pts, w=1.0, clip="body", thr=0.4)
    s.fill("plated", [(80, 68), (88, 80, 1), (74, 80, 1), (70, 70)], group="body", clip="body")
    # head
    head = [(30, 26), (29, 38), (31, 48), (35, 57), (41, 64), (49, 66), (57, 64), (63, 57), (67, 48), (69, 38),
            (68, 26), (63, 13), (49, 8), (35, 13)]
    s.fill("red", head, group="head", line="line")
    # plates: brow, two cheeks, nose ridge
    s.fill("plate", [(31, 22), (40, 12), (49, 10), (58, 12), (67, 22), (66, 31), (57, 29), (50, 31), (48, 31),
                     (41, 29), (32, 31)], group="head", clip="head")
    s.fill("plate", [(30, 38), (40, 40), (43, 47), (40, 54), (34, 54), (30.5, 46)], group="head", clip="head")
    s.fill("plate", [(68, 38), (58, 40), (55, 47), (58, 54), (64, 54), (67.5, 46)], group="head", clip="head")
    s.fill("plate", [(46, 31), (52, 31), (52.5, 45), (49, 47), (45.5, 45)], group="head", clip="head")
    s.fill("plated", [(58, 12), (67, 22), (66, 31), (60, 29), (62, 20)], group="head", clip="head")
    s.fill("plated", [(68, 38), (67.5, 46), (64, 54), (61, 52), (64, 42)], group="head", clip="head")
    s.fill("platel", [(38, 15), (46, 11.5), (48, 13.5), (40, 17.5)], group="head", clip="head")
    # cracks along the plate edges
    for pts in ([(36, 20), (38, 24), (37, 28)], [(60, 18), (59, 23)], [(34, 44), (37, 48)], [(64, 44), (61, 48)]):
        s.stroke("plated", pts, w=0.7, clip="head", thr=0.45)
    # sockets and blank eyes
    s.fill("line", ellipse(39.5, 35, 6.5, 3.8), group="head", clip="head", raw=True)
    s.fill("line", ellipse(58.5, 35, 6.5, 3.8), group="head", clip="head", raw=True)
    eye(s, 0, 39.5, 35.4, 8.6, 4.4, -1, eyes, look=0, tilt=-1.2, lid=1.0, lower=0.0, iris_w=0.12, flick=0)
    eye(s, 1, 58.5, 35.4, 8.6, 4.4, +1, eyes, look=0, tilt=-1.2, lid=1.0, lower=0.0, iris_w=0.12, flick=0)
    jaw(s, mouth)


def jaw(s, state):
    """Armoured ridges in place of lips; they part for speech."""
    gap = {"open": 3.0, "half": 1.5, "smile_open": 3.0, "smile_half": 1.5}.get(state, 0.0)
    s.fill("gum", [(39, 52), (59, 52), (58, 60 + gap), (40, 60 + gap)], group="jaw", line="line")
    s.fill("plate", [(39.5, 52.5), (58.5, 52.5), (58, 56), (40, 56)], group="jaw", clip="jaw")
    s.fill("plate", [(40.5, 56.5 + gap), (57.5, 56.5 + gap), (57, 60 + gap), (41, 60 + gap)], group="jaw", clip="jaw")
    for x in range(42, 58, 2):
        s.stroke("plated", [(x, 52.6), (x, 55.8)], w=0.6, clip="jaw", thr=0.5)
        s.stroke("plated", [(x + 1, 56.6 + gap), (x + 1, 59.8 + gap)], w=0.6, clip="jaw", thr=0.5)
    s.fill("plate", [(43, 61 + gap), (55, 61 + gap), (53, 65), (45, 65)], group="chin", line="line")
