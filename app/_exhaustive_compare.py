"""
Exhaustive SWF comparison: every single difference between OG and RT fox.ssf.
Compares: SWF header, top-level tags, DefineSprite inner timelines,
PlaceObject fields, SymbolClass, DoABC, shapes, bitmaps, etc.
"""
import struct, zlib, io, hashlib
from collections import Counter, defaultdict

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

TAG_NAMES = {
    0:'End', 1:'ShowFrame', 2:'DefineShape', 4:'PlaceObject',
    5:'RemoveObject', 6:'DefineBits', 9:'SetBackgroundColor',
    10:'DefineFont', 11:'DefineText', 12:'DoAction', 13:'DefineFontInfo',
    14:'DefineSound', 15:'StartSound', 20:'DefineBitsLossless',
    21:'DefineBitsJPEG2', 22:'DefineShape2', 24:'Protect',
    26:'PlaceObject2', 28:'RemoveObject2', 32:'DefineShape3',
    33:'DefineBitsJPEG3', 34:'DefineBitsLossless2', 35:'DefineBitsJPEG3',
    36:'DefineEditText', 37:'DefineSprite_old', 39:'DefineSprite',
    43:'FrameLabel', 45:'SoundStreamHead2', 46:'SoundStreamBlock',
    48:'DefineFont2', 56:'ExportAssets', 59:'DoInitAction',
    69:'FileAttributes', 70:'PlaceObject3', 73:'DefineFontAlignZones',
    75:'CSMTextSettings', 76:'SymbolClass', 77:'Metadata',
    78:'DefineScalingGrid', 82:'DoABC2', 83:'DefineShape4',
    84:'DefineMorphShape2', 86:'DefineSceneAndFrameLabelData',
    87:'DefineBinaryData', 88:'DefineFontName', 91:'DefineFont4',
}

def read_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('<B', f.read(1))[0]
        file_len = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    elif sig == b'ZWS':
        import lzma
        rest = lzma.decompress(rest)
    return sig, ver, file_len, rest

