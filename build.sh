#!/usr/bin/env bash
# Build the hack on Linux.
#
#   ./build.sh          full build: tables, text, maps, then assemble
#   ./build.sh quick    assemble only (skip tables, text and maps)
#
# Needs FE8_clean.gba (a clean FE8U ROM) in the repo root and a one-time
# scripts/setup-linux.sh. Writes build/AoT.gba, build/AoT.sym and build/AoT.ups
# (the patch to share; it applies to a clean FE8U ROM).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tools="$root/.tools"
clean="$root/FE8_clean.gba"
clean_sha1="c25b145e37456171ada4b0d440bf88a19f4d509f"
out="$root/build"

die() {
  echo "build.sh: $*" >&2
  exit 1
}

case "${1:-}" in
  "" | quick) ;;
  *) die "unknown argument '$1' (expected nothing or 'quick')" ;;
esac

[ -f "$clean" ] || die "missing FE8_clean.gba: copy your own clean FE8U ROM to $clean"
actual_sha1="$(sha1sum "$clean" | cut -d' ' -f1)"
[ "$actual_sha1" = "$clean_sha1" ] ||
  die "FE8_clean.gba has SHA1 $actual_sha1, expected $clean_sha1 (clean FE8U)"
[ -x "$tools/venv/bin/python3" ] && [ -e "$tools/libffi7/libffi.so.7" ] ||
  die "tools not set up: run scripts/setup-linux.sh first"

# ColorzCore targets .NET 6; let it run on the newer runtime that is installed.
export DOTNET_ROLL_FORWARD=Major
export LD_LIBRARY_PATH="$tools/libffi7${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="$tools/venv/bin:$PATH"

mkdir -p "$out"
log="$out/build.log"
"$root/MakeHack.sh" "$@" 2>&1 | tee "$log"

# MakeHack.sh exits 0 even when assembly fails (the ROM is then an unmodified
# copy), so check ColorzCore's own verdict.
if grep -q "Errors occurred" "$log" || ! grep -q "No errors" "$log"; then
  die "assembly failed, see the errors above (also saved in build/build.log)"
fi

mv -f "$root/SkillsTest.gba" "$out/AoT.gba"
mv -f "$root/SkillsTest.sym" "$out/AoT.sym"
python3 "$root/scripts/ups.py" create "$clean" "$out/AoT.gba" "$out/AoT.ups"

echo
echo "Built:"
sha1sum "$out/AoT.gba" "$out/AoT.ups"
