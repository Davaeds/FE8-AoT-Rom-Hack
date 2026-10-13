"""Titan map sprites: the common Titans (titans_common.py) and the special
Titans and training dummy (titans_special.py)."""
import titans_common
import titans_special


def frames(name):
    if name in titans_special.BUILD:
        return titans_special.frames(name)
    return titans_common.frames(name)
