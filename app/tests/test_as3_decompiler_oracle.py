#!/usr/bin/env python3
"""
test_as3_decompiler_oracle.py — Measure AS3 decompiler accuracy
against ground truth produced by Adobe Animate's compiler.

Workflow
--------
1. Author small .as fixtures in `_dev_docs/jsfl/as3_fixtures/`.
2. Run `_dev_docs/jsfl/as3_oracle.jsfl` inside Animate. This
   produces `_dev_docs/jsfl/output/as3_oracle/<name>.swf` paired
   with `<name>.as` and a `MANIFEST.json`.
3. Run this script. For each manifest entry it:
     a) Decompiles the SWF via the Next2Flash AS3 decompiler.
     b) Normalises both the original and decompiled source
        (strip comments + whitespace, sort imports).
     c) Computes a similarity score and prints a report.
4. The output dashboard tells us, axis-by-axis, where the
   decompiler diverges from ground truth.

Notes
-----
- We do NOT yet implement the ABC-equivalence round-trip (decompile
  -> recompile -> compare bytecode). That requires a second Animate
  pass and is wired in once the source-level metrics stabilise.
- Exit code is non-zero only on infrastructure failure, not on
  decompile drift, so this can run in CI as a tracking metric
  without blocking builds.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

SCRIPT_DIR  = Path(__file__).resolve().parent
APP_DIR     = SCRIPT_DIR.parent
REPO_ROOT   = APP_DIR.parent
DEFAULT_ORACLE = REPO_ROOT / "_dev_docs" / "jsfl" / "output" / "as3_oracle"


# ---------- normalisation ----------

_LINE_COMMENT = re.compile(r"//[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_WHITESPACE = re.compile(r"\s+")
_IMPORT_LINE = re.compile(r"^\s*import\s+([\w\.\*]+)\s*;", re.MULTILINE)


def normalise(src: str) -> str:
    """Aggressive normalisation for textual comparison.

    Strips comments, collapses whitespace, sorts imports. Throws
    away formatting differences so we focus on semantic drift.
    """
    src = _BLOCK_COMMENT.sub(" ", src)
    src = _LINE_COMMENT.sub(" ", src)
    imports = sorted(set(_IMPORT_LINE.findall(src)))
    src = _IMPORT_LINE.sub("", src)
    src = _WHITESPACE.sub(" ", src).strip()
    return "IMPORTS[" + ",".join(imports) + "] " + src


def similarity(a: str, b: str) -> float:
    """Ratio in [0, 1] from difflib's quick_ratio."""
    return difflib.SequenceMatcher(None, a, b).ratio()


# ---------- decompiler invocation ----------

def decompile(swf_path: Path, classname: str) -> Tuple[str, str]:
    """Run `python -m as3_decompiler` against the SWF. Returns
    (source_text, stderr). Raises on subprocess failure."""
    cmd = [
        sys.executable, "-m", "as3_decompiler",
        str(swf_path), "--class", classname
    ]
    res = subprocess.run(
        cmd,
        cwd=str(APP_DIR),
        capture_output=True,
        text=True,
        timeout=60
    )
    if res.returncode != 0:
        raise RuntimeError(
            f"decompiler exited {res.returncode}: {res.stderr.strip()[:500]}"
        )
    return res.stdout, res.stderr


# ---------- evaluation ----------

def evaluate_one(oracle_dir: Path, entry: Dict[str, Any]) -> Dict[str, Any]:
    name = entry["source"]
    swf_path = oracle_dir / entry["swf"]
    src_path = oracle_dir / (entry["swf"].replace(".swf", ".as"))
    result: Dict[str, Any] = {
        "name": name,
        "class": entry["class"],
        "compiled_ok": bool(entry.get("ok")),
        "decompile_ok": False,
        "similarity": 0.0,
        "error": None,
    }

    if not entry.get("ok"):
        result["error"] = "oracle compile failed: " + str(entry.get("error"))
        return result
    if not swf_path.is_file():
        result["error"] = f"SWF missing: {swf_path}"
        return result
    if not src_path.is_file():
        result["error"] = f"source missing: {src_path}"
        return result

    original = src_path.read_text(encoding="utf-8")
    classname = entry["class"]

    try:
        decompiled, _ = decompile(swf_path, classname)
    except Exception as exc:
        result["error"] = f"decompile threw: {exc}"
        return result

    norm_orig = normalise(original)
    norm_dec  = normalise(decompiled)
    result["decompile_ok"] = True
    result["similarity"] = round(similarity(norm_orig, norm_dec), 4)
    result["original_chars"] = len(norm_orig)
    result["decompiled_chars"] = len(norm_dec)
    return result


def print_report(results: List[Dict[str, Any]]) -> None:
    print()
    print("=" * 78)
    print(" AS3 DECOMPILER ORACLE REPORT")
    print("=" * 78)
    print(f" {'NAME':<35} {'COMPILED':<9} {'DECOMP':<7} {'SIM':>6}  ERROR")
    print("-" * 78)
    for r in results:
        sim = f"{r['similarity']:.3f}" if r["decompile_ok"] else "-----"
        err = (r["error"] or "")[:30]
        print(f" {r['name']:<35} "
              f"{'OK' if r['compiled_ok'] else 'FAIL':<9} "
              f"{'OK' if r['decompile_ok'] else 'FAIL':<7} "
              f"{sim:>6}  {err}")
    print("-" * 78)
    n = len(results)
    n_dec = sum(1 for r in results if r["decompile_ok"])
    avg = (sum(r["similarity"] for r in results if r["decompile_ok"])
           / max(1, n_dec))
    print(f" Decompiled {n_dec}/{n}   mean similarity {avg:.3f}")
    print("=" * 78)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--oracle-dir", default=str(DEFAULT_ORACLE),
        help="Folder produced by as3_oracle.jsfl "
             "(default: %(default)s)")
    ap.add_argument("--json", help="Write full results as JSON to this path")
    args = ap.parse_args()

    oracle_dir = Path(args.oracle_dir)
    manifest = oracle_dir / "MANIFEST.json"
    if not manifest.is_file():
        sys.stderr.write(
            f"ERROR: manifest not found: {manifest}\n"
            "Run _dev_docs/jsfl/as3_oracle.jsfl inside Animate first.\n"
        )
        return 2

    entries = json.loads(manifest.read_text(encoding="utf-8"))
    results = [evaluate_one(oracle_dir, e) for e in entries]
    print_report(results)

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2),
                                   encoding="utf-8")
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
