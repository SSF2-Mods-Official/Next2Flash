"""Check if DefineSprite tags appear before their PlaceObject references.

In SWF, a DefineSprite must be defined BEFORE it's referenced by a
PlaceObject inside another sprite. If the order is wrong, Flash Player
may fail to instantiate the character.
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import parse_swf

OG_SWF = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT_SWF = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"

TAG_DEFINESPRITE = 39
TAG_DEFINEBITMAP = {20, 21, 35, 36, 90}  # DefineBitsLossless, JPEG2, etc.
TAG_DEFINESHAPE = {2, 22, 32, 83}  # DefineShape 1-4
TAG_SYMBOLCLASS = 76
TAG_DOABC = 82
TAG_DOABC2 = 72
TAG_PLACEOBJECT2 = 26
TAG_PLACEOBJECT3 = 70
TAG_END = 0

# All define tags
DEFINE_TAGS = {
    1: "ShowFrame",
    2: "DefineShape", 4: "PlaceObject", 9: "SetBackgroundColor",
    20: "DefineBitsLossless", 21: "DefineBitsJPEG2",
    22: "DefineShape2", 26: "PlaceObject2", 28: "RemoveObject2",
    32: "DefineShape3", 35: "DefineBitsJPEG3",
    36: "DefineBitsLossless2", 39: "DefineSprite",
    43: "FrameLabel", 46: "DefineMorphShape",
    69: "FileAttributes", 70: "PlaceObject3",
    72: "DoABC", 76: "SymbolClass", 82: "DoABC2",
    83: "DefineShape4", 84: "DefineMorphShape2",
}


def analyze_tag_order(swf_path, label="SWF"):
    """Check that all character definitions appear before their references."""
    with open(swf_path, 'rb') as f:
        swf_data = f.read()
    header, tags_raw = parse_swf(swf_data)
    tags = [(t.tag_type, t.data) for t in tags_raw]
    
    # First pass: collect definition positions
    defined_at = {}  # cid → tag index
    for i, (tt, td) in enumerate(tags):
        if tt == TAG_DEFINESPRITE and len(td) >= 4:
            cid = struct.unpack_from('<H', td, 0)[0]
            defined_at[cid] = i
        elif tt in TAG_DEFINESHAPE and len(td) >= 2:
            cid = struct.unpack_from('<H', td, 0)[0]
            defined_at[cid] = i
        elif tt in TAG_DEFINEBITMAP and len(td) >= 2:
            cid = struct.unpack_from('<H', td, 0)[0]
            defined_at[cid] = i
        elif tt in (46, 84) and len(td) >= 2:  # DefineMorphShape
            cid = struct.unpack_from('<H', td, 0)[0]
            defined_at[cid] = i
    
    # Get SymbolClass
    sym = {}
    for tt, td in tags:
        if tt == TAG_SYMBOLCLASS and len(td) >= 2:
            num = struct.unpack_from('<H', td, 0)[0]
            pos = 2
            for _ in range(num):
                cid = struct.unpack_from('<H', td, pos)[0]; pos += 2
                end = td.index(0, pos)
                name = td[pos:end].decode('utf-8', errors='replace')
                pos = end + 1
                sym[cid] = name
    
    # Second pass: check references inside DefineSprite tags
    forward_refs = []
    for i, (tt, td) in enumerate(tags):
        if tt == TAG_DEFINESPRITE and len(td) >= 4:
            parent_cid = struct.unpack_from('<H', td, 0)[0]
            parent_name = sym.get(parent_cid, f"sprite_{parent_cid}")
            
            # Parse inner tags for PlaceObject references
            pos = 4
            while pos < len(td):
                if pos + 2 > len(td):
                    break
                tag_code_and_len = struct.unpack_from('<H', td, pos)[0]
                inner_type = tag_code_and_len >> 6
                inner_len = tag_code_and_len & 0x3F
                pos += 2
                if inner_len == 0x3F:
                    if pos + 4 > len(td):
                        break
                    inner_len = struct.unpack_from('<I', td, pos)[0]
                    pos += 4
                inner_data = td[pos:pos+inner_len]
                pos += inner_len
                
                if inner_type in (TAG_PLACEOBJECT2, TAG_PLACEOBJECT3) and inner_data:
                    # Get character ID from PlaceObject
                    ipos = 0
                    if inner_type == TAG_PLACEOBJECT2:
                        flags = inner_data[ipos]; ipos += 1
                        has_character = bool(flags & 0x02)
                        depth = struct.unpack_from('<H', inner_data, ipos)[0]; ipos += 2
                        if has_character:
                            ref_cid = struct.unpack_from('<H', inner_data, ipos)[0]
                            ref_def_pos = defined_at.get(ref_cid)
                            if ref_def_pos is not None and ref_def_pos > i:
                                ref_name = sym.get(ref_cid, f"char_{ref_cid}")
                                forward_refs.append((parent_name, parent_cid, ref_name, ref_cid, i, ref_def_pos))
                    elif inner_type == TAG_PLACEOBJECT3:
                        flags1 = inner_data[ipos]; ipos += 1
                        flags2 = inner_data[ipos]; ipos += 1
                        has_character = bool(flags1 & 0x02)
                        has_class_name = bool(flags2 & 0x08)
                        has_image = bool(flags2 & 0x10)
                        depth = struct.unpack_from('<H', inner_data, ipos)[0]; ipos += 2
                        if has_class_name or (has_image and has_character):
                            end = inner_data.index(0, ipos)
                            ipos = end + 1
                        if has_character:
                            ref_cid = struct.unpack_from('<H', inner_data, ipos)[0]
                            ref_def_pos = defined_at.get(ref_cid)
                            if ref_def_pos is not None and ref_def_pos > i:
                                ref_name = sym.get(ref_cid, f"char_{ref_cid}")
                                forward_refs.append((parent_name, parent_cid, ref_name, ref_cid, i, ref_def_pos))
                
                if inner_type == TAG_END:
                    break
    
    print(f"\n{label}: {swf_path}")
    print(f"  Total definitions: {len(defined_at)}")
    if forward_refs:
        print(f"  FORWARD REFERENCES FOUND: {len(forward_refs)}")
        for parent_name, parent_cid, ref_name, ref_cid, parent_pos, ref_pos in forward_refs[:20]:
            print(f"    {parent_name}(cid={parent_cid}) @ tag#{parent_pos} references {ref_name}(cid={ref_cid}) defined at tag#{ref_pos}")
    else:
        print(f"  No forward references - tag ordering is correct!")
    
    return forward_refs


def main():
    og_refs = analyze_tag_order(OG_SWF, "ORIGINAL")
    rt_refs = analyze_tag_order(RT_SWF, "ROUND-TRIP")
    
    if og_refs and not rt_refs:
        print("\nOG has forward refs but RT doesn't — OG is broken, RT is correct")
    elif not og_refs and rt_refs:
        print("\nRT has FORWARD REFERENCES that OG doesn't — THIS COULD CAUSE ISSUES!")
    elif og_refs and rt_refs:
        print(f"\nBoth have forward refs: OG={len(og_refs)}, RT={len(rt_refs)}")
    else:
        print("\nBoth have correct tag ordering")


if __name__ == '__main__':
    main()
