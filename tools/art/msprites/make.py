"""Write every AoT map sprite sheet and the map sprite palettes.

    python3 tools/art/msprites/make.py [--preview PATH]

Outputs (committed; the build converts them with Png2Dmp):
  AoT/Graphics/MapSprites/<name>_sms.png  standing sheet: 3 idle frames stacked
  AoT/Graphics/MapSprites/<name>_mms.png  moving sheet: 15 32x32 frames stacked
                                          (0-3 left, 4-7 down, 8-11 up, 12-14 selected)
  AoT/Graphics/MapSprites/palettes.dmp    the 5 faction palettes for 0x59EE20
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import civilians, kids, soldier, titans  # noqa: E402
from kit import place, preview  # noqa: E402
from pal import PALETTES, gba_bytes  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'AoT', 'Graphics', 'MapSprites')

# png name: (module, character, faction palette for the PNG preview colours)
SPRITES = {
    'eren': (kids, 'eren', 0), 'mikasa': (kids, 'mikasa', 0), 'armin': (kids, 'armin', 0),
    'cadet_eren': (soldier, 'eren', 0), 'cadet_mikasa': (soldier, 'mikasa', 0),
    'cadet_armin': (soldier, 'armin', 0), 'cadet_jean': (soldier, 'jean', 0),
    'cadet_cadet': (soldier, 'cadet', 0), 'garrison': (soldier, 'garrison', 0),
    'hannes': (soldier, 'hannes', 0),
    'carla': (civilians, 'carla', 2), 'townsman': (civilians, 'townsman', 2),
    'townswoman': (civilians, 'townswoman', 2),
    'titan_a': (titans, 'titan_a', 1), 'titan_b': (titans, 'titan_b', 1),
    'smiling': (titans, 'smiling', 1), 'armored': (titans, 'armored', 1),
    'colossal': (titans, 'colossal', 1), 'dummy': (titans, 'dummy', 1),
}


def save(idx, name, pal):
    im = Image.fromarray(idx.astype(np.uint8), 'P')
    flat = []
    for k, c in enumerate(PALETTES[pal]):
        flat += list(c) if k else [128, 160, 128]
    im.putpalette(flat)
    im.save(os.path.join(OUT, name + '.png'), transparency=0)


def main(argv):
    items = []
    for name, (mod, who, pal) in SPRITES.items():
        f = mod.frames(who)
        w = f['sms'][0].shape[1]
        sms = np.vstack(f['sms'])
        mms = np.vstack([place(a, 32, 32) for a in f['left'] + f['down'] + f['up'] + f['sel']])
        assert sms.shape == (3 * w, w) and mms.shape == (480, 32), (name, sms.shape, mms.shape)
        save(sms, name + '_sms', pal)
        save(mms, name + '_mms', pal)
        items.append((name, f['sms'][0], pal))
    with open(os.path.join(OUT, 'palettes.dmp'), 'wb') as fh:
        fh.write(gba_bytes(PALETTES))
    if '--preview' in argv:
        preview(items, argv[argv.index('--preview') + 1], scale=4, cols=10)
    print(f'wrote {len(SPRITES)} sprites to {OUT}')


if __name__ == '__main__':
    main(sys.argv[1:])
