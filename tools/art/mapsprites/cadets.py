"""104th Cadet Corps map sprites (chapter 2) and the wooden Titan training dummy.

Cadets wear the same uniform as the Garrison soldier in adults.py (tan jacket,
white trousers, ODM gear), with their own hair and the Training Corps crossed
swords on the back. 16 wide x 22 tall, shown as 16x32 SMS.
"""
import adults
from adults import BASE, FRONT, SIDE, SIDE_STEP, BACK

HEADS = {
'eren': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHHHHHHO...",
"..OHHHHHHHHHHO..",
"..OHhHHhHHhHHO..",
"..OhSHSSSSHShO..",
"...OSESSSSESO...",
"...OSSSSSSSSO...",
"....OSSSSSSO....",
],
'mikasa': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHHHHHHO...",
"..OHHHHHHHHHHO..",
"..OHHhHHHHhHHO..",
"..OHSSSSSSSSHO..",
"..OHSESSSSESHO..",
"..OHSSSSSSSSHO..",
"..OHHOSSSSOHHO..",
],
'armin': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHHHHHHO...",
"..OHHHHHHHHHHO..",
"..OHHHHhHHHHHO..",
"..OHhSSSSSShHO..",
"..OHSESSSSESHO..",
"..OHSSSSSSSSHO..",
"...OhSSSSSShO...",
],
'jean': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHHHHHHO...",
"...OHHHHHHHHO...",
"...OhHHHHHHhO...",
"...OhSSHSSShO...",
"...OSESSSSESO...",
"...OSSSSSSSSO...",
"....OSSSSSSO....",
],
'cadet': FRONT[:9],
}

COLORS = {
    'eren':   dict(BASE, H=4, h=15, T=6),
    'mikasa': dict(BASE, H=15, h=1, T=6),
    'armin':  dict(BASE, H=12, h=5, T=6),
    'jean':   dict(BASE, H=5, h=4, T=6),
    'cadet':  dict(BASE, H=4, h=15, T=6),
}

# Training Corps emblem (two crossed swords) on the back of the jacket.
CADET_BACK = BACK[:12] + ["..OJJJWJJWJjjO..", "..OJJJJWWJJjjO..", "..OSOJWJJWjOSO.."] + BACK[15:]
SCARF_FRONT = ["...OHRRRRRRHO...", "...ORRRWWRRRO..."]
SCARF_SIDE = ["......ORRRRO....", ".....ORRRRO....."]
SCARF_BACK = ["...OHRRRRRRHO...", "...ORRRRRRRRO..."]


def frames(who):
    front = HEADS[who] + FRONT[9:]
    side, side_step, back = list(SIDE), list(SIDE_STEP), list(CADET_BACK)
    if who == 'mikasa':
        front[9:11] = SCARF_FRONT
        side[9:11] = side_step[9:11] = SCARF_SIDE
        back[9:11] = SCARF_BACK
    step = front[:18] + adults.FRONT_STEP[18:]
    back_step = back[:18] + adults.FRONT_STEP[18:]
    t = dict(front=front, front_step=step, side=side, side_step=side_step, back=back, back_step=back_step)
    for f in t.values():
        assert len(f) == 22 and all(len(r) == 16 for r in f), (who, f)
    return t


FRAMES = {who: frames(who) for who in HEADS}

# ---------------------------------------------------------------- dummy
# Wooden Titan cut-out on a post, the nape marked with a red target patch.
DUMMY_COLORS = {'.': 0, 'O': 15, 'W': 5, 'w': 4, 'N': 9, 'D': 13, 'S': 6}
DUMMY = [
".....OOOOOO.....",
"....OWWWWWWO....",
"...OWWwWWwWWO...",
"...OWOOWWOOWO...",
"...OWWWWWWWWO...",
"...OWWOOOOWWO...",
"....OWWWWWWO....",
".....ONNNNO.....",
"..OOOOWWWWOOOO..",
".OWWWWWWWWWWWWO.",
".OwOOOWWWWOOOwO.",
".OO..OWWWWO..OO.",
".....OWwWWO.....",
".....OWWWwO.....",
".....OWWWWO.....",
"......OwwO......",
"......OwwO......",
"......OwwO......",
"......OwwO......",
"....OOOwwOOO....",
"...OwwwwwwwwO...",
"...DDDDDDDDDD...",
]
DUMMY_BACK = DUMMY[:3] + ["...OWWWWWWWWO...", "...OWWWWWWWWO...", "...OWWWWWWWWO...", "....OWWWWWWO....",
                          ".....ONNNNO....."] + DUMMY[8:]
assert all(len(r) == 16 for r in DUMMY + DUMMY_BACK) and len(DUMMY) == len(DUMMY_BACK) == 22
