import swf_to_n2d, math

path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\captainfalcon.swf'
with open(path, 'rb') as f:
    data = f.read()
header, tags = swf_to_n2d.parse_swf(data)

sprite_names = {}
for t in tags:
    if t.tag_type == 76:
        sprite_names.update(swf_to_n2d.parse_symbol_class(t.data))

results = []
for t in tags:
    if t.tag_type in (26, 70):
        try:
            pl = swf_to_n2d.parse_place_object2(t.data) if t.tag_type == 26 else swf_to_n2d.parse_place_object3(t.data)
            m = pl.get('matrix')
            if m:
                sx = math.sqrt(m[0]**2 + m[2]**2)
                sy = math.sqrt(m[1]**2 + m[3]**2)
                if sx > 5 or sy > 5:
                    cid = pl.get('charId')
                    name = sprite_names.get(cid, str(cid))
                    results.append((sx, sy, pl['depth'], cid, name, m))
        except Exception as e:
            pass

results.sort(key=lambda x: -max(x[0], x[1]))
for sx, sy, depth, cid, name, m in results[:20]:
    print('scaleX=%.1f scaleY=%.1f depth=%d cid=%s name=%s' % (sx, sy, depth, cid, name))
print('Total oversized placements:', len(results))
