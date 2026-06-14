#!/usr/bin/env python3
"""
Audit decompiler fidelity against SSF2 IDK source-of-truth classes.

Three-way comparison:
  - IDK .as reference (source of truth for intended game code)
  - SWF ABC method/getter/setter traits (what is actually in the binary)
  - Decompiler output (what Next2Flash emits)

A method listed only under IDK is not a decompiler bug — it is absent from
this SWF build.  Methods in ABC but missing from decompile are real gaps.

Usage:
  py -3 tests/idk_decompile_audit.py --swf path/to/SSF2.swf --idk-root path/to/com \\
      --class com.mcleodgaming.ssf2.Main --class com.mcleodgaming.ssf2.util.Utils

  py -3 tests/idk_decompile_audit.py --swf ... --idk-root ... --discover --limit 30
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

SCRIPT_DIR = Path(__file__).resolve().parent
APP_DIR = SCRIPT_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

_LINE_COMMENT = re.compile(r"//[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_IMPORT_LINE = re.compile(r"^\s*import\s+([\w\.\*]+)\s*;", re.MULTILINE)
_FN_NAME = re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\(")
_GETTER = re.compile(r"\bfunction\s+get\s+([A-Za-z_]\w*)\s*\(")
_SETTER = re.compile(r"\bfunction\s+set\s+([A-Za-z_]\w*)\s*\(")
_WS = re.compile(r"\s+")

# Import after path setup when used as script
def _import_abc():
    from as3_decompiler.swf_reader import read_abc_blocks
    from as3_decompiler.abc_parser import ABCFile
    from as3_decompiler.abc_parser import (
        TRAIT_Method,
        TRAIT_Getter,
        TRAIT_Setter,
        TRAIT_Function,
    )
    return read_abc_blocks, ABCFile, TRAIT_Method, TRAIT_Getter, TRAIT_Setter, TRAIT_Function


def _normalize(src: str) -> str:
    src = _BLOCK_COMMENT.sub(" ", src)
    src = _LINE_COMMENT.sub(" ", src)
    imports = sorted(set(_IMPORT_LINE.findall(src)))
    src = _IMPORT_LINE.sub("", src)
    src = _WS.sub(" ", src).strip()
    return "IMPORTS[" + ",".join(imports) + "] " + src


def _similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def decompile_class_from_swf(swf_path: Path, class_name: str) -> str:
    """Decompile one class using per-block ABC (PSB SWF has 470 DoABC tags)."""
    read_abc_blocks, ABCFile, *_ = _import_abc()
    from as3_decompiler.class_decompiler import AS3Decompiler
    from as3_decompiler.postprocess import finalize_decompiled_source

    _, blocks = read_abc_blocks(str(swf_path))
    for _block_name, data in blocks:
        abc = ABCFile(data)
        decompiler = AS3Decompiler(abc)
        for cls_info in decompiler.list_classes():
            pkg = cls_info.get("package", "")
            name = cls_info.get("name", "")
            full = f"{pkg}.{name}" if pkg else name
            if full != class_name:
                continue
            source = decompiler.decompile_class(cls_info["index"])
            return finalize_decompiled_source(source)
    raise RuntimeError(f"class not found in SWF ABC blocks: {class_name}")


def _decompile_class(swf_path: Path, class_name: str) -> str:
    return decompile_class_from_swf(swf_path, class_name)


def _idk_source_path(idk_com_root: Path, class_name: str) -> Path:
    rel = class_name.replace(".", "/") + ".as"
    if rel.startswith("com/"):
        rel = rel[4:]
    return idk_com_root / rel


def _member_names_from_source(src: str) -> Set[str]:
    names: Set[str] = set(_FN_NAME.findall(src))
    names.update(_GETTER.findall(src))
    names.update(_SETTER.findall(src))
    return names


def _member_names_from_decompile(src: str) -> Set[str]:
    return _member_names_from_source(src)


def _abc_method_traits(swf: Path, class_name: str) -> Set[str]:
    read_abc_blocks, ABCFile, TM, TG, TS, TF = _import_abc()
    _, blocks = read_abc_blocks(str(swf))
    names: Set[str] = set()
    for _block_name, data in blocks:
        abc = ABCFile(data)
        for ci, inst in enumerate(abc.instances):
            if abc.mn_full(inst.name_idx) != class_name:
                continue
            cls = abc.classes[ci]
            for t in inst.traits + cls.traits:
                if t.kind in (TM, TG, TS, TF):
                    names.add(abc.mn_name(t.name_idx))
    return names


def audit_one(swf: Path, idk_com_root: Path, class_name: str) -> Dict[str, object]:
    source_path = _idk_source_path(idk_com_root, class_name)
    if not source_path.is_file():
        return {
            "class": class_name,
            "ok": False,
            "error": f"source missing: {source_path}",
        }

    original = source_path.read_text(encoding="utf-8", errors="ignore")
    try:
        decompiled = _decompile_class(swf, class_name)
    except Exception as exc:
        return {"class": class_name, "ok": False, "error": str(exc)}

    idk_members = _member_names_from_source(original)
    dec_members = _member_names_from_decompile(decompiled)
    abc_members = _abc_method_traits(swf, class_name)

    idk_not_abc = sorted(idk_members - abc_members)
    abc_not_dec = sorted(abc_members - dec_members)
    dec_not_abc = sorted(dec_members - abc_members)
    idk_not_dec = sorted(idk_members - dec_members)

    norm_o = _normalize(original)
    norm_d = _normalize(decompiled)

    return {
        "class": class_name,
        "ok": True,
        "similarity": round(_similarity(norm_o, norm_d), 4),
        "idkMemberCount": len(idk_members),
        "abcTraitCount": len(abc_members),
        "decompiledMemberCount": len(dec_members),
        "idkOnlyNotInSwf": idk_not_abc[:40],
        "idkOnlyNotInSwfCount": len(idk_not_abc),
        "abcNotDecompiled": abc_not_dec[:40],
        "abcNotDecompiledCount": len(abc_not_dec),
        "decompiledNotInAbc": dec_not_abc[:40],
        "idkNotDecompiled": idk_not_dec[:40],
        "idkNotDecompiledCount": len(idk_not_dec),
        "activationArtifacts": "__activation__" in decompiled,
    }


def discover_classes(swf: Path, idk_com_root: Path, limit: int) -> List[str]:
    read_abc_blocks, ABCFile, *_ = _import_abc()
    _, blocks = read_abc_blocks(str(swf))
    swf_classes: List[str] = []
    for _block_name, data in blocks:
        abc = ABCFile(data)
        for inst in abc.instances:
            pkg = abc.mn_ns(inst.name_idx)
            name = abc.mn_name(inst.name_idx)
            fqn = f"{pkg}.{name}" if pkg else name
            if fqn.startswith("com.mcleodgaming"):
                swf_classes.append(fqn)
    swf_classes = sorted(set(swf_classes))
    found: List[str] = []
    for fqn in swf_classes:
        if _idk_source_path(idk_com_root, fqn).is_file():
            found.append(fqn)
        if len(found) >= limit:
            break
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit SSF2 decompile fidelity vs IDK source")
    ap.add_argument("--swf", required=True, help="Path to source SWF")
    ap.add_argument(
        "--idk-root",
        required=True,
        help="Path to IDK com root (e.g. .../Super Smash Flash 2 Beta v1.4.0.1/com)",
    )
    ap.add_argument(
        "--class",
        dest="classes",
        action="append",
        help="Fully-qualified class (repeatable)",
    )
    ap.add_argument(
        "--discover",
        action="store_true",
        help="Auto-pick com.mcleodgaming.* classes that exist in IDK tree",
    )
    ap.add_argument("--limit", type=int, default=25, help="Max classes with --discover")
    ap.add_argument("--json", help="Optional output json path")
    args = ap.parse_args()

    swf = Path(args.swf)
    idk = Path(args.idk_root)
    if not swf.is_file():
        print(f"ERROR: swf not found: {swf}", file=sys.stderr)
        return 2
    if not idk.is_dir():
        print(f"ERROR: idk root not found: {idk}", file=sys.stderr)
        return 2

    classes = list(args.classes or [])
    if args.discover:
        classes = discover_classes(swf, idk, args.limit)
    if not classes:
        print("ERROR: specify --class or --discover", file=sys.stderr)
        return 2

    results = [audit_one(swf, idk, cls) for cls in classes]

    print("\nIDK Decompile Audit (IDK vs ABC vs decompiler)")
    print("-" * 100)
    print(
        f"{'CLASS':<44} {'OK':<4} {'SIM':>6} "
        f"{'IDK':>4} {'ABC':>4} {'DEC':>4} "
        f"{'!SWF':>5} {'!DEC':>5}"
    )
    print("-" * 100)
    for r in results:
        if not r.get("ok"):
            print(f"{r['class']:<44} FAIL")
            print(f"  error: {r.get('error')}")
            continue
        print(
            f"{r['class']:<44} "
            f"{'OK':<4} "
            f"{r['similarity']:>6.3f} "
            f"{r['idkMemberCount']:>4} "
            f"{r['abcTraitCount']:>4} "
            f"{r['decompiledMemberCount']:>4} "
            f"{r['idkOnlyNotInSwfCount']:>5} "
            f"{r['abcNotDecompiledCount']:>5}"
        )

    ok_rows = [r for r in results if r.get("ok")]
    if ok_rows:
        avg = sum(float(r["similarity"]) for r in ok_rows) / len(ok_rows)
        dec_gaps = sum(int(r["abcNotDecompiledCount"]) for r in ok_rows)
        swf_gaps = sum(int(r["idkOnlyNotInSwfCount"]) for r in ok_rows)
        print("-" * 100)
        print(
            f"{len(ok_rows)} class(es)  avg sim {avg:.3f}  "
            f"decompiler gaps (abc->dec): {dec_gaps}  "
            f"idk-only (not in swf): {swf_gaps}"
        )

    worst_dec = sorted(
        [r for r in ok_rows if r.get("abcNotDecompiledCount", 0) > 0],
        key=lambda x: -int(x["abcNotDecompiledCount"]),
    )[:5]
    if worst_dec:
        print("\nWorst decompiler gaps (in SWF ABC but not decompiled):")
        for r in worst_dec:
            print(f"  {r['class']}: {r['abcNotDecompiled']}")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nwrote {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
