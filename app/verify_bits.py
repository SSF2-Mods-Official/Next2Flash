"""
verify_bits.py — verify bit reader position at the has_new record
"""
import sys; sys.path.insert(0, '.')
from swf_to_n2d import parse_swf
from swf_shape_to_recodes import _BitReader, _read_fill_style_array, _read_line_style_array

with open(r'C:\Users\glwex\AppData\Local\Temp\MicrosoftEdgeDownloads\b2655a24-55f5-4204-84a5-87bd47832f87\project.swf', 'rb') as f:
    data = f.read()
header, tags = parse_swf(data)

for tag in tags:
    if tag.tag_type != 32: continue
    cid = int.from_bytes(tag.data[:2], 'little')
    if cid != 445: continue
    body = tag.data[2:]
    br = _BitReader(body, 0)
    # Skip RECT
    nbits = br.read_ub(5)
    for _ in range(4): br.read_sb(nbits)
    fill_styles = _read_fill_style_array(br, 32)
    line_styles = _read_line_style_array(br, 32)
    nb = br.read_ui8()
    fill_bits = nb >> 4; line_bits = nb & 0x0F
    print(f'Initial: {len(fill_styles)} fills, {len(line_styles)} lines, fbits={fill_bits} lbits={line_bits}')
    print(f'After initial: byte_pos={br.byte_pos} bit_pos={br.bit_pos}')

    records = 0
    while br.remaining > 0 and records < 100:
        saved_bp = br.byte_pos; saved_btp = br.bit_pos
        tf = br.read_ub(1)
        if tf == 1:
            s = br.read_ub(1); nbits_e = br.read_ub(4)+2
            if s:
                g = br.read_ub(1)
                if g:
                    br.read_sb(nbits_e); br.read_sb(nbits_e)
                else:
                    v = br.read_ub(1)
                    if not v: br.read_sb(nbits_e)
                    br.read_sb(nbits_e)
            else:
                for _ in range(4): br.read_sb(nbits_e)
        else:
            flags = br.read_ub(5)
            if flags == 0:
                print(f'END at byte_pos={br.byte_pos}')
                break
            hn=(flags>>4)&1; hl=(flags>>3)&1; hf1=(flags>>2)&1; hf0=(flags>>1)&1; hm=flags&1
            print(f'  [rec {records}] byte={saved_bp} bit={saved_btp} raw_byte={body[saved_bp]:08b}  flags={flags:#07b}  hn={hn} hl={hl} hf1={hf1} hf0={hf0} hm={hm}')
            if hm:
                mb = br.read_ub(5)
                cx = br.read_sb(mb)
                cy = br.read_sb(mb)
                print(f'    MOVE: mb={mb} x={cx} y={cy} = ({cx/20:.2f},{cy/20:.2f})')
            if hf0: br.read_ub(fill_bits)
            if hf1: br.read_ub(fill_bits)
            if hl: br.read_ub(line_bits)
            if hn:
                print(f'    NEW STYLES at byte_pos={br.byte_pos}')
                fill_styles = _read_fill_style_array(br, 32)
                line_styles = _read_line_style_array(br, 32)
                nb = br.read_ui8(); fill_bits = nb>>4; line_bits = nb&0x0F
                print(f'    -> {len(fill_styles)} fills, {len(line_styles)} lines, fbits={fill_bits} lbits={line_bits}')
            records += 1
    break
