#!/usr/bin/env python3
"""Assemble the small Thumb routines under AoT/ into .dmp files.

    python3 tools/asm.py AoT/Engine/BoardCarried.s [more.s ...]

Writes <name>.dmp next to each source. The build includes the .dmp files, so
this only needs to run after editing a .s file. Needs `pip install
keystone-engine capstone` (not part of the normal build).

The GBA CPU is ARMv4T, which only has 16-bit Thumb instructions plus the
two-halfword BL. Keystone assembles for a newer CPU and will silently pick
32-bit Thumb-2 encodings (mov.w, bic.w, ...), so every instruction is checked
after assembly and anything else is rejected. Routines must be position
independent: call ROM functions through a register (ldr r3, =Func; bl call_r3).
"""
import pathlib
import re
import sys

import capstone
import keystone

BASE = 0x08000000  # any address works for position-independent code


def assemble(path):
    src = pathlib.Path(path).read_text()
    ks = keystone.Ks(keystone.KS_ARCH_ARM, keystone.KS_MODE_THUMB)
    encoding, _ = ks.asm(src, BASE)
    code = bytes(encoding)

    # Size of the instructions alone: drop the literal pool and give every
    # `ldr rX, =value` a same-size placeholder.
    body = re.sub(r"ldr\s+(r\d)\s*,\s*=\s*\w+", r"ldr \1, [pc, #0]", src.split(".ltorg")[0])
    code_len = len(ks.asm(body, BASE)[0])

    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    checked = 0
    for insn in md.disasm(code[:code_len], BASE):
        if insn.size == 4 and insn.mnemonic != "bl":
            raise SystemExit(
                f"{path}: 32-bit Thumb-2 instruction at +{insn.address - BASE:#x}: "
                f"{insn.mnemonic} {insn.op_str} (ARMv4T cannot run it)"
            )
        checked += insn.size
    if checked != code_len:
        raise SystemExit(f"{path}: could not disassemble past +{checked:#x}")

    out = pathlib.Path(path).with_suffix(".dmp")
    out.write_bytes(code)
    print(f"{out}: {len(code)} bytes")


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    for path in argv:
        assemble(path)


if __name__ == "__main__":
    main(sys.argv[1:])
