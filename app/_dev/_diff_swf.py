"""Find exact byte-level differences between original SSF and roundtrip SWF."""
import struct

def parse_tags(path):
    raw = open(path, 'rb').read()
    data = raw  # FWS - no decompression
    nbits = (data[8] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    rect_end = 8 + (total_bits + 7) // 8
    tag_start = rect_end + 4
    tags = []
    i = tag_start
    while i < len(data):
        if i + 2 > len(data): break
        h = struct.unpack_from('<H', data, i)[0]
        tt = h >> 6
        ln = h & 0x3f
        hdr = 2
        if ln == 0x3f:
            ln = struct.unpack_from('<I', data, i+2)[0]
            hdr = 6
        body = data[i+hdr:i+hdr+ln]
        tags.append((tt, hdr, ln, body))
        i += hdr + ln
        if tt == 0: break
    return tags, data

TAG_NAMES = {0:'End',1:'ShowFrame',2:'DefineShape',9:'SetBgColor',
    14:'DefineSound',20:'DefineBitsLossless',21:'DefineBitsJPEG2',
    22:'DefineShape2',24:'Protect',26:'PlaceObject2',28:'RemoveObject2',
    32:'DefineShape3',35:'DefineBitsJPEG3',36:'DefineBitsLossless2',
    39:'DefineSprite',43:'FrameLabel',45:'SoundStreamHead2',46:'MorphShape',
    48:'DefineFont2',69:'FileAttributes',70:'PlaceObject3',72:'DoABC',
    73:'FontAlignZones',74:'CSMTextSettings',75:'DefineFont3',
    76:'SymbolClass',82:'DoABC2',83:'DefineShape4',84:'MorphShape2',
    86:'SceneFrameLabel',87:'DefineBinaryData',88:'DefineFontName'}

orig_tags, orig_data = parse_tags(r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.ssf')
rt_tags, rt_data = parse_tags('_roundtrip_test.swf')

print(f"Original: {len(orig_tags)} tags, {len(orig_data)} bytes")
print(f"Roundtrip: {len(rt_tags)} tags, {len(rt_data)} bytes")

# Compare tags side by side until we find differences
i_orig = 0
i_rt = 0
diffs = 0
while i_orig < len(orig_tags) and i_rt < len(rt_tags):
    ott, ohdr, oln, obody = orig_tags[i_orig]
    rtt, rhdr, rln, rbody = rt_tags[i_rt]
    
    oname = TAG_NAMES.get(ott, f'tag{ott}')
    rname = TAG_NAMES.get(rtt, f'tag{rtt}')
    
    if ott == rtt and obody == rbody:
        i_orig += 1
        i_rt += 1
        continue
    
    # Different!
    if ott != rtt:
        print(f"\nTag type mismatch at orig[{i_orig}] vs rt[{i_rt}]:")
        print(f"  Orig: {oname}(type={ott}) len={oln}")
        print(f"  RT:   {rname}(type={rtt}) len={rln}")
        # Check if one has an extra tag
        # Look ahead to find where they sync up again
        found_extra_rt = False
        found_extra_orig = False
        for lookahead in range(1, 5):
            if i_rt + lookahead < len(rt_tags):
                nrtt = rt_tags[i_rt + lookahead][0]
                if nrtt == ott:
                    print(f"  → Roundtrip has {lookahead} EXTRA tag(s) before sync:")
                    for x in range(lookahead):
                        xtt, _, xln, xbody = rt_tags[i_rt + x]
                        xname = TAG_NAMES.get(xtt, f'tag{xtt}')
                        cid_str = ""
                        if len(xbody) >= 2:
                            cid_str = f" charId={struct.unpack_from('<H', xbody, 0)[0]}"
                        print(f"    {xname}(type={xtt}){cid_str} len={xln}")
                    i_rt += lookahead
                    found_extra_rt = True
                    break
            if i_orig + lookahead < len(orig_tags):
                nott = orig_tags[i_orig + lookahead][0]
                if nott == rtt:
                    print(f"  → Original has {lookahead} EXTRA tag(s) before sync:")
                    for x in range(lookahead):
                        xtt, _, xln, xbody = orig_tags[i_orig + x]
                        xname = TAG_NAMES.get(xtt, f'tag{xtt}')
                        cid_str = ""
                        if len(xbody) >= 2:
                            cid_str = f" charId={struct.unpack_from('<H', xbody, 0)[0]}"
                        print(f"    {xname}(type={xtt}){cid_str} len={xln}")
                    i_orig += lookahead
                    found_extra_orig = True
                    break
        if not found_extra_rt and not found_extra_orig:
            i_orig += 1
            i_rt += 1
        diffs += 1
    else:
        # Same type, different body
        ocid = struct.unpack_from('<H', obody, 0)[0] if len(obody) >= 2 else -1
        rcid = struct.unpack_from('<H', rbody, 0)[0] if len(rbody) >= 2 else -1
        print(f"\nBody mismatch at [{i_orig}]: {oname}(type={ott}) charId orig={ocid} rt={rcid}")
        print(f"  Orig len={oln}, RT len={rln}, delta={rln-oln}")
        # Find first differing byte
        for b in range(min(len(obody), len(rbody))):
            if obody[b] != rbody[b]:
                print(f"  First diff at byte {b}: orig=0x{obody[b]:02x} rt=0x{rbody[b]:02x}")
                print(f"  Orig [{b}:{b+20}]: {obody[b:b+20].hex()}")
                print(f"  RT   [{b}:{b+20}]: {rbody[b:b+20].hex()}")
                break
        i_orig += 1
        i_rt += 1
        diffs += 1
    
    if diffs > 20:
        print("\n... (truncated after 20 diffs)")
        break

print(f"\nTotal differences found: {diffs}")

# Show remaining tags if one is longer
if i_orig < len(orig_tags):
    print(f"\nOriginal has {len(orig_tags) - i_orig} remaining tags")
if i_rt < len(rt_tags):
    print(f"\nRoundtrip has {len(rt_tags) - i_rt} remaining tags")
    for i in range(i_rt, min(i_rt + 5, len(rt_tags))):
        tt, _, ln, body = rt_tags[i]
        name = TAG_NAMES.get(tt, f'tag{tt}')
        cid_str = ""
        if len(body) >= 2:
            cid_str = f" charId={struct.unpack_from('<H', body, 0)[0]}"
        print(f"  {name}(type={tt}){cid_str} len={ln}")
