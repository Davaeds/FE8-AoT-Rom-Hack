# Attack on Titan: Fire Emblem (working title)

A fan-made ROM hack of Fire Emblem: The Sacred Stones (GBA) based on Attack on Titan.
It is built with Event Assembler on top of the [FE8 Skill System](https://github.com/FireEmblemUniverse/SkillSystem_FE8).

## Status

Pre-alpha. The build pipeline works, but the playable content is still the Skill System's
test chapter. That chapter is retitled "Shiganshina" to prove our edits reach the game.
The first real chapter, the fall of Wall Maria, is next.

## Playing

This repository never contains a ROM. You need:

1. Your own dump of **Fire Emblem: The Sacred Stones (USA, Australia)**:
   SHA1 `c25b145e37456171ada4b0d440bf88a19f4d509f`, CRC32 `a47246ae`.
   On Windows you can check it with `certutil -hashfile "your.gba" SHA1`.
2. The `AoT.ups` patch, applied to that ROM with a UPS-capable patcher such as
   [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) (in the browser) or Flips.
3. An emulator such as [mGBA](https://mgba.io/).

## Building

### Linux (Ubuntu 24.04, x86-64)

```sh
scripts/setup-linux.sh          # once: .NET runtime, Python venv, libffi7, smoke-test runner
cp /path/to/your/rom.gba FE8_clean.gba
./build.sh                      # writes build/AoT.gba, build/AoT.sym, build/AoT.ups
scripts/smoke.sh                # optional: boot it headlessly, screenshots in build/smoke/
```

`./build.sh quick` skips the table, text, and map conversion steps. Use it only when you
changed nothing but `.event` files.

### Windows

The Skill System ships Windows versions of every tool. Put your ROM next to
`MAKE_HACK_full.cmd` as `FE8_clean.gba` and run `MAKE_HACK_full.cmd`. It writes
`SkillsTest.gba` and `SkillsTest.ups`. This route comes from upstream and has not been
tested for this project yet.

## Layout

| Path | What it is |
|---|---|
| `AoT/` | Attack on Titan content. `AoT/AoT.event` is included last from `ROMBuildfile.event`. |
| `build.sh`, `scripts/` | Linux build, UPS patch tool (`scripts/ups.py`), headless smoke test |
| everything else | The FE8 Skill System, vendored unchanged except for small hooks. Its own readme is [docs/SkillSystem-README.md](docs/SkillSystem-README.md). |

## Updating the Skill System

Upstream snapshots live on the `vendor/skillsystem` branch, and `main` merges them:

```sh
git fetch --depth 1 https://github.com/FireEmblemUniverse/SkillSystem_FE8 master
git switch vendor/skillsystem
git read-tree -u --reset FETCH_HEAD
git commit -m "Import FE8 Skill System at $(git rev-parse --short FETCH_HEAD)"
git switch main
git merge vendor/skillsystem
```

## Credits and legal

- Attack on Titan belongs to Hajime Isayama and Kodansha. Fire Emblem belongs to
  Nintendo and Intelligent Systems. This is an unaffiliated, non-commercial fan project,
  distributed only as a patch.
- The FE8 Skill System (CC0 1.0) is by Circleseverywhere and many contributors; see
  [CREDITS.md](CREDITS.md).
