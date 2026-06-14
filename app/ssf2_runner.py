#!/usr/bin/env python3
"""
SSF2 round-trip test helpers: settings, SWF preflight, compile, deploy paths.

Used by server.py API and optional CLI. ADL launch is handled in Electron (main process).
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import struct
import time
from typing import Any, Dict, List, Optional, Tuple

log = logging.getLogger(__name__)

# Default paths for local SSF2 IDK (user can override via settings file / API).
DEFAULT_SOURCE_SWF = (
    r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\PSB 1.4 v2\SSF2.swf"
)
DEFAULT_ADL_ROOT = (
    r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1"
)
DEFAULT_GAME_ROOT = (
    r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\PSB 1.4 v2"
)
# IDK VS Code launch.json extdir; ADL 32 accepts only one -extdir argument.
DEFAULT_ADL_EXTDIR = ".as3mxml-unpackaged-anes"
DEFAULT_AIR_SDK_CANDIDATES = [
    os.environ.get("N2F_AIR_SDK", ""),
    r"C:\aflex_sdk",
    r"C:\flex_sdk",
]

SETTINGS_FILENAME = "ssf2-debug-settings.json"
BACKUP_SUFFIX = ".n2f-backup"

# AIR / AS3 runtime failures (mirrors electron/main.js SSF2_ADL_FATAL_RE)
ADL_FATAL_RE = re.compile(
    r"Error #\d+|TypeError:|ReferenceError:|SecurityError:|VerifyError:|"
    r"cannot be loaded|could not be found|The -extdir argument|"
    r"Variable .+ is not defined",
    re.IGNORECASE,
)

ADL_SUCCESS_RE = re.compile(
    r"Utils class initialized|Main\.logToFile|\[ssf2\]|game loaded",
    re.IGNORECASE,
)


def settings_path(server_dir: str) -> str:
    return os.path.join(server_dir, "converted", SETTINGS_FILENAME)


def load_settings(server_dir: str) -> Dict[str, Any]:
    path = settings_path(server_dir)
    defaults = {
        "sourceSwf": DEFAULT_SOURCE_SWF,
        "adlRoot": DEFAULT_ADL_ROOT,
        "gameRoot": DEFAULT_GAME_ROOT,
        "airSdk": find_air_sdk() or "",
        "projectName": "ssf2-roundtrip",
        "deployToGameRoot": True,
        "deployToAdlRoot": True,
        "adlExtDir": DEFAULT_ADL_EXTDIR,
        # Folder with com/mcleodgaming/... AS3 sources (IDK src tree); used to fix decompiler stubs.
        "idkSourceRoot": DEFAULT_ADL_ROOT,
        "overlayIdkSources": True,
        "overlayIdkStubsOnly": True,
        "doubleRoundtripVerify": True,
    }
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                defaults.update(stored)
        except Exception as e:
            log.warning("load_settings: %s", e)
    return defaults


def save_settings(server_dir: str, data: Dict[str, Any]) -> Dict[str, Any]:
    os.makedirs(os.path.join(server_dir, "converted"), exist_ok=True)
    current = load_settings(server_dir)
    current.update({k: v for k, v in data.items() if v is not None})
    path = settings_path(server_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)
    return current


def find_air_sdk() -> Optional[str]:
    for cand in DEFAULT_AIR_SDK_CANDIDATES:
        if not cand:
            continue
        adl = os.path.join(cand, "bin", "adl.exe")
        if os.path.isfile(adl):
            return os.path.normpath(cand)
    try:
        import compile_n2d as c2n
        sdk = c2n.find_sdk()
        if sdk and os.path.isfile(os.path.join(sdk, "bin", "adl.exe")):
            return sdk
    except Exception:
        pass
    return None


def find_adl_exe(air_sdk: str) -> Optional[str]:
    if not air_sdk:
        return None
    adl = os.path.join(air_sdk, "bin", "adl.exe")
    return adl if os.path.isfile(adl) else None


def resolve_adl_ext_dir(adl_root: str, ext_rel: Optional[str] = None) -> Dict[str, Any]:
    """Pick ADL -extdir folder (single path; matches IDK launch.json)."""
    adl_root = os.path.normpath(adl_root)
    rel = (ext_rel or DEFAULT_ADL_EXTDIR).strip() or DEFAULT_ADL_EXTDIR
    abs_path = os.path.join(adl_root, rel) if rel != "." else adl_root
    anes: List[str] = []
    if os.path.isdir(abs_path):
        anes = sorted(f for f in os.listdir(abs_path) if f.lower().endswith(".ane"))
    if not anes and rel != ".":
        abs_path = adl_root
        rel = "."
        if os.path.isdir(abs_path):
            anes = sorted(f for f in os.listdir(abs_path) if f.lower().endswith(".ane"))
    return {"rel": rel, "abs": abs_path, "aneFiles": anes}


def resolve_adl_launch(
    adl_root: str, air_sdk: str, ext_rel: Optional[str] = None
) -> Dict[str, Any]:
    """Validate ADL launch environment (matches IDK VS Code launch.json)."""
    adl_root = os.path.normpath(adl_root)
    air_sdk = os.path.normpath(air_sdk) if air_sdk else ""
    app_xml = os.path.join(adl_root, "SSF2-app.xml")
    swf = os.path.join(adl_root, "SSF2.swf")
    data_dir = os.path.join(adl_root, "data")
    adl_exe = find_adl_exe(air_sdk)
    ext = resolve_adl_ext_dir(adl_root, ext_rel)
    issues = []
    if not adl_exe:
        issues.append(f"adl.exe not found under airSdk: {air_sdk or '(empty)'}")
    if not os.path.isfile(app_xml):
        issues.append(f"SSF2-app.xml missing in adlRoot: {adl_root}")
    if not os.path.isfile(swf):
        issues.append(f"SSF2.swf missing in adlRoot (deploy compiled SWF first): {swf}")
    if not os.path.isdir(data_dir):
        issues.append(f"data/ folder missing in adlRoot: {data_dir}")
    if not ext["aneFiles"]:
        issues.append(
            f"No .ane files in ADL extdir ({ext['rel']}). "
            "Build IDK with --unpackage-anes=true or copy ANEs into that folder."
        )
    return {
        "ok": len(issues) == 0,
        "adlExe": adl_exe or "",
        "adlRoot": adl_root,
        "appXml": app_xml,
        "swfPath": swf,
        "adlExtDir": ext["rel"],
        "adlExtDirAbs": ext["abs"],
        "aneFiles": ext["aneFiles"],
        "issues": issues,
    }


def _tag_counts(tags: List[Any]) -> Dict[int, int]:
    counts: Dict[int, int] = {}
    for t in tags:
        tt = getattr(t, "tag_type", None) or getattr(t, "type", None)
        if tt is not None:
            counts[tt] = counts.get(tt, 0) + 1
    return counts


def swf_preflight(path: str, label: str = "") -> Dict[str, Any]:
    """Structural summary of a SWF for SSF2 debug comparisons."""
    from swf_to_n2d import parse_swf, parse_symbol_class

    out: Dict[str, Any] = {"path": path, "label": label or os.path.basename(path)}
    if not os.path.isfile(path):
        out["error"] = "file not found"
        return out
    st = os.stat(path)
    out["size"] = st.st_size
    with open(path, "rb") as f:
        data = f.read()
    try:
        header, tags = parse_swf(data)
    except Exception as e:
        out["error"] = str(e)
        return out
    out["version"] = header.get("version")
    out["compressed"] = header.get("compressed")
    out["frameSize"] = header.get("frameSize")
    out["frameRate"] = header.get("frameRate")
    out["frameCount"] = header.get("frameCount")
    counts = _tag_counts(tags)
    out["tagCounts"] = {str(k): v for k, v in sorted(counts.items())}
    out["doabc2Count"] = counts.get(82, 0)
    symbol_map: Dict[int, str] = {}
    for t in tags:
        tt = getattr(t, "tag_type", None) or getattr(t, "type", None)
        if tt == 76:
            try:
                symbol_map.update(parse_symbol_class(t.data))
            except Exception:
                pass
    out["symbolClassCount"] = len(symbol_map)
    out["documentClass"] = symbol_map.get(0, "")
    out["symbolClassSample"] = [
        {"charId": cid, "className": name}
        for cid, name in sorted(symbol_map.items())[:12]
    ]
    return out


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def script_roundtrip_warnings(project_dir: str) -> List[str]:
    """Detect decompiler stubs and boot-critical gaps before mxmlc recompile."""
    warnings: List[str] = []
    scripts_dir = os.path.join(project_dir, "scripts")
    main_rel = "com/mcleodgaming/ssf2/Main.as"
    utils_rel = "com/mcleodgaming/ssf2/util/Utils.as"

    checks = [
        (
            os.path.join(scripts_dir, "com", "mcleodgaming", "ssf2", "util", "Utils.as"),
            "initializeUtilsClass",
            "Utils.as is missing initializeUtilsClass() — Main() will throw Error #1006 after recompile",
        ),
        (
            os.path.join(scripts_dir, "com", "mcleodgaming", "ssf2", "Main.as"),
            "function Main",
            "Main.as looks incomplete — document class may not run",
        ),
        (
            os.path.join(scripts_dir, "com", "mcleodgaming", "ssf2", "Main.as"),
            "logToFile",
            "Main.as is missing logToFile() — IDK Logger.as companion will throw Error #1006 at boot",
        ),
        (
            os.path.join(scripts_dir, "com", "mcleodgaming", "ssf2", "Main.as"),
            "initErrorHandler",
            "Main.as is missing initErrorHandler() — uncaught errors show AIR popups only",
        ),
    ]
    for path, needle, msg in checks:
        if not os.path.isfile(path):
            continue
        src = _read_text(path)
        non_empty = [ln for ln in src.splitlines() if ln.strip() and not ln.strip().startswith("//")]
        if len(non_empty) <= 12:
            warnings.append(f"{msg} (decompiler stub: {len(non_empty)} lines)")
        elif needle not in src:
            warnings.append(msg)

    main_path = os.path.join(scripts_dir, *main_rel.split("/"))
    main_src = _read_text(main_path) if os.path.isfile(main_path) else ""
    if main_src and "function initErrorHandler" in main_src and "initErrorHandler()" not in main_src:
        warnings.append(
            "Main.as defines initErrorHandler() but ctor never calls it — boot errors won't be handled"
        )
    if main_src and re.search(r"_local_\d+\.slot\d+", main_src):
        warnings.append(
            "Main.as has activation .slotN artifacts — ContextMenu setup may fail at runtime (!BODY)"
        )

    embed_main, disk_main = _main_embed_vs_disk_bytes(project_dir, main_rel)
    if embed_main and disk_main and not _main_embed_matches_disk(project_dir, main_rel):
        warnings.append(
            f"!PERSIST: Main.as disk ({disk_main} bytes) != project.n2d embedded ({embed_main} bytes)"
        )
    if embed_main and embed_main < 20000:
        warnings.append(
            f"!PERSIST: embedded Main.as is only {embed_main} bytes — likely stale truncated import; re-run roundtrip"
        )

    return warnings


def boot_critical_roundtrip_failures(project_dir: str) -> List[str]:
    """Subset of script_roundtrip_warnings that must block deploy/ADL."""
    fatal_markers = (
        "logToFile",
        "initializeUtilsClass",
        "decompiler stub",
        "!PERSIST",
        "looks incomplete",
    )
    return [
        w for w in script_roundtrip_warnings(project_dir)
        if any(m in w for m in fatal_markers)
    ]


def _main_embed_vs_disk_bytes(project_dir: str, rel_path: str) -> Tuple[int, int]:
    """Return (embedded_bytes, disk_bytes) for a script path in the N2D project."""
    import zipfile

    embed_bytes = 0
    embed_source = ""
    n2d_path = os.path.join(project_dir, "project.n2d")
    if os.path.isfile(n2d_path):
        try:
            import msgpack

            with zipfile.ZipFile(n2d_path) as zf:
                data = msgpack.unpackb(zf.read("project.msgpack"), raw=False)
            for script in data.get("scripts") or []:
                if (script.get("path") or "").replace("\\", "/") == rel_path:
                    embed_source = script.get("source") or ""
                    embed_bytes = len(embed_source.encode("utf-8"))
                    break
        except Exception:
            pass
    disk_path = os.path.join(project_dir, "scripts", rel_path.replace("/", os.sep))
    disk_bytes = 0
    disk_source = ""
    if os.path.isfile(disk_path):
        try:
            with open(disk_path, "r", encoding="utf-8", errors="ignore") as f:
                disk_source = f.read()
            disk_bytes = len(disk_source.encode("utf-8"))
        except OSError:
            pass
    return embed_bytes, disk_bytes


def _main_embed_matches_disk(project_dir: str, rel_path: str) -> bool:
    """True when embedded and on-disk script text match (ignoring CRLF vs LF)."""
    import zipfile

    embed_source = ""
    n2d_path = os.path.join(project_dir, "project.n2d")
    if os.path.isfile(n2d_path):
        try:
            import msgpack

            with zipfile.ZipFile(n2d_path) as zf:
                data = msgpack.unpackb(zf.read("project.msgpack"), raw=False)
            for script in data.get("scripts") or []:
                if (script.get("path") or "").replace("\\", "/") == rel_path:
                    embed_source = script.get("source") or ""
                    break
        except Exception:
            pass
    disk_path = os.path.join(project_dir, "scripts", rel_path.replace("/", os.sep))
    if not embed_source or not os.path.isfile(disk_path):
        return not embed_source and not os.path.isfile(disk_path)
    try:
        with open(disk_path, "r", encoding="utf-8", errors="ignore") as f:
            disk_source = f.read()
    except OSError:
        return False
    norm = lambda s: s.replace("\r\n", "\n")
    return norm(embed_source) == norm(disk_source)


def _is_decompiler_stub_source(source: str, rel_path: str) -> bool:
    """True when decompiled .as is an empty shell (recompile loses methods)."""
    lines = [
        ln
        for ln in source.splitlines()
        if ln.strip() and not ln.strip().startswith("//")
    ]
    if len(lines) <= 12:
        return True
    base = os.path.basename(rel_path)
    class_name = base[:-3] if base.lower().endswith(".as") else base
    if f"function {class_name}" in source:
        return False
    if source.count("function ") <= 1 and "class " in source:
        return True
    return False


def overlay_idk_sources(
    project_dir: str,
    idk_root: str,
    *,
    stubs_only: bool = True,
    force_rel_paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Replace decompiler stub scripts with IDK .as sources when available.

    Full-tree overlay breaks mxmlc (IDK uses SSF2.swc + [Embed] asset paths).
    Default stubs_only=True only patches empty decompiled classes (e.g. Utils).
    """
    idk_root = os.path.normpath(idk_root)
    scripts_dir = os.path.join(project_dir, "scripts")
    if not os.path.isdir(scripts_dir):
        return {"overlaid": 0, "skipped": True, "reason": "no scripts/ folder"}
    if not os.path.isdir(os.path.join(idk_root, "com")):
        return {"overlaid": 0, "skipped": True, "reason": f"no com/ under {idk_root}"}

    force_set = {p.replace("\\", "/") for p in (force_rel_paths or [])}
    # Always patch Utils when stub — fixes Main() Error #1006.
    force_set.add("com/mcleodgaming/ssf2/util/Utils.as")

    overlaid: List[str] = []
    skipped_non_stub = 0
    for root, _dirs, files in os.walk(scripts_dir):
        for fn in files:
            if not fn.lower().endswith(".as"):
                continue
            rel = os.path.relpath(os.path.join(root, fn), scripts_dir).replace("\\", "/")
            dest = os.path.join(scripts_dir, rel)
            idk_path = os.path.join(idk_root, rel)
            if not os.path.isfile(idk_path):
                continue
            if stubs_only and rel not in force_set:
                current = _read_text(dest)
                if not _is_decompiler_stub_source(current, rel):
                    skipped_non_stub += 1
                    continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(idk_path, dest)
            overlaid.append(rel)
    return {
        "overlaid": len(overlaid),
        "files": overlaid[:40],
        "idkRoot": idk_root,
        "stubsOnly": stubs_only,
        "skippedNonStub": skipped_non_stub,
    }


