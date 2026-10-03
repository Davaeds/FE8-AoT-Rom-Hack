"""Garrison soldier and Hannes map sprites, 16 wide x 22 tall (16x32 SMS).

Tan Garrison jacket over a white shirt, ODM gear boxes on the hips, white
trousers, brown boots. Only palette indices that look the same in every
faction palette are used (4, 5, 6, 11-15), so colours do not shift with allegiance.
"""

BASE = {'.': 0, 'O': 15, 'S': 6, 's': 5, 'E': 15, 'D': 13,
        'J': 5, 'j': 4, 'L': 6,       # jacket, jacket shade, jacket light
        'W': 14,                      # shirt
        'P': 14, 'p': 13,             # trousers and their shade
        'B': 4, 'b': 15,              # boots, straps
        'X': 13, 'R': 11}             # ODM gear boxes, Garrison rose
COLORS = {
    'garrison': dict(BASE, H=4, h=15, T='S'),
    'hannes':   dict(BASE, H=12, h=5, T='s'),
}

FRONT = [
"......OOOO......",
".....OHHHHO.....",
"....OHHHHHHO....",
"...OHHHHHHHHO...",
"...OHhHHHHhHO...",
"...OHSSSSSShO...",
"...OSESSSSESO...",
"...OSSSSSSSSO...",
"....OSTssTSO....",
".....OSSSSO.....",
"....OJOWWOJO....",
"...OJJJWWJJJO...",
"..OJJLJWWJJjjO..",
"..OJLLJWWJJjjO..",
"..OSOLJWWJjOSO..",
"..OSObbbbbbOSO..",
"..OXOPPbbPPOXO..",
"..OXOPPOOPpOXO..",
"....OPPOOPpO....",
"....OBBOOBbO....",
"....OBBOOBbO....",
"...DOOODDOOOD...",
]
FRONT_STEP = FRONT[:18] + [
"....OPPOOPpO....",
"....OBBOOPpO....",
"....OBBOOBbO....",
"...DOOODDOOOD...",
]
SIDE = [
"......OOOOO.....",
".....OHHHHHO....",
"....OHHHHHHHO...",
"....OhHHHHHHHO..",
"....OhHHHHSSSO..",
"....OhHHHSSSSO..",
"....OhHHSSSESO..",
".....OHSSSSSSO..",
".....OhSSTssO...",
"......OSSSSO....",
".....OJJWWO.....",
"....OJJJJWJO....",
"....OJLJJJjO....",
"....OJLJJjjO....",
"....OXOLJjjO....",
"....OXOSJjO.....",
"....OXbbbbbO....",
".....OPPPPpO....",
".....OPPPPpO....",
".....OBBOBbO....",
".....OBBOBbbO...",
"....DDDDDDDDD...",
]
SIDE_STEP = SIDE[:17] + [
"....OPPPOPpO....",
"...OPPO.OPpO....",
"...OBBO..OBbO...",
"...OBBbO.OBbbO..",
"...DDDDDDDDDD...",
]
BACK = [
"......OOOO......",
".....OHHHHO.....",
"....OHHHHHHO....",
"...OHHHHHHHHO...",
"...OHHHHHHHHO...",
"...OHhHHHHhHO...",
"...OHHHhhHHHO...",
"...OhHHHHHHhO...",
"....OHHHHHHO....",
".....OSSSSO.....",
"....OJJJJJJO....",
"...OJJJJJJJJO...",
"..OJJJRWWRJjjO..",
"..OJJJWRRWJjjO..",
"..OSOJJRRJjOSO..",
"..OSObbbbbbOSO..",
"..OXOPPPPPPOXO..",
"..OXOPPOOPpOXO..",
"....OPPOOPpO....",
"....OBBOOBbO....",
"....OBBOOBbO....",
"...DOOODDOOOD...",
]
BACK_STEP = BACK[:18] + FRONT_STEP[18:]


def _resolve(colors):
    """T is an alias (stubble for Hannes, plain skin for the soldier)."""
    c = dict(colors)
    c['T'] = c[c['T']]
    return c


FRAMES = {who: dict(front=FRONT, front_step=FRONT_STEP, side=SIDE, side_step=SIDE_STEP,
                    back=BACK, back_step=BACK_STEP) for who in COLORS}
COLORS = {who: _resolve(c) for who, c in COLORS.items()}
for _f in (FRONT, FRONT_STEP, SIDE, SIDE_STEP, BACK, BACK_STEP):
    assert len(_f) == 22 and all(len(r) == 16 for r in _f), _f
