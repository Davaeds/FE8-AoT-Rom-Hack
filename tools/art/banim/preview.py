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