def compare_preflight(og: Dict[str, Any], rt: Dict[str, Any]) -> Dict[str, Any]:
    warnings: List[str] = []
    if og.get("error"):
        warnings.append(f"Original: {og['error']}")
    if rt.get("error"):
        warnings.append(f"Roundtrip: {rt['error']}")
    if og.get("documentClass") and rt.get("documentClass"):
        if og["documentClass"] != rt["documentClass"]:
            warnings.append(
                f"Document class changed: {og['documentClass']!r} -> {rt['documentClass']!r}"
            )
    og_dc = og.get("documentClass") or ""
    if rt.get("documentClass") == "Main" and "mcleodgaming" in og_dc:
        warnings.append(
            "Roundtrip SymbolClass char 0 is 'Main' but original uses package "
            f"{og_dc!r} — likely AIR blank screen"
        )
    og_sz = og.get("size") or 0
    rt_sz = rt.get("size") or 0
    if og_sz and rt_sz:
        pct = abs(rt_sz - og_sz) / og_sz * 100
        if pct > 15:
            warnings.append(f"SWF size delta {pct:.1f}% ({og_sz} -> {rt_sz} bytes)")
    og_abc = og.get("doabc2Count", 0)
    rt_abc = rt.get("doabc2Count", 0)
    if og_abc and rt_abc != og_abc:
        warnings.append(f"DoABC2 tag count: {og_abc} -> {rt_abc}")
    return {"warnings": warnings, "ok": len(warnings) == 0}


