"""Check start edge fill convention for all morphs in lloyd_rt.swf."""
import struct, zlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_binary_io import BitReader

def check_morph_start_edges(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('B', f.read(1))[0]
        flen = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos = rect_bytes + 4
    
    fill0_count = 0
    fill1_count = 0
    both_count = 0
    total = 0
    edge_counts = []
    
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]
        pos += 2
        tt = tc >> 6
        ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]
            pos += 4
        if tt in (46, 84):
            body = rest[pos:pos+ll]
            cid = struct.unpack_from('<H', body, 0)[0]
            br = BitReader(body, 2)
            # Skip bounds
            for _ in range(2):
                nb = br.read_ub(5)
                for __ in range(4): br.read_sb(nb)
                br.align()
            if tt == 84:
                for _ in range(2):
                    nb = br.read_ub(5)
                    for __ in range(4): br.read_sb(nb)
                    br.align()
                br.read_ui8()
            br.align()
            # Skip offset
            br.byte_pos += 4
            
            # Skip fill style array
            fc = br.read_ui8()
            if fc == 0xFF: fc = br.read_ui16()
            for _ in range(fc):
                ft = br.read_ui8()
                if ft == 0x00: br.byte_pos += 8
                elif ft in (0x10, 0x12, 0x13):
                    # Skip 2 matrices + gradient
                    for __ in range(2):
                        hs = br.read_ub(1)
                        if hs: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        hr = br.read_ub(1)
                        if hr: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
                    ng = br.read_ui8()
                    br.byte_pos += ng * 10
                elif ft in (0x40, 0x41, 0x42, 0x43):
                    br.byte_pos += 2
                    for __ in range(2):
                        hs = br.read_ub(1)
                        if hs: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        hr = br.read_ub(1)
                        if hr: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                        nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
            
            # Skip line style array  
            lc = br.read_ui8()
            if lc == 0xFF: lc = br.read_ui16()
            if tt == 46:
                br.byte_pos += lc * 12
            else:
                for _ in range(lc):
                    br.byte_pos += 4  # 2 widths
                    flags2 = struct.unpack_from('<H', br.data, br.byte_pos)[0]
                    br.byte_pos += 2
                    join = (flags2 >> 2) & 3
                    has_fill = (flags2 >> 4) & 1
                    if join == 2: br.byte_pos += 2
                    if has_fill:
                        sfc = br.read_ui8()
                        if sfc == 0xFF: sfc = br.read_ui16()
                        for __ in range(sfc):
                            sft = br.read_ui8()
                            if sft == 0x00: br.byte_pos += 8
                            elif sft in (0x10,0x12,0x13):
                                for ___ in range(2):
                                    hs = br.read_ub(1)
                                    if hs: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                                    hr = br.read_ub(1)
                                    if hr: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                                    nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
                                ng = br.read_ui8()
                                br.byte_pos += ng * 10
                            elif sft in (0x40,0x41,0x42,0x43):
                                br.byte_pos += 2
                                for ___ in range(2):
                                    hs = br.read_ub(1)
                                    if hs: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                                    hr = br.read_ub(1)
                                    if hr: nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2)
                                    nb2=br.read_ub(5); br.read_sb(nb2); br.read_sb(nb2); br.align()
                    else:
                        br.byte_pos += 8
            
            # Now at start edges
            sfb = br.read_ub(4)
            slb = br.read_ub(4)
            
            # Read first style change flags
            tf = br.read_ub(1)
            if tf == 0:
                flags = br.read_ub(5)
                has_move = flags & 0x01
                has_f0 = (flags >> 1) & 1
                has_f1 = (flags >> 2) & 1
                has_ln = (flags >> 3) & 1
                
                # Count edges
                if has_move:
                    mb = br.read_ub(5)
                    br.read_sb(mb); br.read_sb(mb)
                
                f0_val = br.read_ub(sfb) if has_f0 else 0
                f1_val = br.read_ub(sfb) if has_f1 else 0
                ln_val = br.read_ub(slb) if has_ln else 0
                
                total += 1
                if has_f0 and not has_f1:
                    fill0_count += 1
                elif has_f1 and not has_f0:
                    fill1_count += 1
                elif has_f0 and has_f1:
                    both_count += 1
                
                # Count edge records
                ec = 0
                try:
                    for _ in range(500):
                        etf = br.read_ub(1)
                        if etf == 0:
                            ef = br.read_ub(5)
                            if ef == 0: break
                            if ef & 0x01:
                                mb = br.read_ub(5); br.read_sb(mb); br.read_sb(mb)
                            if ef & 0x02: br.read_ub(sfb)
                            if ef & 0x04: br.read_ub(sfb)
                            if ef & 0x08: br.read_ub(slb)
                        else:
                            ec += 1
                            st = br.read_ub(1)
                            if st:
                                nb = br.read_ub(4) + 2
                                gf = br.read_ub(1)
                                if gf: br.read_sb(nb); br.read_sb(nb)
                                else:
                                    br.read_ub(1)
                                    br.read_sb(nb)
                            else:
                                nb = br.read_ub(4) + 2
                                br.read_sb(nb); br.read_sb(nb); br.read_sb(nb); br.read_sb(nb)
                    edge_counts.append(ec)
                except:
                    edge_counts.append(-1)
                    
                if total <= 5:
                    print(f"  cid={cid} tag={tt}: fill_bits={sfb} line_bits={slb} f0={has_f0}({f0_val}) f1={has_f1}({f1_val}) ln={has_ln}({ln_val}) edges={ec}")
        
        pos += ll
        if tt == 0: break
    
    print(f"\nSummary: {total} morphs")
    print(f"  fill0 only: {fill0_count}")
    print(f"  fill1 only: {fill1_count}")
    print(f"  both f0+f1: {both_count}")
    print(f"  Edge counts: min={min(edge_counts)} max={max(edge_counts)} avg={sum(edge_counts)/len(edge_counts):.1f}")

print("=== lloyd_rt.swf ===")
check_morph_start_edges("test_swfs/lloyd_rt.swf")
