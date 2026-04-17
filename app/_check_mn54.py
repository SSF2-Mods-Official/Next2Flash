"""Inspect the multiname mn[54] and mn[1070] used by existing SSF2API.print calls."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from as3_decompiler.abc_parser import ABCFile
from as3_decompiler.swf_patcher import read_swf_full, _extract_abc_data_from_tag, TAG_DOABC, TAG_DOABC2

RT_SWF = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"

swf_info = read_swf_full(RT_SWF)
for tag_type, body in swf_info['tags']:
    if tag_type in (TAG_DOABC, TAG_DOABC2):
        _, abc_data = _extract_abc_data_from_tag(tag_type, body)
        abc = ABCFile(abc_data)
        
        # Check mn[54] - used by existing getlex SSF2API
        print("=== mn[54] (SSF2API getlex) ===")
        kind, data = abc.multinames[54]
        print(f"  kind={kind}, data={data}")
        print(f"  full: {abc.mn_full(54)}")
        print(f"  name: {abc.mn_name(54)}")
        if data:
            ns_idx = data[0]
            ns_kind, ns_name_idx = abc.namespaces[ns_idx]
            ns_name = abc.strings[ns_name_idx] if ns_name_idx > 0 else '""'
            print(f"  namespace[{ns_idx}]: kind={ns_kind:#x} name={ns_name}")
        
        # Check mn[1070] - used by existing callpropvoid print
        print("\n=== mn[1070] (print callpropvoid) ===")
        kind, data = abc.multinames[1070]
        print(f"  kind={kind}, data={data}")
        print(f"  full: {abc.mn_full(1070)}")
        print(f"  name: {abc.mn_name(1070)}")
        if kind == 0x07:  # QName
            ns_idx = data[0]
            ns_kind, ns_name_idx = abc.namespaces[ns_idx]
            ns_name = abc.strings[ns_name_idx] if ns_name_idx > 0 else '""'
            print(f"  namespace[{ns_idx}]: kind={ns_kind:#x} name={ns_name}")
        elif kind == 0x09:  # Multiname
            name_idx, ns_set_idx = data
            print(f"  name_idx={name_idx} -> '{abc.strings[name_idx]}'")
            print(f"  ns_set_idx={ns_set_idx} -> {abc.ns_sets[ns_set_idx]}")
            for nsi in abc.ns_sets[ns_set_idx]:
                nk, nni = abc.namespaces[nsi]
                nn = abc.strings[nni] if nni > 0 else '""'
                print(f"    ns[{nsi}]: kind={nk:#x} name={nn}")
        
        break
