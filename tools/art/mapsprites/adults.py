"""Garrison soldier and Hannes map sprites, hand-drawn (11x18, shown as 16x32 SMS)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE = {'.': 0, 'O': 15, 'S': 6, 's': 5, 'E': 15, 'D': 13,
        'J': 5, 'j': 4, 'L': 6,          # tan Garrison jacket
        'W': 14,                         # shirt
        'P': 14, 'p': 3,                 # white trousers (shade takes the faction tint)
        'B': 4, 'b': 15,                 # boots, straps
        'X': 8, 'x': 9}                  # ODM blade boxes in the faction colour
COLORS = {
    'garrison': dict(BASE, H=4, h=15),
    'hannes':   dict(BASE, H=12, h=5),
}

FRONT = [
"...OOOOO...",
"..OHHHHHO..",
".OHHHHHHHO.",
".OHSSSSShO.",
".OSESSSESO.",
"..OSSsSSO..",
"..OJOSOJO..",
".OJJJWJJJO.",
"OJJLJWJJjjO",
"OSOLJWJjOSO",
"OSOJJWJjOSO",
".OXbbbbbXO.",
".OxPPbPPxO.",
"..OPPOPpO..",
"..OPbOPbO..",
"..OBBOBBO..",
"..ObbObbO..",
".DDDDDDDDD.",
]
FRONT_STEP = FRONT[:13] + [
"..OPPOPpO..",
"..OPbOPBO..",
"..OBBOObO..",
"..ObbO.....",
".DDDDDDDDD.",
]
SIDE = [
"...OOOOO...",
"..OHHHHHO..",
".OhHHHHHHO.",
".OhHHHSSSO.",
".OhHHSSESO.",
"..OHSSSsO..",
"...OJSJO...",
"..OJJJJJO..",
"..OJLJJjO..",
"..OXLJjjO..",
"..OXSJjO...",
"..ObbbbO...",
"...OPPPO...",
"...OPPpO...",
"...OPbpO...",
"...OBBBO...",
"...ObbbbO..",
"..DDDDDDD..",
]
SIDE_STEP = SIDE[:12] + [
"..OPPPPO...",
".OPPOOPPO..",
".OPbO.OPbO.",
".OBBO.OBBO.",
"ObbbO.ObbbO",
"..DDDDDDD..",
]
BACK = [
"...OOOOO...",
"..OHHHHHO..",
".OHHHHHHHO.",
".OHHHHHHHO.",
".OHHHHHHHO.",
"..OHHHHHO..",
"..OJSSSJO..",
".OJJJJJJJO.",
"OJJXJJJXJjO",
"OSOXJJJXOSO",
"OSOJJJJjOSO",
".OXbbbbbXO.",
".OxPPbPPxO.",
"..OPPOPpO..",
"..OPbOPbO..",
"..OBBOBBO..",
"..ObbObbO..",
".DDDDDDDDD.",
]
BACK_STEP = BACK[:13] + [
"..OPPOPpO..",
"..OPbOPBO..",
"..OBBOObO..",
"..ObbO.....",
".DDDDDDDDD.",
]
HANNES_FRONT = FRONT[:5] + ["..OSssSSO.."] + FRONT[6:]   # stubble
HANNES_FRONT_STEP = HANNES_FRONT[:13] + FRONT_STEP[13:]

FRAMES = {
    'garrison': {'front': FRONT, 'front_step': FRONT_STEP, 'side': SIDE, 'side_step': SIDE_STEP, 'back': BACK, 'back_step': BACK_STEP},
    'hannes': {'front': HANNES_FRONT, 'front_step': HANNES_FRONT_STEP, 'side': SIDE, 'side_step': SIDE_STEP, 'back': BACK, 'back_step': BACK_STEP},
}
