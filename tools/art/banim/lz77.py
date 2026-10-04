"""GBA BIOS LZ77 (type 0x10) compression, as used for battle animation data."""


def decompress(data, off=0):
    assert data[off] == 0x10, hex(data[off])
    size = data[off + 1] | data[off + 2] << 8 | data[off + 3] << 16
    out = bytearray()
    i = off + 4
    while len(out) < size:
        flags = data[i]; i += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b0, b1 = data[i], data[i + 1]; i += 2
                n = (b0 >> 4) + 3
                disp = ((b0 & 0xF) << 8 | b1) + 1
                for _ in range(n):
                    out.append(out[-disp])
            else:
                out.append(data[i]); i += 1
    return bytes(out)


def compress(data):
    """Greedy LZ77 with a 4 KiB window and hash chains. Displacement >= 2 keeps
    the stream safe for the BIOS VRAM decompressor too."""
    data = bytes(data)
    n = len(data)
    out = bytearray([0x10, n & 0xFF, n >> 8 & 0xFF, n >> 16 & 0xFF])
    chains = {}
    i = 0

    def remember(k):
        if k + 2 < n:
            chains.setdefault(data[k:k + 3], []).append(k)

    while i < n:
        flag_pos = len(out); out.append(0); flags = 0
        for bit in range(8):
            if i >= n:
                break
            best_len, best_disp = 0, 0
            for j in reversed(chains.get(data[i:i + 3], [])):
                if i - j > 4096:
                    break
                if i - j < 2:
                    continue
                L = 3
                while L < 18 and i + L < n and data[j + L] == data[i + L]:
                    L += 1
                if L > best_len:
                    best_len, best_disp = L, i - j
                    if L == 18:
                        break
            if best_len >= 3:
                flags |= 0x80 >> bit
                d = best_disp - 1
                out += bytes([(best_len - 3) << 4 | d >> 8, d & 0xFF])
                for k in range(i, i + best_len):
                    remember(k)
                i += best_len
            else:
                out.append(data[i]); remember(i); i += 1
        out[flag_pos] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)
