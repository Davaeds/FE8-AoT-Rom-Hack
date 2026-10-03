# Working on this repo

Attack on Titan ROM hack of FE8U (Fire Emblem: The Sacred Stones, US), built with
Event Assembler (ColorzCore) on the vendored FE8 Skill System. See README.md.

## Build and verify (Linux)

```sh
scripts/setup-linux.sh        # once per machine/container
cp <clean FE8U ROM> FE8_clean.gba
./build.sh                    # build/AoT.gba + build/AoT.ups; fails loudly on assembly errors
scripts/smoke.sh              # headless boot to the first map, screenshots in build/smoke/
```

- In the Claude project, Ethan's clean ROM is the project upload at
  `/mnt/project-files/uploads/hearth/347cd906-a326-4c38-a9e4-1b63b601d8eb`
  (SHA1 c25b145e37456171ada4b0d440bf88a19f4d509f).
- Always run `./build.sh` rather than `MakeHack.sh` directly. `MakeHack.sh` exits 0 even when
  assembly fails and leaves an unmodified ROM behind.
- Look at `build/smoke/sheet.png` before saying a change works in game. Write a new script
  in `scripts/smoketest/` to reach new content (format is documented in `mgba_smoke.c`).
- Builds are reproducible: the same sources give the same `AoT.gba` SHA1.

## Rules

- Never commit ROMs, saves, or patches (`*.gba`, `*.ups`, `*.sav` are gitignored). This repo
  is public. Releases ship as UPS patches.
- Hack content goes under `AoT/`. Keep edits to vendored Skill System files small (hooks and
  config toggles) so upstream updates merge cleanly. See "Updating the Skill System" in README.md.
- Use original art only. Do not rip graphics from official Attack on Titan games.
