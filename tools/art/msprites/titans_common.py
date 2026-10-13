"""Common Titans: 32x32 map sprites for the red (enemy) faction.

    titan_a  the classic common Titan: stocky, pudgy, short dark hair, fixed toothy grin
    titan_b  a lanky, hunched Titan: long shaggy hair, gaping mouth, long reaching arms
    smiling  the Smiling Titan: tall and slender, blond centre-parted hair, closed-lip smile

Each view is built from 32x32 layers drawn in frame coordinates and stacked
back to front (far arm, legs, torso, head, near arm). A layer can be offset
for the body bob, and can "selout": its outline pixels that land on another
body part become skin shade instead of the hard outline.
"""
import numpy as np
from kit import grid, shift
from titans_special import lift
from pal import LEGEND

O, K = LEGEND['o'], LEGEND['k']


def L(text, y=0, x=0):
    """A 32x32 layer from ASCII art whose first row sits at row y (column x)."""
    g = grid(text)
    out = np.zeros((32 + 64, 32 + 64), np.uint8)
    h, w = g.shape
    out[32 + y:32 + y + h, 32 + x:32 + x + w] = g
    return out[32:64, 32:64].copy()


def comp(*layers):
    """Stack layers back to front. A layer is an array or (array, dx, dy[, selout])."""
    out = np.zeros((32, 32), np.uint8)
    for item in layers:
        if item is None:
            continue
        if isinstance(item, tuple):
            a, dx, dy = item[:3]
            sel = item[3] if len(item) > 3 else None
            a = shift(a, dx, dy)
        else:
            a, sel = item, None
        if sel is not None:
            a = a.copy()
            a[(a == O) & (out != 0) & (out != O)] = sel
        m = a != 0
        out[m] = a[m]
    return out


# =====================================================================
# titan_a: the classic common Titan
# =====================================================================
A = {}

# ---- side view (facing left) -----------------------------------------
A['head_s'] = L('''
......oooooo
....oodbbbbddo
...odbbbbbddddo
..odbbSSbddbdddo
..oSSSSSSSSdbddo
.oSSSSSSSSsdkddo
.oSSoSSSoSssSkdo
.oSSSSsSSssskkdo
.okWWWWWWWWsskdo
.okoooooooookkdo
..oWwWwWwWwsskko
...oSSSSSSsskko
....ookkkkkkoo
''')
A['torso_s'] = L('''
..............oooo
............ooSSssoo
..........ooSSSSsssko
........ooSSSSSSssskko
.......oSSSSSSSSsssskko
......oSSSSSSSSSsssskko
......oSssSSSSSSsssskko
.....oSSSSSsSSSssssskko
.....oSSSSSSSSSssssskko
.....oSSSSSSSSsssssskko
.....oSSSSkSSSsssssskkko
.....oSSSSSSSssssssskkko
......okSSSSsssssskkkko
.......okksssssskkkkoo
........oookkkkkoooo
''', 10)
A['near_s'] = {
    'hang': L('''
..............oooooo
.............oSSSSsko
.............oSSSsskko
.............oSSSsskko
.............oSSssko
............oSSssko
............oSSsko
............oSSsko
...........oSSsko
...........oSSsko
...........oSSsko
..........oSSSsko
..........oSSSsko
..........oSoSoko
...........o.o.o
''', 11),
    'fwd': L('''
..............oooooo
.............oSSSSsko
.............oSSSsskko
............oSSSsskko
...........oSSSssko
..........oSSssko
.........oSSssko
.........oSSsko
........oSSsko
........oSSsko
.......oSSSsko
.......oSSSsko
.......oSoSoko
........o.o.o
''', 11),
    'back': L('''
..............oooooo
.............oSSSSsko
.............oSSSsskko
.............oSSSsskko
.............oSSssko
.............oSSsko
.............oSSsko
..............oSSsko
..............oSSsko
..............oSSsko
..............oSSSsko
..............oSSSsko
..............oSoSoko
...............o.o.o
''', 11),
}
A['far_s'] = {
    'reach': L('''
........oo
......ooskko
....oosskkko
..oosskkoo
.osskkoo
osssko
oSssko
oSoSko
.o.o.o
''', 13),
}
A['legs_s'] = {
    'stand': L('''
.......osssssssskkko
......oSSSSssoSSsskko
.....oSSSSssooSSSsskko
.....oSSSsso.oSSSsskko
.....oSSSsko..oSSsskko
.....oSSsko...oSSssko
....oSSSsko...oSSssko
...oSSSssko..oSSsssko
...ooooooo...oooooooo
....________________
''', 22),
    'cA': L('''
.......ossssssskkkko
......osssssssoSSSsko
.....osssskkooSSSsskko
....ossskko..oSSSsskko
...ossskko....oSSSssko
...osskko......oSSssko
..osssko.......oSSsko
.oSsssko.......oSSsko
.ooooooo.......ooooo
..___________________
''', 22),
    'p1': L('''
.......ossssssskkkko
.......ossssoSSSsskko
.......osssoSSSssskko
......osskoSSSsssko
......ossoSSSssko
.......oooSSSsko
.........oSSSsko
........oSSSssko
........ooooooo
......____________
''', 22),
    'cB': L('''
.......ossssssskkkko
......oSSSSSsssssskko
.....oSSSSsoossssskko
....oSSSsso..ossskko
...oSSSsso....ossko
...oSSsso.....osskko
..oSSSsko......osskko
.oSSSssko......ossko
.oooooooo......oooo
..___________________
''', 22),
    'p2': L('''
.......ossssssskkkko
.......oSSSSSssssskko
.......oSSSSsosssskko
.......oSSSso.osskko
.......oSSSso.ossko
.......oSSSso..ooo
.......oSSSsko
......oSSSsssko
......ooooooooo
......____________
''', 22),
}

