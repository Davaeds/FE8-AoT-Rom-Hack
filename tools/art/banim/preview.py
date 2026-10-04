"""Preview helpers: strips of frames and animated GIFs for review."""
import numpy as np
from PIL import Image

BG = (120, 168, 120)


def to_rgb(im, palette):
    lut = np.array([BG] + [tuple(c) for c in palette], np.uint8)
    return lut[im]


def strip(frames, palette, path, box=(40, 20, 200, 112), zoom=3):
    ims = [Image.fromarray(to_rgb(f, palette)).crop(box) for f in frames]
    w, h = ims[0].size
    out = Image.new("RGB", (w * len(ims), h))
    for i, im in enumerate(ims):
        out.paste(im, (i * w, 0))
    out.resize((out.width * zoom, out.height * zoom), Image.NEAREST).save(path)


def gif(seq, palette, path, box=(0, 0, 240, 160), zoom=2, backdrop=None):
    """seq: list of (frame array, duration in game frames)."""
    ims, durs = [], []
    for f, d in seq:
        rgb = to_rgb(f, palette)
        if backdrop is not None:
            m = f == 0
            rgb[m] = backdrop[m]
        im = Image.fromarray(rgb).crop(box)
        ims.append(im.resize((im.width * zoom, im.height * zoom), Image.NEAREST))
        durs.append(max(20, round(d * 1000 / 60)))
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=durs, loop=0)


def fight_gif(right_mod, left_mod, mode, path, backdrop, left_frame="idle", zoom=2, crop=(0, 0, 240, 120)):
    """Approximate a close-range fight: right_mod plays `mode` (index into
    MODES) while left_mod stands, mirrored to the left position."""
    R, L = right_mod.frames(), left_mod.frames()
    lut_r = np.array([BG] + [tuple(c) for c in right_mod.PALETTE], np.uint8)
    lut_l = np.array([BG] + [tuple(c) for c in left_mod.PALETTE], np.uint8)
    left = L[left_frame][:, ::-1]                       # mirror: x -> 239 - x (anchor 148 -> 91)
    ims, durs = [], []
    for tok in right_mod.MODES[mode]:
        if tok[0] != "f":
            continue
        img = backdrop.copy()
        m = left > 0
        img[m] = lut_l[left[m]]
        f = R[tok[1]]
        m = f > 0
        img[m] = lut_r[f[m]]
        im = Image.fromarray(img).crop(crop)
        ims.append(im.resize((im.width * zoom, im.height * zoom), Image.NEAREST))
        durs.append(max(20, round(tok[2] * 1000 / 60)))
    durs[-1] = 600
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=durs, loop=0)
    return ims
