"""Compare sprite frame counts and frame labels between OG and RT SWFs.

If frame counts differ, addFrameScript() calls in DoABC might reference
frames that don't exist in the RT MovieClip, causing animations to loop
instead of reaching endAttack() calls.
"""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))

from as3_decompiler.swf_reader import iter_tags

OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT_PATH = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"


def parse_sprites(path):
    """Return dict mapping charId -> (frameCount, labels, charId)."""
    sprites = {}
    for tag_code, tag_data in iter_tags(path):
        if tag_code == 39:  # DefineSprite
            sprite_id = struct.unpack_from('<H', tag_data, 0)[0]
            frame_count = struct.unpack_from('<H', tag_data, 2)[0]
            # Parse inner tags for frame labels
            labels = []
            inner = tag_data[4:]
            pos = 0
            current_frame = 0
            while pos < len(inner):
                if pos + 2 > len(inner):
                    break
                tag_and_len = struct.unpack_from('<H', inner, pos)[0]
                inner_code = tag_and_len >> 6
                inner_len = tag_and_len & 0x3F
                pos += 2
                if inner_len == 0x3F:
                    if pos + 4 > len(inner):
                        break
                    inner_len = struct.unpack_from('<I', inner, pos)[0]
                    pos += 4
                tag_body = inner[pos:pos + inner_len]
                pos += inner_len
                if inner_code == 0:  # End
                    break
                elif inner_code == 1:  # ShowFrame
                    current_frame += 1
                elif inner_code == 43:  # FrameLabel
                    null_idx = tag_body.find(b'\x00')
                    if null_idx >= 0:
                        label = tag_body[:null_idx].decode('utf-8', errors='replace')
                        labels.append((current_frame, label))
            sprites[sprite_id] = {
                'frames': frame_count,
                'labels': labels,
            }
    return sprites


def parse_symbol_class(path):
    """Return dict mapping charId -> className."""
    symbols = {}
    for tag_code, tag_data in iter_tags(path):
        if tag_code == 76:  # SymbolClass
            count = struct.unpack_from('<H', tag_data, 0)[0]
            pos = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', tag_data, pos)[0]
                pos += 2
                null_idx = tag_data.find(b'\x00', pos)
                name = tag_data[pos:null_idx].decode('utf-8', errors='replace')
                pos = null_idx + 1
                symbols[cid] = name
    return symbols


def main():
    print("Reading OG:", OG_PATH)
    og_sprites = parse_sprites(OG_PATH)
    og_symbols = parse_symbol_class(OG_PATH)

    print("Reading RT:", RT_PATH)
    rt_sprites = parse_sprites(RT_PATH)
    rt_symbols = parse_symbol_class(RT_PATH)

    # Build name -> sprite info mappings
    og_by_name = {}
    for cid, info in og_sprites.items():
        name = og_symbols.get(cid, f"unnamed_{cid}")
        og_by_name[name] = info

    rt_by_name = {}
    for cid, info in rt_sprites.items():
        name = rt_symbols.get(cid, f"unnamed_{cid}")
        rt_by_name[name] = info

    # Compare
    all_names = sorted(set(og_by_name.keys()) | set(rt_by_name.keys()))

    frame_diffs = []
    label_diffs = []
    missing_in_rt = []
    missing_in_og = []

    for name in all_names:
        og = og_by_name.get(name)
        rt = rt_by_name.get(name)

        if og and not rt:
            missing_in_rt.append(name)
            continue
        if rt and not og:
            missing_in_og.append(name)
            continue

        if og['frames'] != rt['frames']:
            frame_diffs.append((name, og['frames'], rt['frames']))

        og_labels = sorted(og.get('labels', []))
        rt_labels = sorted(rt.get('labels', []))
        if og_labels != rt_labels:
            label_diffs.append((name, og_labels, rt_labels))

    # Report
    print(f"\n=== FRAME COUNT COMPARISON ===")
    print(f"OG sprites: {len(og_sprites)}, RT sprites: {len(rt_sprites)}")
    print(f"Matched by name: {len(all_names) - len(missing_in_rt) - len(missing_in_og)}")

    if frame_diffs:
        print(f"\n--- FRAME COUNT MISMATCHES ({len(frame_diffs)}) ---")
        for name, og_fc, rt_fc in sorted(frame_diffs, key=lambda x: abs(x[1]-x[2]), reverse=True):
            print(f"  {name}: OG={og_fc} RT={rt_fc} (diff={rt_fc-og_fc})")
    else:
        print("\nNo frame count mismatches!")

    if label_diffs:
        print(f"\n--- FRAME LABEL MISMATCHES ({len(label_diffs)}) ---")
        for name, og_labels, rt_labels in label_diffs:
            og_only = set(og_labels) - set(rt_labels)
            rt_only = set(rt_labels) - set(og_labels)
            print(f"  {name}:")
            if og_only:
                print(f"    OG only: {sorted(og_only)}")
            if rt_only:
                print(f"    RT only: {sorted(rt_only)}")
    else:
        print("\nNo frame label mismatches!")

    if missing_in_rt:
        print(f"\n--- MISSING IN RT ({len(missing_in_rt)}) ---")
        for n in missing_in_rt:
            print(f"  {n}")
    if missing_in_og:
        print(f"\n--- ONLY IN RT ({len(missing_in_og)}) ---")
        for n in missing_in_og:
            print(f"  {n}")


if __name__ == '__main__':
    main()
