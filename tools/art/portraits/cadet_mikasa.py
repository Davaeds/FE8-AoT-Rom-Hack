"""Mikasa Ackerman as a 104th cadet, age 15 (year 850): straight black hair to
the shoulders with a full fringe, calm grey eyes, the red scarf Eren gave her,
Training Corps uniform."""
from face import eye, brow, mouth as draw_mouth, clump
from pkit import ellipse
from body import neck, cadet

PALETTE = {
    "line":   (26, 20, 26),
    "skin":   (252, 224, 200),
    "skind":  (232, 180, 156),
    "skinx":  (172, 108, 98),
    "white":  (248, 248, 240),
    "hair":   (44, 40, 52),
    "haird":  (22, 20, 28),
    "hairl":  (90, 86, 108),
    "iris":   (104, 104, 118),
    "irisd":  (44, 42, 54),
    "red":    (196, 40, 44),
    "redd":   (124, 22, 30),
    "jacket": (176, 136, 92),
    "jacketd": (122, 88, 60),
    "strap":  (62, 42, 34),
}

MOUTH = (4, 6)
EYES = (4, 4)

# straight locks hanging from the crown: root, tip, width, bend
SIDES = [((34, 14), (25, 68), 11, 1.5), ((30, 22), (22, 62), 10, 1.0), ((62, 14), (72, 66), 11, -1.5),
         ((66, 22), (76, 60), 10, -1.0)]
FRINGE = [((33, 14), (31.5, 34), 7, 0.6), ((38, 12), (37, 35), 7, 0.3), ((43, 12), (43, 35.5), 7, 0),
          ((48, 12), (47.5, 38), 6, 0), ((53, 12), (53.5, 35), 7, -0.2), ((58, 13), (59.5, 34.5), 7, -0.4),
          ((63, 15), (65, 33), 7, -0.6)]


def build(s, mouth="closed", eyes="open"):
    hl = dict(group="hair", line="line")
    s.fill("hair", ellipse(48.5, 27, 23, 22), **hl, raw=True)
    for root, tip, w, bend in SIDES:
        s.fill("hair", clump(root, tip, w, bend, taper=0.85), **hl)
    # straight curtain of hair behind the head
    s.fill("hair", [(26, 22), (71, 22), (76, 64), (69, 66), (64, 56), (34, 56), (29, 66), (21, 64)], **hl)
    s.fill("haird", [(18, 64), (26, 30), (48, 22), (70, 30), (80, 64)], group="hair", clip="hair")
    neck(s, 43, 55, 52)
    cadet(s, scarf="red", dy=3, shirtd="skind")
    # face: softer jaw
    face = [(33, 27), (32.5, 36), (34, 45), (38, 52), (43, 57.5), (46.5, 59.5), (50, 58.5), (55.5, 53.5),
            (60, 47), (62.5, 40), (63, 30), (60, 21), (48, 17), (37, 20)]
    s.fill("skin", face, group="skin", line="skinx")
    s.fill("skind", [(58, 32), (63, 30), (62.5, 40), (60, 47), (55.5, 53.5), (52, 56.5), (56, 47.5), (58, 40)],
           group="skin", clip="skin")
    for root, tip, w, bend in FRINGE:
        s.fill("skind", clump((root[0], root[1] + 2.5), (tip[0] + 0.6, tip[1] + 2.0), w, bend), group="skin", clip="skin")
    eye(s, 0, 39.0, 40.5, 8.0, 5.8, -1, eyes, look=-0.9, tilt=-0.3, lid=1.7, lower=0.45)
    eye(s, 1, 53.5, 40.5, 10.0, 6.2, +1, eyes, look=-1.3, tilt=-0.4, lid=1.8, lower=0.45)
    s.stroke("skind", [(43.6, 45.0), (42.4, 48.0), (43.8, 48.4)], w=0.8, thr=0.45)
    draw_mouth(s, 45.0, 53.6, mouth, w=3.8, frown=0.2, key="redd")
    # fringe and the locks in front of the ears
    for root, tip, w, bend in FRINGE:
        s.fill("hair", clump(root, tip, w, bend), **hl)
    s.fill("hair", clump((34, 20), (31.5, 52), 6, 0.8), **hl)
    s.fill("hair", clump((62, 20), (65.5, 50), 6, -0.8), **hl)
    s.fill("hairl", [(30, 17), (36, 11), (46, 8), (56, 9), (65, 14), (62, 15), (55, 12), (46, 11.5), (37, 14),
                     (32, 19, 1)], group="hair", clip="hair")
    for a, b in [((40, 18), (39, 31)), ((51, 18), (52, 31)), ((60, 19), (62, 30)), ((28, 34), (26, 50)), ((70, 34), (72, 48))]:
        s.stroke("haird", [a, b], w=0.9, clip="hair", thr=0.45)
    # level brows
    brow(s, [(35, 35.0), (39, 34.4), (42.5, 35.2)], w=1.1)
    brow(s, [(49, 35.2), (53.5, 34.2), (58, 34.6)], w=1.2)
