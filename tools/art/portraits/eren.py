"""Eren Yeager, age 10 (year 845): shaggy dark brown hair in pointed clumps,
big teal-green eyes under angry brows, off-white collarless shirt."""
from face import eye, brow, mouth, clump
from pkit import ellipse

PALETTE = {
    "line":   (34, 22, 24),
    "skin":   (250, 218, 186),
    "skind":  (228, 172, 140),
    "skinx":  (170, 104, 90),
    "white":  (248, 248, 240),
    "hair":   (96, 64, 46),
    "haird":  (58, 38, 32),
    "hairl":  (146, 106, 74),
    "iris":   (48, 170, 150),
    "irisd":  (20, 92, 88),
    "irisl":  (128, 220, 196),
    "cloth":  (238, 232, 214),
    "clothd": (194, 184, 164),
    "clothx": (138, 126, 112),
    "mouth":  (128, 48, 48),
}

MOUTH = (4, 6)
EYES = (4, 4)
CROWN = (52, 15)

# outer clumps: tip, root width, bend
BACK = [((25, 52), 12, 2.0), ((21, 42), 14, 1.5), ((20, 31), 16, 1.0), ((23, 19), 17, 0.5),
        ((31, 8), 17, 0), ((43, 1.5), 17, 0), ((56, 1), 17, 0), ((67, 5), 17, -0.5),
        ((75, 13), 16, -1), ((79, 25), 15, -1.5), ((78, 38), 13, -2), ((74, 49), 11, -2),
        ((70, 57), 9, -1.5)]
# bangs over the forehead: root, tip, width, bend
BANGS = [((31, 14), (28.5, 33), 7, 1.0), ((36, 13), (33.5, 33.5), 7, 0.8), ((41, 12), (39.5, 34.5), 8, 0.4),
         ((47, 12), (46.5, 37.5), 7, 0), ((52, 12), (52.5, 32.5), 7, -0.3), ((57, 13), (59, 31.5), 7, -0.6),
         ((62, 14), (65, 30), 7, -0.8), ((66, 16), (68.5, 32), 6, -1)]