def n2d_script_inventory(project_dir: str) -> Dict[str, Dict[str, Any]]:
    """Map script rel-path -> metadata for every .as under project scripts/."""
    scripts_dir = os.path.join(project_dir, "scripts")
    inv: Dict[str, Dict[str, Any]] = {}
    if not os.path.isdir(scripts_dir):
        return inv
    for dirpath, _dn, filenames in os.walk(scripts_dir):
        rel_dir = os.path.relpath(dirpath, scripts_dir)
        for fn in filenames:
            if not fn.endswith(".as"):
                continue
            rel = fn if rel_dir == "." else os.path.join(rel_dir, fn).replace("\\", "/")
            fpath = os.path.join(dirpath, fn)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as sf:
                    src = sf.read()
            except OSError:
                continue
            lines = src.splitlines()
            non_empty = [
                ln for ln in lines if ln.strip() and not ln.strip().startswith("//")
            ]
            inv[rel] = {
                "path": rel,
                "lines": len(lines),
                "nonEmptyLines": len(non_empty),
                "bytes": len(src.encode("utf-8")),
                "functions": src.count("function "),
                "shellRecovered": "@n2f-shell-recovered" in src[:400],
                "referenceCompanion": "@n2f-reference-companion" in src[:400],
            }
    return inv


