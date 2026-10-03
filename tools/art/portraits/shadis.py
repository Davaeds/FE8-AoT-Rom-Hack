"""Chief Instructor Keith Shadis: shaved head, deep-set staring eyes in dark
sockets, hollow cheeks, short dark goatee, heavy build in the Training Corps
uniform."""
from face import eye, brow, mouth as draw_mouth
from pkit import ellipse
from body import neck, cadet

PALETTE = {
    "line":   (30, 22, 20),
    "skin":   (236, 196, 160),
    "skind":  (200, 148, 116),
    "skinx":  (140, 90, 72),
    "white":  (240, 236, 222),
    "hair":   (74, 56, 46),
    "haird":  (44, 32, 28),
    "hairl":  (252, 232, 206),
    "iris":   (150, 120, 84),
    "irisd":  (70, 50, 34),
    "jacket": (176, 136, 92),
    "jacketd": (122, 88, 60),
    "strap":  (62, 42, 34),
    "shirtd": (196, 190, 178),
    "mouth":  (110, 52, 44),
}

MOUTH = (4, 6)
EYES = (4, 4)


def build(s, mouth="closed", eyes="open"):
    neck(s, 39, 59, 50)
    cadet(s, dy=5, broad=4)
    # ear
    s.fill("skin", [(63, 33), (68, 31), (70.5, 37), (69, 46), (64, 48)], group="ear", line="skinx")
    s.fill("skind", [(65, 35), (68.5, 36), (68, 44), (65, 45)], group="ear", clip="ear")
    # bald, long head with a strong jaw
    head = [(31, 30), (31, 40), (33, 49), (37, 56), (43, 61), (48, 62.5), (53, 61), (59, 55), (62.5, 47),
            (64.5, 38), (65, 26), (61, 14), (50, 8), (39, 9.5), (32.5, 17)]
    s.fill("skin", head, group="skin", line="skinx")
    # shading: right side, temples, hollow cheeks
    s.fill("skind", [(57, 14), (65, 26), (64.5, 38), (62.5, 47), (59, 55), (54, 59), (57.5, 47), (59, 34), (58, 22)],
           group="skin", clip="skin")
    s.fill("skind", [(34, 45), (37, 43), (39.5, 51), (37, 54)], group="skin", clip="skin")
    s.fill("skind", [(53, 50), (57.5, 44), (58, 52)], group="skin", clip="skin")
    # shine on the scalp
    s.fill("hairl", [(38, 13), (45, 10), (50, 10.5), (44, 13), (39, 16)], group="skin", clip="skin")
    # deep sockets under a heavy brow ridge
    s.fill("skinx", ellipse(39.5, 37.5, 6.5, 4.2), group="skin", clip="skin", raw=True)
    s.fill("skinx", ellipse(54, 37.5, 7.5, 4.4), group="skin", clip="skin", raw=True)
    eye(s, 0, 39.5, 38.5, 7.0, 4.4, -1, eyes, look=-0.6, tilt=-0.6, lid=1.6, lower=0.6, iris_w=0.27, flick=0)
    eye(s, 1, 54.0, 38.5, 8.6, 4.6, +1, eyes, look=-0.9, tilt=-0.8, lid=1.7, lower=0.6, iris_w=0.27, flick=0)
    brow(s, [(33.5, 32.8), (38, 32.0), (44, 33.6)], w=1.7, key="hair")
    brow(s, [(49, 33.6), (55, 31.8), (61, 32.4)], w=1.8, key="hair")
    # forehead and eye-bag lines
    s.stroke("skinx", [(38, 25), (48, 24.2), (56, 25)], w=0.6, thr=0.5)
    s.stroke("skinx", [(36, 43.2), (40, 44.4), (43, 43.4)], w=0.6, thr=0.5)
    s.stroke("skinx", [(51, 43.4), (55, 44.6), (59, 43.4)], w=0.6, thr=0.5)
    # nose
    s.stroke("skinx", [(46, 40), (44.6, 48.4), (47.6, 49.4)], w=0.9, thr=0.4)
    s.stroke("skinx", [(37.5, 49), (41.5, 54.5)], w=0.6, thr=0.5)
    # thin moustache and a goatee on the chin
    draw_mouth(s, 47.2, 55.4, mouth, w=4.8, frown=0.7)
    s.stroke("hair", [(42.5, 53.6), (45, 52.4), (47.2, 52.8), (49.5, 52.4), (52, 53.6)], w=1.1, thr=0.4)
    s.fill("hair", [(43.5, 58.6), (47.2, 57.8), (51, 58.6), (51.5, 61.5), (49, 64.2), (47.2, 64.8), (45.4, 64.2), (43, 61.5)],
           group="beard", line="haird")
    s.fill("haird", [(47.6, 59), (51, 58.6), (51.5, 61.5), (49, 64.2), (47.6, 64.6)], group="beard", clip="beard")