# ---- front view (walking down / selected) -----------------------------
A['head_f'] = L('''
...........oooooooooo
.........oodbbbbbbdddoo
........odbbbbbbbbbddddo
........odbbbbbbbddbdddo
........oddSSSSSSSSSSddo
........odSSSSSSSSSSssdo
........oSSSSSSSSSSSSsko
........oSSSoSSSSSSoSsko
........oSSSSSSssSSSSsko
........okWWWWWWWWWWWWko
........okooooooooooookko
........okWwWwWwWwWwWwko
.........oSSSSSSSSSsssko
..........oooooooooooo
''')
A['torso_f'] = L('''
..........oSSSSSSSSSsso
........ooSSSSSSSSSSsssoo
......ooSSSSSSSSSSSSssskkoo
......oSSSSSSSSSSSSSsssskko
......oSSSSSSSSSSSSSssssskko
.......oSssSSSSSSSssssskko
.......oSSSssSSSSsssssskko
.......oSSSSSSSSSSssssskko
.......oSSSSSSSSSssssssko
.......oSSSSSSSkSsssssko
........oSSSSSSSsssssko
........okSSSSSsssskkko
.........okkssssskkkoo
..........ooookkkkooo
''', 12)
A['arm_l'] = {
    'hang': L('''
.......oo
......oSSo
.....oSSSso
.....oSSsko
....oSSsko
....oSSsko
....oSSko
....oSSko
...oSSsko
...oSSsko
...oSSsko
...oSoSko
....o.o.
''', 13),
}
A['arm_r'] = {
    'hang': L('''
.....................oo
.....................oSso
.....................ossko
.....................osskko
......................osskko
......................osskko
.......................oskko
.......................oskko
.......................osskko
.......................osskko
.......................osskko
.......................oskoko
........................o.o.
''', 13),
}
A['legs_f'] = {
    'stand': L('''
.........oSSSSSSSssssskko
.........oSSSSSSsoSSssskko
.........oSSSSSso.oSSssko
.........oSSSSso..oSSssko
..........oSSsko..oSSsko
..........oSSsko..oSSsko
.........oSSSsko..oSSssko
........oSSSssko..oSSsssko
........oooooooo..oooooooo
.........________________
''', 22),
}

