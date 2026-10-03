"""Kid map sprites (Eren, Mikasa, Armin), full 16x16 FE-style frames.

Letters map to FE8 map-sprite palette indices (blue player palette):
1 dark purple, 3 pale blue-white, 4 brown-grey, 5 tan, 6 cream skin, 7-10 blues,
11 red, 12 yellow, 13 shadow, 14 white, 15 outline.
Rows: hair and head 0-9, body 10-13, legs 14, feet and ground shadow 15.
"""

BASE = {'.': 0, 'O': 15, 'S': 6, 's': 5, 'E': 15, 'D': 13, 'W': 14, 'w': 3}

COLORS = {
    'eren':   dict(BASE, H=4, h=15, L=4, C=14, c=3, P=5, p=4, B=15, R=4),
    'mikasa': dict(BASE, H=15, h=1, L=4, C=6, c=5, P=1, p=15, B=15, R=11),
    'armin':  dict(BASE, H=12, h=5, L=14, C=5, c=4, P=4, p=15, B=15, R=4),
}

HEAD_ROWS = 10

# ---------------------------------------------------------------- Eren
# Shaggy dark brown hair with pointed bangs, white shirt, tan trousers.
EREN = {
'front': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHLLHHHO...",
"..OHHHHHHHHHHO..",
".OHHhHHHHHHhHHO.",
".OHhHHhHHhHHhHO.",
".OhHSHSSSSHSHhO.",
"..OhSESSSSESHO..",
"..OHSESSSSESHO..",
"...OSSSSsSSO....",
"...OCOOSSOOCO...",
"..OSCCCCCCCcSO..",
"..OSOCCCCCcOSO..",
"....OPPPPppO....",
"....OPPOOPpO....",
"...DOBBODOBBOD..",
],
'front_step': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHLLHHHO...",
"..OHHHHHHHHHHO..",
".OHHhHHHHHHhHHO.",
".OHhHHhHHhHHhHO.",
".OhHSHSSSSHSHhO.",
"..OhSESSSSESHO..",
"..OHSESSSSESHO..",
"...OSSSSsSSO....",
"...OCOOSSOOCO...",
"..OSCCCCCCCcSO..",
"..OSOCCCCCcOSO..",
"....OPPPPppO....",
"....OPPOOBBO....",
"...DOBBODDDDD...",
],
'side': [
"......OOOOO.....",
"....OOHHHHHO....",
"...OHHLLHHHHO...",
"..OHHHHHHHHHHO..",
"..OHHHHHHHhHHHO.",
"..OhHHhHHhHHHhO.",
"...OSHSSHhHHHO..",
"...OESSSShHHO...",
"..OSESSSShHHO...",
"...OSSSSShHO....",
"....OOSSOOO.....",
"....OCCCCcO.....",
"....OSCCCcO.....",
"....OPPPpO......",
"....OPPOpO......",
"...DOBBOBBOD....",
],
'side_step': [
"......OOOOO.....",
"....OOHHHHHO....",
"...OHHLLHHHHO...",
"..OHHHHHHHHHHO..",
"..OHHHHHHHhHHHO.",
"..OhHHhHHhHHHhO.",
"...OSHSSHhHHHO..",
"...OESSSShHHO...",
"..OSESSSShHHO...",
"...OSSSSShHO....",
"....OOSSOOO.....",
"...OSCCCCcO.....",
"....OCCCCcSO....",
"....OPPPPpO.....",
"...OPPO.OpPO....",
"..DOBBODDOBBO...",
],
'back': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHLLHHHO...",
"..OHHHHHHHHHHO..",
".OHHHHHHHHHHHHO.",
".OHHhHHHHHHhHHO.",
".OHHHHhHHhHHHHO.",
"..OHhHHHHHHhHO..",
"..OHHhHHHHhHHO..",
"...OhHHhHHHhO...",
"...OCOhOOhOCO...",
"..OSCCCCCCCcSO..",
"..OSOCCcCCcOSO..",
"....OPPPPppO....",
"....OPPOOPpO....",
"...DOBBODOBBOD..",
],
}
EREN['back_step'] = EREN['back'][:14] + ["....OPPOOBBO....", "...DOBBODDDDD..."]

