#!/usr/bin/env bash
# Boot build/AoT.gba in a headless emulator, follow an input script, and save
# screenshots to build/smoke/ (one PNG per shot plus sheet.png with all of them).
#
#   scripts/smoke.sh [SCRIPT]    default SCRIPT: scripts/smoketest/boot_to_map.txt
#
# See scripts/smoketest/mgba_smoke.c for the script format.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
runner="$root/.tools/mgba_smoke"
rom="$root/build/AoT.gba"
script="${1:-$root/scripts/smoketest/boot_to_map.txt}"
out="$root/build/smoke"

[ -x "$runner" ] || { echo "smoke.sh: run scripts/setup-linux.sh first" >&2; exit 1; }
[ -f "$rom" ] || { echo "smoke.sh: no build/AoT.gba, run ./build.sh first" >&2; exit 1; }

rm -rf "$out"
mkdir -p "$out"
"$runner" "$rom" "$out" "$script"

shopt -s nullglob
shots=("$out"/*.ppm)
if [ ${#shots[@]} -gt 0 ]; then
  python3 "$root/scripts/smoketest/sheet.py" "$out/sheet.png" "${shots[@]}" >/dev/null
  python3 "$root/scripts/smoketest/ppm2png.py" "${shots[@]}" >/dev/null
  rm -f "${shots[@]}"
fi
echo "Screenshots in build/smoke/ (overview: build/smoke/sheet.png)"