# ---- back view (walking up) ------------------------------------------
A['head_b'] = L('''
...........oooooooooo
.........oodbbbbbbdddoo
........odbbbbbbbbbddddo
........odbbbbbbbbdddddo
........odbbbbbbbddddddo
........odbbbbbbdddddddo
........odbbbbbddddddddo
........osdbbbdddddddddo
........oSsdddddddddddko
........oSSsddddddddddko
.........oSSssddddddsko
.........oSSSsssssssko
..........okSssssskkoo
..........oooooooooooo
''')
A['torso_b'] = L('''
..........oSSSSSSSSsso
........ooSSSSSSSSSSsssoo
......ooSSSSSSSSSSSSssskkoo
......oSSSskSSSSSSksssskkko
......oSSSSSkSSSSkssssssko
.......oSSSSSSSkSSsssssko
.......oSSSSSSSkSsssssskko
.......oSSSSSSSkSsssssko
.......oSSSSSSSkSssssko
........oSSSSSSkSsssko
........oSSSSSSksssssko
........okSSSSskssskkko
.........okkssskssskkoo
..........ooookkkkooo
''', 12)


# =====================================================================
# titan_b: lanky, hunched, long shaggy hair, gaping mouth
# =====================================================================
B = {}

B['head_s'] = L('''
.....oooooo
...oobBBBbboo
..obBBBBBbbbbo
.obBBBbbbbbbbdo
obBbbBbbbbbdbdo
obbSbbSbbbdbbdo
obSSSSSSbbdbbdo
oSSoSSSSsbdbdbo
oSSSSSSssbdbbdo
oSSSSSsssbdbdo
okWWWWosskbdbdo
onnnnnosskbdbdo
onGGGnnoskbbdbdo
onnnnnoskkbdbdo
.oSSSsskkbdbbdo
..oookkkobdbdo
......obdbobdo
.......obo.oo
........o
''', 3, 0)
B['torso_s'] = L('''
..........ooooo
........ooSSSssoo
.......oSSSSSssskoo
......oSSSSSSsssskoo
......oSSSSSSssssskko
.......oSSSSSsssssskko
........ooSSSSssssssko
..........oSSSSssssskko
...........oSSSsssssskko
............oSSSssssskko
.............oSSsssssskko
.............oSSssssssskko
..............oSssssssskko
..............okssssssskko
...............okkkkkkkkoo
................oooooooo
''', 6)
B['near_s'] = {
    'hang': L('''
..........oooo
.........oSSsko
........oSSssko
........oSSsko
.......oSSsko
.......oSSko
......oSSsko
......oSSko
.....oSSsko
.....oSSko
.....oSSko
....oSSsko
....oSSSko
....oSoSoko
.....o.o.o
''', 9),
}
B['far_s'] = {
    'hang': L('''
.........ooo
........osko
.......oskko
.......osko
......oskko
......osko
.....oskko
.....osko
....oskko
....osko
....osko
...oskko
...osko
...osoko
....o.o
''', 10, -2),
}
B['legs_s'] = {
    'stand': L('''
...............oSSSsssskko
..............oSSSSssssskko
.............oSSSssoSssskko
............oSSSsso.oSsskko
............oSSsko..oSsskko
............oSSko...oSsskko
............oSSko....oSsko
............oSSko....oSssko
............oSSko.....oSsko
...........oSSsko.....oSsko
..........oSSssko....oSSssko
..........ooooooo....ooooooo
..........__________________
''', 19),
}