def swf_abc_class_inventory(swf_path: str) -> Dict[str, Dict[str, Any]]:
    """Map FQCN -> trait metadata from main DoABC block(s)."""
    from as3_decompiler.swf_reader import read_abc_blocks
    from as3_decompiler.abc_parser import ABCFile
    from as3_decompiler.class_decompiler import AS3Decompiler

    inv: Dict[str, Dict[str, Any]] = {}
    if not os.path.isfile(swf_path):
        return inv
    try:
        _, blocks = read_abc_blocks(swf_path)
    except Exception as e:
        log.warning("swf_abc_class_inventory: %s", e)
        return inv
    for _tag_idx, abc_bytes in blocks:
        abc = ABCFile(abc_bytes)
        decomp = AS3Decompiler(abc)
        for cls in decomp.list_classes():
            inv[cls["full_name"]] = {
                "fullName": cls["full_name"],
                "package": cls["package"],
                "name": cls["name"],
                "traitCount": cls["trait_count"],
                "isInterface": cls["is_interface"],
            }
    return inv


_UNQUALIFIED_CALL_RE = re.compile(
    r"(?<![.\w])([A-Z][A-Za-z0-9_]*)\s*\("
)


def _find_unqualified_calls(source: str) -> List[str]:
    """Heuristic: uppercase identifiers called like functions without import."""
    if not source:
        return []
    imported: set = set()
    for m in re.finditer(r"^\s*import\s+([\w.]+)(?:\.\*)?\s*;", source, re.MULTILINE):
        imp = m.group(1)
        imported.add(imp.rsplit(".", 1)[-1])
        imported.add(imp)
    defined_in_file: set = set()
    for m in re.finditer(
        r"^\s*(?:public|private|protected|internal|static)\s+(?:const|var|function)\s+(\w+)",
        source,
        re.MULTILINE,
    ):
        defined_in_file.add(m.group(1))
    for m in re.finditer(r"^\s*function\s+(\w+)\s*\(", source, re.MULTILINE):
        defined_in_file.add(m.group(1))
    skip = {
        "String", "Number", "Boolean", "int", "uint", "Array", "Object",
        "Date", "Math", "Error", "RegExp", "XML", "Vector", "Function",
        "JSON", "isNaN", "parseInt", "parseFloat", "encodeURIComponent",
        "decodeURIComponent", "If", "For", "While", "Switch", "Catch",
        "Return", "Throw", "New", "Delete", "typeof", "trace", "Event",
        "Timer", "Loader", "Bitmap", "Sprite", "MovieClip", "Stage",
    }
    hits: List[str] = []
    for m in _UNQUALIFIED_CALL_RE.finditer(source):
        name = m.group(1)
        if name in skip or name in imported or name in defined_in_file:
            continue
        if name not in hits:
            hits.append(name)
    return hits


