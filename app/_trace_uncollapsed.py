"""Trace sub_paths for morphs that didn't collapse in lloyd."""
import os, sys, zipfile, msgpack
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shape_converter import parse_next2d_shape_buffer, _morph_collapse_fill_merge

n2d_path = os.path.join(os.path.dirname(__file__), "test_swfs", "lloyd.n2d")
with zipfile.ZipFile(n2d_path) as z:
    with z.open("project.msgpack") as f:
        proj = msgpack.unpack(f, raw=False)

libs = proj.get("libraries", [])
morphs = [it for it in libs if it.get("type") == "shape" and "endRecodes" in it]

for m in morphs:
    name = m.get("name", "???")
    swf_cid = m.get("swfCharId", m.get("characterId", -1))
    recodes = m.get("recodes", [])
    end_recodes = m.get("endRecodes", [])
    
    start_result = parse_next2d_shape_buffer(recodes)
    end_result = parse_next2d_shape_buffer(end_recodes)
    start_paths = start_result[2]
    end_paths = end_result[2]
    
    # Try collapse
    collapsed_start, did_collapse = _morph_collapse_fill_merge(start_paths)
    
    total_start_edges = sum(len(sp.edges) for sp in start_paths)
    total_end_edges = sum(len(sp.edges) for sp in end_paths)
    
    if True:  # show all morphs
        print(f"\n{'='*60}")
        print(f"Morph: {name} (swfCharId={swf_cid})")
        print(f"  Recodes length: {len(recodes)}, EndRecodes length: {len(end_recodes)}")
        print(f"  Start sub_paths: {len(start_paths)}, End sub_paths: {len(end_paths)}")
        print(f"  Collapsed: {did_collapse} → {len(collapsed_start)} paths")
        for i, sp in enumerate(start_paths):
            edge_types = [type(e).__name__ for e in sp.edges[:5]]
            print(f"  StartPath[{i}]: fill={sp.fill_style_idx} line={sp.line_style_idx} edges={len(sp.edges)} start=({sp.start_x:.1f},{sp.start_y:.1f}) types={edge_types}...")
        for i, sp in enumerate(end_paths):
            print(f"  EndPath[{i}]: fill={sp.fill_style_idx} line={sp.line_style_idx} edges={len(sp.edges)} start=({sp.start_x:.1f},{sp.start_y:.1f})")