B['head_f'] = L('''
.....oooooo
...oobBBBbboo
..obBBBBBBbbbo
.obBBbbbbbbbbbo
.obbbbbbbbbbbdo
obbbSbbSSbbSbbdo
obbSSSSSSSSSSbdo
obbSoSSSSSSoSbdo
obdSSSSSSSSSsbdo
obdSSSSssSSSsbdo
obdSSkoooooksbdo
obddSoWWWWWosbdo
obbdSonnnnnosbdo
obddSonGGGnosddo
obdbSSonnnosSdbo
.obdbSSoooosdbo
..odbdoSSSsodbo
...odbo....odbo
....oo......oo
''', 4, 8)
B['torso_f'] = L('''
...........oooooooooo
.........ooSSSSSSSSSSsoo
.......ooSSSSSSSSSSSSsssoo
.....ooSSSSSSSSSSSSSSssssko
....oSSSSSSSSSSSSSSSSsssskko
....oSSSSSSSSSSSSSSSSssssskko
.....oSSSSSSSSSSSSSSsssssko
......oSSSSSSSSSSSSssssskko
.......oSSSSSSSSSSssssskko
........oSSSSSSSSSsssskko
.........oSSSSSSSssssko
.........oSSSSSSSssssko
.........oSSSSSSsssssko
.........oSSSSSSsssssko
.........oSSSSSsssssko
.........oSSSSSssssskko
.........okSSSSssssskko
..........okkssssskkko
...........oookkkkooo
''', 3)
B['arm_l'] = {
    'hang': L('''
.....ooo
....oSSso
....oSSsko
....oSSko
....oSSko
....oSSko
...oSSsko
...oSSko
...oSSko
...oSSko
...oSSko
..oSSsko
..oSSko
..oSSko
..oSSko
..oSSsko
.oSSSsko
.oSoSoko
..o.o.o
''', 7),
}
B['arm_r'] = {
    'hang': L('''
.......................ooo
......................osskoo
......................osskko
.......................oskko
.......................oskko
.......................oskko
.......................osskko
........................oskko
........................oskko
........................oskko
........................oskko
........................osskko
.........................oskko
.........................oskko
.........................oskko
.........................osskko
.........................ossskko
.........................oskoskko
..........................o.o.o
''', 7),
}
B['legs_f'] = {
    'stand': L('''
..........oSSSSSSSssssskko
..........oSSSSSSsoSssskko
.........oSSSSSso.oSSsskko
.........oSSSsso...oSsskko
.........oSSsko....oSssko
.........oSSko......oSsko
.........oSSko......oSsko
.........oSSko......oSsko
.........oSSko......oSsko
........oSSsko......oSssko
.......oSSssko......oSsssko
.......ooooooo......ooooooo
.......__________________
''', 19),
}
B['head_b'] = L('''
.....oooooo
...oobBBBbboo
..obBBBBBBbbbo
.obBBbbbbbbbbbo
.obbbbbbbbbbbdo
obbbbbbbbbbbbbdo
obbbbbbbbbbbbddo
obbdbbbbbbbbdbdo
obdbbdbbbbdbbddo
''', 0, 8)
B['torso_b'] = L('''
...........oooooooooo
.........ooSSSSSSSSSSsoo
.......ooSSSSSSSSSSSSsssoo
.....ooSSSSSSSSSSSSSSssssko
....oSSSSSSSSSSkSSSSSsssskko
....oSSSSkSSSSSkSSSSkssssskko
.....oSSSSkSSSSkSSSkssssssko
......oSSSSSSSSkSSSsssssskko
.......oSSSSSSSkSSssssssko
........oSSSSSSkSSsssskko
.........oSSSSSkSssssko
.........oSSSSSkSssssko
.........oSSSSSkSssssko
.........oSSSSSkssssssko
.........oSSSSSkssssko
.........oSSSSSksssskko
.........okSSSSkssssskko
..........okksssksskkko
...........oookkkkooo
''', 6)

