#!/usr/bin/env python3
"""
Bulk audit: roundtrip project scripts vs IDK source-of-truth under com/.

Answers:
  - How many .as files roundtrip with acceptable fidelity?
  - What systemic failure modes dominate (stubs, member loss, activation slots, …)?

Compares:
  IDK   …/Super Smash Flash 2 Beta v1.4.0.1/com/**/*.as
  RT    …/ssf2-roundtrip/scripts/com/**/*.as  (or --roundtrip-scripts)

Optional --swf supplies ABC trait ground truth (PSB SSF2.swf recommended).

Usage:
  py -3 tests/idk_roundtrip_audit.py \\
      --idk-root "…/Super Smash Flash 2 Beta v1.4.0.1/com" \\
      --roundtrip-scripts "…/ssf2-roundtrip/scripts" \\
      --swf "…/PSB 1.4 v2/SSF2.swf" \\
      --json report.json
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
APP_DIR = SCRIPT_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from tests.idk_decompile_audit import (  # noqa: E402
    _member_names_from_source,
    _normalize,
    _similarity,
)
from ssf2_runner import _is_decompiler_stub_source  # noqa: E402

_ACTIVATION = re.compile(r"__activation__|_local_\d+\.slot\d+")
_SYNTAX_ARTIFACT = re.compile(
    r"new\s+\._[A-Za-z]|\b\d{4,}\.[a-zA-Z]|Security\.loadPolicyFile"
)
_LINE_COMMENT = re.compile(r"//[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def _non_empty_lines(src: str) -> int:
    return len(
        [
            ln
            for ln in src.splitlines()
            if ln.strip() and not ln.strip().startswith("//")
        ]
    )


def _estimate_similarity(idk_src: str, rt_src: str) -> float:
    """Fast text similarity — quick_ratio for large classes, full ratio for small."""
    norm_a = _normalize(idk_src)
    norm_b = _normalize(rt_src)
    if norm_a == norm_b:
        return 1.0
    if max(len(norm_a), len(norm_b)) > 20_000:
        return difflib.SequenceMatcher(None, norm_a, norm_b, autojunk=True).quick_ratio()
    return _similarity(norm_a, norm_b)


def _member_jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 1.0


def _norm_hash(src: str) -> str:
    return hashlib.sha256(_normalize(src).encode("utf-8")).hexdigest()[:16]


    return hashlib.sha256(_normalize(src).encode("utf-8")).hexdigest()[:16]


def _rel_com_path(path: Path, com_root: Path) -> str:
    rel = path.relative_to(com_root).as_posix()
    return rel


def _fqn_from_com_rel(rel: str) -> str:
    base = rel[:-3] if rel.lower().endswith(".as") else rel
    return "com." + base.replace("/", ".")


def _load_abc_member_traits(swf: Optional[Path]) -> Dict[str, Set[str]]:
    """FQCN -> method/getter/setter names for com.* classes (single SWF pass)."""
    if not swf or not swf.is_file():
        return {}
    from as3_decompiler.swf_reader import read_abc_blocks
    from as3_decompiler.abc_parser import ABCFile, TRAIT_Method, TRAIT_Getter, TRAIT_Setter, TRAIT_Function

    trait_kinds = {TRAIT_Method, TRAIT_Getter, TRAIT_Setter, TRAIT_Function}
    out: Dict[str, Set[str]] = {}
    _, blocks = read_abc_blocks(str(swf))
    for _name, data in blocks:
        abc = ABCFile(data)
        for ci, inst in enumerate(abc.instances):
            fqn = abc.mn_full(inst.name_idx)
            if not fqn.startswith("com."):
                continue
            cls = abc.classes[ci]
            names = out.setdefault(fqn, set())
            for t in inst.traits + cls.traits:
                if t.kind in trait_kinds:
                    names.add(abc.mn_name(t.name_idx))
    return out


def _load_abc_classes(swf: Optional[Path]) -> Dict[str, int]:
    """FQCN -> trait count for classes under com.* in the SWF."""
    if not swf or not swf.is_file():
        return {}
    from as3_decompiler.swf_reader import read_abc_blocks
    from as3_decompiler.abc_parser import ABCFile, TRAIT_Method, TRAIT_Getter, TRAIT_Setter, TRAIT_Function

    trait_kinds = {TRAIT_Method, TRAIT_Getter, TRAIT_Setter, TRAIT_Function}
    out: Dict[str, int] = {}
    _, blocks = read_abc_blocks(str(swf))
    for _name, data in blocks:
        abc = ABCFile(data)
        for ci, inst in enumerate(abc.instances):
            fqn = abc.mn_full(inst.name_idx)
            if not fqn.startswith("com."):
                continue
            cls = abc.classes[ci]
            count = 0
            for t in inst.traits + cls.traits:
                if t.kind in trait_kinds:
                    count += 1
            out[fqn] = count
    return out


def _tier(
    *,
    similarity: float,
    is_stub: bool,
    abc_coverage: float,
    line_ratio: float,
    has_artifacts: bool,
    abc_not_dec_count: int,
) -> str:
    if is_stub:
        return "stub"
    if abc_coverage < 0.5 or line_ratio < 0.25:
        return "broken"
    if similarity >= 0.95 and abc_coverage >= 0.98 and abc_not_dec_count == 0:
        return "excellent"
    if similarity >= 0.88 and abc_coverage >= 0.95 and not has_artifacts:
        return "good"
    if similarity >= 0.75 and abc_coverage >= 0.85:
        return "acceptable"
    if similarity >= 0.55 or abc_coverage >= 0.65:
        return "degraded"
    return "poor"


def _roundtrip_ok(tier: str) -> bool:
    return tier in ("excellent", "good", "acceptable")


def audit_file(
    rel: str,
    idk_src: str,
    rt_src: str,
    *,
    abc_traits: Set[str],
    idk_path: Path,
) -> Dict[str, object]:
    idk_members = _member_names_from_source(idk_src)
    rt_members = _member_names_from_source(rt_src)
    abc_members = abc_traits or set()

    idk_lines = _non_empty_lines(idk_src)
    rt_lines = _non_empty_lines(rt_src)
    line_ratio = (rt_lines / idk_lines) if idk_lines else 1.0

    sim = _estimate_similarity(idk_src, rt_src)
    norm_match = _norm_hash(idk_src) == _norm_hash(rt_src)

    abc_in_rt = abc_members & rt_members
    abc_coverage = (len(abc_in_rt) / len(abc_members)) if abc_members else 1.0
    abc_not_dec = sorted(abc_members - rt_members)
    idk_not_in_swf = sorted(idk_members - abc_members) if abc_members else []
    idk_not_rt = sorted(idk_members - rt_members)

    is_stub = _is_decompiler_stub_source(rt_src, f"com/{rel}")
    has_activation = bool(_ACTIVATION.search(rt_src))
    has_syntax_art = bool(_SYNTAX_ARTIFACT.search(rt_src))

    tier = _tier(
        similarity=sim,
        is_stub=is_stub,
        abc_coverage=abc_coverage,
        line_ratio=line_ratio,
        has_artifacts=has_activation or has_syntax_art,
        abc_not_dec_count=len(abc_not_dec),
    )

    issues: List[str] = []
    if is_stub:
        issues.append("decompiler_stub")
    if abc_not_dec:
        issues.append(f"abc_not_decompiled({len(abc_not_dec)})")
    if has_activation:
        issues.append("activation_slots")
    if has_syntax_art:
        issues.append("syntax_artifacts")
    if line_ratio < 0.5:
        issues.append(f"line_shrink({line_ratio:.0%})")
    if sim < 0.75:
        issues.append(f"low_similarity({sim:.2f})")
    if idk_not_rt and not idk_not_in_swf:
        issues.append(f"idk_members_missing({len(idk_not_rt)})")

    return {
        "rel": rel,
        "fqn": _fqn_from_com_rel(rel),
        "tier": tier,
        "roundtripOk": _roundtrip_ok(tier),
        "similarity": round(sim, 4),
        "memberJaccard": round(_member_jaccard(idk_members, rt_members), 3),
        "normMatch": norm_match,
        "idkLines": idk_lines,
        "rtLines": rt_lines,
        "lineRatio": round(line_ratio, 3),
        "idkMembers": len(idk_members),
        "rtMembers": len(rt_members),
        "abcTraits": len(abc_members),
        "abcCoverage": round(abc_coverage, 3),
        "abcNotDecompiledCount": len(abc_not_dec),
        "abcNotDecompiledSample": abc_not_dec[:8],
        "idkOnlyNotInSwfCount": len(idk_not_in_swf),
        "issues": issues,
        "idkPath": str(idk_path),
    }


def run_audit(
    idk_com: Path,
    rt_scripts: Path,
    swf: Optional[Path] = None,
) -> Dict[str, object]:
    rt_com = rt_scripts / "com"
    if not idk_com.is_dir():
        raise FileNotFoundError(f"IDK com root missing: {idk_com}")
    if not rt_com.is_dir():
        raise FileNotFoundError(f"Roundtrip scripts/com missing: {rt_com}")

    abc_member_traits = _load_abc_member_traits(swf)
    abc_class_traits: Dict[str, int] = {
        fqn: len(names) for fqn, names in abc_member_traits.items()
    }

    idk_files = sorted(idk_com.rglob("*.as"))
    rt_files = sorted(rt_com.rglob("*.as"))

    idk_rels = {_rel_com_path(p, idk_com) for p in idk_files}
    rt_rels = {_rel_com_path(p, rt_com) for p in rt_files}

    paired = sorted(idk_rels & rt_rels)
    idk_only = sorted(idk_rels - rt_rels)
    rt_only = sorted(rt_rels - idk_rels)

    file_reports: List[Dict[str, object]] = []
    tier_counts: Counter = Counter()
    issue_counts: Counter = Counter()
    pkg_tier: Dict[str, Counter] = defaultdict(Counter)

    for rel in paired:
        idk_path = idk_com / Path(rel)
        rt_path = rt_com / Path(rel)
        idk_src = idk_path.read_text(encoding="utf-8", errors="ignore")
        rt_src = rt_path.read_text(encoding="utf-8", errors="ignore")
        fqn = _fqn_from_com_rel(rel)
        abc_traits = abc_member_traits.get(fqn, set())

        row = audit_file(rel, idk_src, rt_src, abc_traits=abc_traits, idk_path=idk_path)
        file_reports.append(row)
        tier = str(row["tier"])
        tier_counts[tier] += 1
        pkg = rel.split("/")[0] if "/" in rel else rel.split("\\")[0]
        pkg_tier[pkg][tier] += 1
        for issue in row["issues"]:
            key = issue.split("(")[0]
            issue_counts[key] += 1

    # IDK-only: classify as dev-only vs missing-from-roundtrip
    idk_only_in_swf: List[str] = []
    idk_only_not_in_swf: List[str] = []
    for rel in idk_only:
        fqn = _fqn_from_com_rel(rel)
        if fqn in abc_class_traits:
            idk_only_in_swf.append(rel)
        else:
            idk_only_not_in_swf.append(rel)

    rt_only_rows = [{"rel": rel, "fqn": _fqn_from_com_rel(rel)} for rel in rt_only]

    ok_count = sum(1 for r in file_reports if r["roundtripOk"])
    paired_count = len(paired)

    # Systemic buckets (paired files only)
    systemic = {
        "decompiler_stub": tier_counts.get("stub", 0),
        "broken_shell": tier_counts.get("broken", 0),
        "abc_methods_lost": sum(
            1 for r in file_reports if r.get("abcNotDecompiledCount", 0) > 0
        ),
        "activation_slot_artifacts": sum(
            1 for r in file_reports if "activation_slots" in r.get("issues", [])
        ),
        "syntax_artifacts": sum(
            1 for r in file_reports if "syntax_artifacts" in r.get("issues", [])
        ),
        "severe_line_shrink": sum(
            1 for r in file_reports if (r.get("lineRatio") or 1) < 0.5
        ),
        "low_similarity_under_75": sum(
            1 for r in file_reports if (r.get("similarity") or 1) < 0.75
        ),
    }

    worst = sorted(
        [r for r in file_reports if not r["roundtripOk"]],
        key=lambda r: (r.get("similarity") or 0, -(r.get("abcNotDecompiledCount") or 0)),
    )[:25]

    return {
        "idkComRoot": str(idk_com),
        "roundtripScripts": str(rt_scripts),
        "swf": str(swf) if swf else None,
        "counts": {
            "idkComFiles": len(idk_files),
            "roundtripComFiles": len(rt_files),
            "paired": paired_count,
            "idkOnly": len(idk_only),
            "idkOnlyInSwf": len(idk_only_in_swf),
            "idkOnlyNotInSwf": len(idk_only_not_in_swf),
            "roundtripOnly": len(rt_only),
            "roundtripOk": ok_count,
            "roundtripNotOk": paired_count - ok_count,
            "roundtripOkPct": round(100 * ok_count / paired_count, 1) if paired_count else 0,
        },
        "tierCounts": dict(tier_counts),
        "tierLegend": {
            "excellent": "≥95% sim, ≥98% ABC members, no ABC gaps",
            "good": "≥88% sim, ≥95% ABC members, no activation/syntax artifacts",
            "acceptable": "≥75% sim, ≥85% ABC members",
            "degraded": "partial fidelity — boots may hit runtime errors here",
            "poor": "heavy loss — likely runtime failures",
            "broken": "<50% ABC coverage or <25% lines vs IDK",
            "stub": "empty decompiler shell (≤12 lines / no real ctor)",
        },
        "systemicIssues": systemic,
        "issueTagCounts": dict(issue_counts.most_common(20)),
        "packageTierBreakdown": {k: dict(v) for k, v in sorted(pkg_tier.items())},
        "worstFiles": worst,
        "idkOnlyInSwfSample": idk_only_in_swf[:20],
        "roundtripOnlySample": rt_only_rows[:20],
        "files": file_reports,
    }


def _print_summary(report: Dict[str, object]) -> None:
    c = report["counts"]
    print("=" * 60)
    print("IDK vs Roundtrip scripts/com audit")
    print("=" * 60)
    print(f"IDK com/ files:        {c['idkComFiles']}")
    print(f"Roundtrip com/ files:  {c['roundtripComFiles']}")
    print(f"Paired (same path):    {c['paired']}")
    print(f"  Roundtrip OK:        {c['roundtripOk']} ({c['roundtripOkPct']}%)")
    print(f"  Roundtrip NOT OK:    {c['roundtripNotOk']}")
    print(f"IDK only:              {c['idkOnly']}  (in SWF: {c['idkOnlyInSwf']}, dev-only: {c['idkOnlyNotInSwf']})")
    print(f"Roundtrip only:        {c['roundtripOnly']}")
    print()
    print("Tier breakdown (paired files):")
    for tier in ("excellent", "good", "acceptable", "degraded", "poor", "broken", "stub"):
        n = report["tierCounts"].get(tier, 0)
        if n:
            print(f"  {tier:12} {n:4}")
    print()
    print("Systemic issue prevalence (paired files):")
    for k, v in report["systemicIssues"].items():
        print(f"  {k:28} {v:4}")
    print()
    print("Top issue tags:")
    for tag, n in list(report.get("issueTagCounts", {}).items())[:12]:
        print(f"  {tag:28} {n:4}")
    print()
    print("Package tier breakdown:")
    for pkg, tiers in report.get("packageTierBreakdown", {}).items():
        total = sum(tiers.values())
        ok = sum(tiers.get(t, 0) for t in ("excellent", "good", "acceptable"))
        print(f"  {pkg:12} {ok}/{total} OK  {dict(tiers)}")
    print()
    print("Worst 15 files:")
    for row in report.get("worstFiles", [])[:15]:
        issues = ", ".join(row.get("issues") or []) or "-"
        print(
            f"  {row['rel']:50} tier={row['tier']:10} "
            f"sim={row.get('similarity', 0):.2f} abc_gap={row.get('abcNotDecompiledCount', 0):3}  {issues}"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Bulk IDK vs roundtrip scripts/com audit")
    ap.add_argument(
        "--idk-root",
        required=True,
        help="Path to IDK com/ folder (…/Super Smash Flash 2 Beta v1.4.0.1/com)",
    )
    ap.add_argument(
        "--roundtrip-scripts",
        required=True,
        help="Path to roundtrip scripts/ folder (parent of com/)",
    )
    ap.add_argument(
        "--swf",
        help="PSB SSF2.swf for ABC trait ground truth (strongly recommended)",
    )
    ap.add_argument("--json", help="Write full JSON report to this path")
    ap.add_argument("--quiet", action="store_true", help="Skip per-file listing in JSON stdout")
    args = ap.parse_args()

    idk_com = Path(args.idk_root)
    rt_scripts = Path(args.roundtrip_scripts)
    swf = Path(args.swf) if args.swf else None

    report = run_audit(idk_com, rt_scripts, swf)
    _print_summary(report)

    if args.json:
        out = dict(report)
        if args.quiet:
            out.pop("files", None)
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"\nFull report: {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
