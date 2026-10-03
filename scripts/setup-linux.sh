#!/usr/bin/env bash
# One-time setup for building the hack on Linux (tested on Ubuntu 24.04 x86-64).
# Installs everything into .tools/ (gitignored) except the apt packages.
#
#   scripts/setup-linux.sh
#
# Windows users do not need this: the Skill System ships Windows tools, see README.md.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tools="$root/.tools"
mkdir -p "$tools"

sudo=""
if [ "$(id -u)" -ne 0 ]; then
  sudo="sudo"
fi

# 1. System packages:
#    dotnet-runtime-8.0  runs ColorzCore (Event Assembler)
#    python3-venv        isolated Python for the table/text/map converters
#    libmgba-dev, gcc    headless smoke test (scripts/smoke.sh)
echo "== apt packages"
$sudo apt-get update -qq
$sudo apt-get install -y -qq dotnet-runtime-8.0 python3-venv libmgba-dev gcc curl

# 2. libffi.so.7: the Skill System's bundled Linux Png2Dmp and PortraitFormatter
#    binaries link against it, but Ubuntu 22.04+ only ships libffi8. Take the
#    library from Ubuntu 20.04's official package, pinned by SHA256.
echo "== libffi7"
if [ ! -e "$tools/libffi7/libffi.so.7" ]; then
  deb="libffi7_3.3-4_amd64.deb"
  sha256="4584aa8fef1bf5086168ce2f7078cd2ebd78fdc4cc0d86d958d795d4e0b0f50d"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  for mirror in http://archive.ubuntu.com/ubuntu http://old-releases.ubuntu.com/ubuntu; do
    if curl -fsSL -o "$tmp/$deb" "$mirror/pool/main/libf/libffi/$deb"; then
      break
    fi
  done
  echo "$sha256  $tmp/$deb" | sha256sum -c --quiet -
  dpkg-deb -x "$tmp/$deb" "$tmp/extract"
  mkdir -p "$tools/libffi7"
  cp -a "$tmp/extract/usr/lib/x86_64-linux-gnu/"libffi.so.7* "$tools/libffi7/"
fi

# 3. Python packages for Tools/tmx2ea (map converter). A venv is used because
#    tmx 1.10's setup.py does not build against Debian's patched setuptools.
echo "== python venv"
if [ ! -x "$tools/venv/bin/python3" ]; then
  python3 -m venv "$tools/venv"
fi
"$tools/venv/bin/pip" install --quiet --disable-pip-version-check "tmx==1.10" "six==1.17.0"

# 4. Headless emulator runner for smoke tests.
echo "== mgba_smoke"
gcc -O2 -Wall -Wextra -o "$tools/mgba_smoke" "$root/scripts/smoketest/mgba_smoke.c" -lmgba

echo "Setup complete. Put your clean FE8U ROM at FE8_clean.gba, then run ./build.sh"