def compare_n2d_inventories(
    before: Dict[str, Dict[str, Any]],
    after: Dict[str, Dict[str, Any]],
    *,
    before_label: str = "import1",
    after_label: str = "import2",
    line_regression_ratio: float = 0.5,
) -> Dict[str, Any]:
    """Diff two N2D script inventories (SWF→N2D before vs after recompile re-import)."""
    before_paths = set(before)
    after_paths = set(after)
    missing = sorted(before_paths - after_paths)
    added = sorted(after_paths - before_paths)
    regressions: List[Dict[str, Any]] = []
    for rel in sorted(before_paths & after_paths):
        b = before[rel]
        a = after[rel]
        b_lines = b.get("nonEmptyLines") or 0
        a_lines = a.get("nonEmptyLines") or 0
        if b_lines >= 20 and a_lines < max(12, int(b_lines * line_regression_ratio)):
            regressions.append({
                "path": rel,
                "beforeLines": b_lines,
                "afterLines": a_lines,
                "beforeFunctions": b.get("functions", 0),
                "afterFunctions": a.get("functions", 0),
                "shellRecoveredBefore": b.get("shellRecovered", False),
            })
    return {
        "beforeLabel": before_label,
        "afterLabel": after_label,
        "beforeCount": len(before),
        "afterCount": len(after),
        "missingAfterCompile": missing,
        "addedAfterCompile": added,
        "lineRegressions": regressions,
    }


