"""Turn generated pixel-art poses into clean FE-style battle sprite frames.

The generator (a free text-to-image model, prompted for crisp pixel art) draws
poses on a flat background with an effective pixel grid of 5-10 screen pixels.
convert() recovers the art at a target height:

  1. drop the background (flood fill from the border, colour distance),
  2. map every source pixel to the nearest colour of the animation's palette,
  3. downscale by majority vote per output cell (transparent only on a
     clear majority, so thin blades and outlines survive),
  4. clean up: orphan pixels take their neighbours' colour, and every opaque
     pixel touching transparency becomes outline unless it is a highlight
     colour listed in `keep_edge` (blade glints, steam).
"""
from collections import deque

import numpy as np
from PIL import Image


def background_mask(rgb, tol=48):
    h, w, _ = rgb.shape
    a = rgb.astype(np.int32)
    ref = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    close = np.abs(a - ref).sum(-1) < tol
    bg = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if close[y, x] and not bg[y, x]:
                bg[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if close[y, x] and not bg[y, x]:
                bg[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and close[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True; q.append((ny, nx))
    return bg


def nearest(rgb, palette):
    p = np.array(palette[1:], np.float32)
    # perceptual-ish weights
    wgt = np.array([0.30, 0.59, 0.11], np.float32) * 3
    d = (((rgb[..., None, :].astype(np.float32) - p) ** 2) * wgt).sum(-1)
    return d.argmin(-1).astype(np.uint8) + 1


def downscale(idx, out_w, out_h, transparent_share=0.5):
    H, W = idx.shape
    out = np.zeros((out_h, out_w), np.uint8)
    for y in range(out_h):
        y0, y1 = y * H // out_h, max(y * H // out_h + 1, (y + 1) * H // out_h)
        for x in range(out_w):
            x0, x1 = x * W // out_w, max(x * W // out_w + 1, (x + 1) * W // out_w)
            # sample the centre region of the cell to avoid seams of the source grid
            cy0, cy1 = y0 + (y1 - y0) // 4, y1 - (y1 - y0) // 4
            cx0, cx1 = x0 + (x1 - x0) // 4, x1 - (x1 - x0) // 4
            c = idx[cy0:max(cy1, cy0 + 1), cx0:max(cx1, cx0 + 1)].ravel()
            cnt = np.bincount(c, minlength=16)
            if cnt[0] > c.size * transparent_share:
                continue
            cnt[0] = 0
            out[y, x] = cnt.argmax()
    return out


def cleanup(a, outline=1, keep_edge=(), passes=2):
    a = a.copy()
    h, w = a.shape
    for _ in range(passes):
        b = a.copy()
        for y in range(h):
            for x in range(w):
                v = a[y, x]
                n = [a[yy, xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                     if 0 <= yy < h and 0 <= xx < w]
                if v and all(m != v for m in n):
                    vals = [m for m in n if m]
                    if len(n) == 4 and vals:
                        b[y, x] = max(set(vals), key=vals.count)
                    elif not vals:
                        b[y, x] = 0
        a = b
    # outline pass
    b = a.copy()
    for y in range(h):
        for x in range(w):
            v = a[y, x]
            if not v or v == outline or v in keep_edge:
                continue
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if not (0 <= yy < h and 0 <= xx < w) or a[yy, xx] == 0:
                    b[y, x] = outline
                    break
    return b


def convert(path, box, height, palette, keep_edge=(), tol=48, outline=1, clean=True, drop_shadow=0.12):
    """Crop `box` from the image at `path` and return an indexed array `height` tall."""
    im = Image.open(path).convert('RGB').crop(box)
    rgb = np.array(im)
    bg = background_mask(rgb, tol)
    # enclosed background (between legs, inside arms) is not reached by the
    # flood fill: drop any pixel very close to the background colour too
    a = rgb.astype(np.int32)
    ref = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    bg |= np.abs(a - ref).sum(-1) < tol // 2
    if drop_shadow:
        # the generator bakes a grey ground ellipse under the feet
        sat = a.max(-1) - a.min(-1)
        low = np.zeros_like(bg); low[int(len(a) * (1 - drop_shadow)):] = True
        bg |= low & (sat < 18) & (a.mean(-1) > 120) & (a.mean(-1) < ref.mean() + 8)
    idx = nearest(rgb, palette)
    idx[bg] = 0
    ys, xs = np.nonzero(idx)
    idx = idx[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    H, W = idx.shape
    out_w = max(1, round(W * height / H))
    a = downscale(idx, out_w, height)
    return cleanup(a, outline, keep_edge) if clean else a


def to_rgb(a, palette, bg=(60, 60, 80)):
    p = [bg] + list(palette[1:])
    return Image.fromarray(np.array([[p[v] for v in r] for r in a], np.uint8))


def figures(path, tol=48, min_area=2000, gap=6):
    """Find the separate figures on a generated sheet. Returns boxes (x0, y0, x1, y1)
    in reading order (rows top to bottom, left to right within a row)."""
    from scipy import ndimage
    rgb = np.array(Image.open(path).convert('RGB'))
    fg = ~background_mask(rgb, tol)
    fg = ndimage.binary_dilation(fg, iterations=gap)
    lab, n = ndimage.label(fg)
    boxes = []
    for sl in ndimage.find_objects(lab):
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if (y1 - y0) * (x1 - x0) >= min_area:
            boxes.append((x0 + gap, y0 + gap, x1 - gap, y1 - gap))
    boxes.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows, cur = [], []
    for b in boxes:
        if cur and b[1] > max(c[3] for c in cur) - 10:
            rows.append(cur); cur = []
        cur.append(b)
    if cur:
        rows.append(cur)
    return [b for r in rows for b in sorted(r)]
