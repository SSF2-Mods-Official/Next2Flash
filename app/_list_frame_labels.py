"""List all frame labels in all sprites of the OG fox SWF.

Looking for "done1", "done2", "redo", "continue" etc.
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import parse_swf

OG_SWF = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

TAG_DEFINESPRITE = 39
TAG_SYMBOLCLASS = 76
TAG_FRAMELABEL = 43
TAG_SHOWFRAME = 1
TAG_END = 0


def get_swf_tags(swf_path):
    with open(swf_path, 'rb') as f:
        swf_data = f.read()
    header, tags_raw = parse_swf(swf_data)
    return [(t.tag_type, t.data) for t in tags_raw]


def get_symbol_class(tags):
    result = {}
    for tt, td in tags:
        if tt == TAG_SYMBOLCLASS and len(td) >= 2:
            num = struct.unpack_from('<H', td, 0)[0]
            pos = 2
            for _ in range(num):
                cid = struct.unpack_from('<H', td, pos)[0]; pos += 2
                end = td.index(0, pos)
                name = td[pos:end].decode('utf-8', errors='replace')
                pos = end + 1
                result[cid] = name
    return result


def get_sprite_labels(tags, sym_map):
    """Get frame labels for all sprites."""
    results = {}
    for tt, td in tags:
        if tt == TAG_DEFINESPRITE and len(td) >= 4:
            cid = struct.unpack_from('<H', td, 0)[0]
            fc = struct.unpack_from('<H', td, 2)[0]
            class_name = sym_map.get(cid, f"unnamed_{cid}")
            
            labels = []
            frame = 0
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
                
                if inner_type == TAG_FRAMELABEL and inner_data:
                    label = inner_data[:inner_data.index(0)].decode('utf-8', errors='replace')
                    labels.append((frame + 1, label))
                elif inner_type == TAG_SHOWFRAME:
                    frame += 1
                elif inner_type == TAG_END:
                    break
            
            if labels:
                results[cid] = (class_name, fc, labels)
    
    return results


def main():
    print("Loading OG SWF...")
    tags = get_swf_tags(OG_SWF)
    sym = get_symbol_class(tags)
    
    sprite_labels = get_sprite_labels(tags, sym)
    
    # Search for specific labels
    targets = ["done", "done1", "done2", "redo", "continue", "dead", "run", "loop", "finish"]
    
    print(f"\nSearching for labels: {targets}")
    print(f"{'='*70}")
    
    for cid, (class_name, fc, labels) in sorted(sprite_labels.items(), key=lambda x: x[1][0]):
        matching = [(f, l) for f, l in labels if any(t in l.lower() for t in targets)]
        if matching:
            print(f"\n  {class_name} (cid={cid}, {fc} frames):")
            for f, l in labels:
                marker = " <--" if any(t in l.lower() for t in targets) else ""
                print(f"    Frame {f}: '{l}'{marker}")
    
    # Also show all unique labels across all sprites
    all_labels = set()
    for cid, (class_name, fc, labels) in sprite_labels.items():
        for f, l in labels:
            all_labels.add(l)
    
    print(f"\n{'='*70}")
    print(f"All unique frame labels ({len(all_labels)}):")
    for l in sorted(all_labels):
        print(f"  '{l}'")


if __name__ == '__main__':
    main()
