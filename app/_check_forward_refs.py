"""Check RT smashville for forward references and undefined character IDs."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\stage\smashville.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\stage\smashville.ssf"

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS': return raw[:8] + zlib.decompress(raw[8:])
    return raw

def get_offset(data):
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4): br.read_sb(nb)
    br.align()
    return br.byte_pos + 4

def parse_tags(data, offset):
    tags = []
    while offset < len(data):
        if offset + 2 > len(data): break
        tag_code_and_length = struct.unpack_from('<H', data, offset)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        offset += 2
        if tag_length == 0x3F:
            if offset + 4 > len(data): break
            tag_length = struct.unpack_from('<I', data, offset)[0]
            offset += 4
        tag_data = data[offset:offset + tag_length]
        tags.append((tag_type, tag_data))
        offset += tag_length
        if tag_type == 0: break
    return tags

def get_char_id(tag_type, tag_data):
    """Get character ID from a definition tag."""
    # All definition tags start with UI16 characterId
    DEF_TAGS = {2, 22, 32, 46, 36, 37, 20, 21, 6, 14, 10, 48, 75, 39, 83, 73, 74, 84, 88, 11, 33, 34, 35}
    if tag_type in DEF_TAGS and len(tag_data) >= 2:
        return struct.unpack_from('<H', tag_data, 0)[0]
    return None

def get_po_refs(tag_type, tag_data):
    """Get character IDs referenced by PlaceObject2/3."""
    refs = []
    if tag_type == 26:  # PO2
        flags = tag_data[0]
        if flags & 0x02:
            refs.append(struct.unpack_from('<H', tag_data, 3)[0])
    elif tag_type == 70:  # PO3
        flags = struct.unpack_from('<H', tag_data, 0)[0]
        off = 4
        if flags & 0x800:
            end = tag_data.index(0, off)
            off = end + 1
        if flags & 0x02:
            refs.append(struct.unpack_from('<H', tag_data, off)[0])
    return refs

def check_forward_refs(label, path):
    with open(path, 'rb') as f:
        raw = f.read()
    data = decompress_swf(raw)
    offset = get_offset(data)
    tags = parse_tags(data, offset)
    
    print(f"\n{'='*60}")
    print(f"  {label}: Forward Reference Check")
    print(f"{'='*60}")
    
    # Track defined character IDs in order
    defined = set()
    forward_refs = []  # (referencing_context, referenced_cid)
    undefined_refs = []
    
    # Process top-level tags
    for tag_idx, (tt, td) in enumerate(tags):
        # Check if this is a definition tag
        cid = get_char_id(tt, td)
        if cid is not None:
            defined.add(cid)
        
        # Check if this is a PlaceObject that references a character
        if tt in (26, 70):
            refs = get_po_refs(tt, td)
            for ref_cid in refs:
                if ref_cid not in defined:
                    forward_refs.append((f"root tag#{tag_idx} (tag{tt})", ref_cid))
        
        # Check sprites for internal forward refs
        if tt == 39 and len(td) >= 4:
            sprite_cid = struct.unpack_from('<H', td, 0)[0]
            inner = parse_tags(td, 4)
            for inner_idx, (itt, itd) in enumerate(inner):
                if itt in (26, 70):
                    refs = get_po_refs(itt, itd)
                    for ref_cid in refs:
                        if ref_cid not in defined:
                            forward_refs.append((f"sprite#{sprite_cid} inner#{inner_idx} (tag{itt})", ref_cid))
    
    if forward_refs:
        print(f"  FORWARD REFERENCES FOUND: {len(forward_refs)}")
        # Group by referenced cid
        by_cid = {}
        for ctx, cid in forward_refs:
            by_cid.setdefault(cid, []).append(ctx)
        for cid in sorted(by_cid.keys()):
            in_defined = "EVENTUALLY DEFINED" if cid in defined else "NEVER DEFINED"
            print(f"    cid {cid} ({in_defined}): referenced by {len(by_cid[cid])} PlaceObject(s)")
            for ctx in by_cid[cid][:5]:
                print(f"      - {ctx}")
            if len(by_cid[cid]) > 5:
                print(f"      ... and {len(by_cid[cid]) - 5} more")
    else:
        print(f"  No forward references found ✓")
    
    # Also check: all referenced cids eventually defined?
    all_refs = set()
    for tt, td in tags:
        if tt in (26, 70):
            all_refs.update(get_po_refs(tt, td))
        if tt == 39 and len(td) >= 4:
            inner = parse_tags(td, 4)
            for itt, itd in inner:
                if itt in (26, 70):
                    all_refs.update(get_po_refs(itt, itd))
    
    never_defined = all_refs - defined
    if never_defined:
        print(f"\n  NEVER-DEFINED character IDs referenced: {sorted(never_defined)}")
    else:
        print(f"  All referenced character IDs are defined ✓")

check_forward_refs("OG", OG)
check_forward_refs("RT", RT)
