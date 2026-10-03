"""Pure Titans built on the rig: body from capsules, hand-drawn heads."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rig import *
from tkit import preview, mirror

SKIN = Ramp([4, 2, 6], [0.05, 0.50])      # shadow mauve, lilac-pink mid, cream highlight
SKIN_FAR = Ramp([4, 2, 6], [0.30, 0.75])  # limbs behind the body read darker


class Titan:
    def __init__(self, **kw):
        # proportions (pixels)
        self.leg = 10.5         # hip to sole
        self.torso = 8.5        # hip to shoulder line
        self.sh = 5.5           # shoulder half width (joint centres)
        self.hip = 2.4          # hip joint half spacing
        self.r_leg = (1.9, 1.5)
        self.r_arm = (1.5, 1.3)
        self.arm = 10.0
        self.torso_rows = None  # (hl, hr) per row from shoulders to crotch, front view
        self.side_rows = None   # (front, back) per row, side view facing left
        self.heads = {}         # 'front'/'back'/'side' -> (rows, cmap, dx, dy)
        self.belly = None
        self.foot = 1.0
        self.hand = 1.0
        self.neck = (1.9, 2.1)
        self.ramps = {}
        self.__dict__.update(kw)

    def ramp(self, part, far=False):
        r = self.ramps.get(part, SKIN)
        if far:
            return Ramp(r.cols, [c + 0.25 for c in r.cuts])
        return r

    # ------------------------------------------------------------ front/back
    def front(self, phase=0, back=False):
        cx = 16
        hip_y = FEET + 0.5 - self.leg
        sway = {0: 0, 1: 1, 2: 0, 3: -1}[phase]
        lift = {0: (0, 0), 1: (2, 0), 2: (0, 0), 3: (0, 2)}[phase]
        bob = 1 if phase in (1, 3) else 0
        hip_y += bob
        sh_y = hip_y - self.torso
        layers = []
        legs = Layer(); legs.contour = None
        for side, s in ((-1, 0), (1, 1)):
            hx = cx + sway + side * self.hip
            fy = FEET - 0.5 - lift[s]
            fx = cx + side * (self.hip + 0.3)
            capsule(legs, (hx, hip_y), (fx, fy - 0.5), *self.r_leg, self.ramp('leg'))
            capsule(legs, (fx - 0.2 * -side, fy), (fx + side * 0.9 * self.foot, fy + 0.2), 1.2 * self.foot, 1.1 * self.foot, self.ramp('foot'))
            self.leg_details(legs, hx, hip_y, fx, fy)
        layers.append(legs)
        neck = Layer(); neck.contour = None
        capsule(neck, (cx + sway, sh_y - 2.5), (cx + sway, sh_y + 0.5), *self.neck, self.ramp('neck'))
        layers.append(neck)
        body = Layer(); body.contour = None
        torso(body, cx + sway, int(sh_y), self.torso_rows, self.ramp('torso'))
        if self.belly and not back:
            bx, by, rx, ry = self.belly
            ellipse(body, cx + sway + bx, sh_y + by, rx, ry, self.ramp('torso'))
        layers.append(body)
        det = Layer(); det.contour = None
        self.torso_details(det, cx + sway, sh_y, back)
        layers.append(det)
        for side in (-1, 1):
            arm = Layer()
            sx, sy = cx + sway + side * self.sh, sh_y + 1.5
            hx, hy = cx + sway + side * (self.sh + 1.0), sh_y + 1.5 + self.arm
            capsule(arm, (sx, sy), (hx, hy), *self.r_arm, self.ramp('arm'))
            ellipse(arm, hx, hy + 0.8 * self.hand, 1.5 * self.hand, 1.7 * self.hand, self.ramp('hand'))
            self.arm_details(arm, sx, sy, hx, hy)
            layers.append(arm)
        head = Layer()
        rows, cmap, dx, dy = self.heads['back' if back else 'front']
        w = len(rows[0])
        stamp(head, rows, cmap, int(cx + sway - w // 2 + dx), int(sh_y) - len(rows) + dy)
        layers.append(head)
        return composite(layers)

    # ------------------------------------------------------------ side (facing left)
    def side(self, phase=0):
        hx, hy = 16.5, FEET + 0.5 - self.leg + (-1 if phase in (1, 3) else 0) + 1
        sh = (hx - 1.2, hy - self.torso)
        poses = {
            'fwd':  ((-2.0, 4.6), (-3.6, 9.6)),
            'pass': ((-0.3, 5.0), (0.2, 10.0)),
            'back': ((1.6, 4.7), (3.6, 9.4)),
            'lift': ((-1.6, 4.4), (0.6, 8.0)),
        }
        ks = self.leg / 10.5
        poses = {k: ((a * ks, b * ks), (c * ks, d * ks)) for k, ((a, b), (c, d)) in poses.items()}
        near, far = {0: ('fwd', 'back'), 1: ('pass', 'lift'), 2: ('back', 'fwd'), 3: ('lift', 'pass')}[phase]
        arm_near, arm_far = {0: ('back', 'fwd'), 1: ('mid', 'mid'), 2: ('fwd', 'back'), 3: ('mid', 'mid')}[phase]
        ka = self.arm / 10.0
        hands = {k: (a * ka, b * ka) for k, (a, b) in {'fwd': (-3.2, 8.6), 'mid': (0.0, 9.6), 'back': (3.2, 8.8)}.items()}

        def leg(pose, far):
            lay = Layer()
            ramp = self.ramp('leg', far)
            (kx, ky), (ax, ay) = poses[pose]
            k = (hx + kx, hy + ky); a = (hx + ax, min(hy + ay, FEET - 0.5))
            capsule(lay, (hx, hy), k, self.r_leg[0], self.r_leg[0] - 0.1, ramp)
            capsule(lay, k, a, self.r_leg[0] - 0.1, self.r_leg[1], ramp)
            capsule(lay, (a[0] + 0.4, a[1]), (a[0] - 1.8 * self.foot, a[1] + 0.3), 1.1 * self.foot, 1.0 * self.foot, self.ramp('foot', far))
            self.leg_details(lay, hx, hy, k[0], k[1], side=True)
            return lay

        def arm(pose, far):
            lay = Layer()
            dxh, dyh = hands[pose]
            s = (sh[0] + 0.5, sh[1] + 1.5)
            h = (s[0] + dxh, s[1] + dyh)
            capsule(lay, s, h, *self.r_arm, self.ramp('arm', far))
            ellipse(lay, h[0], h[1] + 0.8 * self.hand, 1.4 * self.hand, 1.6 * self.hand, self.ramp('hand', far))
            self.arm_details(lay, s[0], s[1], h[0], h[1])
            return lay

        layers = [arm(arm_far, True), leg(far, True)]
        neck = Layer(); neck.contour = None
        capsule(neck, (sh[0] - 0.2, sh[1] - 2.5), (sh[0] + 0.3, sh[1] + 0.8), *self.neck, self.ramp('neck'))
        layers.append(neck)
        body = Layer(); body.contour = None
        torso(body, sh[0] + 0.6, int(sh[1]), self.side_rows, self.ramp('torso'))
        layers.append(body)
        det = Layer(); det.contour = None
        self.side_details(det, sh)
        layers.append(det)
        layers.append(leg(near, False))
        layers.append(arm(arm_near, False))
        head = Layer()
        rows, cmap, dx, dy = self.heads['side']
        stamp(head, rows, cmap, int(sh[0]) - len(rows[0]) // 2 + dx, int(sh[1]) - len(rows) + dy)
        layers.append(head)
        return composite(layers)

    def torso_details(self, lay, cx, sh_y, back):
        pass

    def side_details(self, lay, sh):
        pass

    def leg_details(self, lay, hx, hy, kx, ky, side=False):
        pass

    def arm_details(self, lay, sx, sy, hx, hy):
        pass

    def frames(self):
        f = {}
        for p in range(4):
            f[f'front{p}'] = self.front(p)
            f[f'back{p}'] = self.front(p, back=True)
            f[f'side{p}'] = self.side(p)
        return f


# ---------------------------------------------------------------- Titan A
A_CMAP = {'R': 4, 'r': 15, 'S': 2}
A_FRONT = [
"..rRrRRrRr...",
".rRRrRRRrRRr.",
".RRHHHrHHHRR.",
".RHHHHHHHHHR.",
"SHWWHHHHHWWHS",
"SHWKHHHHHKWHS",
".HHHHHsHHHSS.",
".SOWWWWWWWOS.",
".SOWMMMMMWOS.",
".SSOwWWWwOSs.",
"..SSOOOOOSs..",
]
A_BACK = [
"..rRrRRrRr...",
".rRRRRRRRRRr.",
".RRRRRRRRRRR.",
".RRRRRRRRRRR.",
"SRRRRRRRRRRRS",
"SRRRRRRRRRRRS",
".RRRRRRRRRRR.",
".rRRrRRRrRRr.",
".HrRRrRrRRrS.",
"..HHrSHrSSs..",
"...SHHHHSs...",
]
A_SIDE = [
"...rRrRrRr..",
".rRRRRRRRRRr",
".RHHRRRRRRRR",
".HHHHHRRRRRR",
".HKWHHHSRRRr",
"HHHHHHSSRRr.",
".HHHHHSSRr..",
"OWWWWWHSs...",
"OMMMMWHSs...",
".OwWWWSs....",
"..OOOSSs....",
]


class TitanA(Titan):
    def torso_details(self, lay, cx, sh_y, back):
        y = int(sh_y)
        if back:
            plot(lay, [(int(cx), y + k) for k in range(2, 8)], 2)           # spine
            plot(lay, [(int(cx) - 3, y + 3), (int(cx) + 2, y + 3)], 2)       # shoulder blades
        else:
            plot(lay, [(int(cx) - 3, y + 4), (int(cx) - 2, y + 4), (int(cx) + 1, y + 4), (int(cx) + 2, y + 4)], 2)  # pecs
            plot(lay, [(int(cx), y + 7)], 4)                                  # navel


def titan_a():
    rows = [(6.5, 6.5), (6.0, 6.0), (5.2, 5.2), (5.0, 5.0), (4.8, 4.8), (4.4, 4.4), (4.2, 4.2), (4.2, 4.2), (4.5, 4.5), (4.6, 4.6), (4.3, 4.3)]
    side = [(2.8, 3.6), (3.4, 3.8), (3.6, 3.6), (3.4, 3.4), (3.1, 3.2), (3.0, 3.1), (3.1, 3.2), (3.3, 3.4), (3.3, 3.6), (3.0, 3.6), (2.6, 3.0)]
    return TitanA(torso_rows=rows, side_rows=side,
                  heads={'front': (A_FRONT, A_CMAP, 0, -1), 'back': (A_BACK, A_CMAP, 0, -1), 'side': (A_SIDE, A_CMAP, -1, -1)}, leg=10.0, torso=7.5, arm=10.5)



# ---------------------------------------------------------------- Titan B: fat, bald, clenched grin
B_CMAP = {'R': 15, 'r': 4, 'S': 2}
B_FRONT = [
"...RRRRRRR...",
"..RRrRRRrRR..",
".RRRRRRRRRRR.",
".RHHHHHHHHHR.",
"SHOOHHHHHOOHS",
"SHWKHHHHHKWHS",
".HHHHHsHHHSS.",
"SOWWWWWWWWWOS",
"SOWOWOWOWOWOS",
".SOOOOOOOOOS.",
"..SSHHHHHSs..",
]
B_BACK = [
"...RRRRRRR...",
"..RRRRRRRRR..",
".RRRRrRRRRRR.",
".RRRRRRRRRRR.",
"SRRRRRRRRRRRS",
"SRRRRRRRRRRRS",
".RRRrRRRrRRR.",
".SHRRRRRRRSS.",
"SHHHHHHHHHSSS",
".SHHHHHHHSSS.",
"..SSHHHHHSs..",
]
B_SIDE = [
"...RRRRRR...",
".RRRRRRRRRR.",
".RRRRRRRRRRR",
".HHHHRRRRRRR",
"OOHHHHHSRRRr",
"KWHHHHSSRRr.",
"HHHHHHSSRR..",
"WWWWWWHSs...",
"WOWOWOSSs...",
"OOOOOSSSs...",
".SSHHHSSs...",
]

class TitanB(Titan):
    def torso_details(self, lay, cx, sh_y, back):
        y, c = int(sh_y), int(cx)
        if back:
            plot(lay, [(c, y + k) for k in range(2, 7)], 2)
            plot(lay, [(c - 3, y + 8), (c - 2, y + 9), (c + 2, y + 9), (c + 3, y + 8)], 2)
        else:
            plot(lay, [(c - 4, y + 3), (c - 3, y + 4), (c - 2, y + 4), (c + 2, y + 4), (c + 3, y + 4), (c + 4, y + 3)], 2)  # chest
            plot(lay, [(c, y + 7)], 4)                                                                          # navel
            plot(lay, [(c - 4, y + 9), (c - 3, y + 10), (c - 2, y + 10), (c - 1, y + 10), (c, y + 10),
                       (c + 1, y + 10), (c + 2, y + 10), (c + 3, y + 10), (c + 4, y + 9)], 2)                   # belly fold


def titan_b():
    rows = [(7.0, 7.0), (6.8, 6.8), (6.4, 6.4), (6.6, 6.6), (6.9, 6.9), (7.0, 7.0), (6.8, 6.8), (6.2, 6.2), (5.6, 5.6), (5.0, 5.0)]
    side = [(3.0, 3.8), (3.8, 4.0), (4.6, 3.8), (5.4, 3.6), (5.8, 3.6), (5.8, 3.6), (5.4, 3.7), (4.6, 3.8), (3.8, 3.8), (3.2, 3.4)]
    return TitanB(torso_rows=rows, side_rows=side, belly=(0, 6.0, 5.2, 3.8),
                  leg=8.5, torso=8.0, sh=6.6, hip=2.8, r_leg=(2.4, 2.0), r_arm=(1.9, 1.6), arm=9.0,
                  heads={'front': (B_FRONT, B_CMAP, 0, 0), 'back': (B_BACK, B_CMAP, 0, 0), 'side': (B_SIDE, B_CMAP, -1, 0)})


# ---------------------------------------------------------------- Smiling Titan: slender, long hair, huge closed smile
SM_CMAP = {'R': 5, 'r': 4, 'y': 12, 'S': 2}
SM_FRONT = [
"...rRRRRRr...",
"..RyyRrRRRR..",
".RyyRRrHRRRR.",
".RyRHHHHHHRR.",
"RRHOOHHHOOHRR",
"RyHWKHHHKWHRR",
"RyHHHHsHHHHRR",
"RROHHHHHHHORR",
"RRHOHHHHHOHRR",
"RRHHOOOOOHHRr",
"rRRSHHHHHSRRr",
"rR..SHHHS..Rr",
]
SM_BACK = [
"...rRRRRRr...",
"..RyyRRRRRR..",
".RyyyRRRRRRR.",
".RyyRRRRRRRR.",
"RRyRRRRRRRRRR",
"RRRRRRRRRRRRR",
"RRRRRRRRRRRRR",
"RRRRrRRRrRRRR",
"rRRRRRRRRRRRr",
"rRRrRRRRRrRRr",
"rRRRRRRRRRRRr",
"rRr..SHS..rRr",
]
SM_SIDE = [
"....rRRRRRr..",
"..RRyyRRRRRR.",
".RRyyRRRRRRRr",
".RRHyRRRRRRRr",
".HHHHRRRRRRRr",
"OOHHHHRRRRRRr",
"KWHHHHSRRRRRr",
"HHHHHHSRRRRRr",
"OHHHHHSRRRRr.",
"HOHHHSSRRrRr.",
"SHOOOSSRRRr..",
".SSSSSRRRr...",
]


class Smiling(Titan):
    def torso_details(self, lay, cx, sh_y, back):
        y = int(sh_y)
        if back:
            plot(lay, [(int(cx), y + k) for k in range(3, 8)], 2)
        else:
            plot(lay, [(int(cx) - 2, y + 4), (int(cx) + 2, y + 4)], 2)
            plot(lay, [(int(cx), y + 7)], 4)


def smiling():
    rows = [(5.6, 5.6), (5.0, 5.0), (4.4, 4.4), (4.0, 4.0), (3.8, 3.8), (3.6, 3.6), (3.6, 3.6), (3.8, 3.8), (4.0, 4.0), (3.8, 3.8)]
    side = [(2.4, 3.2), (2.8, 3.2), (2.8, 2.8), (2.5, 2.5), (2.3, 2.4), (2.2, 2.4), (2.3, 2.5), (2.5, 2.7), (2.5, 2.8), (2.3, 2.6)]
    return Smiling(torso_rows=rows, side_rows=side,
                   leg=10.5, torso=7.0, sh=4.8, hip=2.0, r_leg=(1.6, 1.2), r_arm=(1.2, 1.0), arm=10.0,
                   heads={'front': (SM_FRONT, SM_CMAP, 0, 0), 'back': (SM_BACK, SM_CMAP, 0, 0), 'side': (SM_SIDE, SM_CMAP, -1, 0)})


# ---------------------------------------------------------------- Armored Titan
ARMOR = Ramp([4, 5, 6], [0.05, 0.45])
MUSCLE = Ramp([7, 8, 9], [0.10, 0.55])
AR_CMAP = {'Y': 5, 'y': 12, 'A': 6, 'a': 5, 'm': 8, 'D': 7}
AR_FRONT = [
"...yYYYYYy...",
"..YYyYYYyYY..",
".YyAAAAAAAyY.",
".YAAaAAAaAAY.",
"yAOOOaAaOOOAy",
"yaOWWOaOWWOay",
".aAaAOAOaAa..",
".maOWOWOWOam.",
".mOWWWWWWWOm.",
".maOOOOOOOam.",
"..maaAAAaam..",
]
AR_BACK = [
"...yYYYYYy...",
"..YYyYYYyYY..",
".YYYYyYYYYYY.",
".YyYYYYYyYYY.",
"YYYYYYYYYYYYY",
"yYYYyYYYyYYYy",
".yYYYYYYYYYy.",
".aAyYyYyYyAa.",
".maAAAAAAAam.",
".mmaAAAAAamm.",
"..mmaAAAamm..",
]
AR_SIDE = [
"....yYYYYy..",
"..YYYYyYYYY.",
".AAAYYYYyYYY",
".AaAAYYYYYYy",
"OOOaAAYYYYY.",
"WWOAaAAYYYy.",
"AAAOaAAmYy..",
"OWOWOaAm....",
"WWWWOAAm....",
"OOOOaAm.....",
".maaAAm.....",
]


class Armored(Titan):
    def torso_details(self, lay, cx, sh_y, back):
        y, c = int(sh_y), int(cx)
        red = 8
        if back:
            plot(lay, [(c, y + k) for k in range(1, 9)], red)
            plot(lay, [(c - k, y + 4) for k in range(2, 5)] + [(c + k, y + 4) for k in range(2, 5)], red)
        else:
            plot(lay, [(c - 4, y + 4), (c - 3, y + 5), (c - 2, y + 5), (c - 1, y + 5), (c + 1, y + 5), (c + 2, y + 5), (c + 3, y + 5), (c + 4, y + 4)], red)
            plot(lay, [(c, y + k) for k in range(5, 10)], red)
            plot(lay, [(c - 2, y + 7), (c - 1, y + 7), (c + 1, y + 7), (c + 2, y + 7)], red)
            plot(lay, [(c - 2, y + 9), (c - 1, y + 9), (c + 1, y + 9), (c + 2, y + 9)], red)
            plot(lay, [(c - 4, y + 7), (c - 4, y + 8), (c + 4, y + 7), (c + 4, y + 8)], 7)

    def side_details(self, lay, sh):
        x, y = int(sh[0]), int(sh[1])
        plot(lay, [(x - 1, y + 5), (x, y + 5), (x + 1, y + 5), (x - 1, y + 7), (x, y + 7)], 8)

    def leg_details(self, lay, hx, hy, kx, ky, side=False):
        y = int(ky if side else (hy + ky) / 2)
        for x in range(32):
            v = lay.idx[y, x]
            if v:
                lay.idx[y, x] = 7 if v == 4 else 8

    def arm_details(self, lay, sx, sy, hx, hy):
        # red muscle at the armpit and elbow, plates elsewhere
        bands = [int(sy + (hy - sy) * 0.30), int(sy + (hy - sy) * 0.55)]
        for y in bands:
            for x in range(32):
                v = lay.idx[y, x]
                if v:
                    lay.idx[y, x] = {4: 7, 5: 8, 6: 8}.get(int(v), v)


def armored():
    rows = [(7.6, 7.6), (7.2, 7.2), (6.4, 6.4), (5.8, 5.8), (5.4, 5.4), (5.0, 5.0), (4.8, 4.8), (4.8, 4.8), (5.0, 5.0), (5.0, 5.0), (4.6, 4.6)]
    side = [(3.4, 4.2), (4.0, 4.4), (4.2, 4.2), (4.0, 4.0), (3.6, 3.6), (3.4, 3.4), (3.4, 3.4), (3.5, 3.6), (3.6, 3.8), (3.4, 3.8), (3.0, 3.4)]
    return Armored(torso_rows=rows, side_rows=side, leg=10.0, torso=8.0, sh=7.0, hip=2.8,
                   r_leg=(2.4, 1.9), r_arm=(2.2, 1.8), arm=9.5,
                   ramps={'leg': ARMOR, 'foot': ARMOR, 'torso': ARMOR, 'arm': ARMOR, 'hand': ARMOR, 'neck': MUSCLE},
                   heads={'front': (AR_FRONT, AR_CMAP, 0, 0), 'back': (AR_BACK, AR_CMAP, 0, 0), 'side': (AR_SIDE, AR_CMAP, -1, 0)})


def sheet_preview(t, path):
    f = t.frames()
    order = [k for k in f if k.startswith('front')] + [k for k in f if k.startswith('side')] + [k for k in f if k.startswith('back')]
    preview([(k, f[k]) for k in order], path, pal=1, scale=5, cols=4)


if __name__ == '__main__':
    D = ''
    sheet_preview(titan_a(), D + 'titan_a2.png')
    sheet_preview(titan_b(), D + 'titan_b.png')
    sheet_preview(smiling(), D + 'smiling.png')
    sheet_preview(armored(), D + "armored.png")


# ---------------------------------------------------------------- Garrison soldier / Hannes (adult humans, 16x32 SMS)
HSKIN = Ramp([5, 6, 6], [0.05, 0.35])
JACKET = Ramp([4, 5, 6], [0.20, 0.80])
PANTS = Ramp([3, 14, 14], [0.30, 0.5])
BOOTS = Ramp([15, 4, 4], [0.2, 0.7])
SO_CMAP = {'R': 4, 'r': 15, 'S': 5}
HN_CMAP = {'R': 12, 'r': 5, 'S': 5}
SO_FRONT = [
".rRRRr.",
"rRRRRRr",
"RRHHHRR",
"RHKHKHR",
".HHHHH.",
"..SHS..",
]
SO_BACK = [
".rRRRr.",
"rRRRRRr",
"RRRRRRR",
"RRRRRRR",
".RRRRR.",
"..SSS..",
]
SO_SIDE = [
"..rRRr.",
".RRRRRr",
"HHRRRRR",
"KHHSRRR",
"HHHHRR.",
".HHS...",
]
HN_FRONT = [
".rRRRr.",
"rRRRRRr",
"RRHHHRR",
"RHKHKHR",
".HSSSH.",
"..SHS..",
]
HN_SIDE = [
"..rRRr.",
".RRRRRr",
"HHRRRRR",
"KHHSRRR",
"SSHHRR.",
".SHS...",
]


class Soldier(Titan):
    def leg_details(self, lay, hx, hy, kx, ky, side=False):
        # boots from mid-shin down, blade box on the hip (faction colour), thigh strap
        top = int(hy + (FEET - hy) * 0.62)
        for y in range(top, 32):
            for x in range(32):
                v = lay.idx[y, x]
                if v in (3, 14):
                    lay.idx[y, x] = 4 if v == 14 else 15
        y = int(hy + 2)
        for x in range(32):
            if lay.idx[y, x] in (3, 14):
                lay.idx[y, x] = 4

    def torso_details(self, lay, cx, sh_y, back):
        y, c = int(sh_y), int(cx)
        # belt and blade boxes (faction colours) at the hips
        plot(lay, [(c + k, y + 5) for k in range(-3, 4)], 15)
        plot(lay, [(c - 4, y + 6), (c - 4, y + 7), (c + 4, y + 6), (c + 4, y + 7)], 8)
        plot(lay, [(c - 4, y + 8), (c + 4, y + 8)], 9)
        if not back:
            plot(lay, [(c, y + 1), (c, y + 2)], 14)  # shirt opening

    def side_details(self, lay, sh):
        x, y = int(sh[0]), int(sh[1])
        plot(lay, [(x + k, y + 5) for k in range(-1, 3)], 15)
        plot(lay, [(x + 1, y + 6), (x + 2, y + 6), (x + 3, y + 6), (x + 1, y + 7), (x + 2, y + 7), (x + 3, y + 7)], 8)
        plot(lay, [(x + 4, y + 2), (x + 4, y + 3), (x + 4, y + 4)], 9)   # gas canister on the back


def soldier(hannes=False):
    rows = [(4.2, 4.2), (4.0, 4.0), (3.8, 3.8), (3.6, 3.6), (3.5, 3.5), (3.5, 3.5)]
    side = [(2.0, 2.4), (2.4, 2.4), (2.4, 2.2), (2.2, 2.2), (2.1, 2.1), (2.1, 2.2)]
    cm = HN_CMAP if hannes else SO_CMAP
    front = HN_FRONT if hannes else SO_FRONT
    sidev = HN_SIDE if hannes else SO_SIDE
    return Soldier(torso_rows=rows, side_rows=side, leg=9.0, torso=6.0, sh=3.6, hip=1.5,
                   r_leg=(1.4, 1.2), r_arm=(1.1, 0.9), arm=6.5, foot=0.9, hand=0.7, neck=(1.0, 1.2),
                   ramps={'leg': PANTS, 'foot': BOOTS, 'torso': JACKET, 'arm': JACKET, 'hand': HSKIN, 'neck': HSKIN},
                   heads={'front': (front, cm, 0, 0), 'back': (SO_BACK, cm, 0, 0), 'side': (sidev, cm, 0, 0)})


if __name__ == '__main__':
    D = ''
    sheet_preview(soldier(), D + 'soldier.png')
    f = soldier(True).frames()
    preview([(k, f[k]) for k in ('front0', 'front1', 'side0', 'side1', 'back0')], D + 'hannes.png', pal=0, scale=5, cols=5)
