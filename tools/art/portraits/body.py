"""Shared bodies for the portraits: the Training Corps uniform (tan cropped
jacket with a fold-down collar, white shirt, ODM harness straps, crossed-swords
emblem on the left breast)."""


def neck(s, x0=42, x1=56, top=50, line="skinx"):
    s.fill("skin", [(x0, top), (x1, top - 2), (x1 + 3, 74), (x0 - 1, 74)], group="neck", line=line)
    s.fill("skind", [(x0, top), (x1, top - 2), (x1 + 1.5, 57), (49, 60), (x0 + 1, 59)], group="neck", clip="neck")


class _Shift:
    """Scene proxy that moves every point down by dy (rows at y >= 80 stay at the bottom edge)."""

    def __init__(self, s, dy):
        self.s, self.dy = s, dy

    def _pts(self, pts):
        return [(p[0], min(p[1] + self.dy, 80) if p[1] < 80 else p[1]) + tuple(p[2:]) for p in pts]

    def fill(self, key, pts, **kw):
        self.s.fill(key, self._pts(pts), **kw)

    def stroke(self, key, pts, **kw):
        self.s.stroke(key, self._pts(pts), **kw)


def cadet(s, scarf=None, broad=0.0, dy=0.0, shirtd="shirtd"):
    """Jacket open in a V over the shirt. scarf: palette key of a scarf, or None.
    broad widens the shoulders (pixels each side); dy lowers the collar line."""
    b = broad
    s = _Shift(s, dy)
    # shirt
    s.fill("white", [(36, 61), (49, 58), (61, 59), (60, 80, 1), (38, 80, 1)], group="shirt", line=shirtd)
    s.fill(shirtd, [(52, 64), (61, 59), (60, 80, 1), (54, 80, 1)], group="shirt", clip="shirt")
    if scarf:
        s.fill(scarf, [(36, 56), (49, 54), (62, 55), (63, 63), (56, 67), (49, 68), (42, 66), (35, 63)],
               group="scarf", line="line")
        s.fill(scarf + "d", [(52, 60), (62, 57), (63, 63), (56, 67), (50, 67.5)], group="scarf", clip="scarf")
        s.stroke(scarf + "d", [(38, 62), (45, 64.5), (52, 64)], w=0.9, clip="scarf", thr=0.4)
    # jacket halves, with the lapels folded out
    left = [(5 - b, 80, 1), (8 - b, 69), (19 - b, 63), (31, 60), (36, 61, 1), (41, 70), (46, 80, 1)]
    right = [(52, 80, 1), (55, 70), (61, 59, 1), (66, 58), (77 + b, 62), (88 + b, 69), (92 + b, 80, 1)]
    s.fill("jacket", left, group="jacket", line="line")
    s.fill("jacket", right, group="jacket", line="line")
    s.fill("jacketd", [(61, 59, 1), (77 + b, 62), (88 + b, 69), (92 + b, 80, 1), (74, 80, 1), (72, 71), (64, 66)],
           group="jacket", clip="jacket")
    s.fill("jacketd", [(5 - b, 80, 1), (8 - b, 69), (15 - b, 65), (20, 73), (22, 80, 1)], group="jacket", clip="jacket")
    # lapels
    s.fill("jacketd", [(36, 61, 1), (30, 66), (36, 71, 1), (41, 70)], group="jacket", clip="jacket")
    s.fill("jacketd", [(61, 59, 1), (66, 64), (60, 70, 1), (55, 70)], group="jacket", clip="jacket")
    s.stroke("line", [(36, 61), (30.5, 66), (36, 71)], w=0.9, thr=0.45)
    s.stroke("line", [(61, 59), (66, 64), (60, 70)], w=0.9, thr=0.45)
    # ODM harness straps over the jacket
    s.stroke("strap", [(26 - b, 66), (28, 73), (29, 80)], w=2.2, thr=0.35)
    s.stroke("strap", [(71 + b, 65), (69, 72), (68, 80)], w=2.2, thr=0.35)
    s.stroke("strap", [(28, 75), (41, 76)], w=1.6, thr=0.35)
    s.stroke("strap", [(57, 76), (69, 75)], w=1.6, thr=0.35)
    # Training Corps emblem on the left breast (viewer's right): crossed swords on a shield
    s.fill("white", [(74, 66), (80, 66), (80, 71), (77, 74), (74, 71)], group="emblem", line="line", smooth=False)
    s.stroke("jacketd", [(75, 67), (79, 72)], w=0.8, thr=0.45)
    s.stroke("jacketd", [(79, 67), (75, 72)], w=0.8, thr=0.45)
