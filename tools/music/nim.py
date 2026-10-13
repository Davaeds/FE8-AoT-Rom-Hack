"""A General MIDI ordered voicegroup made of FE8's own instruments.

FE8 gives every song its own 128-voice table, and the composers' voice numbers
follow General MIDI program numbers. For each program we take the voice entry
that the vanilla songs use most often for it, so one table holds strings
(48-51), choir (52-54), brass (56-63), timpani (47), harp (46), woodwinds,
pianos and the GM-layout drum kit (127).

The table only points at sample data inside the player's own ROM; it is built
from the clean ROM at build time and never committed.
"""
import collections
import struct

SONG_TABLE = 0x224470
# argument byte counts of the M4A track commands that take a fixed number
ARGS = {0xB1: 0, 0xB2: 4, 0xB3: 4, 0xB4: 0, 0xB5: 5, 0xB6: 0, 0xB7: 0, 0xB8: 0, 0xB9: 3, 0xBA: 1,
        0xBB: 1, 0xBC: 1, 0xBD: 1, 0xBE: 1, 0xBF: 1, 0xC0: 1, 0xC1: 1, 0xC2: 1, 0xC3: 1, 0xC4: 1,
        0xC5: 1, 0xC8: 1}


def u32(rom, o):
    return struct.unpack_from("<I", rom, o)[0]


def songs(rom):
    for i in range(1, 0x80):
        h = u32(rom, SONG_TABLE + i * 8) - 0x08000000
        if 0 <= h < len(rom) and 0 < rom[h] <= 16:
            yield i, h


def voices_used(rom, track):
    """Voice numbers set by VOICE commands, parsing note arguments and running status."""
    q, end, out, last = track, track + 20000, set(), None
    while q < end:
        c = rom[q]
        if c < 0x80:  # running status: the last command again with new arguments
            if last is None:
                break
            c, q = last, q - 1
        else:
            last = c if c >= 0xBD else last
        if c == 0xB1 or c == 0xB2:
            break
        q += 1
        if c >= 0xCF:  # TIE or note: up to 3 argument bytes
            for _ in range(3):
                if rom[q] < 0x80:
                    q += 1
                else:
                    break
            last = c
        elif c == 0xCE:  # EOT, optional key
            if rom[q] < 0x80:
                q += 1
        elif c in ARGS:
            if c == 0xBD:
                out.add(rom[q])
            q += ARGS[c]
    return out


def build(rom):
    use = collections.defaultdict(collections.Counter)
    for _, h in songs(rom):
        vg = u32(rom, h + 4) - 0x08000000
        for t in range(rom[h]):
            for v in voices_used(rom, u32(rom, h + 8 + 4 * t) - 0x08000000):
                use[v][rom[vg + v * 12:vg + v * 12 + 12]] += 1
    used = sorted(use)
    silent = use[48].most_common(1)[0][0]  # fallback for programs FE8 never uses: strings
    table = bytearray()
    for prog in range(128):
        table += use[prog].most_common(1)[0][0] if prog in use else silent
    return bytes(table), used


if __name__ == "__main__":
    import sys
    rom = open(sys.argv[1], "rb").read()
    data, progs = build(rom)
    open(sys.argv[2], "wb").write(data)
    print("programs from vanilla songs:", progs)
