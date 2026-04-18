"""Search ABC for bm_dairHand constructor to find super() call dimensions."""
import struct, zlib

def read_swf_tags(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    if sig == b'CWS':
        body = zlib.decompress(data[8:])
        data = data[:8] + body
    off = 8
    nbits = (data[off] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    off += (total_bits + 7) // 8
    off += 4
    tags = []
    while off < len(data):
        if off + 2 > len(data): break
        tw = struct.unpack_from('<H', data, off)[0]
        tag_type = tw >> 6
        tag_len = tw & 0x3f
        off += 2
        if tag_len == 63:
            tag_len = struct.unpack_from('<i', data, off)[0]
            off += 4
        tags.append((tag_type, off, tag_len))
        off += tag_len
    return tags, data

def read_u30(data, off):
    result = 0
    shift = 0
    while True:
        b = data[off]
        off += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, off

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)

for (t, o, l) in og_tags:
    if t == 82:
        abc_data = og_data[o:o+l]
        break

# Skip flags + null-term name
abc_off = 4
while abc_off < len(abc_data) and abc_data[abc_off] != 0:
    abc_off += 1
abc_off += 1
abc_body = abc_data[abc_off:]

# Search for "bm_dairHand" string 
bm_pos = abc_body.find(b'bm_dairHand')
print(f'bm_dairHand at abc_body offset {bm_pos}')
print(f'Context (50 bytes before + 50 after): ...{abc_body[bm_pos-10:bm_pos+20].hex()}...')

# The bm_dairHand class will have its methods in the ABC method bodies.
# Let's find all occurrences of pushbyte(5) = 0x24 0x05 in the file
hits_24_05 = [i for i in range(len(abc_body)-1) if abc_body[i] == 0x24 and abc_body[i+1] == 5]
print(f'\npushbyte(5) occurrences: {len(hits_24_05)}')
for pos in hits_24_05[:20]:
    print(f'  offset {pos}: {abc_body[pos:pos+10].hex()}')

# Search for constructsuper opcode (0x49) preceded by pushbyte(5) pushbyte(5)
# The constructor should: pushbyte 5, pushbyte 5, [optional pushfalse/pushtrue/pushuint], constructsuper
# constructsuper = 0x49, arg_count follows
# Look for 0x24 0x05 ... 0x49 nearby
print('\n=== Patterns: pushbyte(5) near constructsuper ===')
for pos in hits_24_05:
    # Look within next 20 bytes for constructsuper (0x49)
    region = abc_body[pos:pos+30]
    if 0x49 in region:
        cs_off = region.index(0x49)
        print(f'  pos={pos}: {abc_body[pos:pos+20].hex()}')
        print(f'    constructsuper at +{cs_off}')

# Also find: look in raw ABC body for the bm_dairHand constructor
# The method body for bm_dairHand constructor should be near the class def
# Let's scan for 0x24 0x05 0x24 0x05 with any bytes in between followed by 0x49
import re
pattern = rb'\x24\x05.{0,10}\x24\x05.{0,20}\x49'
matches = [(m.start(), m.group()) for m in re.finditer(pattern, abc_body, re.DOTALL)]
print(f'\nRegex matches of pushbyte(5)...pushbyte(5)...constructsuper: {len(matches)}')
for pos, match in matches[:10]:
    print(f'  offset {pos}: {abc_body[pos:pos+30].hex()}')

# Also: getproperty and callproperty opcodes
# Look for the string "bm_dairHand" in the context to find where the class is defined
# In ABC, class names are in the multiname table, referenced by index
# Let's just look at the raw bytes around "bm_dairHand" string in the constant pool
# and then search for that multiname index in method bodies

# Simpler: search for any occurrence of 0x05 as an integer literal
# In ABC, getlocal_0, pushscope, [width push], [height push], ... constructsuper
# getlocal_0 = 0xD0, pushscope = 0x30

# Look for getlocal_0 (0xD0) pushscope (0x30) pattern 
# which typically starts instance init (constructor body)
ctor_starts = [i for i in range(len(abc_body)-1) if abc_body[i] == 0xD0 and abc_body[i+1] == 0x30]
print(f'\ngetlocal_0+pushscope patterns: {len(ctor_starts)}')

# For each constructor-like function, check if it has pushbyte 5 pushbyte 5
for pos in ctor_starts:
    # Get next 50 bytes and look for pushbyte 5 five positions
    region = abc_body[pos:pos+100]
    # Count pushbyte 5 occurrences
    pb5_count = 0
    for i in range(len(region)-1):
        if region[i] == 0x24 and region[i+1] == 5:
            pb5_count += 1
    if pb5_count >= 2:
        print(f'  Constructor at {pos} has {pb5_count} pushbyte(5): {abc_body[pos:pos+50].hex()}')

# Look for opcodes around the bm_dairHand iinit directly
# Try scanning from the position of bm_dairHand string backwards to find the class definition
# In the class trait, the class name multiname index points to bm_dairHand
# The method body index for iinit should be nearby

print('\n=== Raw bytes scan near bm_dairHand string ===')
# The string "bm_dairHand" is at abc_body[bm_pos:bm_pos+11]
# In the constant pool, strings have length prefix (u30)
# Let's look at ABC class defs

# Actually, let's try a different approach: find "iinit" method bodies
# by looking for the constructor pattern for a BitmapData subclass
# In AS3, BitmapData constructor is: BitmapData(width, height, transparent=true, fillColor=0xFFFFFFFF)
# So the bm_dairHand iinit should call super(5, 5) which pushes 5 twice

# Search for pushshort (0x25) in case width/height use pushshort instead of pushbyte
hits_25 = [i for i in range(len(abc_body)-2) if abc_body[i] == 0x25]
print(f'pushshort occurrences: {len(hits_25)}')
for pos in hits_25[:10]:
    val = struct.unpack_from('<h', abc_body, pos+1)[0]
    print(f'  offset {pos}: pushshort({val}) = {abc_body[pos:pos+6].hex()}')

# Also look for pushint (0x2D)
hits_2D = [i for i in range(len(abc_body)-1) if abc_body[i] == 0x2D]
print(f'pushint occurrences: {len(hits_2D)}')
# Check which ones push the value 5
for pos in hits_2D[:5]:
    print(f'  offset {pos}: {abc_body[pos:pos+6].hex()}')
