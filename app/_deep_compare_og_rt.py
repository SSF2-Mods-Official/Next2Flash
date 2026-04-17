"""
Deep comparison of OG fox.ssf vs RT fox_fixed.swf:
1. DoABC byte comparison
2. SymbolClass mappings
3. DefineSprite frame counts
4. Frame label comparison per sprite
"""
import struct, sys, os, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"

def parse_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('<B', f.read(1))[0]
        length = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    elif sig == b'ZWS':
        import lzma
        rest = lzma.decompress(rest)
    elif sig != b'FWS':
        raise ValueError(f"Unknown SWF sig: {sig}")
    # skip rect
    data = rest
    nbits = (data[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    data = data[rect_bytes:]
    # frame rate, frame count
    data = data[4:]  # skip frame_rate(2) + frame_count(2)
    return data

def iter_tags(data):
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data):
            break
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        tag_type = tag_code_and_length >> 6
        length = tag_code_and_length & 0x3F
        if length == 0x3F:
            if pos + 4 > len(data):
                break
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        tag_data = data[pos:pos+length]
        yield tag_type, tag_data
        pos += length
        if tag_type == 0:
            break

def parse_symbol_class(tag_data):
    """Parse SymbolClass tag -> {charID: className}"""
    num = struct.unpack_from('<H', tag_data, 0)[0]
    off = 2
    result = {}
    for _ in range(num):
        cid = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
        end = tag_data.index(0, off)
        name = tag_data[off:end].decode('utf-8')
        off = end + 1
        result[cid] = name
    return result

def parse_define_sprite(tag_data):
    """Parse DefineSprite -> (charID, frameCount, inner_tags_data)"""
    cid = struct.unpack_from('<H', tag_data, 0)[0]
    fc = struct.unpack_from('<H', tag_data, 2)[0]
    return cid, fc, tag_data[4:]

def get_frame_labels(inner_data):
    """Get frame labels from inner tags of a DefineSprite"""
    labels = {}
    frame = 0
    for tt, td in iter_tags(inner_data):
        if tt == 1:  # ShowFrame
            frame += 1
        elif tt == 43:  # FrameLabel
            end = td.index(0)
            name = td[:end].decode('utf-8')
            labels[frame] = name
    return labels

def analyze_swf(path):
    data = parse_swf(path)
    result = {
        'symbol_class': {},
        'sprites': {},  # cid -> (frame_count, labels)
        'doabc': [],
        'doabc_bytes': b'',
        'tag_sequence': [],
    }
    for tt, td in iter_tags(data):
        result['tag_sequence'].append(tt)
        if tt == 76:  # SymbolClass
            result['symbol_class'].update(parse_symbol_class(td))
        elif tt == 39:  # DefineSprite
            cid, fc, inner = parse_define_sprite(td)
            labels = get_frame_labels(inner)
            result['sprites'][cid] = (fc, labels)
        elif tt == 82:  # DoABC2
            result['doabc'].append(td)
            result['doabc_bytes'] = td
    return result

print("Analyzing OG...")
og = analyze_swf(OG)
print("Analyzing RT...")
rt = analyze_swf(RT)

# 1. DoABC comparison
print("\n=== DoABC COMPARISON ===")
if len(og['doabc']) != len(rt['doabc']):
    print(f"  Different number of DoABC tags: OG={len(og['doabc'])}, RT={len(rt['doabc'])}")
else:
    for i, (a, b) in enumerate(zip(og['doabc'], rt['doabc'])):
        if a == b:
            print(f"  DoABC[{i}]: IDENTICAL ({len(a)} bytes)")
        else:
            print(f"  DoABC[{i}]: DIFFERENT! OG={len(a)} bytes, RT={len(b)} bytes")
            # Find first difference
            for j in range(min(len(a), len(b))):
                if a[j] != b[j]:
                    print(f"    First diff at byte {j}: OG=0x{a[j]:02x}, RT=0x{b[j]:02x}")
                    print(f"    Context OG: {a[max(0,j-8):j+8].hex()}")
                    print(f"    Context RT: {b[max(0,j-8):j+8].hex()}")
                    break

# 2. SymbolClass comparison
print("\n=== SYMBOLCLASS COMPARISON ===")
og_by_name = {v: k for k, v in og['symbol_class'].items()}
rt_by_name = {v: k for k, v in rt['symbol_class'].items()}

og_names = set(og['symbol_class'].values())
rt_names = set(rt['symbol_class'].values())

missing_in_rt = og_names - rt_names
missing_in_og = rt_names - og_names

if missing_in_rt:
    print(f"  Classes in OG but NOT in RT ({len(missing_in_rt)}):")
    for n in sorted(missing_in_rt)[:20]:
        print(f"    {n} (OG CID={og_by_name[n]})")

if missing_in_og:
    print(f"  Classes in RT but NOT in OG ({len(missing_in_og)}):")
    for n in sorted(missing_in_og)[:20]:
        print(f"    {n} (RT CID={rt_by_name[n]})")

if not missing_in_rt and not missing_in_og:
    print(f"  Same {len(og_names)} class names in both")

# 3. Compare frame counts for stance MCs (classes shared between both)
print("\n=== FRAME COUNT COMPARISON (stance MCs) ===")
common_names = og_names & rt_names
mismatches = []
for name in sorted(common_names):
    og_cid = og_by_name[name]
    rt_cid = rt_by_name[name]
    og_info = og['sprites'].get(og_cid)
    rt_info = rt['sprites'].get(rt_cid)
    if og_info is None and rt_info is None:
        continue  # not a sprite
    if og_info is None:
        mismatches.append(f"  {name}: OG CID {og_cid} NOT a DefineSprite, RT CID {rt_cid} IS ({rt_info[0]} frames)")
        continue
    if rt_info is None:
        mismatches.append(f"  {name}: OG CID {og_cid} IS a DefineSprite ({og_info[0]} frames), RT CID {rt_cid} NOT")
        continue
    og_fc, og_labels = og_info
    rt_fc, rt_labels = rt_info
    if og_fc != rt_fc:
        mismatches.append(f"  {name}: frame count OG={og_fc} RT={rt_fc}")
    if og_labels != rt_labels:
        mismatches.append(f"  {name}: labels OG={og_labels} RT={rt_labels}")

if mismatches:
    print(f"  {len(mismatches)} differences found:")
    for m in mismatches[:50]:
        print(m)
else:
    print("  All frame counts and labels match!")

# 4. Check a few key stances in detail
print("\n=== KEY STANCE DETAILS ===")
key_stances = [
    'fox_fla.fox_combo_36', 'fox_fla.fox_hurt_103', 'fox_fla.fox_idle_14',
    'fox_fla.fox_DashA_37', 'fox_fla.fox_tiltS_38', 'fox_fla.fox_smashS_39',
    'fox_fla.fox_fall_31', 'fox_fla.fox_jump_29', 'fox_fla.fox_run_27',
    'fox_fla.Fox_Knockback_113', 'fox_fla.fox_specialN_48',
]
for name in key_stances:
    og_cid = og_by_name.get(name)
    rt_cid = rt_by_name.get(name)
    if og_cid is None:
        print(f"  {name}: NOT in OG SymbolClass")
        continue
    if rt_cid is None:
        print(f"  {name}: NOT in RT SymbolClass")
        continue
    og_info = og['sprites'].get(og_cid, ('N/A', {}))
    rt_info = rt['sprites'].get(rt_cid, ('N/A', {}))
    status = "OK" if og_info == rt_info else "DIFF"
    print(f"  [{status}] {name}")
    print(f"    OG: CID={og_cid}, frames={og_info[0]}, labels={og_info[1]}")
    print(f"    RT: CID={rt_cid}, frames={rt_info[0]}, labels={rt_info[1]}")

# 5. Overall sprite stats
print(f"\n=== SPRITE STATS ===")
print(f"  OG: {len(og['sprites'])} DefineSprite tags, {len(og['symbol_class'])} SymbolClass entries")
print(f"  RT: {len(rt['sprites'])} DefineSprite tags, {len(rt['symbol_class'])} SymbolClass entries")
