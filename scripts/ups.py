#!/usr/bin/env python3
"""Create and apply UPS patches (byuu's format), standard library only.

    ups.py create SOURCE TARGET PATCH   write a patch that turns SOURCE into TARGET
    ups.py apply  SOURCE PATCH OUTPUT   apply PATCH to SOURCE and write OUTPUT

Applying checks the source, output and patch CRC32s stored in the patch, so a
wrong base ROM or a corrupted patch is reported instead of producing a bad file.
"""
import argparse
import sys
import zlib

MAGIC = b"UPS1"


def _encode_varint(value):
    out = bytearray()
    while True:
        low = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(0x80 | low)
            return bytes(out)
        out.append(low)
        value -= 1


def _decode_varint(data, pos):
    value, shift = 0, 1
    while True:
        byte = data[pos]
        pos += 1
        value += (byte & 0x7F) * shift
        if byte & 0x80:
            return value, pos
        shift <<= 7
        value += shift


def create(source, target):
    patch = bytearray(MAGIC)
    patch += _encode_varint(len(source))
    patch += _encode_varint(len(target))

    src_len, tgt_len = len(source), len(target)
    length = max(src_len, tgt_len)
    relative = 0
    i = 0
    while i < length:
        x = source[i] if i < src_len else 0
        y = target[i] if i < tgt_len else 0
        if x == y:
            i += 1
            continue
        patch += _encode_varint(i - relative)
        # XOR run until (and including) the first matching byte, which doubles
        # as the 0x00 hunk terminator.
        while True:
            if i >= length:
                patch.append(0)
                break
            x = source[i] if i < src_len else 0
            y = target[i] if i < tgt_len else 0
            i += 1
            patch.append(x ^ y)
            if x == y:
                break
        relative = i

    patch += zlib.crc32(source).to_bytes(4, "little")
    patch += zlib.crc32(target).to_bytes(4, "little")
    patch += zlib.crc32(patch).to_bytes(4, "little")
    return bytes(patch)


def apply(source, patch):
    if patch[:4] != MAGIC or len(patch) < 18:
        raise ValueError("not a UPS patch")
    if zlib.crc32(patch[:-4]) != int.from_bytes(patch[-4:], "little"):
        raise ValueError("patch is corrupted (patch CRC32 mismatch)")
    src_crc = int.from_bytes(patch[-12:-8], "little")
    out_crc = int.from_bytes(patch[-8:-4], "little")
    if zlib.crc32(source) != src_crc:
        raise ValueError(f"wrong source file: CRC32 {zlib.crc32(source):08x}, patch expects {src_crc:08x}")

    pos = 4
    src_size, pos = _decode_varint(patch, pos)
    out_size, pos = _decode_varint(patch, pos)
    if len(source) != src_size:
        raise ValueError("wrong source file size")

    out = bytearray(source[:out_size])
    out.extend(b"\x00" * (out_size - len(out)))
    end = len(patch) - 12
    i = 0
    while pos < end:
        skip, pos = _decode_varint(patch, pos)
        i += skip
        while True:
            byte = patch[pos]
            pos += 1
            if byte == 0:
                i += 1
                break
            if i < out_size:
                out[i] ^= byte
            i += 1
    if zlib.crc32(out) != out_crc:
        raise ValueError("output CRC32 mismatch after applying patch")
    return bytes(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("source")
    c.add_argument("target")
    c.add_argument("patch")
    a = sub.add_parser("apply")
    a.add_argument("source")
    a.add_argument("patch")
    a.add_argument("output")
    args = parser.parse_args(argv)

    try:
        if args.cmd == "create":
            with open(args.source, "rb") as f:
                source = f.read()
            with open(args.target, "rb") as f:
                target = f.read()
            patch = create(source, target)
            if apply(source, patch) != target:
                raise ValueError("internal error: patch does not round-trip")
            with open(args.patch, "wb") as f:
                f.write(patch)
            print(f"wrote {args.patch} ({len(patch)} bytes)")
        else:
            with open(args.source, "rb") as f:
                source = f.read()
            with open(args.patch, "rb") as f:
                patch = f.read()
            with open(args.output, "wb") as f:
                f.write(apply(source, patch))
            print(f"wrote {args.output}")
    except (OSError, ValueError) as e:
        print(f"ups.py: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
