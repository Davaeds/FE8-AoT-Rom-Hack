"""A small MML dialect for writing the AoT soundtrack, compiled to FE8's sound
engine (MP2K / "M4A") track data.

Song file (tools/music/songs/<name>.mml):

    #title  Shiganshina Burns         ; free text
    #song   0x16                      ; song id it replaces
    #tempo  152                       ; beats per minute (even values are exact)
    #reverb 0                         ; optional, 0-127
    #priority 10                      ; optional, as the vanilla song in that slot
    #define STRINGS  @48 v96 p64      ; text macros, used as $STRINGS

    A: $STRINGS o3 l16 L [e e b e  e e c+ e]4 ...
    B: ...

One line per track, a track may continue on the next lines that start with the
same letter. Commands:

    c d e f g a b   note; + or # sharp, - flat; then a length (1 2 4 8 16 32,
                    3 6 12 24 for triplets, dots allowed) or none for `l`
    r               rest, same lengths
    ^len            extend the previous note or rest (tie)
    {c e g}4        chord
    o4 > <          octave (o4 c = middle C), up, down
    l8              default length
    @48             instrument (General MIDI program)
    v100            track volume, 0-127
    V100            note velocity, 0-127
    !               accent: the next note is played 30 louder
    p64             pan (0 left, 64 centre, 127 right)
    k-12            transpose this track by semitones
    q6              gate: notes sound for q/8 of their length (8 = legato)
    m20 s30         vibrato depth and speed
    [ ... ]4        repeat
    L               loop point: the track jumps back here at its end
    | /             bar marks, ignored
    ; comment       to end of line
"""
import re

TICKS_WHOLE = 96  # 24 per quarter note


class Event:
    __slots__ = ("tick", "kind", "a", "b", "c")

    def __init__(self, tick, kind, a=0, b=0, c=0):
        self.tick, self.kind, self.a, self.b, self.c = tick, kind, a, b, c

    def __repr__(self):
        return f"{self.tick}:{self.kind}({self.a},{self.b},{self.c})"


NOTE = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


class Parser:
    def __init__(self, text, name):
        self.s = text
        self.i = 0
        self.name = name

    def error(self, msg):
        raise SyntaxError(f"track {self.name}: {msg} at ...{self.s[self.i:self.i + 30]!r}")

    def peek(self):
        self.skip()
        return self.s[self.i] if self.i < len(self.s) else ""

    def skip(self):
        while self.i < len(self.s) and self.s[self.i] in " \t\n|/":
            self.i += 1

    def number(self, signed=False):
        m = re.compile(r"-?\d+" if signed else r"\d+").match(self.s, self.i)
        if not m:
            return None
        self.i = m.end()
        return int(m.group())

    def length(self, default):
        n = self.number()
        if n is None:
            ticks = default
        else:
            if TICKS_WHOLE % n:
                self.error(f"length {n} does not divide a whole note")
            ticks = TICKS_WHOLE // n
        add = ticks
        while self.i < len(self.s) and self.s[self.i] == ".":
            add //= 2
            ticks += add
            self.i += 1
        return ticks


def expand_loops(text):
    """Expand [ ... ]n repeats (nested allowed)."""
    while "[" in text:
        m = re.search(r"\[([^\[\]]*)\](\d*)", text)
        if not m:
            raise SyntaxError("unbalanced [ ]")
        n = int(m.group(2) or 2)
        text = text[:m.start()] + " ".join([m.group(1)] * n) + text[m.end():]
    return text


def parse_track(text, name):
    """Returns (events, loop_tick or None, end_tick)."""
    text = expand_loops(text)
    p = Parser(text, name)
    tick, octave, deflen, vel, trans, gate = 0, 4, 24, 100, 0, 8
    events, loop = [], None
    last_note = None  # (event list) of the last note/chord, for ties
    accent = 0
    while True:
        c = p.peek()
        if not c:
            break
        p.i += 1
        if c in NOTE or c == "r" or c == "{":
            if c == "{":
                keys = []
                while True:
                    d = p.peek()
                    if d == "}":
                        p.i += 1
                        break
                    if d == ">":
                        octave += 1; p.i += 1; continue
                    if d == "<":
                        octave -= 1; p.i += 1; continue
                    if d not in NOTE:
                        p.error("bad chord")
                    p.i += 1
                    k = NOTE[d]
                    while p.i < len(p.s) and p.s[p.i] in "+#-":
                        k += -1 if p.s[p.i] == "-" else 1
                        p.i += 1
                    keys.append(12 * (octave + 1) + k + trans)
            elif c == "r":
                keys = []
            else:
                k = NOTE[c]
                while p.i < len(p.s) and p.s[p.i] in "+#-":
                    k += -1 if p.s[p.i] == "-" else 1
                    p.i += 1
                keys = [12 * (octave + 1) + k + trans]
            ln = p.length(deflen)
            notes = []
            for k in keys:
                if not 0 <= k < 128:
                    p.error(f"key {k} out of range")
                e = Event(tick, "note", k, min(127, vel + accent), ln)
                events.append(e)
                notes.append(e)
            last_note = (notes, gate)
            accent = 0
            tick += ln
            if notes:
                for e in notes:
                    e.c = max(1, ln * gate // 8) if gate < 8 else ln
        elif c == "^":
            ln = p.length(deflen)
            tick += ln
            if last_note:
                notes, g = last_note
                for e in notes:
                    full = tick - e.tick
                    e.c = max(1, full * g // 8) if g < 8 else full
        elif c == "o":
            octave = p.number()
        elif c == ">":
            octave += 1
        elif c == "<":
            octave -= 1
        elif c == "l":
            deflen = p.length(deflen)
        elif c == "@":
            events.append(Event(tick, "voice", p.number()))
        elif c == "v":
            events.append(Event(tick, "vol", p.number()))
        elif c == "V":
            vel = p.number()
        elif c == "p":
            events.append(Event(tick, "pan", p.number()))
        elif c == "k":
            trans = p.number(signed=True)
        elif c == "q":
            gate = p.number()
        elif c == "m":
            events.append(Event(tick, "mod", p.number()))
        elif c == "s":
            events.append(Event(tick, "lfos", p.number()))
        elif c == "L":
            loop = tick
        elif c == "!":
            accent = 30
        else:
            p.i -= 1
            p.error("unknown command")
    return events, loop, tick


def parse_song(path):
    meta, defines, tracks = {}, {}, {}
    order = []
    for raw in open(path, encoding="utf-8"):
        line = raw.split(";", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("#define"):
            _, key, val = line.split(None, 2)
            defines[key] = val
            continue
        if line.startswith("#"):
            key, _, val = line[1:].partition(" ")
            meta[key] = val.strip()
            continue
        m = re.match(r"\s*([A-Z])\s*:(.*)", line)
        if not m:
            raise SyntaxError(f"{path}: expected 'X: ...' track line: {line!r}")
        name, body = m.group(1), m.group(2)
        for k in sorted(defines, key=len, reverse=True):
            body = body.replace("$" + k, " " + defines[k] + " ")
        if name not in tracks:
            tracks[name] = ""
            order.append(name)
        tracks[name] += " " + body
    parsed = [(n,) + parse_track(tracks[n], n) for n in order]
    return meta, parsed
