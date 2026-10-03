import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from render import to_idx, sheet, colorize
from sheets import *
from kids import KIDS, COLORS, HEAD_ROWS

def nod(a, head_rows=HEAD_ROWS):
    out = a.copy()
    out[0:head_rows+1] = 0
    blit(out, a[0:head_rows], 0, 1)
    # keep collar pixels not covered
    for x in range(a.shape[1]):
        if out[head_rows, x] == 0:
            out[head_rows, x] = a[head_rows, x]
    return out

def hop(a):
    """Whole figure 1px up, shadow row stays."""
    out = np.zeros_like(a)
    body, shadow = a[:-1], a[-1:]
    out[-1:] = shadow
    blit(out, body, 0, -1)
    return out

def kid_frames(name):
    t = KIDS[name]; c = COLORS[name]
    f = {k: to_idx(v, c) for k, v in t.items()}
    sms = [f['front'], nod(f['front']), f['front']]
    left = [mirror(f['side']), mirror(f['side_step']), mirror(f['side']), mirror(f['side_step'])]
    down = [f['front'], f['front_step'], f['front'], mirror(f['front_step'])]
    up = [f['back'], f['back_step'], f['back'], mirror(f['back_step'])]
    sel = [f['front'], hop(f['front']), f['front']]
    return sms, left, down, up, sel

if __name__ == '__main__':
    previews = []
    for name in ('eren', 'mikasa', 'armin'):
        sms, left, down, up, sel = kid_frames(name)
        s = sms_sheet(sms, 16, 16, cx=8)
        m = mms_sheet(left, down, up, sel, cx=16)
        save_png(s, f'{name}_sms'); save_png(m, f'{name}_mms')
        previews.append((name + ' sms', s)); previews.append((name + ' mms', m))
    # preview: sms sheets and mms sheets side by side, 4x
    items = [(n, a) for n, a in previews]
    from PIL import Image
    cols = []
    for n, a in items:
        cols.append(colorize(a, 0).resize((a.shape[1]*3, a.shape[0]*3), Image.NEAREST))
    W = sum(c.width + 6 for c in cols); H = max(c.height for c in cols)
    out = Image.new('RGB', (W, H), (20, 20, 20)); x = 0
    for c in cols:
        out.paste(c, (x, 0)); x += c.width + 6
    out.save('kids_sheets.png')
    print(out.size)
