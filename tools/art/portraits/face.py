"""Shared face parts in the show's style: heavy upper eyelids, tall irises
shaded dark at the top, thin partial lower lids, and simple mouths.
Faces are drawn in three-quarter view looking left (the game mirrors them)."""
import math

from pkit import ellipse


def clump(root, tip, w, bend=0.0, taper=0.45):
    """Pointed hair clump from root to tip; bend bows it sideways (pixels)."""
    dx, dy = tip[0] - root[0], tip[1] - root[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    mid = (root[0] + dx * taper + nx * bend, root[1] + dy * taper + ny * bend)
    return [(root[0] + nx * w / 2, root[1] + ny * w / 2),
            (mid[0] + nx * w * 0.42, mid[1] + ny * w * 0.42),
            (tip[0], tip[1], 1),
            (mid[0] - nx * w * 0.42, mid[1] - ny * w * 0.42),
            (root[0] - nx * w / 2, root[1] - ny * w / 2)]


def eye(s, n, cx, cy, w, h, side, state, look=-0.6, tilt=0.0, lid=1.5,
        iris="iris", irisd="irisd", irisl=None, lower=0.55, flick=1.4, iris_w=0.34):
    """side -1: far eye (outer corner on the left); +1: near eye.
    tilt raises (negative) or lowers the outer corner."""
    g = f"eye{n}"
    outer = (cx + side * w / 2, cy + tilt, 1)
    inner = (cx - side * w / 2, cy + 0.6, 1)
    peak = (cx + side * w * 0.12, cy - h / 2)
    bottom = (cx - side * w * 0.05, cy + h / 2)
    tip = (outer[0] + side * flick, outer[1] - 0.6)
    if state == "closed":
        s.stroke("line", [tip, (outer[0], outer[1] + 0.4), (cx, cy + h * 0.32), (inner[0], inner[1] + 0.2)], w=lid * 0.8)
        return
    if state == "half":
        peak = (cx + side * w * 0.12, cy + 0.2)
    rx, ry = w * iris_w, h * 0.62
    ic = (cx + look, cy + 0.6)
    s.fill("white", [outer, peak, inner, bottom], group=g, outline=False)
    s.fill(iris, ellipse(ic[0], ic[1], rx, ry), group=g, outline=False, clip=g, raw=True)
    s.fill(irisd, ellipse(ic[0], ic[1] - ry * 0.55, rx * 1.05, ry * 0.62), group=g, outline=False, clip=g, raw=True)
    if irisl:
        s.fill(irisl, ellipse(ic[0] + 0.2, ic[1] + ry * 0.55, rx * 0.7, ry * 0.35), group=g, outline=False, clip=g, raw=True)
    s.fill("line", ellipse(ic[0] - 0.1, ic[1], rx * 0.42, ry * 0.42), group=g, outline=False, clip=g, raw=True)
    s.stroke("line", [tip, outer, peak, inner], w=lid)
    # partial lower lid on the outer side
    lo = [(outer[0] - side * 0.3, outer[1] + 0.8), (outer[0] - side * w * 0.3, bottom[1] + 0.2),
          (outer[0] - side * w * lower, bottom[1] + 0.4)]
    s.stroke("line", lo, w=0.85, thr=0.4)
    if state == "open":
        s.dot("white", ic[0] - rx * 0.35, ic[1] - ry * 0.25, clip=g)


def brow(s, pts, w=1.3, key="line"):
    s.stroke(key, pts, w=w)


def mouth(s, cx, cy, state, w=4.0, frown=0.4, key="mouth", line="line", teeth=True):
    """Mouth centred at (cx, cy). frown > 0 turns the corners down."""
    smile = state.startswith("smile")
    st = state.replace("smile_", "")
    bend = -0.9 if smile else frown
    l, r = (cx - w / 2, cy + bend), (cx + w / 2, cy + bend * 0.6)
    if st in ("closed", "closed_talk") or state == "closed":
        s.stroke(line, [l, (cx, cy), r], w=0.9, thr=0.4)
        if st == "closed_talk":
            s.fill(key, ellipse(cx, cy + 0.6, w * 0.25, 0.6), group="mouth", outline=False, raw=True)
        return
    oh = 1.3 if st == "half" else 2.6
    s.fill(key, [l + (1,), (cx, cy - 0.3), r + (1,), (cx + w * 0.15, cy + oh), (cx - w * 0.15, cy + oh)],
           group="mouth", outline=False)
    if teeth and st == "open":
        s.fill("white", [(cx - w * 0.35, cy - 0.2), (cx + w * 0.35, cy - 0.2), (cx + w * 0.3, cy + 0.8), (cx - w * 0.3, cy + 0.8)],
               group="mouth", outline=False, clip="mouth", smooth=False)
    s.stroke(line, [l, (cx, cy - 0.4), r], w=0.9, thr=0.4)
