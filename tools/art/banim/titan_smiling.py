"""Battle animation: the Smiling Titan. Same body and moves as the common
Titan (pure_titan.py), with its fair, shoulder-length hair."""
import pure_titan as titan
from pure_titan import MODES, frames  # noqa: F401

ABBR = "aot_smiling"
SLOT = 3
PAL = dict(titan.PAL, hair=(212, 172, 104), haird=(160, 120, 64))
PALETTE = list(PAL.values())