# =====================================================================
# smiling: the Smiling Titan
# =====================================================================
C = {}
C['head_s'] = L('''
.....ooooooo
...ooYYYYYBBoo
..oYYYYYYBBBBBo
.oYYYYYBYYYYBBBo
.oYYYSSBBYYYYBBo
oYYSSSSSBYYYYBBo
oYSkSSkSSBYYBBBo
oYWoSWoSSsYYYBBo
oYSSSSSSssYYYBBo
oYkSSSSSsskYBBBo
oBSkSSSSkkYYBBBo
oBSSkkkksYYBBBBo
.oSSSSSSsYBBBBo
..oookksoYBBBo
.......oooooo
''', 0, 3)
C['torso_s'] = L('''
...........oSso
..........oSsko
........ooSSskoo
.......oSSSSsskko
......oSSSSSssskko
......oSSSSSssskko
......oSSSSsssskko
.......oSSSsssskko
.......oSSSssskko
.......oSSSssskko
.......oSSsssskko
.......oksssskkko
........ookkkkoo
..........oooo
''', 12)
C['near_s'] = {
    'hang': L('''
............ooo
...........oSSso
...........oSssko
...........oSsko
...........oSsko
...........oSsko
...........oSsko
...........oSsko
............oSko
............oSsko
............oSsko
............oSsko
............oSSko
............oSoSo
.............o.o
''', 14),
}
C['far_s'] = {
    'hang': L('''
.......oo
......osko
......osko
.....osko
.....osko
.....osko
....osko
....osko
....osko
....oosko
.....oko
''', 15),
}
C['legs_s'] = {
    'stand': L('''
........oSSSssskko
.......oSSSSsssskko
.......oSSSsoSsskko
.......oSSso.oSssko
.......oSSso.oSssko
.......oSSso..oSsko
.......oSSso..oSsko
.......oSSso..oSsko
......oSSsko..oSsko
......oSSso...oSssko
.....oSSsko..oSSssko
.....oooooo..ooooooo
.....______________
''', 19),
}
C['head_f'] = L('''
...........oooooooooo
.........ooYYYYYBYYYYoo
........oYYYYYYBSBYYYYYo
.......oYYYYYYBSSSBYYYYBo
.......oYYYYYBSSSSSBYYYBo
.......oYYYYBSSSSSSSBYYBo
.......oYYYBSSSSSSSSSBYBo
.......oYYBSkkSSSSkkSsBBo
.......oYYSWoSSSSSWoSsBBo
.......oYBSSSSSSSSSSSsBBo
.......oYBkSSSSSSSSSskBBo
.......oYBSkkSSSSSSkksBBo
.......oYBSSskkkkkksSBBBo
.......oYBBSSSSSSSSsBBBBo
.......oYBBoSSSSSssoBBBBo
.......oooo.oooooooo.oooo
''')
C['torso_f'] = L('''
.............oSSSSso
...........ooSSSSSssoo
.........ooSSSSSSSSssskoo
........oSSSSSSSSSSsssskko
........oSSSSSSSSSSsssskko
.........oSssSSSSSsssskko
.........oSSSSSSSSsssskko
.........oSSSSSSSSssssko
..........oSSSSSSsssssko
..........oSSSSSkSsssko
..........oSSSSSSssssko
..........okSSSSsssskko
...........okkssssskkoo
............ooookkkoo
''', 13)
C['arm_l'] = {
    'hang': L('''
........oo
.......oSSo
......oSSsko
......oSSko
......oSSko
......oSSko
......oSSko
......oSsko
.....oSSko
.....oSSko
.....oSsko
.....oSSko
.....oSoSo
......o.o
''', 14),
}
C['arm_r'] = {
    'hang': L('''
.......................oo
.......................osoo
......................osskko
.......................oskko
.......................oskko
.......................oskko
.......................oskko
.......................oskko
........................oskko
........................oskko
........................oskko
........................oskko
........................oskoko
.........................o.o
''', 14),
}
C['legs_f'] = {
    'stand': L('''
..........oSSSSSSsssskko
..........oSSSSSsoSsssko
..........oSSSSso.oSsssko
..........oSSSso..oSssko
..........oSSSso..oSssko
..........oSSso...oSsko
..........oSSso...oSsko
..........oSSso...oSsko
.........oSSsso...oSssko
.........oSSsso...oSssko
........oSSssko...oSsssko
........ooooooo...ooooooo
........_________________
''', 19),
}
C['head_b'] = L('''
...........oooooooooo
.........ooYYYYYYYYYYoo
........oYYYYYYYYYYYYYBo
.......oYYYYYYYYYYYYYYBBo
.......oYYYYYYYYYYYYYBBBo
.......oYYYYYYYYYYYYYBBBo
.......oYYYYYYYYYYYYBBBBo
.......oYYYYYYYYYYYBBBBBo
.......oYYYYYYYYYYYBBBBBo
.......oYYYBYYYYYBYBBBBBo
.......oYYYBYYYYYBYBBBBBo
.......oYYBBYYYYBBYBBBBBo
.......oYYBYYBYYBYBBBBBBo
.......oYBBYBBYBBYBBBBBBo
.......oYBoYBoYBoYoBBoBBo
.......ooo.oo.oo.oo.oo.oo
''')
C['torso_b'] = L('''
.............oSSSSso
...........ooSSSSSssoo
.........ooSSSSSSSSssskoo
........oSSSkSSSSSSksssskko
........oSSSSkSSSSkssssskko
.........oSSSSSSkSsssssko
.........oSSSSSSkSssssko
.........oSSSSSSkSssssko
..........oSSSSSkSsssko
..........oSSSSSkSsssko
..........oSSSSSkssssko
..........okSSSSkssskko
...........okksssksskoo
............ooookkkoo
''', 13)


