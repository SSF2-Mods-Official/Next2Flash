"""Build display list for Idle_3 frame 26 in OG vs RT pichu."""
import struct, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\pichu.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\pichu.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    if sig in (b'CWS', b'ZWS'):
        data = data[:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset=0):
    tags = []
    pos = offset
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        tag_type = h >> 6; length = h & 0x3F; pos += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]; pos += 4
        tags.append((tag_type, data[pos:pos+length]))
        pos += length
        if tag_type == 0: break
    return tags

def skip_header(data):
    pos = 8
    nbits = data[pos] >> 3
    pos += (5 + nbits * 4 + 7) // 8 + 4
    return pos

def parse_symbol_class(data):
    pos = 0; count = struct.unpack_from('<H', data, pos)[0]; pos += 2
    symbols = {}
    for _ in range(count):
        cid = struct.unpack_from('<H', data, pos)[0]; pos += 2
        end = data.index(0, pos)
        symbols[data[pos:end].decode('utf-8')] = cid; pos = end + 1
    return symbols

def parse_po2_full(data):
    flags = data[0]; pos = 1
    depth = struct.unpack_from('<H', data, pos)[0]; pos += 2
    r = {'flags': flags, 'depth': depth, 'is_move': bool(flags & 1)}
    if flags & 0x02:
        r['cid'] = struct.unpack_from('<H', data, pos)[0]; pos += 2
    return r

og = read_swf(OG); rt = read_swf(RT)
og_tags = parse_tags(og, skip_header(og))
rt_tags = parse_tags(rt, skip_header(rt))

og_sym = rt_sym = None
for t, d in og_tags:
    if t == 76: og_sym = parse_symbol_class(d)
for t, d in rt_tags:
    if t == 76: rt_sym = parse_symbol_class(d)

idle_name = [n for n in og_sym if 'Idle_3' in n][0]
print("Symbol:", idle_name)

og_cid_to_name = {v: k for k, v in og_sym.items()}
rt_cid_to_name = {v: k for k, v in rt_sym.items()}

og_sprites = {}; rt_sprites = {}
for t, d in og_tags:
    if t in (39, 37):
        cid = struct.unpack_from('<H', d, 0)[0]
        og_sprites[cid] = parse_tags(d, 4)
for t, d in rt_tags:
    if t in (39, 37):
        cid = struct.unpack_from('<H', d, 0)[0]
        rt_sprites[cid] = parse_tags(d, 4)

og_cid = og_sym[idle_name]
rt_cid = rt_sym[idle_name]

def build_display_list(inner_tags):
    dl = {}
    frames = []
    frame_actions = []  # track what happens each frame
    cur_actions = []
    for t, d in inner_tags:
        if t in (26, 70):
            po = parse_po2_full(d)
            depth = po['depth']
            cur_actions.append(('place', depth, po.get('cid'), po['is_move']))
            if po['is_move']:
                if depth in dl:
                    dl[depth] = {**dl[depth], **{k: v for k, v in po.items() if k not in ('is_move',)}}
                else:
                    dl[depth] = po.copy()
            else:
                dl[depth] = po.copy()
        elif t == 28:
            depth = struct.unpack_from('<H', d, 0)[0]
            cur_actions.append(('remove', depth))
            dl.pop(depth, None)
        elif t == 1:
            frames.append(dict(dl))
            frame_actions.append(cur_actions)
            cur_actions = []
    return frames, frame_actions

og_dl, og_actions = build_display_list(og_sprites[og_cid])
rt_dl, rt_actions = build_display_list(rt_sprites[rt_cid])
print("OG frames:", len(og_dl), "RT frames:", len(rt_dl))

# Show display list around frame 26
for fi in range(max(0, 20), min(len(og_dl), len(rt_dl), 30)):
    og_depths = set(og_dl[fi].keys())
    rt_depths = set(rt_dl[fi].keys())
    only_og = og_depths - rt_depths
    only_rt = rt_depths - og_depths
    
    if only_og or only_rt:
        print(f"\nFrame {fi+1}: DISPLAY LIST DIFFERS")
        if only_og:
            for d in sorted(only_og):
                cid = og_dl[fi][d].get('cid', '?')
                name = og_cid_to_name.get(cid, '')
                print(f"  Only in OG: depth={d} cid={cid} {name}")
        if only_rt:
            for d in sorted(only_rt):
                cid = rt_dl[fi][d].get('cid', '?')
                name = rt_cid_to_name.get(cid, '')
                print(f"  Only in RT: depth={d} cid={cid} {name}")
    
    # Check CID diffs at common depths
    for d in sorted(og_depths & rt_depths):
        og_c = og_dl[fi][d].get('cid')
        rt_c = rt_dl[fi][d].get('cid')
        if og_c and rt_c:
            og_name = og_cid_to_name.get(og_c, '')
            rt_name = rt_cid_to_name.get(rt_c, '')
            if og_name != rt_name:
                print(f"  Frame {fi+1} depth={d}: OG={og_name}(cid={og_c}) vs RT={rt_name}(cid={rt_c})")

# Focus: what's at depth 1 across frames?
print("\n\n=== Depth 1 tracking (the removed depth in OG) ===")
for fi in range(min(len(og_dl), 30)):
    og_has = 1 in og_dl[fi]
    rt_has = 1 in rt_dl[fi] if fi < len(rt_dl) else False
    if og_has != rt_has or fi >= 24:
        og_cid_v = og_dl[fi].get(1, {}).get('cid', '-')
        rt_cid_v = rt_dl[fi].get(1, {}).get('cid', '-') if fi < len(rt_dl) else '-'
        og_name_v = og_cid_to_name.get(og_cid_v, '') if isinstance(og_cid_v, int) else ''
        rt_name_v = rt_cid_to_name.get(rt_cid_v, '') if isinstance(rt_cid_v, int) else ''
        print(f"  Frame {fi+1}: OG depth1={'YES cid='+str(og_cid_v)+' '+og_name_v if og_has else 'NO'}, RT depth1={'YES cid='+str(rt_cid_v)+' '+rt_name_v if rt_has else 'NO'}")

# What about the frame26 script? Check the AS3 source
print("\n\n=== Frame actions around frame 26 ===")
for fi in range(24, min(30, len(og_actions))):
    if og_actions[fi]:
        print(f"OG frame {fi+1}: {og_actions[fi]}")
    if fi < len(rt_actions) and rt_actions[fi]:
        print(f"RT frame {fi+1}: {rt_actions[fi]}")
