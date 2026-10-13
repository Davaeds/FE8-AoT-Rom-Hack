"""Encode parsed MML tracks into FE8 (MP2K) song data, as Event Assembler text.

Track bytes follow the engine's command set (as documented by the GBA
decompilation projects): waits 0x80-0xB0, notes 0xD0-0xFF (length from the
table below) followed by key, velocity; TIE 0xCF / EOT 0xCE for notes longer
than the table; FINE 0xB1, GOTO 0xB2 + pointer, TEMPO 0xBB (bpm / 2),
KEYSH 0xBC, VOICE 0xBD, VOL 0xBE, PAN 0xBF (64 = centre), MOD 0xC4, LFOS 0xC2.
"""
LENGTHS = list(range(0, 25)) + [28, 30, 32, 36, 40, 42, 44, 48, 52, 54, 56, 60, 64, 66, 68, 72, 76,
                                78, 80, 84, 88, 90, 92, 96]
WAIT = {n: 0x80 + i for i, n in enumerate(LENGTHS)}           # W00..W96
NOTE = {n: 0xCF + i for i, n in enumerate(LENGTHS) if n}       # N01..N96
# Track volumes are scaled so the soundtrack sits at the loudness of FE8's own
# songs (and its sound effects stay audible over it).
MASTER = 0.55
FINE, GOTO, TEMPO, KEYSH, VOICE, VOL, PAN, LFOS, MOD, EOT, TIE = (
    0xB1, 0xB2, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF, 0xC2, 0xC4, 0xCE, 0xCF)


def waits(ticks):
    out = []
    while ticks > 0:
        n = max(v for v in LENGTHS if v <= ticks)
        out.append(WAIT[n])
        ticks -= n
    return out


def encode_track(events, loop, end, tempo=None, label="T"):
    """Returns a list of chunks: bytes, or ("goto", label) / ("label", name)."""
    # Expand notes into on/off actions on a timeline.
    acts = []  # (tick, order, kind, payload)
    for e in events:
        if e.kind == "note":
            ln = e.c
            if ln in NOTE:
                acts.append((e.tick, 2, "n", (e.a, e.b, ln)))
            else:
                acts.append((e.tick, 2, "tie", (e.a, e.b)))
                acts.append((e.tick + ln, 0, "eot", (e.a,)))
        else:
            acts.append((e.tick, 1, e.kind, (e.a,)))
    if loop is not None:
        acts.append((loop, -1, "loop", ()))
    acts.sort(key=lambda a: (a[0], a[1]))

    out = bytearray()
    chunks = []
    if tempo:
        out += bytes((TEMPO, tempo // 2))
    out += bytes((KEYSH, 0))
    t = 0
    for tick, _, kind, pl in acts:
        if tick > end:
            continue
        out += bytes(waits(tick - t))
        t = tick
        if kind == "loop":
            chunks.append(bytes(out)); out = bytearray()
            chunks.append(("label", label + "_loop"))
        elif kind == "n":
            out += bytes((NOTE[pl[2]], pl[0], max(1, min(127, pl[1]))))
        elif kind == "tie":
            out += bytes((TIE, pl[0], max(1, min(127, pl[1]))))
        elif kind == "eot":
            out += bytes((EOT, pl[0]))
        elif kind == "voice":
            out += bytes((VOICE, pl[0]))
        elif kind == "vol":
            out += bytes((VOL, max(1, min(127, round(pl[0] * MASTER)))))
        elif kind == "pan":
            out += bytes((PAN, pl[0]))
        elif kind == "mod":
            out += bytes((MOD, pl[0]))
        elif kind == "lfos":
            out += bytes((LFOS, pl[0]))
    out += bytes(waits(end - t))
    chunks.append(bytes(out))
    if loop is not None:
        chunks.append(bytes((GOTO,)))
        chunks.append(("goto", label + "_loop"))
    chunks.append(bytes((FINE,)))
    return chunks


def song_event(name, meta, tracks, voicegroup_label):
    """Event Assembler text for one song: track data, then the header."""
    tempo = int(meta.get("tempo", 120))
    reverb = int(meta.get("reverb", 0))
    priority = int(meta.get("priority", 10))
    lines = [f"// {meta.get('title', name)}"]
    labels = []
    for k, (tname, events, loop, end) in enumerate(tracks):
        lab = f"AoT_Song_{name}_{tname}"
        labels.append(lab)
        lines.append("ALIGN 4")
        lines.append(f"{lab}:")
        for ch in encode_track(events, loop, end, tempo if k == 0 else None, lab):
            if isinstance(ch, bytes):
                for i in range(0, len(ch), 24):
                    lines.append("BYTE " + " ".join(f"0x{b:02X}" for b in ch[i:i + 24]))
            elif ch[0] == "label":
                lines.append(f"{ch[1]}:")
            else:  # GOTO target: a pointer that is not word aligned, so no POIN
                t = ch[1]  # EA labels already carry the 0x08000000 ROM base
                lines.append(f"BYTE ({t} & 0xFF) (({t} >> 8) & 0xFF) (({t} >> 16) & 0xFF) (({t} >> 24) & 0xFF)")
    lines.append("ALIGN 4")
    lines.append(f"AoT_Song_{name}:")
    lines.append(f"BYTE {len(tracks)} 0 {priority} {0x80 | reverb if reverb else 0}")
    lines.append(f"POIN {voicegroup_label}")
    lines.append("POIN " + " ".join(labels))
    return "\n".join(lines)