def compare_abc_inventories(
    before: Dict[str, Dict[str, Any]],
    after: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Diff ABC class inventories between original SWF and roundtrip SWF."""
    before_names = set(before)
    after_names = set(after)
    missing = sorted(before_names - after_names)
    added = sorted(after_names - before_names)
    trait_regressions: List[Dict[str, Any]] = []
    for name in sorted(before_names & after_names):
        bt = before[name].get("traitCount", 0)
        at = after[name].get("traitCount", 0)
        if bt >= 4 and at < max(1, bt // 2):
            trait_regressions.append({
                "fullName": name,
                "beforeTraits": bt,
                "afterTraits": at,
            })
    return {
        "beforeCount": len(before),
        "afterCount": len(after),
        "missingClasses": missing,
        "addedClasses": added,
        "traitRegressions": trait_regressions,
    }


def _inventory_with_calls(project_dir: str) -> Dict[str, Dict[str, Any]]:
    inv = n2d_script_inventory(project_dir)
    scripts_dir = os.path.join(project_dir, "scripts")
    for rel, meta in inv.items():
        fpath = os.path.join(scripts_dir, rel.replace("/", os.sep))
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as sf:
                src = sf.read()
        except OSError:
            src = ""
        meta["unqualifiedCalls"] = _find_unqualified_calls(src)
    return inv


def verify_swf_n2d_swf_n2d(
    project_dir: str,
    roundtrip_swf: str,
    original_swf: str,
    conversion_service,
    get_swf_to_n2d,
    *,
    reimport_name: str = "verify-reimport",
) -> Dict[str, Any]:
    """
    SWF → N2D (project_dir) → SWF (roundtrip_swf) → N2D (reimport) and diff inventories.

    Surfaces scripts/classes/symbols lost during compile — e.g. Logger, shell-recovered
    Utils shrinking back to stubs, ABC trait loss.
    """
    import1 = _inventory_with_calls(project_dir)
    abc_original = swf_abc_class_inventory(original_swf)
    abc_roundtrip = swf_abc_class_inventory(roundtrip_swf)

    reimport_dir = os.path.join(project_dir, reimport_name)
    if os.path.isdir(reimport_dir):
        shutil.rmtree(reimport_dir)

    t0 = time.perf_counter()
    with open(roundtrip_swf, "rb") as f:
        swf_data = f.read()
    n2d_json = conversion_service.convert_swf_to_n2d(
        swf_data,
        name=reimport_name,
        include_scripts=True,
        embed_bitmaps=False,
    )
    get_swf_to_n2d().save_project_folder(n2d_json, reimport_dir)
    reimport_ms = (time.perf_counter() - t0) * 1000

    import2 = _inventory_with_calls(reimport_dir)
    n2d_diff = compare_n2d_inventories(import1, import2)
    abc_diff = compare_abc_inventories(abc_original, abc_roundtrip)

    # Symbols called in import1 but absent from roundtrip ABC and import2 scripts
    script_names = {os.path.splitext(os.path.basename(p))[0] for p in import2}
    class_names = {info["name"] for info in abc_roundtrip.values()}
    runtime_available = script_names | class_names
    missing_runtime: List[Dict[str, str]] = []
    seen_sym: set = set()
    for rel, meta in import1.items():
        for sym in meta.get("unqualifiedCalls") or []:
            if sym in runtime_available or sym in seen_sym:
                continue
            seen_sym.add(sym)
            missing_runtime.append({
                "symbol": sym,
                "referencedFrom": rel,
                "reason": "called in import1 source but missing from roundtrip ABC and re-import scripts",
            })

    warnings: List[str] = []
    for rel in n2d_diff["missingAfterCompile"][:40]:
        warnings.append(f"Script lost after compile: {rel}")
    if len(n2d_diff["missingAfterCompile"]) > 40:
        warnings.append(
            f"... and {len(n2d_diff['missingAfterCompile']) - 40} more missing scripts"
        )
    for reg in n2d_diff["lineRegressions"][:30]:
        warnings.append(
            f"Line regression {reg['path']}: {reg['beforeLines']} → {reg['afterLines']} non-empty lines"
            + (" (was shell-recovered)" if reg.get("shellRecoveredBefore") else "")
        )
    for cls in abc_diff["missingClasses"][:30]:
        warnings.append(f"ABC class missing in roundtrip SWF: {cls}")
    for reg in abc_diff["traitRegressions"][:20]:
        warnings.append(
            f"ABC trait regression {reg['fullName']}: {reg['beforeTraits']} → {reg['afterTraits']} traits"
        )
    for item in missing_runtime[:30]:
        warnings.append(
            f"Unresolved runtime symbol {item['symbol']} (from {item['referencedFrom']}) — "
            "likely compile omission (e.g. Logger.as)"
        )

    report = {
        "ok": len(warnings) == 0,
        "warnings": warnings,
        "reimportDir": reimport_dir,
        "reimportMs": round(reimport_ms),
        "import1Count": len(import1),
        "import2Count": len(import2),
        "n2dDiff": n2d_diff,
        "abcDiff": abc_diff,
        "missingRuntimeSymbols": missing_runtime,
    }

    report_path = os.path.join(project_dir, "roundtrip-verify.json")
    try:
        with open(report_path, "w", encoding="utf-8") as rf:
            json.dump(report, rf, indent=2)
        report["reportPath"] = report_path
    except OSError as e:
        log.warning("verify_swf_n2d_swf_n2d: could not write report: %s", e)

    return report


def format_verify_report_summary(report: Dict[str, Any]) -> str:
    """Human-readable summary for CLI / logs."""
    lines = [
        "Double roundtrip verify (SWF→N2D→SWF→N2D):",
        f"  Import1 scripts: {report.get('import1Count', '?')}",
        f"  Import2 scripts: {report.get('import2Count', '?')} "
        f"(reimport in {report.get('reimportMs', '?')} ms)",
    ]
    n2d = report.get("n2dDiff") or {}
    abc = report.get("abcDiff") or {}
    lines.append(f"  Missing scripts after compile: {len(n2d.get('missingAfterCompile') or [])}")
    lines.append(f"  Line regressions: {len(n2d.get('lineRegressions') or [])}")
    lines.append(f"  ABC classes lost: {len(abc.get('missingClasses') or [])}")
    lines.append(f"  Unresolved runtime symbols: {len(report.get('missingRuntimeSymbols') or [])}")
    for w in (report.get("warnings") or [])[:15]:
        lines.append(f"    - {w}")
    extra = len(report.get("warnings") or []) - 15
    if extra > 0:
        lines.append(f"    ... and {extra} more (see roundtrip-verify.json)")
    return "\n".join(lines)


def backup_file(path: str) -> Optional[str]:
    if not os.path.isfile(path):
        return None
    bak = path + BACKUP_SUFFIX
    shutil.copy2(path, bak)
    return bak


def deploy_swf(swf_path: str, target_dir: str, target_name: str = "SSF2.swf") -> Dict[str, Any]:
    """Copy compiled SWF into target_dir/SSF2.swf with backup."""
    target_dir = os.path.normpath(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    dest = os.path.join(target_dir, target_name)
    bak = backup_file(dest)
    shutil.copy2(swf_path, dest)
    return {
        "deployed": dest,
        "backup": bak,
        "size": os.path.getsize(dest),
    }


def compile_project_to_swf(
    project_dir: str,
    output_path: str,
    server_dir: str,
) -> Dict[str, Any]:
    """Compile project.n2d to output_path using N2DCompiler."""
    import compile_n2d as c2n
    import tempfile

    n2d_path = os.path.join(project_dir, "project.n2d")
    if not os.path.isfile(n2d_path):
        raise FileNotFoundError(f"No project.n2d in {project_dir}")
    shared_dir = os.path.join(server_dir, "..", "shared")
    if not os.path.isdir(shared_dir):
        shared_dir = tempfile.mkdtemp()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    t0 = time.perf_counter()
    compiler = c2n.N2DCompiler(
        n2d_path=n2d_path,
        shared_dir=shared_dir,
        output_path=output_path,
    )
    compiler.compile()
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return {
        "swfPath": output_path,
        "size": os.path.getsize(output_path),
        "compileMs": round(elapsed_ms),
    }


def roundtrip_pipeline(
    server_dir: str,
    source_swf: str,
    project_name: str,
    conversion_service,
    get_swf_to_n2d,
    get_compile_n2d,
    *,
    overwrite_project: bool = True,
    deploy_adl: bool = True,
    deploy_game: bool = True,
    adl_root: str = "",
    game_root: str = "",
    settings: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Import source SWF -> project, compile to SWF, optional deploy, return preflight.
    """
    settings = settings or load_settings(server_dir)
    adl_root = os.path.normpath(adl_root or settings.get("adlRoot") or DEFAULT_ADL_ROOT)
    game_root = os.path.normpath(game_root or settings.get("gameRoot") or DEFAULT_GAME_ROOT)
    source_swf = os.path.normpath(source_swf)
    if not os.path.isfile(source_swf):
        raise FileNotFoundError(f"Source SWF not found: {source_swf}")

    project_dir = os.path.join(server_dir, "converted", project_name)
    if overwrite_project and os.path.isdir(project_dir):
        shutil.rmtree(project_dir)

    t0 = time.perf_counter()
    with open(source_swf, "rb") as f:
        swf_data = f.read()
    from conversion_service import ConversionError

    idk_root = os.path.normpath(
        settings.get("idkSourceRoot") or settings.get("adlRoot") or DEFAULT_ADL_ROOT
    )
    # Point shell-recovery at IDK sources (com/ + Logger.as + fl/) during SWF import.
    prev_ref_roots = os.environ.get("N2F_DECOMPILER_REFERENCE_ROOTS", "")
    if idk_root and os.path.isdir(idk_root):
        os.environ["N2F_DECOMPILER_REFERENCE_ROOTS"] = idk_root

    try:
        n2d_json = conversion_service.convert_swf_to_n2d(
            swf_data,
            name=project_name,
            include_scripts=True,
            embed_bitmaps=True,
        )
    except Exception as e:
        raise RuntimeError(f"SWF import failed: {e}") from e
    finally:
        if prev_ref_roots:
            os.environ["N2F_DECOMPILER_REFERENCE_ROOTS"] = prev_ref_roots
        elif idk_root and os.path.isdir(idk_root):
            os.environ.pop("N2F_DECOMPILER_REFERENCE_ROOTS", None)

    mod = get_swf_to_n2d()
    mod.save_project_folder(n2d_json, project_dir)
    import_ms = (time.perf_counter() - t0) * 1000

    overlay_info: Dict[str, Any] = {"overlaid": 0}
    if settings.get("overlayIdkSources", True):
        idk_root = os.path.normpath(
            settings.get("idkSourceRoot") or settings.get("adlRoot") or DEFAULT_ADL_ROOT
        )
        overlay_info = overlay_idk_sources(
            project_dir,
            idk_root,
            stubs_only=settings.get("overlayIdkStubsOnly", True),
        )

    script_warnings = script_roundtrip_warnings(project_dir)
    boot_fatal = boot_critical_roundtrip_failures(project_dir)

    out_swf = os.path.join(project_dir, "roundtrip.swf")
    compile_info = compile_project_to_swf(project_dir, out_swf, server_dir)

    og_pf = swf_preflight(source_swf, "original")
    rt_pf = swf_preflight(out_swf, "roundtrip")
    cmp_pf = compare_preflight(og_pf, rt_pf)
    if script_warnings:
        cmp_pf = dict(cmp_pf)
        cmp_pf["warnings"] = list(cmp_pf.get("warnings") or []) + script_warnings
        cmp_pf["ok"] = False

    verify_report: Optional[Dict[str, Any]] = None
    if settings.get("doubleRoundtripVerify", True):
        try:
            verify_report = verify_swf_n2d_swf_n2d(
                project_dir,
                out_swf,
                source_swf,
                conversion_service,
                get_swf_to_n2d,
            )
            cmp_pf = dict(cmp_pf)
            cmp_pf["warnings"] = list(cmp_pf.get("warnings") or []) + (
                verify_report.get("warnings") or []
            )
            cmp_pf["ok"] = len(cmp_pf.get("warnings") or []) == 0
            cmp_pf["doubleRoundtripVerify"] = verify_report
        except Exception as e:
            log.exception("double roundtrip verify failed")
            cmp_pf = dict(cmp_pf)
            cmp_pf["warnings"] = list(cmp_pf.get("warnings") or []) + [
                f"Double roundtrip verify failed: {e}"
            ]
            cmp_pf["ok"] = False

    deploys: Dict[str, Any] = {}
    skip_deploy_reason = ""
    if boot_fatal:
        skip_deploy_reason = (
            "boot-critical preflight failures — fix project and re-import before deploy"
        )
        log.warning("Skipping deploy: %s", "; ".join(boot_fatal[:3]))
    if deploy_adl and not skip_deploy_reason:
        deploys["adl"] = deploy_swf(out_swf, adl_root)
    if deploy_game and not skip_deploy_reason:
        deploys["game"] = deploy_swf(out_swf, game_root)
    if skip_deploy_reason:
        deploys["skipped"] = {"reason": skip_deploy_reason, "failures": boot_fatal}

    import hashlib

    def _sha256(path: str) -> str:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    built_hash = _sha256(out_swf)
    for key, info in deploys.items():
        if key == "skipped" or not isinstance(info, dict):
            continue
        dest = info.get("deployed")
        if dest and os.path.isfile(dest):
            info["sha256"] = _sha256(dest)
            info["matchesRoundtrip"] = info["sha256"] == built_hash
            if not info["matchesRoundtrip"]:
                log.warning(
                    "deploy %s: %s does not match roundtrip.swf — restart ADL after deploy",
                    key,
                    dest,
                )

    adl_info = resolve_adl_launch(
        adl_root,
        settings.get("airSdk") or find_air_sdk() or "",
        settings.get("adlExtDir"),
    )

    return {
        "ok": True,
        "sourceSwf": source_swf,
        "projectDir": project_dir,
        "roundtripSwf": out_swf,
        "importMs": round(import_ms),
        "idkOverlay": overlay_info,
        "compile": compile_info,
        "preflight": {"original": og_pf, "roundtrip": rt_pf, "compare": cmp_pf},
        "doubleRoundtripVerify": verify_report,
        "deploys": deploys,
        "bootFatal": boot_fatal,
        "adlLaunch": adl_info,
    }


def launch_adl_cli(
    adl_root: str,
    air_sdk: Optional[str] = None,
    ext_rel: Optional[str] = None,
    *,
    probe_seconds: float = 15.0,
    keep_running: bool = True,
    on_output: Optional[Any] = None,
    success_quiet_seconds: float = 8.0,
) -> Dict[str, Any]:
    """
    Launch ADL, stream stderr/stdout + ssf2_debug.log in real time, detect fatal
    runtime errors, and optionally terminate ADL on failure.
    """
    import subprocess
    import threading

    def _emit(line: str, stream: str = "stderr") -> None:
        line = line.rstrip()
        if not line:
            return
        if on_output:
            on_output(line, stream)
        else:
            prefix = "[ADL stderr] " if stream == "stderr" else "[ADL stdout] "
            print(prefix + line, flush=True)

    adl_root = os.path.normpath(adl_root)
    sdk = air_sdk or find_air_sdk() or ""
    launch = resolve_adl_launch(adl_root, sdk, ext_rel)
    if not launch.get("ok"):
        return {"ok": False, "error": "; ".join(launch.get("issues") or []), "launch": launch}

    ext = resolve_adl_ext_dir(adl_root, ext_rel)
    adl_exe = launch["adlExe"]
    cmd = [adl_exe, "-extdir", ext["abs"], "SSF2-app.xml"]
    log_path = os.path.join(adl_root, "ssf2_debug.log")
    log.info("launch_adl_cli: %s (cwd=%s)", cmd, adl_root)

    if os.name == "nt":
        for image in ("Super Smash Flash 2 Beta.exe", "adl.exe"):
            try:
                subprocess.run(
                    ["taskkill", "/IM", image, "/F"],
                    capture_output=True,
                    timeout=10,
                )
            except Exception:
                pass

    proc = subprocess.Popen(
        cmd,
        cwd=adl_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stderr_lines: List[str] = []
    stdout_lines: List[str] = []
    fatal_errors: List[str] = []
    success_signals: List[str] = []
    lock = threading.Lock()

    def _record(line: str, stream: str) -> None:
        with lock:
            if stream == "stderr":
                stderr_lines.append(line)
            else:
                stdout_lines.append(line)
            if ADL_FATAL_RE.search(line):
                fatal_errors.append(line)
            if ADL_SUCCESS_RE.search(line):
                success_signals.append(line)
        _emit(line, stream)

    def _pump(stream, name: str) -> None:
        try:
            for raw in iter(stream.readline, b""):
                _record(raw.decode("utf-8", errors="replace"), name)
        except Exception:
            pass

    threading.Thread(target=_pump, args=(proc.stdout, "stdout"), daemon=True).start()
    threading.Thread(target=_pump, args=(proc.stderr, "stderr"), daemon=True).start()

    log_offset = 0
    if os.path.isfile(log_path):
        try:
            log_offset = os.path.getsize(log_path)
        except OSError:
            log_offset = 0

    deadline = time.time() + probe_seconds
    last_fatal_time = 0.0
    while time.time() < deadline:
        rc = proc.poll()
        if rc is not None:
            break
        # Tail ssf2_debug.log
        if os.path.isfile(log_path):
            try:
                st = os.stat(log_path)
                if st.st_size > log_offset:
                    with open(log_path, "r", encoding="utf-8", errors="replace") as lf:
                        lf.seek(log_offset)
                        chunk = lf.read()
                    log_offset = st.st_size
                    for line in chunk.splitlines():
                        _record(line, "log")
            except OSError:
                pass
        with lock:
            if fatal_errors:
                last_fatal_time = time.time()
                break
            if success_signals and (time.time() + success_quiet_seconds <= deadline):
                # Saw boot signal — extend probe slightly for stability
                deadline = max(deadline, time.time() + success_quiet_seconds)
        time.sleep(0.25)

    rc = proc.poll()
    terminated = False
    with lock:
        had_fatal = bool(fatal_errors)

    if had_fatal and rc is None:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        terminated = True
        rc = proc.poll()

    if not keep_running and rc is None:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            pass
        terminated = True
        rc = proc.poll()

    running = rc is None
    stderr_text = "\n".join(stderr_lines).strip()
    ok = running and not had_fatal
    if rc == 0 and not had_fatal:
        ok = True
    if had_fatal:
        ok = False

    return {
        "ok": ok,
        "running": running,
        "exitCode": rc,
        "pid": proc.pid,
        "stderr": stderr_text,
        "stdout": "\n".join(stdout_lines).strip(),
        "fatalErrors": fatal_errors,
        "successSignals": success_signals,
        "logPath": log_path,
        "command": cmd,
        "adlRoot": adl_root,
        "adlExtDir": ext["rel"],
        "terminated": terminated,
        "error": fatal_errors[0] if fatal_errors else (
            f"ADL exited with code {rc}" if rc not in (None, 0) else ""
        ),
    }


def run_roundtrip_adl_attempt(
    server_dir: str,
    source_swf: str,
    project_name: str,
    conversion_service,
    get_swf_to_n2d,
    get_compile_n2d,
    settings: Dict[str, Any],
    *,
    overwrite_project: bool = True,
    adl_probe_seconds: float = 30.0,
    keep_adl_running: bool = False,
) -> Dict[str, Any]:
    """Single roundtrip + verify + ADL probe; terminates ADL on runtime error."""
    adl_root = settings.get("adlRoot") or DEFAULT_ADL_ROOT
    result = roundtrip_pipeline(
        server_dir,
        source_swf,
        project_name,
        conversion_service,
        get_swf_to_n2d,
        get_compile_n2d,
        overwrite_project=overwrite_project,
        deploy_adl=True,
        deploy_game=False,
        adl_root=adl_root,
        game_root=settings.get("gameRoot") or "",
        settings=settings,
    )
    verify = result.get("doubleRoundtripVerify") or {}
    verify_ok = verify.get("ok", True)
    adl_res = launch_adl_cli(
        adl_root,
        settings.get("airSdk"),
        settings.get("adlExtDir"),
        probe_seconds=adl_probe_seconds,
        keep_running=keep_adl_running,
    )
    result["adl"] = adl_res
    result["verifyOk"] = verify_ok
    result["launchOk"] = bool(adl_res.get("ok")) and verify_ok
    return result