def build(s, mouth="closed", eyes="open"):
    hl = dict(group="hair", line="line")
    # back hair
    s.fill("hair", ellipse(49.5, 26, 25, 23), **hl, raw=True)
    for tip, w, bend in BACK:
        root = (CROWN[0] + (tip[0] - CROWN[0]) * 0.25, CROWN[1] + (tip[1] - CROWN[1]) * 0.25)
        s.fill("hair", clump(root, tip, w, bend, taper=0.55), **hl)
    # cowlicks on top
    for root, tip, w, bend in [((44, 8), (38, -1), 6, 1.0), ((55, 7), (60, -1.5), 6, -1.0), ((63, 9), (71, 3), 5, -1.0)]:
        s.fill("hair", clump(root, tip, w, bend), **hl)
    s.fill("haird", [(16, 60), (24, 30), (34, 20), (48, 17), (62, 20), (74, 30), (84, 60), (84, 72), (16, 72)],
           group="hair", clip="hair")
    # neck and shirt
    s.fill("skin", [(42, 50), (56, 48), (59, 74), (41, 74)], group="neck", line="skinx")
    s.fill("skind", [(42, 50), (56, 48), (57.5, 57), (50, 59.5), (43, 58)], group="neck", clip="neck")
    s.fill("cloth", [(8, 80, 1), (12, 72), (23, 66), (38, 62, 1), (45, 67.5), (53, 66.5), (60, 60, 1),
                     (75, 64), (85, 71), (90, 80, 1)], group="shirt", line="clothx")
    s.fill("clothd", [(60, 60, 1), (75, 64), (85, 71), (90, 80, 1), (71, 80, 1), (69, 71), (63, 65)], group="shirt", clip="shirt")
    s.fill("clothd", [(8, 80, 1), (12, 72), (21, 68), (25, 74), (27, 80, 1)], group="shirt", clip="shirt")
    s.fill("clothd", [(38, 62, 1), (45, 67.5), (53, 66.5), (60, 60, 1), (54, 69), (45, 70)], group="shirt", clip="shirt")
    s.stroke("clothx", [(38, 62), (44.5, 68), (53, 67), (60, 60)], w=0.9, clip="shirt", thr=0.4)
    s.stroke("clothd", [(33, 70), (35, 76), (36, 80)], w=0.9, clip="shirt")
    s.stroke("clothd", [(47, 74), (49, 80)], w=0.9, clip="shirt")
    s.stroke("clothx", [(68, 70), (66, 80)], w=0.9, clip="shirt", thr=0.45)
    # ear
    s.fill("skin", [(62, 35), (66, 33), (68.5, 38), (67, 45), (63, 47)], group="ear", line="skinx")
    s.fill("skind", [(64, 36), (66.5, 37), (66, 43), (64, 44)], group="ear", clip="ear")
    # face
    face = [(33, 27), (32, 35), (33, 43), (36, 49), (41, 55), (45, 57.5), (49, 57), (55, 53),
            (60, 47), (63, 40), (63.5, 30), (60, 21), (48, 17), (37, 20)]
    s.fill("skin", face, group="skin", line="skinx")
    s.fill("skind", [(57.5, 32), (63.5, 30), (63, 40), (60, 47), (55, 53), (51, 55.5), (55.5, 47), (57.5, 40)],
           group="skin", clip="skin")
    # shadow cast by the bangs
    for root, tip, w, bend in BANGS:
        s.fill("skind", clump((root[0], root[1] + 2.5), (tip[0] + 0.8, tip[1] + 2.2), w, bend), group="skin", clip="skin")
    # eyes
    eye(s, 0, 39.0, 40.0, 8.0, 7.0, -1, eyes, look=-1.0, tilt=-0.8, lid=1.8, irisl="irisl")
    eye(s, 1, 53.5, 40.0, 10.0, 7.5, +1, eyes, look=-1.4, tilt=-1.1, lid=1.9, irisl="irisl")
    # nose and mouth
    s.stroke("skind", [(43.4, 44.8), (42.1, 47.4), (44.0, 47.9)], w=0.9, thr=0.4)
    s.dot("skinx", 42, 47)
    mouth_(s, mouth)
    # bangs
    for root, tip, w, bend in BANGS:
        s.fill("hair", clump(root, tip, w, bend), **hl)
    for root, tip, w, bend in BANGS[::3]:
        s.fill("haird", clump((root[0] + w * 0.25, root[1] + 6), (tip[0] + 0.1, tip[1] - 0.8), w * 0.35, bend),
               group="hair", clip="hair")
    # sheen ring around the crown
    s.fill("hairl", [(28, 19), (33, 12), (42, 8), (52, 7), (62, 9), (70, 15), (67, 15.5), (60, 11.5), (52, 10),
                     (43, 11), (35, 14.5), (30, 20, 1)], group="hair", clip="hair")
    for x in (38, 49, 60):
        s.stroke("hair", [(x, 6), (x - 1.5, 13)], w=1.0, clip="hair", thr=0.4)
    # strands
    for a, b in [((26, 24), (24, 33)), ((30, 10), (28, 16)), ((70, 20), (73, 30)), ((60, 4), (58, 9))]:
        s.stroke("haird", [a, b], w=0.9, clip="hair", thr=0.45)
    # angry brows drawn over the bangs
    brow(s, [(34.5, 34.0), (38.5, 34.4), (43, 36.6)], w=1.5)
    brow(s, [(48.5, 36.4), (53, 33.9), (58.5, 33.6)], w=1.6)
    s.stroke("skinx", [(45.4, 34.8), (45.7, 36.2)], w=0.7, thr=0.45)


def mouth_(s, m):
    mouth(s, 44.5, 52.2, m, w=4.6, frown=0.5)