# ---------------------------------------------------------------- Mikasa
# Straight black hair to the shoulders with bangs, red scarf, cream top, dark skirt.
MIKASA = {
'front': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHLLHHHO...",
"..OHHHHHHHHHHO..",
"..OHHHHHHHHHHO..",
"..OHhHHhHHhHHO..",
"..OHSSSSSSSSHO..",
"..OHSESSSSESHO..",
"..OHSESSSSESHO..",
"..OHHSSSSSSHHO..",
"..OHRRRRRRRRHO..",
"..OSRRRORRRRSO..",
"..OSOCCCCCcOSO..",
"....OPPPPPPO....",
"....OPPPPPpO....",
"...DOBBODOBBOD..",
],
'side': [
"......OOOOO.....",
"....OOHHHHHO....",
"...OHHLLHHHHO...",
"..OHHHHHHHHHHO..",
"..OHHHHHHHHHHHO.",
"..OhHHhHHhHHHHO.",
"...OSSSShHHHHO..",
"...OESSSShHHHO..",
"..OSESSSShHHHO..",
"...OSSSSShHHHO..",
"....ORRRRRRHO...",
"....ORRCCcRO....",
"....OSCCCcO.....",
"....OPPPPpO.....",
"....OPPPPpO.....",
"...DOBBOBBOD....",
],
'back': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHLLHHHO...",
"..OHHHHHHHHHHO..",
"..OHHHHHHHHHHO..",
"..OHHhHHHHhHHO..",
"..OHHHHhHHHHHO..",
"..OHHhHHHHhHHO..",
"..OHHHHHHHHHHO..",
"..OHhHHHhHHHhO..",
"..OHRRRRRRRRHO..",
"..OSRRRRRRRRSO..",
"..OSOCCCCCcOSO..",
"....OPPPPPPO....",
"....OPPPPPpO....",
"...DOBBODOBBOD..",
],
}

# ---------------------------------------------------------------- Armin
# Blond bob cut with a centre part, big eyes, tan shirt, brown shorts.
ARMIN = {
'front': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHLLHHHHO...",
"..OHHLLHHHHHHO..",
"..OHHHHHHHHHHO..",
"..OHHHhHHhHHHO..",
"..OHhSSSSSShHO..",
"..OHSESSSSESHO..",
"..OHSESSSSESHO..",
"..OhHSSSsSSHhO..",
"...OOCOSSOCOO...",
"..OSCCCCCCCcSO..",
"..OSOCCCCCcOSO..",
"....OPPPPppO....",
"....OSSOOSsO....",
"...DOBBODOBBOD..",
],
'side': [
"......OOOOO.....",
"....OOHHHHHO....",
"...OHLLHHHHHO...",
"..OHLLHHHHHHHO..",
"..OHHHHHHHHHHO..",
"..OHHHhHHhHHHO..",
"...OSSSShHHHHO..",
"...OESSSShHHHO..",
"..OSESSSShHHO...",
"...OSSSSShHhO...",
"....OOSSOOO.....",
"....OCCCCcO.....",
"....OSCCCcO.....",
"....OPPPpO......",
"....OSSOsO......",
"...DOBBOBBOD....",
],
'back': [
"......OOOO......",
"....OOHHHHOO....",
"...OHHHLLHHHO...",
"..OHHHLLHHHHHO..",
"..OHHHHHHHHHHO..",
"..OHHHHhHHHHHO..",
"..OHHhHHHHhHHO..",
"..OHHHHHHHHHHO..",
"..OHhHHHHHHhHO..",
"..OhHHHHHHHHhO..",
"...OOCOOOOCOO...",
"..OSCCCCCCCcSO..",
"..OSOCCcCCcOSO..",
"....OPPPPppO....",
"....OSSOOSsO....",
"...DOBBODOBBOD..",
],
}


def _steps(t):
    """Derive step frames: one foot forward (front/back), legs apart (side)."""
    def front_step(f):
        return f[:14] + [f[14][:8] + "OBBO....", f[15][:8] + "DDDDD..."]
    t.setdefault('front_step', front_step(t['front']))
    t.setdefault('back_step', front_step(t['back']))
    if 'side_step' not in t:
        s = list(t['side'])
        s[14] = "...OPPO.OpPO...."
        s[15] = "..DOBBODDOBBO..."
        t['side_step'] = s
    return t


KIDS = {'eren': _steps(EREN), 'mikasa': _steps(MIKASA), 'armin': _steps(ARMIN)}
for _k in KIDS.values():
    for _f in _k.values():
        assert len(_f) == 16 and all(len(r) == 16 for r in _f), _f
