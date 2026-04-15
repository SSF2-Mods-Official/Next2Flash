"""Detailed binary inspection of morph shape start+end edges in lloyd_rt.swf."""
import struct, zlib, os
from swf_binary_io import BitReader

def inspect_morphs(path, max_show=5):
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
    shown = 0
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]
        pos += 2
        tt = tc >> 6
        ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]
            pos += 4
        if tt in (46, 84) and shown < max_show:
            body = rest[pos:pos+ll]
            cid = struct.unpack_from('<H', body, 0)[0]
            br2 = BitReader(body, 2)
            # Skip start+end bounds
            for _ in range(2):
                nb2 = br2.read_ub(5)
                for __ in range(4): br2.read_sb(nb2)
                br2.align()
            if tt == 84:
                for _ in range(2):
                    nb2 = br2.read_ub(5)
                    for __ in range(4): br2.read_sb(nb2)
                    br2.align()
                br2.read_ui8()
            br2.align()
            offset = struct.unpack_from('<I', br2.data, br2.byte_pos)[0]
            br2.byte_pos += 4
            after_offset = br2.byte_pos

            # Read start edges header (NumFillBits/NumLineBits)
            # First skip fill/line style arrays to get to start edges
            # The offset measures from after Offset to EndEdges
            end_pos = after_offset + offset

            # Start edges are just before end_pos
            # We need to find them - they're after fill+line style arrays
            # For now, just check the end edges
            br_end = BitReader(body, end_pos)
            efb = br_end.read_ub(4)
            elb = br_end.read_ub(4)

            # Read first few records in end state to check geometry
            end_records = []
            for _ in range(5):
                flag = br_end.read_ub(1)  # type flag
                if flag == 0:  # non-edge
                    flags = br_end.read_ub(5)
                    if flags == 0:
                        end_records.append("EndShape")
                        break
                    rec = "StyleChange("
                    if flags & 0x01:  # MoveTo
                        mb = br_end.read_ub(5)
                        mx = br_end.read_sb(mb)
                        my = br_end.read_sb(mb)
                        rec += f"move={mx},{my} "
                    if flags & 0x02: rec += "fill0! "
                    if flags & 0x04: rec += "fill1! "
                    if flags & 0x08: rec += "line! "
                    if flags & 0x10: rec += "newStyles! "
                    end_records.append(rec.strip() + ")")
                else:  # edge
                    straight = br_end.read_ub(1)
                    if straight:
                        nb = br_end.read_ub(4) + 2
                        gf = br_end.read_ub(1)
                        if gf == 1:
                            dx = br_end.read_sb(nb)
                            dy = br_end.read_sb(nb)
                            end_records.append(f"StraightEdge({dx},{dy})")
                        else:
                            vl = br_end.read_ub(1)
                            if vl:
                                dy = br_end.read_sb(nb)
                                end_records.append(f"VLine({dy})")
                            else:
                                dx = br_end.read_sb(nb)
                                end_records.append(f"HLine({dx})")
                    else:
                        nb = br_end.read_ub(4) + 2
                        cx = br_end.read_sb(nb)
                        cy = br_end.read_sb(nb)
                        ax = br_end.read_sb(nb)
                        ay = br_end.read_sb(nb)
                        end_records.append(f"CurvedEdge(c={cx},{cy} a={ax},{ay})")

            print(f"tag={tt} charId={cid} len={ll}: end fill_bits={efb} line_bits={elb}")
            for r in end_records:
                print(f"    {r}")
            shown += 1
        pos += ll
        if tt == 0: break

lloyd_rt = "test_swfs/lloyd_rt.swf"
print("=== lloyd_rt.swf first 5 morphs ===")
inspect_morphs(lloyd_rt)