def parse_header(data):
    nbits = (data[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    
    # Parse rect
    br = BitReader(data[:rect_bytes])
    nb = br.read_bits(5)
    xmin = br.read_bits_signed(nb)
    xmax = br.read_bits_signed(nb)
    ymin = br.read_bits_signed(nb)
    ymax = br.read_bits_signed(nb)
    
    off = rect_bytes
    fps_raw = struct.unpack_from('<H', data, off)[0]
    off += 2
    frame_count = struct.unpack_from('<H', data, off)[0]
    off += 2
    
    return {
        'rect': (xmin, xmax, ymin, ymax),
        'fps_raw': fps_raw,
        'fps': fps_raw >> 8,
        'fps_frac': fps_raw & 0xFF,
        'frame_count': frame_count,
        'data_offset': off,
    }

class BitReader:
    def __init__(self, data):
        self.data = data
        self.byte_pos = 0
        self.bit_pos = 0
    
    def read_bits(self, n):
        val = 0
        for _ in range(n):
            if self.byte_pos >= len(self.data):
                return val
            byte = self.data[self.byte_pos]
            bit = (byte >> (7 - self.bit_pos)) & 1
            val = (val << 1) | bit
            self.bit_pos += 1
            if self.bit_pos == 8:
                self.bit_pos = 0
                self.byte_pos += 1
        return val
    
    def read_bits_signed(self, n):
        val = self.read_bits(n)
        if n > 0 and (val >> (n-1)):
            val -= (1 << n)
        return val

def iter_tags(data):
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        tag_start = pos
        pos += 2
        tt = h >> 6
        length = h & 0x3F
        if length == 0x3F:
            if pos + 4 > len(data): break
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        yield tt, body, tag_start
        pos += length
        if tt == 0: break

def tag_name(tt):
    return TAG_NAMES.get(tt, f'Unknown_{tt}')

def parse_place_object2(body):
    if len(body) < 3:
        return {'raw': body}
    flags = body[0]
    depth = struct.unpack_from('<H', body, 1)[0]
    off = 3
    result = {'flags': flags, 'depth': depth}
    
    if flags & 0x02:  # HasCharacter
        result['char_id'] = struct.unpack_from('<H', body, off)[0]
        off += 2
    if flags & 0x04:  # HasMatrix
        result['matrix_start'] = off
        # Skip matrix (variable length bit field)
        mat_end = skip_matrix(body, off)
        result['matrix_bytes'] = body[off:mat_end]
        off = mat_end
    if flags & 0x08:  # HasColorTransform
        ct_end = skip_cxform(body, off)
        result['cxform_bytes'] = body[off:ct_end]
        off = ct_end
    if flags & 0x10:  # HasRatio
        if off + 2 <= len(body):
            result['ratio'] = struct.unpack_from('<H', body, off)[0]
            off += 2
    if flags & 0x20:  # HasName
        end = body.index(b'\x00', off)
        result['name'] = body[off:end].decode('utf-8', errors='replace')
        off = end + 1
    if flags & 0x40:  # HasClipDepth
        if off + 2 <= len(body):
            result['clip_depth'] = struct.unpack_from('<H', body, off)[0]
            off += 2
    return result

def parse_place_object3(body):
    if len(body) < 4:
        return {'raw': body}
    flags = body[0]
    flags2 = body[1]
    depth = struct.unpack_from('<H', body, 2)[0]
    off = 4
    result = {'flags': flags, 'flags2': flags2, 'depth': depth}
    
    if flags & 0x02:
        result['char_id'] = struct.unpack_from('<H', body, off)[0]
        off += 2
    if flags & 0x04:
        mat_end = skip_matrix(body, off)
        result['matrix_bytes'] = body[off:mat_end]
        off = mat_end
    if flags & 0x08:
        ct_end = skip_cxform(body, off)
        result['cxform_bytes'] = body[off:ct_end]
        off = ct_end
    if flags & 0x10:
        if off + 2 <= len(body):
            result['ratio'] = struct.unpack_from('<H', body, off)[0]
            off += 2
    if flags & 0x20:
        end = body.index(b'\x00', off)
        result['name'] = body[off:end].decode('utf-8', errors='replace')
        off = end + 1
    if flags & 0x40:
        if off + 2 <= len(body):
            result['clip_depth'] = struct.unpack_from('<H', body, off)[0]
            off += 2
    # flags2 bits: HasFilterList, HasBlendMode, etc.
    if flags2 & 0x01:  # HasFilterList
        result['has_filters'] = True
    if flags2 & 0x02:  # HasBlendMode
        result['has_blend'] = True
    return result

def skip_matrix(data, off):
    """Skip a MATRIX record, return new offset."""
    if off >= len(data):
        return off
    br = BitReaderAt(data, off)
    has_scale = br.read_bits(1)
    if has_scale:
        n = br.read_bits(5)
        br.read_bits(n)  # scaleX
        br.read_bits(n)  # scaleY
    has_rotate = br.read_bits(1)
    if has_rotate:
        n = br.read_bits(5)
        br.read_bits(n)  # rotSkew0
        br.read_bits(n)  # rotSkew1
    n = br.read_bits(5)
    br.read_bits(n)  # translateX
    br.read_bits(n)  # translateY
    return off + br.bytes_consumed()

def skip_cxform(data, off):
    """Skip a CXFORMWITHALPHA record."""
    if off >= len(data):
        return off
    br = BitReaderAt(data, off)
    has_add = br.read_bits(1)
    has_mult = br.read_bits(1)
    nbits = br.read_bits(4)
    if has_mult:
        for _ in range(4): br.read_bits(nbits)
    if has_add:
        for _ in range(4): br.read_bits(nbits)
    return off + br.bytes_consumed()

class BitReaderAt:
    def __init__(self, data, byte_off):
        self.data = data
        self.base = byte_off
        self.bit_pos = 0  # total bits read
    
    def read_bits(self, n):
        val = 0
        for _ in range(n):
            byte_idx = self.base + (self.bit_pos >> 3)
            bit_idx = 7 - (self.bit_pos & 7)
            if byte_idx < len(self.data):
                val = (val << 1) | ((self.data[byte_idx] >> bit_idx) & 1)
            else:
                val = val << 1
            self.bit_pos += 1
        return val
    
    def bytes_consumed(self):
        return (self.bit_pos + 7) >> 3

def get_cid_from_tag(tt, body):
    """Extract character ID from definition tags."""
    if tt in (2, 22, 32, 83, 84, 39, 20, 34, 21, 33, 35, 6, 36, 10, 48, 14, 46, 87, 75, 73, 88):
        if len(body) >= 2:
            return struct.unpack_from('<H', body, 0)[0]
    return None

def main():
    print("Loading SWFs...")
    og_sig, og_ver, og_flen, og_raw = read_swf(OG)
    rt_sig, rt_ver, rt_flen, rt_raw = read_swf(RT)
    
    og_hdr = parse_header(og_raw)
    rt_hdr = parse_header(rt_raw)
    
    # ========== HEADER COMPARISON ==========
    print("\n" + "="*80)
    print("1. SWF HEADER")
    print("="*80)
    fields = [
        ('Signature', og_sig, rt_sig),
        ('Version', og_ver, rt_ver),
        ('File Length', og_flen, rt_flen),
        ('Decompressed Size', len(og_raw)+8, len(rt_raw)+8),
        ('Rect (xMin,xMax,yMin,yMax)', og_hdr['rect'], rt_hdr['rect']),
        ('FPS (raw hex)', f'0x{og_hdr["fps_raw"]:04X}', f'0x{rt_hdr["fps_raw"]:04X}'),
        ('FPS (integer)', og_hdr['fps'], rt_hdr['fps']),
        ('FPS (fraction)', og_hdr['fps_frac'], rt_hdr['fps_frac']),
        ('Frame Count', og_hdr['frame_count'], rt_hdr['frame_count']),
    ]
    
    print(f"{'Field':40s} {'OG':>20s} {'RT':>20s} {'Match':>6s}")
    print("-"*90)
    for name, og_val, rt_val in fields:
        match = "YES" if og_val == rt_val else "*** NO"
        print(f"{name:40s} {str(og_val):>20s} {str(rt_val):>20s} {match:>6s}")
    
    # ========== TOP-LEVEL TAG INVENTORY ==========
    print("\n" + "="*80)
    print("2. TOP-LEVEL TAG INVENTORY")
    print("="*80)
    
    og_tags = list(iter_tags(og_raw[og_hdr['data_offset']:]))
    rt_tags = list(iter_tags(rt_raw[rt_hdr['data_offset']:]))
    
    og_tag_counts = Counter()
    rt_tag_counts = Counter()
    for tt, body, _ in og_tags:
        og_tag_counts[tt] += 1
    for tt, body, _ in rt_tags:
        rt_tag_counts[tt] += 1
    
    all_types = sorted(set(og_tag_counts.keys()) | set(rt_tag_counts.keys()))
    print(f"{'Tag':40s} {'OG':>6s} {'RT':>6s} {'Match':>6s}")
    print("-"*60)
    for tt in all_types:
        oc = og_tag_counts.get(tt, 0)
        rc = rt_tag_counts.get(tt, 0)
        match = "YES" if oc == rc else "*** NO"
        print(f"{tag_name(tt)+f' ({tt})':40s} {oc:6d} {rc:6d} {match:>6s}")
    
    # ========== DoABC ==========
    print("\n" + "="*80)
    print("3. DoABC2 COMPARISON")
    print("="*80)
    og_abc = [body for tt, body, _ in og_tags if tt == 82]
    rt_abc = [body for tt, body, _ in rt_tags if tt == 82]
    print(f"OG DoABC2 tags: {len(og_abc)}, RT: {len(rt_abc)}")
    if len(og_abc) == len(rt_abc):
        for i in range(len(og_abc)):
            if og_abc[i] == rt_abc[i]:
                print(f"  Tag {i}: IDENTICAL ({len(og_abc[i])} bytes)")
            else:
                print(f"  Tag {i}: *** DIFFERENT (OG={len(og_abc[i])}B RT={len(rt_abc[i])}B)")
                # Find first diff byte
                for j in range(min(len(og_abc[i]), len(rt_abc[i]))):
                    if og_abc[i][j] != rt_abc[i][j]:
                        print(f"    First diff at byte {j}")
                        break
    
    # ========== SymbolClass ==========
    print("\n" + "="*80)
    print("4. SYMBOLCLASS COMPARISON")
    print("="*80)
    og_syms = {}
    rt_syms = {}
    for tt, body, _ in og_tags:
        if tt == 76:
            count = struct.unpack_from('<H', body, 0)[0]
            off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, off)[0]; off += 2
                end = body.index(b'\x00', off)
                name = body[off:end].decode('utf-8', errors='replace'); off = end + 1
                og_syms[name] = cid
    for tt, body, _ in rt_tags:
        if tt == 76:
            count = struct.unpack_from('<H', body, 0)[0]
            off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', body, off)[0]; off += 2
                end = body.index(b'\x00', off)
                name = body[off:end].decode('utf-8', errors='replace'); off = end + 1
                rt_syms[name] = cid
    
    og_names = set(og_syms.keys())
    rt_names = set(rt_syms.keys())
    only_og = og_names - rt_names
    only_rt = rt_names - og_names
    common = og_names & rt_names
    
    cid_mismatches = []
    for name in sorted(common):
        if og_syms[name] != rt_syms[name]:
            cid_mismatches.append((name, og_syms[name], rt_syms[name]))
    
    print(f"OG symbols: {len(og_syms)}, RT: {len(rt_syms)}, Common: {len(common)}")
    print(f"Only in OG: {len(only_og)}, Only in RT: {len(only_rt)}")
    if only_og:
        for n in sorted(only_og)[:20]:
            print(f"  OG only: {n} (CID {og_syms[n]})")
    if only_rt:
        for n in sorted(only_rt)[:20]:
            print(f"  RT only: {n} (CID {rt_syms[n]})")
    print(f"CID mismatches: {len(cid_mismatches)}")
    if cid_mismatches:
        for name, oc, rc in cid_mismatches[:30]:
            print(f"  {name}: OG={oc} RT={rc}")
        if len(cid_mismatches) > 30:
            print(f"  ... and {len(cid_mismatches)-30} more")
    
    # ========== FileAttributes ==========
    print("\n" + "="*80)
    print("5. FILE ATTRIBUTES")
    print("="*80)
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        for tt, body, _ in tags:
            if tt == 69:
                flags = struct.unpack_from('<I', body, 0)[0] if len(body) >= 4 else 0
                print(f"  {label}: flags=0x{flags:08X} (AS3={bool(flags&0x08)}, UseNetwork={bool(flags&0x01)})")
    
    # ========== SetBackgroundColor ==========
    print("\n" + "="*80)
    print("6. SET BACKGROUND COLOR")
    print("="*80)
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        for tt, body, _ in tags:
            if tt == 9:
                r, g, b_ = body[0], body[1], body[2]
                print(f"  {label}: RGB({r},{g},{b_})")
    
    # ========== DefineSceneAndFrameLabelData ==========
    print("\n" + "="*80)
    print("7. SCENE & FRAME LABELS")
    print("="*80)
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        for tt, body, _ in tags:
            if tt == 86:
                print(f"  {label}: {len(body)} bytes, hash={hashlib.md5(body).hexdigest()}")
    
    # ========== DefineSprite comparison ==========
    print("\n" + "="*80)
    print("8. DEFINE SPRITE COMPARISON")
    print("="*80)
    
    og_sprites = {}
    rt_sprites = {}
    for tt, body, _ in og_tags:
        if tt == 39:
            cid = struct.unpack_from('<H', body, 0)[0]
            og_sprites[cid] = body
    for tt, body, _ in rt_tags:
        if tt == 39:
            cid = struct.unpack_from('<H', body, 0)[0]
            rt_sprites[cid] = body
    
    # Map by class name
    og_cls2cid = {v: k for k, v in og_syms.items()}
    rt_cls2cid = {v: k for k, v in rt_syms.items()}
    
    sprite_classes = sorted(set(
        [og_cls2cid.get(cid, f'?cid{cid}') for cid in og_sprites] +
        [rt_cls2cid.get(cid, f'?cid{cid}') for cid in rt_sprites]
    ))
    
    # For sprites with matching classes, compare
    sprite_diffs = []
    for cls in sorted(common):
        og_cid = og_syms[cls]
        rt_cid = rt_syms[cls]
        og_body = og_sprites.get(og_cid)
        rt_body = rt_sprites.get(rt_cid)
        if og_body is None and rt_body is None:
            continue  # Not a sprite
        if og_body is None or rt_body is None:
            sprite_diffs.append((cls, "one missing", None))
            continue
        
        # Compare frame count
        og_fc = struct.unpack_from('<H', og_body, 2)[0]
        rt_fc = struct.unpack_from('<H', rt_body, 2)[0]
        
        og_inner = og_body[4:]
        rt_inner = rt_body[4:]
        
        if og_inner == rt_inner:
            continue  # Identical inner timeline
        
        # Detailed frame comparison
        og_frames = frames_from_inner(og_inner)
        rt_frames = frames_from_inner(rt_inner)
        
        diffs = compare_frames(og_frames, rt_frames, cls)
        if diffs:
            sprite_diffs.extend(diffs)
    
    print(f"\nSprite differences: {len(sprite_diffs)}")
    
    # Categorize
    cats = Counter()
    for cls, diff_type, detail in sprite_diffs:
        cats[diff_type] += 1
    
    print(f"\n{'Category':50s} {'Count':>6s}")
    print("-"*60)
    for cat, count in cats.most_common():
        print(f"{cat:50s} {count:6d}")
    
    # Print all differences
    print(f"\n{'='*80}")
    print("9. DETAILED SPRITE DIFFERENCES")
    print("="*80)
    for cls, diff_type, detail in sprite_diffs[:500]:
        if detail:
            print(f"[{cls}] {diff_type}: {detail}")
        else:
            print(f"[{cls}] {diff_type}")
    if len(sprite_diffs) > 500:
        print(f"... and {len(sprite_diffs)-500} more")
    
    # ========== Non-sprite definition tags ==========
    print(f"\n{'='*80}")
    print("10. NON-SPRITE DEFINITION TAG COMPARISON")
    print("="*80)
    
    # Group non-sprite definition tags by CID
    og_defs = {}  # cid → (tag_type, body_hash, body_len)
    rt_defs = {}
    for tt, body, _ in og_tags:
        if tt == 39: continue  # skip sprites
        cid = get_cid_from_tag(tt, body)
        if cid is not None:
            og_defs[cid] = (tt, hashlib.md5(body).hexdigest(), len(body))
    for tt, body, _ in rt_tags:
        if tt == 39: continue
        cid = get_cid_from_tag(tt, body)
        if cid is not None:
            rt_defs[cid] = (tt, hashlib.md5(body).hexdigest(), len(body))
    
    # Compare by symbol class mapping
    def_diffs = []
    for cls in sorted(common):
        og_cid = og_syms[cls]
        rt_cid = rt_syms[cls]
        if og_cid in og_defs and rt_cid in rt_defs:
            og_tt, og_h, og_l = og_defs[og_cid]
            rt_tt, rt_h, rt_l = rt_defs[rt_cid]
            if og_tt != rt_tt:
                def_diffs.append(f"[{cls}] tag type: OG={tag_name(og_tt)} RT={tag_name(rt_tt)}")
            elif og_h != rt_h:
                def_diffs.append(f"[{cls}] data differs: OG={og_l}B RT={rt_l}B (tag={tag_name(og_tt)})")
    
    print(f"Definition tag differences: {len(def_diffs)}")
    for d in def_diffs[:100]:
        print(f"  {d}")
    if len(def_diffs) > 100:
        print(f"  ... and {len(def_diffs)-100} more")
    
    # ========== Root timeline comparison ==========
    print(f"\n{'='*80}")
    print("11. ROOT TIMELINE COMPARISON")
    print("="*80)
    
    og_root = extract_root_timeline(og_tags)
    rt_root = extract_root_timeline(rt_tags)
    
    if len(og_root) != len(rt_root):
        print(f"Frame count: OG={len(og_root)} RT={len(rt_root)}")
    
    for fi in range(min(len(og_root), len(rt_root))):
        og_ft = og_root[fi]
        rt_ft = rt_root[fi]
        if len(og_ft) != len(rt_ft):
            print(f"  F{fi+1}: tag count OG={len(og_ft)} RT={len(rt_ft)}")
            continue
        for ti in range(len(og_ft)):
            if og_ft[ti] != rt_ft[ti]:
                ott, ob = og_ft[ti]
                rtt, rb = rt_ft[ti]
                print(f"  F{fi+1}[{ti}]: OG {tag_name(ott)}[{len(ob)}B] vs RT {tag_name(rtt)}[{len(rb)}B]")
    
    # ========== Sound tags ==========
    print(f"\n{'='*80}")
    print("12. SOUND TAGS")
    print("="*80)
    og_sounds = [(tt, body) for tt, body, _ in og_tags if tt in (14, 15, 45, 46, 19)]
    rt_sounds = [(tt, body) for tt, body, _ in rt_tags if tt in (14, 15, 45, 46, 19)]
    print(f"OG sound-related tags: {len(og_sounds)}, RT: {len(rt_sounds)}")
    og_sc = Counter(tt for tt, _ in og_sounds)
    rt_sc = Counter(tt for tt, _ in rt_sounds)
    for tt in sorted(set(og_sc.keys()) | set(rt_sc.keys())):
        print(f"  {tag_name(tt)}: OG={og_sc.get(tt,0)} RT={rt_sc.get(tt,0)}")

def frames_from_inner(inner):
    frames = []
    cur = []
    for tt, body in iter_tags_simple(inner):
        if tt == 0: break
        if tt == 1:
            frames.append(cur)
            cur = []
        else:
            cur.append((tt, body))
    return frames

def iter_tags_simple(data):
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        tt = h >> 6
        length = h & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        body = data[pos:pos+length]
        yield tt, body
        pos += length
        if tt == 0: break

def compare_frames(og_frames, rt_frames, cls):
    diffs = []
    if len(og_frames) != len(rt_frames):
        diffs.append((cls, "frame_count", f"OG={len(og_frames)} RT={len(rt_frames)}"))
        return diffs
    
    for fi in range(len(og_frames)):
        og_tags = og_frames[fi]
        rt_tags = rt_frames[fi]
        
        if len(og_tags) != len(rt_tags):
            # Show what's different
            og_summary = [(tag_name(t), len(b)) for t,b in og_tags]
            rt_summary = [(tag_name(t), len(b)) for t,b in rt_tags]
            diffs.append((cls, f"F{fi+1}_tag_count", f"OG={len(og_tags)} {og_summary} RT={len(rt_tags)} {rt_summary}"))
            continue
        
        for ti in range(len(og_tags)):
            ott, ob = og_tags[ti]
            rtt, rb = rt_tags[ti]
            
            if ott != rtt:
                diffs.append((cls, f"F{fi+1}_tag_type", f"OG={tag_name(ott)} RT={tag_name(rtt)}"))
            elif ob != rb:
                # Same type, different data
                if ott == 26:
                    diff_detail = describe_po2_diff(ob, rb)
                    diffs.append((cls, f"F{fi+1}_PO2_d{struct.unpack_from('<H',ob,1)[0]}", diff_detail))
                elif ott == 70:
                    diff_detail = describe_po3_diff(ob, rb)
                    diffs.append((cls, f"F{fi+1}_PO3_d{struct.unpack_from('<H',ob,2)[0]}", diff_detail))
                elif ott == 43:
                    og_label = ob[:ob.index(b'\x00')].decode('utf-8','replace') if b'\x00' in ob else ob.hex()
                    rt_label = rb[:rb.index(b'\x00')].decode('utf-8','replace') if b'\x00' in rb else rb.hex()
                    diffs.append((cls, f"F{fi+1}_label", f"'{og_label}' vs '{rt_label}'"))
                elif ott == 28:
                    og_d = struct.unpack_from('<H',ob,0)[0]
                    rt_d = struct.unpack_from('<H',rb,0)[0]
                    diffs.append((cls, f"F{fi+1}_remove", f"depth OG={og_d} RT={rt_d}"))
                else:
                    diffs.append((cls, f"F{fi+1}_tag{ott}", f"data differs OG={len(ob)}B RT={len(rb)}B"))
    return diffs

def describe_po2_diff(ob, rb):
    parts = []
    of = ob[0]; rf = rb[0]
    od = struct.unpack_from('<H',ob,1)[0]; rd = struct.unpack_from('<H',rb,1)[0]
    
    if of != rf:
        # Describe which flags differ
        diff = of ^ rf
        flag_names = {0x01:'Move', 0x02:'HasChar', 0x04:'HasMatrix', 0x08:'HasCxform',
                      0x10:'HasRatio', 0x20:'HasName', 0x40:'HasClipDepth'}
        for bit, name in flag_names.items():
            if diff & bit:
                og_has = bool(of & bit)
                parts.append(f"{name}:{'OG' if og_has else 'RT'}")
        parts.insert(0, f"flags 0x{of:02x}→0x{rf:02x}")
    
    # Parse both fully
    opo = parse_place_object2(ob)
    rpo = parse_place_object2(rb)
    
    if opo.get('char_id') != rpo.get('char_id'):
        parts.append(f"cid {opo.get('char_id')}→{rpo.get('char_id')}")
    if opo.get('matrix_bytes') != rpo.get('matrix_bytes'):
        parts.append("matrix differs")
    if opo.get('cxform_bytes') != rpo.get('cxform_bytes'):
        parts.append("cxform differs")
    if opo.get('ratio') != rpo.get('ratio'):
        parts.append(f"ratio {opo.get('ratio')}→{rpo.get('ratio')}")
    if opo.get('name') != rpo.get('name'):
        parts.append(f"name '{opo.get('name')}'→'{rpo.get('name')}'")
    if opo.get('clip_depth') != rpo.get('clip_depth'):
        parts.append(f"clipDepth {opo.get('clip_depth')}→{rpo.get('clip_depth')}")
    
    return "; ".join(parts) if parts else f"raw differs OG={len(ob)}B RT={len(rb)}B"

def describe_po3_diff(ob, rb):
    parts = []
    of = ob[0]; rf = rb[0]
    of2 = ob[1]; rf2 = rb[1]
    
    if of != rf:
        parts.append(f"flags 0x{of:02x}→0x{rf:02x}")
    if of2 != rf2:
        parts.append(f"flags2 0x{of2:02x}→0x{rf2:02x}")
    
    opo = parse_place_object3(ob)
    rpo = parse_place_object3(rb)
    
    if opo.get('char_id') != rpo.get('char_id'):
        parts.append(f"cid {opo.get('char_id')}→{rpo.get('char_id')}")
    if opo.get('ratio') != rpo.get('ratio'):
        parts.append(f"ratio {opo.get('ratio')}→{rpo.get('ratio')}")
    if opo.get('name') != rpo.get('name'):
        parts.append(f"name '{opo.get('name')}'→'{rpo.get('name')}'")
    
    return "; ".join(parts) if parts else f"raw differs OG={len(ob)}B RT={len(rb)}B"

def extract_root_timeline(tags):
    """Extract root timeline frames from top-level tags (excluding definitions)."""
    frames = []
    cur = []
    for tt, body, _ in tags:
        if tt == 1:  # ShowFrame
            frames.append(cur)
            cur = []
        elif tt in (26, 70, 28, 43):  # timeline tags
            cur.append((tt, body))
    return frames

if __name__ == '__main__':
    main()
