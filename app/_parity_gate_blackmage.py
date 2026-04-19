"""Parity gate for Black Mage OG vs RT script decompile output.

Fails (exit 1) when:
- missing/extra classes exist, or
- real diff count exceeds threshold.

Usage:
  python _parity_gate_blackmage.py \
    --og <path_to_og_swf> \
    --rt <path_to_rt_swf> \
    [--max-real-diff 0]
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict

from swf_to_n2d import parse_swf, N2DBuilder, decompile_all_scripts


def scripts_from_swf(swf_path: str) -> Dict[str, str]:
    with open(swf_path, "rb") as f:
        data = f.read()
    header, tags = parse_swf(data)
    builder = N2DBuilder(header, name="parity")
    builder.catalog_swf_tags(tags)
    scripts, _frame_scripts = decompile_all_scripts(builder.global_raw_tags)
    return {s.get("path", ""): s.get("source", "") for s in scripts if s.get("path")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--og", required=True, help="Path to OG SWF")
    ap.add_argument("--rt", required=True, help="Path to RT SWF")
    ap.add_argument("--max-real-diff", type=int, default=0, help="Allowed real non-whitespace diff count")
    args = ap.parse_args()

    og = scripts_from_swf(args.og)
    rt = scripts_from_swf(args.rt)

    only_og = sorted([p for p in og if p not in rt])
    only_rt = sorted([p for p in rt if p not in og])
    shared = sorted([p for p in og if p in rt])

    identical = 0
    ws_only = 0
    real = 0
    for p in shared:
        a = og[p]
        b = rt[p]
        if a == b:
            identical += 1
        elif "".join(a.split()) == "".join(b.split()):
            ws_only += 1
        else:
            real += 1

    print(f"PARITY_GATE_OG={len(og)}")
    print(f"PARITY_GATE_RT={len(rt)}")
    print(f"PARITY_GATE_ONLY_OG={len(only_og)}")
    print(f"PARITY_GATE_ONLY_RT={len(only_rt)}")
    print(f"PARITY_GATE_IDENTICAL={identical}")
    print(f"PARITY_GATE_WS_ONLY={ws_only}")
    print(f"PARITY_GATE_REAL_DIFF={real}")
    if only_og:
        print("PARITY_GATE_ONLY_OG_SAMPLE=" + ";".join(only_og[:20]))
    if only_rt:
        print("PARITY_GATE_ONLY_RT_SAMPLE=" + ";".join(only_rt[:20]))

    failed = False
    if only_og or only_rt:
        failed = True
    if real > args.max_real_diff:
        failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
