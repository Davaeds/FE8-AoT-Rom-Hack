"""Jean Kirstein as a 104th cadet, age 15: light ash-brown hair parted in the
middle over a dark shaved undercut, narrow amber eyes, long face with a smug
set to the mouth, Training Corps uniform."""
from face import eye, brow, mouth as draw_mouth, clump
from pkit import ellipse
from body import neck, cadet

PALETTE = {
    "line":   (36, 26, 24),
    "skin":   (250, 220, 190),
    "skind":  (228, 174, 142),
    "skinx":  (168, 104, 90),
    "white":  (248, 248, 240),
    "hair":   (184, 150, 108),
    "haird":  (96, 72, 56),
    "hairl":  (226, 200, 156),
    "iris":   (176, 128, 64),
    "irisd":  (96, 62, 34),
    "jacket": (176, 136, 92),
    "jacketd": (122, 88, 60),
    "strap":  (62, 42, 34),
    "shirtd": (196, 190, 178),
    "mouth":  (140, 56, 52),
}

MOUTH = (4, 6)
EYES = (4, 4)

# the long top layer, falling to both sides of a centre part: root, tip, width, bend
TOP = [((47, 6), (32, 25), 9, 2.4), ((47, 7), (37, 31), 9, 1.4), ((48, 8), (42.5, 33), 7, 0.6),
       ((50, 6), (65, 24), 9, -2.4), ((50, 7), (60, 30), 9, -1.4), ((49, 8), (54.5, 32), 7, -0.6)]


def build(s, mouth="closed", eyes="open"):
    hl = dict(group="hair", line="line")
    # shaved undercut: a close, dark cap
    s.fill("haird", ellipse(48.5, 28, 20, 19), group="hair", line="line", raw=True)
    neck(s, 42, 56, 54)
    cadet(s, dy=4, broad=1)
    # ear
    s.fill("skin", [(62, 35), (66, 33), (68.5, 38), (67, 46), (63, 48)], group="ear", line="skinx")
    s.fill("skind", [(64, 36), (66.5, 37), (66, 44), (64, 45)], group="ear", clip="ear")
    # long face, narrow chin
    face = [(34.5, 30), (33.5, 38), (35, 47), (39, 55), (43.5, 60), (47, 62), (50.5, 61), (56, 55),
            (60.5, 47), (63, 39), (63, 31), (60, 21), (48, 17), (37, 20)]
    s.fill("skin", face, group="skin", line="skinx")
    s.fill("skind", [(58, 32), (63.5, 30), (63, 39), (60.5, 47), (56, 55), (51.5, 59), (56, 49), (58, 40)],
           group="skin", clip="skin")
    for root, tip, w, bend in TOP:
        s.fill("skind", clump((root[0], root[1] + 3), (tip[0] + 0.5, tip[1] + 2.5), w, bend), group="skin", clip="skin")
    # narrow, sharp eyes with a heavy lid
    eye(s, 0, 39.0, 40.5, 8.2, 5.0, -1, eyes, look=-1.0, tilt=-0.8, lid=2.0, lower=0.4)
    eye(s, 1, 53.5, 40.5, 10.0, 5.4, +1, eyes, look=-1.3, tilt=-1.0, lid=2.1, lower=0.4)
    s.stroke("skind", [(43.6, 45.0), (42.2, 49.4), (44.2, 50.0)], w=0.9, thr=0.4)
    s.dot("skinx", 42, 49)
    draw_mouth(s, 45.5, 55.0, mouth, w=4.6, frown=0.25)
    # top layer and its sheen
    s.fill("hair", ellipse(48.5, 15, 17, 10), **hl, raw=True)
    for root, tip, w, bend in TOP:
        s.fill("hair", clump(root, tip, w, bend, taper=0.5), **hl)
    s.fill("hairl", [(34, 15), (40, 10), (47, 8.5), (47, 12), (40, 13.5), (36, 17, 1)], group="hair", clip="hair")
    s.fill("hairl", [(51, 8.5), (58, 10), (63, 14), (60, 15.5), (56, 12.5), (51, 12, 1)], group="hair", clip="hair")
    s.stroke("haird", [(48.5, 8), (48.5, 14)], w=1.0, clip="hair", thr=0.4)
    for a, b in [((40, 17), (35, 28)), ((44, 16), (41, 30)), ((53, 16), (56, 30)), ((57, 17), (62, 28))]:
        s.stroke("haird", [a, b], w=0.8, clip="hair", thr=0.45)
    # stubble texture on the undercut, below the long layer
    for x, y in ((31, 28), (32, 33), (66, 27), (65.5, 31)):
        s.stroke("line", [(x, y), (x + 0.4, y + 2)], w=0.5, clip="hair", thr=0.55)
    # sharp, slightly cocked brows
    brow(s, [(34.5, 34.6), (38.5, 34.0), (43, 35.8)], w=1.4, key="haird")
    brow(s, [(49, 35.4), (53.5, 33.4), (58.5, 33.2)], w=1.5, key="haird")
