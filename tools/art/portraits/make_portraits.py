"""Write the portrait sheets to AoT/Graphics/Portraits.

    python3 tools/art/portraits/make_portraits.py [name ...] [--preview DIR]
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pkit  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "AoT", "Graphics", "Portraits")
CHARACTERS = {"eren": "Eren", "mikasa": "Mikasa", "armin": "Armin", "hannes": "Hannes",
              "carla": "Carla", "soldier": "Soldier",
              "cadet_eren": "CadetEren", "cadet_mikasa": "CadetMikasa", "cadet_armin": "CadetArmin",
              "jean": "Jean", "shadis": "Shadis", "smiling": "Smiling", "colossal": "Colossal",
              "armored": "Armored", "titan": "Titan"}


def main(argv):
    preview = None
    if "--preview" in argv:
        i = argv.index("--preview")
        preview = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    names = argv or list(CHARACTERS)
    for name in names:
        mod = importlib.import_module(name)
        sheet = pkit.build_sheet(mod, mod.MOUTH, mod.EYES, getattr(mod, "MINI", (0.62, 48, 38)))
        sheet.save(os.path.join(OUT, CHARACTERS[name] + ".png"))
        if preview:
            pkit.preview(sheet, os.path.join(preview, name + ".png"))
        print("wrote", CHARACTERS[name] + ".png")


if __name__ == "__main__":
    main(sys.argv[1:])
