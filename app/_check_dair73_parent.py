"""
Find which sprites reference Sprite 1471 (DAir_73) as a child, and
examine those parent sprites for HasImage placements that might
interact with bm_dairHand.

Also: look for FrameLabel tags in the parent to understand the animation structure.
"""
import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

def parse_sprite(pay):
    """Parse a DefineSprite payload into frames, returning frame-separated tag lists."""
    frames = [[]]
    sp_pos = 4
    while sp_pos < len(pay) - 1:
        hdr = struct.unpack_from('<H', pay, sp_pos)[0]
        st = hdr >> 6; ssl = hdr & 0x3f; sp_pos += 2
        if ssl == 0x3f:
            sl2 = struct.unpack_from('<I', pay, sp_pos)[0]; sp_pos += 4
        else:
            sl2 = ssl
        spay = pay[sp_pos:sp_pos+sl2]
        if st == 0: break
        if st == 1:  # ShowFrame
            frames.append([])
        else:
            frames[-1].append((st, sl2, spay))
        sp_pos += sl2
    return frames

def analyze(path, label):
    with open(path, 'rb') as f: raw = f.read()
    if raw[:3] == b'CWS': raw = raw[:8] + zlib.decompress(raw[8:])
    pos = 8
    nb = (raw[pos] >> 3) & 0x1f
    pos += (5 + nb * 4 + 7) // 8 + 4

    ll2_cids = set()
    sprite_payloads = {}
    while pos < len(raw) - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tt = hdr >> 6; sl = hdr & 0x3f; pos += 2
        if sl == 0x3f:
            l = struct.unpack_from('<I', raw, pos)[0]; pos += 4
        else:
            l = sl
        pay = raw[pos:pos+l]
        if tt == 0: break
        if tt == 36 and l >= 2: ll2_cids.add(struct.unpack_from('<H', pay)[0])
        elif tt == 39 and l >= 4: sprite_payloads[struct.unpack_from('<H', pay)[0]] = pay
        pos += l

    print(f"\n=== {label}: Who references Sprite 1471 (DAir_73) ===")
    parents = []
    for sid, spay in sprite_payloads.items():
        frames = parse_sprite(spay)
        for fi, frame_tags in enumerate(frames):
            for st, sl2, payload in frame_tags:
                if st in (26, 70) and sl2 >= 5:
                    has_char = (payload[0] >> 1) & 1 if st == 26 else (struct.unpack_from('<H', payload)[0] >> 1) & 1
                    cid_off = 3 if st == 26 else 4
                    if has_char and sl2 >= cid_off + 2:
                        cid = struct.unpack_from('<H', payload, cid_off)[0]
                        if cid == 1471:
                            depth = struct.unpack_from('<H', payload, 1)[0] if st == 26 else struct.unpack_from('<H', payload, 2)[0]
                            print(f"  Sprite {sid} frame {fi+1}: PO{st-22} depth={depth} -> Sprite 1471 (DAir_73)")
                            parents.append(sid)

    # Also check if any parent sprite has HasImage bitmaps at the same depth as DAir_73
    if parents:
        print(f"\n  Parent sprite details:")
        for pid in set(parents):
            spay = sprite_payloads[pid]
            frames = parse_sprite(spay)
            fc = struct.unpack_from('<H', spay, 2)[0]
            print(f"\n  Sprite {pid} (frameCount={fc}):")
            # Find the depth where DAir_73 is placed
            dair73_depths = set()
            for fi, frame_tags in enumerate(frames):
                for st, sl2, payload in frame_tags:
                    if st in (26, 70) and sl2 >= 5:
                        has_char = (payload[0] >> 1) & 1 if st == 26 else (struct.unpack_from('<H', payload)[0] >> 1) & 1
                        cid_off = 3 if st == 26 else 4
                        if has_char and sl2 >= cid_off + 2:
                            cid = struct.unpack_from('<H', payload, cid_off)[0]
                            if cid == 1471:
                                depth = struct.unpack_from('<H', payload, 1)[0] if st == 26 else struct.unpack_from('<H', payload, 2)[0]
                                dair73_depths.add(depth)
            print(f"    DAir_73 placed at depths: {dair73_depths}")

            # List ALL frame labels
            labels = []
            for fi, frame_tags in enumerate(frames):
                for st, sl2, payload in frame_tags:
                    if st == 43 and sl2 >= 1:  # FrameLabel
                        label_name = payload[:sl2].rstrip(b'\x00').decode('utf-8', errors='replace')
                        labels.append((fi+1, label_name))
            print(f"    Total frames: {len(frames)}, Total labels: {len(labels)}")
            if len(labels) <= 30:
                for fn, ln in labels:
                    print(f"      Frame {fn}: '{ln}'")
            else:
                for fn, ln in labels[:15]:
                    print(f"      Frame {fn}: '{ln}'")
                print(f"      ... and {len(labels)-15} more labels")

            # Check: any HasImage PO3 in parent sprite itself?
            hi_count = 0
            for fi, frame_tags in enumerate(frames):
                for st, sl2, payload in frame_tags:
                    if st == 70 and sl2 >= 6:
                        flags = struct.unpack_from('<H', payload)[0]
                        has_img = (flags >> 12) & 1
                        if has_img: hi_count += 1
            print(f"    HasImage PO3 count in parent: {hi_count}")

analyze(RT, "RT")
analyze(OG, "OG")
