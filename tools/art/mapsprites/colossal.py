"""Colossal Titan: skinless head and shoulders looming at the gate, steam rising. 32x32."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from tkit import art, outline, preview

# D darkest muscle 7, m 8, L 9, l 10 (reds on the enemy palette); W white teeth, w grey; K socket
CMAP = {'D': 7, 'm': 8, 'L': 9, 'l': 10, 'K': 15, 'W': 14, 'w': 3, 'b': 6, 'B': 5}

HALF = [
"................",
"..........OOOOOO",
"........OODmDmLm",
".......ODmLmDmLm",
"......ODmLmDmLlm",
"......ODmLmDmLlm",
".....ODmLmDmmLlm",
".....ODmmDDmmmLm",
".....ODDDDDDDmmL",
".....ODKKKKKDDmL",
".....ODKKKWKKDmL",
".....ODDKKKKDmLm",
".....ODmDDDDmmDm",
".....ODmLmmLmmKK",
"......ODmLmLmmDm",
"......ODmmDDDDDm",
"......ODmOWOWOWO",
"......ODOWWWWWWW",
"......ODOOOOOOOO",
"......ODOWWWWWWW",
"......ODmOWOWOWO",
"......ODmmDDDDDD",
".......ODDmmLmmm",
"........OODmLmmm",
"...OOOOOOODmmLmL",
".OODmmmLmmDDmLlm",
"ODmmLLmLLmmmDmLm",
"DmmLlmLLlmLmmDmm",
"DmLlmLLmLlmLmmDm",
"DmLmmLLmmLlmLmDm",
"DmmmLLmmmLLmmmDD",
"DDmmmmmmmmmmmmDD",
]


def face():
    rows = [h + h[::-1] for h in HALF]
    return art(rows, CMAP)


STEAM = [
[
".ww.............................",
"wWWw.......................ww...",
"wWWw......................wWWw..",
".ww.......................wWWw..",
"..........................wWw...",
"ww.........................w....",
"Ww..............................",
],
[
"wWw.............................",
"wWw........................wWw..",
".w........................wWWWw.",
"ww........................wWWWw.",
"Www........................wWw..",
"ww..............................",
"................................",
],
[
"ww..........................wWw.",
"Ww.........................wWWWw",
"...........................wWWWw",
"ww..........................wWw.",
"Wwww............................",
"wWww............................",
".ww.............................",
],
]


def frames():
    base = outline(face())[1:-1, 1:-1]     # keep 32x32: outline inside the frame
    # re-run the outline on the inner frame so edges at the border stay dark
    out = []
    for s in STEAM:
        f = base.copy()
        st = art(s, CMAP)
        for y in range(st.shape[0]):
            for x in range(st.shape[1]):
                if st[y, x] and f[y, x] == 0:
                    f[y, x] = st[y, x]
        out.append(f)
    return out


if __name__ == '__main__':
    fr = frames()
    preview([(f'sms{k}', a) for k, a in enumerate(fr)], 'colossal.png', pal=1, scale=10, cols=3)
