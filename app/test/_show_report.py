import json, sys
fname = sys.argv[1] if len(sys.argv) > 1 else 'test/roundtrip_menu_xref.json'
d = json.load(open(fname))
for r in d['results']:
    xe = len(r.get('xref_errors', []))
    oxe = len(r.get('orig_xref_errors', []))
    xw = len(r.get('xref_warnings', []))
    print(f"{r['file']:30s}  {r['status']:5s}  xref_err={xe}  orig_xref={oxe}  warns={xw}")
print()
s = d['summary']
print(f"PASS={s['pass']} FAIL={s['fail']} ERROR={s['error']}")
