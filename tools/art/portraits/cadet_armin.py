"""Armin Arlert as a 104th cadet, age 15 (year 850): blond bob to the jaw with a
straight fringe, big blue eyes, soft round face, Training Corps uniform."""
from face import eye, brow, mouth as draw_mouth, clump
from pkit import ellipse
from body import neck, cadet

PALETTE = {
    "line":   (40, 30, 26),
    "skin":   (252, 226, 200),
    "skind":  (232, 182, 152),
    "skinx":  (176, 112, 96),
    "white":  (248, 248, 240),
    "hair":   (236, 204, 112),
    "haird":  (186, 140, 64),
    "hairl":  (252, 240, 176),
    "iris":   (70, 140, 214),
    "irisd":  (28, 64, 132),
    "jacket": (176, 136, 92),
    "jacketd": (122, 88, 60),
    "strap":  (62, 42, 34),
    "shirtd": (196, 190, 178),
    "mouth":  (150, 64, 60),
}

MOUTH = (4, 6)
EYES = (4, 4)

# bob: root, tip, width, bend
SIDES = [((34, 14), (27, 56), 11, 1.5), ((30, 22), (24, 52), 10, 1.0), ((62, 14), (70, 55), 11, -1.5),
         ((66, 22), (73, 51), 10, -1.0)]
FRINGE = [((33, 14), (31.5, 33), 7, 0.6), ((38, 12), (37, 34.5), 7, 0.3), ((43, 12), (43, 35), 7, 0),
          ((48, 12), (48, 36), 6, 0), ((53, 12), (53.5, 34.5), 7, -0.2), ((58, 13), (59.5, 33.5), 7, -0.4),
          ((63, 15), (65, 32), 7, -0.6)]


def build(s, mouth="closed", eyes="open"):
    hl = dict(group="hair", line="line")
    s.fill("hair", ellipse(48.5, 27, 23, 22), **hl, raw=True)
    for root, tip, w, bend in SIDES:
        s.fill("hair", clump(root, tip, w, bend, taper=0.7), **hl)
    s.fill("haird", [(18, 60), (26, 34), (48, 26), (70, 34), (80, 60)], group="hair", clip="hair")
    neck(s, 43, 55, 52)
    cadet(s, dy=4)
    # rounder, softer face
    face = [(33, 27), (32.5, 37), (34.5, 46), (39, 53), (44, 57), (47, 58), (51, 57), (56.5, 52),
            (60.5, 46), (63, 39), (63, 30), (60, 21), (48, 17), (37, 20)]
    s.fill("skin", face, group="skin", line="skinx")
    s.fill("skind", [(58.5, 32), (63, 30), (63, 39), (60.5, 46), (56.5, 52), (52, 55.5), (56.5, 47), (58.5, 40)],
           group="skin", clip="skin")
    for root, tip, w, bend in FRINGE:
        s.fill("skind", clump((root[0], root[1] + 2.5), (tip[0] + 0.6, tip[1] + 2.0), w, bend), group="skin", clip="skin")
    # big, round, worried eyes
    eye(s, 0, 39.0, 41.0, 8.4, 6.8, -1, eyes, look=-0.8, tilt=0.4, lid=1.5, lower=0.5)
    eye(s, 1, 53.5, 41.0, 10.4, 7.2, +1, eyes, look=-1.2, tilt=0.5, lid=1.6, lower=0.5)
    s.stroke("skind", [(43.8, 46.0), (42.8, 48.4), (44.0, 48.8)], w=0.8, thr=0.45)
    draw_mouth(s, 45.5, 53.0, mouth, w=3.6, frown=-0.1)
    for root, tip, w, bend in FRINGE:
        s.fill("hair", clump(root, tip, w, bend), **hl)
    s.fill("hair", clump((34, 20), (31, 50), 7, 0.8), **hl)
    s.fill("hair", clump((62, 20), (66, 49), 7, -0.8), **hl)
    s.fill("hairl", [(30, 17), (36, 11), (46, 8), (56, 9), (65, 14), (62, 15), (55, 12), (46, 11.5), (37, 14),
                     (32, 19, 1)], group="hair", clip="hair")
    for a, b in [((40, 18), (39, 31)), ((51, 18), (52, 31)), ((60, 19), (62, 30)), ((28, 34), (26, 48)),
                 ((70, 34), (72, 47)), ((33, 26), (32, 44)), ((64, 26), (66, 42))]:
        s.stroke("haird", [a, b], w=0.9, clip="hair", thr=0.45)
    # soft raised brows
    brow(s, [(35, 34.2), (39, 33.2), (42.5, 33.6)], w=1.1, key="haird")
    brow(s, [(49, 33.6), (53.5, 33.0), (58, 33.8)], w=1.2, key="haird")
