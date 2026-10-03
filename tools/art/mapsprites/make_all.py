"""Write every AoT map sprite sheet (SMS + MMS indexed PNGs) into AoT/Graphics/MapSprites.

    python3 tools/art/mapsprites/make_all.py

Reads the map palettes from FE8_clean.gba. Needs numpy and Pillow (not part of the
normal build: the PNGs are committed and the build converts them with Png2Dmp).
The art lives here as ASCII rows (kids.py, adults.py, townsfolk.py, colossal.py and
the Titan heads in titans.py); Titan bodies are drawn by rig.py.
"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from render import to_idx, colorize as colorize0
from sheets import place_bottom, save_png, blit, OUT
from tkit import mirror, preview
import titans, colossal, adults, townsfolk
from make_kids import kid_frames, nod, hop


def human_frames(t, cmap):
    f = {k: to_idx(v, cmap) for k, v in t.items()}
    sms = [f['front'], nod(f['front']), f['front']]
    left = [mirror(f['side']), mirror(f['side_step']), mirror(f['side']), mirror(f['side_step'])]
    down = [f['front'], f['front_step'], f['front'], mirror(f['front_step'])]
    up = [f['back'], f['back_step'], f['back'], mirror(f['back_step'])]
    sel = [f['front'], hop(f['front']), f['front']]
    return sms, left, down, up, sel


def stack(frames, fw, fh, cx):
    return np.vstack([place_bottom(fw, fh, a, cx) for a in frames])


def big_nod(a):
    """1px downward bob of everything above the hips (rows 0-19) for 32x32 Titan idles."""
    out = a.copy()
    top = a[:20].copy()
    out[:20] = 0
    out[1:21] = np.where(top != 0, top, out[1:21])
    return out


written = []

def save(idx, name, pal):
    save_png(idx, name, pal)
    written.append((name, idx, pal))

# kids: 16x16 SMS
for name in ('eren', 'mikasa', 'armin'):
    sms, left, down, up, sel = kid_frames(name)
    save(stack(sms, 16, 16, 8), f'{name}_sms', 0)
    save(stack(left + down + up + sel, 32, 32, 16), f'{name}_mms', 0)

# adults: 16x32 SMS
for who, pal in (('garrison', 2), ('hannes', 0)):
    sms, left, down, up, sel = human_frames(adults.FRAMES[who], adults.COLORS[who])
    save(stack(sms, 16, 32, 8), f'{who}_sms', pal)
    save(stack(left + down + up + sel, 32, 32, 16), f'{who}_mms', pal)

# townsfolk and Carla: 16x32 SMS
for who, name in (('man', 'townsman'), ('woman', 'townswoman'), ('carla', 'carla')):
    sms, left, down, up, sel = human_frames(townsfolk.FRAMES[who], townsfolk.COLORS[who])
    save(stack(sms, 16, 32, 8), f'{name}_sms', 2)
    save(stack(left + down + up + sel, 32, 32, 16), f'{name}_mms', 2)

# Titans: 32x32 SMS, frames already 32x32
for name, t in (('titan_a', titans.titan_a()), ('titan_b', titans.titan_b()),
                ('smiling', titans.smiling()), ('armored', titans.armored())):
    f = t.frames()
    sms = [f['front0'], big_nod(f['front0']), f['front0']]
    left = [f['side0'], f['side1'], f['side2'], f['side3']]
    down = [f['front0'], f['front1'], f['front2'], f['front3']]
    up = [f['back0'], f['back1'], f['back2'], f['back3']]
    sel = [f['front0'], f['front0'], f['front0']]
    save(np.vstack(sms), f'{name}_sms', 1)
    save(np.vstack(left + down + up + sel), f'{name}_mms', 1)

# Colossal: SMS = three steam phases; MMS = the same face in every frame
cf = colossal.frames()
save(np.vstack(cf), 'colossal_sms', 1)
save(np.vstack([cf[k % 3] for k in range(15)]), 'colossal_mms', 1)

for name, idx, pal in written:
    assert idx.max() < 16 and idx.shape[1] in (16, 32), name
    print(f'{name:16s} {idx.shape[1]}x{idx.shape[0]} pal {pal}')