def _side(d, legs='stand', near='hang', far='reach', dy=0, head='head_s', hd=(0, 0)):
    return comp((d['far_s'][far], 0, dy), d['legs_s'][legs], (d['torso_s'], 0, dy, K),
                (d[head], hd[0], dy + hd[1]), (d['near_s'][near], 0, dy))


def _front(d, legs='stand', al='hang', ar='hang', dy=0, dx=0, head='head_f', hd=(0, 0),
           torso='torso_f', head_first=False):
    h = (d[head], dx + hd[0], dy + hd[1])
    return comp(d['legs_f'][legs], h if head_first else None, (d[torso], dx, dy, K),
                (d['arm_l'][al], dx, dy), (d['arm_r'][ar], dx, dy), None if head_first else h)


def titan_a():
    d = A
    sms = [_side(d), _side(d, dy=1), _side(d, dy=1, hd=(-1, 0))]
    left = [_side(d, 'cA', 'back'), _side(d, 'p1', 'hang', dy=-1),
            _side(d, 'cB', 'fwd'), _side(d, 'p2', 'hang', dy=-1)]
    down = [_front(d), _front(d, dy=-1), _front(d), _front(d, dy=-1)]
    bk = dict(head='head_b', torso='torso_b')
    up = [_front(d, **bk), _front(d, dy=-1, **bk), _front(d, **bk), _front(d, dy=-1, **bk)]
    sel = [_front(d), _front(d, dy=1), _front(d, dy=1, hd=(0, 1))]
    return dict(sms=sms, left=left, down=down, up=up, sel=sel)


def titan_b():
    d = B
    s = lambda **k: _side(d, far='hang', **k)
    sms = [s(), s(dy=1), s(dy=1, hd=(0, 1))]
    left = [s(), s(dy=-1), s(), s(dy=-1)]
    down = [_front(d), _front(d, dy=-1), _front(d), _front(d, dy=-1)]
    bk = dict(head='head_b', torso='torso_b', head_first=True)
    up = [_front(d, **bk), _front(d, dy=-1, **bk), _front(d, **bk), _front(d, dy=-1, **bk)]
    sel = [_front(d), _front(d, dy=1), _front(d, dy=1, hd=(0, 1))]
    return dict(sms=sms, left=left, down=down, up=up, sel=sel)


def smiling():
    d = C
    s = lambda **k: _side(d, far='hang', **k)
    sms = [s(), s(dy=1), s(dy=1, hd=(1, 0))]
    left = [s(), s(dy=-1), s(), s(dy=-1)]
    down = [_front(d), _front(d, dy=-1), _front(d), _front(d, dy=-1)]
    bk = dict(head='head_b', torso='torso_b')
    up = [_front(d, **bk), _front(d, dy=-1, **bk), _front(d, **bk), _front(d, dy=-1, **bk)]
    sel = [_front(d), _front(d, dy=1), _front(d, dy=1, hd=(0, 1))]
    return dict(sms=sms, left=left, down=down, up=up, sel=sel)


BUILD = {'titan_a': titan_a, 'titan_b': titan_b, 'smiling': smiling}

# Shin regions (x0, x1, y0, y1) lifted on walk frames 1 and 3, so the feet
# alternate: (first lifted leg, second lifted leg) per view.
STEPS = {
    'titan_a': {'down': ((8, 15, 26, 30), (18, 25, 26, 30)), 'up': ((8, 15, 26, 30), (18, 25, 26, 30))},
    'titan_b': {'left': ((10, 17, 26, 30), (20, 28, 26, 30)),
                'down': ((7, 14, 26, 30), (19, 27, 26, 30)), 'up': ((7, 14, 26, 30), (19, 27, 26, 30))},
    'smiling': {'left': ((5, 11, 26, 30), (13, 19, 28, 30)),
                'down': ((9, 15, 27, 30), (18, 25, 27, 30)), 'up': ((9, 15, 27, 30), (18, 25, 27, 30))},
}


def frames(name):
    f = BUILD[name]()
    for view, (first, second) in STEPS[name].items():
        f[view][1] = lift(f[view][1], *first)
        f[view][3] = lift(f[view][3], *second)
    return f
