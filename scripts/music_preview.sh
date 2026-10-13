#!/usr/bin/env bash
# Record one song of the AoT soundtrack from the emulator, for listening checks.
#
#   scripts/music_preview.sh NAME [SECONDS]    -> build/music/NAME.wav
#
# Builds a ROM where song NAME (tools/music/songs/NAME.mml) also plays on the
# title screen, records it, then rebuilds the normal ROM. NAME can also be a
# vanilla song id such as 0x19, to compare against the original soundtrack.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
name="$1"
secs="${2:-60}"
mkdir -p "$root/build/music"
AOT_MUSIC_PREVIEW="$name" "$root/build.sh" quick >/dev/null
script="$(mktemp)"
printf 'wait 230\nrecord %s\nwait %d\nstop\n' "$name" "$((secs * 60))" >"$script"
"$root/.tools/mgba_smoke" "$root/build/AoT.gba" "$root/build/music" "$script" >/dev/null
rm -f "$script"
"$root/build.sh" quick >/dev/null
echo "build/music/$name.wav"
