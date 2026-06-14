#!/usr/bin/env python3
"""
Fingerprint SSF2 roundtrip pipeline stages S0–S4 for boot-critical classes.

Stages:
  S0  SWF ABC trait names
  S1  In-memory decompile (same path as swf_to_n2d import)
  S3  project.n2d embedded source vs scripts/ on disk
  S4  After compile_n2d overlay + strip (what mxmlc would see)

Usage:
  py -3 tests/pipeline_stage_audit.py \\
      --swf "path/to/PSB SSF2.swf" \\
      --project-dir app/converted/ssf2-roundtrip

  py -3 tests/pipeline_stage_audit.py --swf ... --import-only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

SCRIPT_DIR = Path(__file__).resolve().parent
APP_DIR = SCRIPT_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from idk_decompile_audit import (  # noqa: E402
    _abc_method_traits,
    _member_names_from_source,
    decompile_class_from_swf,
)

BOOT_CLASSES = [
    "com.mcleodgaming.ssf2.Main",
    "com.mcleodgaming.ssf2.util.Utils",
    "Logger",
]

BOOT_FLAGS = {
    "com.mcleodgaming.ssf2.Main": ("logToFile", "initErrorHandler", "function Main"),
    "com.mcleodgaming.ssf2.util.Utils": ("initializeUtilsClass",),
    "Logger": ("Main.logToFile",),
}

_SCRIPT_PATHS = {
    "com.mcleodgaming.ssf2.Main": "com/mcleodgaming/ssf2/Main.as",
    "com.mcleodgaming.ssf2.util.Utils": "com/mcleodgaming/ssf2/util/Utils.as",
    "Logger": "Logger.as",
}

_LOCAL_SLOT = re.compile(r"_local_\d+\.slot\d+")


def _flags_present(src: str, flags: tuple[str, ...]) -> Dict[str, bool]:
    return {f: f in src for f in flags}


def _read_embedded_script(project_dir: Path, rel_path: str) -> tuple[str, int]:
    n2d_path = project_dir / "project.n2d"
    if not n2d_path.is_file():
        return "", 0
    import msgpack

    with zipfile.ZipFile(n2d_path) as zf:
        data = msgpack.unpackb(zf.read("project.msgpack"), raw=False)
    for script in data.get("scripts") or []:
        if (script.get("path") or "").replace("\\", "/") == rel_path:
            src = script.get("source") or ""
            return src, len(src.encode("utf-8"))
    return "", 0


def _read_disk_script(project_dir: Path, rel_path: str) -> tuple[str, int]:
    path = project_dir / "scripts" / rel_path
    if not path.is_file():
        return "", 0
    src = path.read_text(encoding="utf-8", errors="ignore")
    return src, len(src.encode("utf-8"))


def _stage_s4_overlay(project_dir: Path, class_name: str, rel_path: str) -> tuple[str, int]:
    import compile_n2d as c2n

    n2d_path = project_dir / "project.n2d"
    if not n2d_path.is_file():
        return "", 0
    data, _ = c2n.load_n2d(str(project_dir))
    for script in data.get("scripts") or []:
        if (script.get("path") or "").replace("\\", "/") != rel_path:
            continue
        src = script.get("source") or ""
        primary = Path(rel_path).stem
        cleaned = c2n._strip_non_primary_classes(src, primary)
        cleaned = c2n._sanitize_embedded_script(cleaned)
        return cleaned, len(cleaned.encode("utf-8"))
    return "", 0


def _abc_not_dec(abc_members: Set[str], dec_members: Set[str]) -> List[str]:
    return sorted(abc_members - dec_members)


def audit_class(
    swf: Path,
    class_name: str,
    *,
    project_dir: Optional[Path] = None,
    memory_source: Optional[str] = None,
) -> Dict[str, Any]:
    rel = _SCRIPT_PATHS.get(class_name, class_name.replace(".", "/") + ".as")
    flags = BOOT_FLAGS.get(class_name, ())

    abc_members = _abc_method_traits(swf, class_name)
    row: Dict[str, Any] = {
        "class": class_name,
        "scriptPath": rel,
        "S0_abcTraits": len(abc_members),
        "S0_abcMembers": sorted(abc_members)[:12],
    }

    try:
        if memory_source is None:
            memory_source = decompile_class_from_swf(swf, class_name)
    except Exception as exc:
        row["error"] = f"S1 decompile failed: {exc}"
        return row

    dec_members = _member_names_from_source(memory_source)
    row["S1_decompileBytes"] = len(memory_source.encode("utf-8"))
    row["S1_decompileMembers"] = len(dec_members)
    row["S1_flags"] = _flags_present(memory_source, flags)
    row["S1_slotArtifacts"] = bool(_LOCAL_SLOT.search(memory_source))
    missing = _abc_not_dec(abc_members, dec_members)
    row["S1_abcNotDecompiled"] = missing[:20]
    row["S1_abcNotDecompiledCount"] = len(missing)

    if project_dir and project_dir.is_dir():
        embed_src, embed_bytes = _read_embedded_script(project_dir, rel)
        disk_src, disk_bytes = _read_disk_script(project_dir, rel)
        row["S3_embedBytes"] = embed_bytes
        row["S3_diskBytes"] = disk_bytes
        row["S3_embedFlags"] = _flags_present(embed_src, flags)
        row["S3_diskFlags"] = _flags_present(disk_src, flags)
        row["S3_diskVsEmbed"] = disk_bytes != embed_bytes
        row["S3_staleTruncation"] = (
            embed_bytes > 0
            and row["S1_decompileBytes"] > 0
            and embed_bytes < int(row["S1_decompileBytes"] * 0.6)
        )
        s4_src, s4_bytes = _stage_s4_overlay(project_dir, class_name, rel)
        row["S4_overlayBytes"] = s4_bytes
        row["S4_overlayFlags"] = _flags_present(s4_src, flags)
        row["S4_slotArtifacts"] = bool(_LOCAL_SLOT.search(s4_src))

    warnings: List[str] = []
    if row.get("S1_abcNotDecompiledCount", 0) > 0:
        warnings.append(f"!DEC: {row['S1_abcNotDecompiledCount']} ABC traits missing from decompile")
    for flag, ok in (row.get("S1_flags") or {}).items():
        if not ok:
            warnings.append(f"S1 missing boot flag: {flag}")
    if row.get("S3_staleTruncation"):
        warnings.append(
            f"!PERSIST: embedded Main truncated ({row.get('S3_embedBytes')} vs "
            f"fresh decompile {row.get('S1_decompileBytes')}) — re-import project"
        )
    if row.get("S3_diskVsEmbed"):
        warnings.append("!PERSIST: disk scripts/ differs from project.n2d embedded source")
    for flag, ok in (row.get("S4_overlayFlags") or {}).items():
        if not ok:
            warnings.append(f"S4 compile-prep missing boot flag: {flag}")
    if row.get("S1_slotArtifacts") or row.get("S4_slotArtifacts"):
        warnings.append("!BODY: activation .slotN artifacts present")
    row["warnings"] = warnings
    row["ok"] = not warnings
    return row


def run_import_fingerprint(swf: Path) -> Dict[str, Any]:
    from conversion_service import ConversionService

    with open(swf, "rb") as f:
        data = f.read()
    n2d = ConversionService().convert_swf_to_n2d(
        data, name="_pipeline_audit", include_scripts=True, embed_bitmaps=False
    )
    memory: Dict[str, str] = {}
    for script in n2d.get("scripts") or []:
        path = (script.get("path") or "").replace("\\", "/")
        for cls, rel in _SCRIPT_PATHS.items():
            if path == rel:
                memory[cls] = script.get("source") or ""
    return memory


def main() -> int:
    ap = argparse.ArgumentParser(description="SSF2 pipeline stage audit (S0–S4)")
    ap.add_argument("--swf", required=True, help="Source PSB SWF path")
    ap.add_argument("--project-dir", help="N2D project folder (e.g. converted/ssf2-roundtrip)")
    ap.add_argument(
        "--import-only",
        action="store_true",
        help="Also run full ConversionService import for S1 memory check",
    )
    ap.add_argument("--json", help="Write JSON report to path")
    args = ap.parse_args()

    swf = Path(args.swf)
    if not swf.is_file():
        print(f"ERROR: swf not found: {swf}", file=sys.stderr)
        return 2

    project_dir = Path(args.project_dir) if args.project_dir else None
    if project_dir and not project_dir.is_dir():
        print(f"ERROR: project dir not found: {project_dir}", file=sys.stderr)
        return 2

    memory_sources: Dict[str, str] = {}
    if args.import_only:
        print("Running full import for S1 memory fingerprint...")
        memory_sources = run_import_fingerprint(swf)

    results = []
    for cls in BOOT_CLASSES:
        try:
            row = audit_class(
                swf,
                cls,
                project_dir=project_dir,
                memory_source=memory_sources.get(cls),
            )
        except Exception as exc:
            row = {"class": cls, "ok": False, "error": str(exc), "warnings": [str(exc)]}
        results.append(row)

    print("\nSSF2 Pipeline Stage Audit (boot-critical classes)")
    print("-" * 110)
    print(
        f"{'CLASS':<36} {'S0':>4} {'S1':>7} {'S3e':>7} {'S3d':>7} {'S4':>7} "
        f"{'!DEC':>5} {'OK':>4}"
    )
    print("-" * 110)
    for r in results:
        if r.get("error") and not r.get("S0_abcTraits"):
            print(f"{r['class']:<36} FAIL  {r.get('error')[:60]}")
            continue
        print(
            f"{r['class']:<36} "
            f"{r.get('S0_abcTraits', 0):>4} "
            f"{r.get('S1_decompileBytes', 0):>7} "
            f"{r.get('S3_embedBytes', '-'):>7} "
            f"{r.get('S3_diskBytes', '-'):>7} "
            f"{r.get('S4_overlayBytes', '-'):>7} "
            f"{r.get('S1_abcNotDecompiledCount', 0):>5} "
            f"{'OK' if r.get('ok') else 'NO':>4}"
        )
        for w in r.get("warnings") or []:
            print(f"  ! {w}")
        for flag, ok in (r.get("S1_flags") or {}).items():
            if not ok:
                print(f"  S1 flag missing: {flag}")

    print("-" * 110)
    any_bad = any(not r.get("ok", False) for r in results)
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"wrote {args.json}")
    return 1 if any_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
