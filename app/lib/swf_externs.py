"""SWCs for the other SWFs a file was linked against.

A decompile writes these once, under the output folder's externs directory.
A later decompile leaves them in place. Nothing here names a particular game file.
"""

from __future__ import annotations

import logging
import os
import subprocess
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

log = logging.getLogger("next2flash")

_SKIP_PREFIXES = ("flash.", "flashx.", "mx.", "spark.", "avmplus.", "avm2.", "__AS3__.")
_QNAME = (0x07, 0x0D)
_PACKAGE_NS = (0x08, 0x16)


def def_id(full_name: str) -> str:
    """com.foo.Bar -> com.foo:Bar. A default-package name stays as it is."""
    package, dot, name = full_name.rpartition(".")
    if not dot:
        return full_name
    return package + ":" + name


def usable_class(full_name: str) -> bool:
    if not full_name or full_name in {"*", "?", "void"}:
        return False
    if any(ch in full_name for ch in "<> \t"):
        return False
    return not full_name.startswith(_SKIP_PREFIXES)


def swc_bytes(
    library_swf: bytes,
    class_names: list[str] | None = None,
    script_name: str = "frame1",
    scripts: list[tuple[str, list[str]]] | None = None,
) -> bytes:
    """A SWC is a zip of the SWF plus a catalog of its classes.

    Each catalog script uses the DoABC name from the SWF. The compiler
    looks classes up by that name.
    """
    if scripts is None:
        scripts = [(script_name, list(class_names or []))]
    parts = []
    for name, classes in scripts:
        defs = "".join(f'<def id="{escape(def_id(cls))}"/>' for cls in classes)
        parts.append(
            f'<script name="{escape(name)}" mod="0" signatureChecksum="0">'
            f"{defs}<dep id=\"AS3\" type=\"s\"/></script>"
        )
    catalog = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<swc xmlns="http://www.adobe.com/flash/swccatalog/9">'
        "<versions><swc version=\"1.2\"/></versions>"
        "<features><feature-script-deps/></features>"
        "<libraries><library path=\"library.swf\">"
        + "".join(parts)
        + "</library></libraries></swc>"
    )
    import io

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("catalog.xml", catalog)
        zf.writestr("library.swf", library_swf)
    return buf.getvalue()


def link_report_xml(libraries: list[tuple[str, list[str]]]) -> str:
    """mxmlc load-externs report. Each entry is (swc file name, class names)."""
    parts = ["<report><scripts>"]
    for swc_name, class_names in libraries:
        for full_name in class_names:
            ident = def_id(full_name)
            parts.append(
                f'<script name="{escape(swc_name)}({escape(ident)})" mod="0" size="0">'
                f"<def id=\"{escape(ident)}\"/>"
                f"<dep id=\"AS3\"/>"
                f"</script>"
            )
    parts.append("</scripts></report>")
    return "".join(parts)


def _classes_in_swf(swf_path: Path) -> tuple[set[str], set[str], list[tuple[str, list[str]]]]:
    from as3_decompiler.abc_parser import ABCFile
    from as3_decompiler.swf_patcher import _extract_abc_data_from_tag
    from as3_decompiler.swf_reader import read_swf

    _, tags = read_swf(str(swf_path))
    defined: set[str] = set()
    referenced: set[str] = set()
    scripts: list[tuple[str, list[str]]] = []
    for tag_type, body in tags:
        if tag_type not in (72, 82):
            continue
        abc_name, abc_bytes = _extract_abc_data_from_tag(tag_type, body)
        abc = ABCFile(abc_bytes)
        classes: list[str] = []
        for inst in abc.instances:
            full = abc.mn_full(inst.name_idx)
            if usable_class(full):
                defined.add(full)
                classes.append(full)
        scripts.append((abc_name, classes))
        for idx in range(1, len(abc.multinames)):
            kind, data = abc.multinames[idx]
            if kind not in _QNAME or not data:
                continue
            if abc.ns_kind(data[0]) not in _PACKAGE_NS:
                continue
            full = abc.mn_full(idx)
            if usable_class(full):
                referenced.add(full)
    return defined, referenced, scripts


def _candidate_swfs(swf_path: Path) -> list[Path]:
    """SWFs in this folder and each parent folder. Subfolders are not searched."""
    found: list[Path] = []
    seen: set[str] = set()
    target = str(swf_path.resolve()).lower()
    directory = swf_path.parent
    for _ in range(8):
        if not directory.exists():
            break
        for path in sorted(directory.glob("*.swf")):
            key = str(path.resolve()).lower()
            if key == target or key in seen:
                continue
            seen.add(key)
            found.append(path)
        parent = directory.parent
        if parent == directory:
            break
        directory = parent
    return found


def compile_sources_to_swc(scripts_root: Path, output: Path) -> int:
    """Build a compiler SWC with compc. airglobal is appended so playerglobal stays on the path."""
    from toolchain_home import aflex_lite_dir, java_exe

    sdk = aflex_lite_dir()
    java = java_exe()
    if not sdk or not java:
        log.info("[decompile] compc=missing")
        return 1
    jar = os.path.join(sdk, "lib", "compc.jar")
    if not os.path.isfile(jar):
        log.info("[decompile] compc=missing jar=%s", jar)
        return 1
    air = os.path.join(sdk, "frameworks", "libs", "air", "airglobal.swc")
    args = [
        "-source-path", str(scripts_root),
        "-include-sources", str(scripts_root),
        "-output", str(output),
        "-target-player", "32.0",
        "-strict=false",
        "-warnings=false",
    ]
    if os.path.isfile(air):
        args.append("-external-library-path+=" + air)
    env = os.environ.copy()
    env["FLEX_HOME"] = sdk
    completed = subprocess.run(
        [
            java,
            "-Xmx384m",
            "-Dsun.io.useCanonCaches=false",
            "-Djava.util.Arrays.useLegacyMergeSort=true",
            "-jar",
            jar,
            "+flexlib=" + os.path.join(sdk, "frameworks"),
            *args,
        ],
        cwd=sdk,
        env=env,
        capture_output=True,
        text=True,
        errors="replace",
    )
    if completed.returncode != 0 or not output.is_file():
        line = ""
        for raw in (completed.stdout + "\n" + completed.stderr).splitlines():
            if "Error:" in raw:
                line = raw.strip()
                break
        log.info("[decompile] compc=fail code=%s error=%s", completed.returncode, line)
        print(f"[decompile] compc=fail code={completed.returncode} error={line}", flush=True)
        return int(completed.returncode or 1)
    return 0


def compiler_swc(swf_path: Path) -> bytes | None:
    """Decompile one SWF and compile its scripts into a SWC mxmlc can read."""
    import shutil
    import tempfile

    from script_export import export_script_files, prepare_compiler_sources

    tmp = Path(tempfile.mkdtemp(prefix="n2f-extern-src-"))
    try:
        if export_script_files(str(swf_path), str(tmp)) != 0:
            log.info("[decompile] extern skip=%s reason=export", swf_path.name)
            return None
        scripts = tmp / "scripts" if (tmp / "scripts").is_dir() else tmp
        prepare_compiler_sources(scripts)
        out = tmp / "library.swc"
        if compile_sources_to_swc(scripts, out) != 0 or not out.is_file():
            return None
        data = out.read_bytes()
        log.info("[decompile] extern swc=%s bytes=%s", swf_path.stem + ".swc", len(data))
        return data
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def write_externs(swf_path: str, out_dir: str) -> int:
    """Write one SWC per linked SWF and one link report. Returns how many SWCs.

    If out/externs/link-report.xml is already there, this does nothing.
    """
    dest = Path(out_dir) / "externs"
    report = dest / "link-report.xml"
    if report.is_file() and any(dest.glob("*.swc")):
        log.info("[decompile] externs=kept dir=%s", dest)
        return 0

    swf = Path(swf_path)
    try:
        defined, referenced, _ = _classes_in_swf(swf)
    except Exception as exc:
        log.info("[decompile] externs=0 reason=%s", exc)
        return 0
    needed = referenced - defined
    libraries: list[tuple[str, list[str], bytes]] = []
    for candidate in _candidate_swfs(swf):
        try:
            theirs, _, _ = _classes_in_swf(candidate)
        except Exception as exc:
            log.info("[decompile] externs skip=%s reason=%s", candidate.name, exc)
            continue
        if not (theirs & needed):
            continue
        blob = compiler_swc(candidate)
        if not blob:
            log.info("[decompile] externs skip=%s reason=compc", candidate.name)
            continue
        libraries.append((candidate.stem + ".swc", sorted(theirs), blob))

    if not libraries:
        log.info("[decompile] externs=0")
        return 0

    dest.mkdir(parents=True, exist_ok=True)
    for swc_name, _names, blob in libraries:
        (dest / swc_name).write_bytes(blob)
    report.write_text(
        link_report_xml([(name, names) for name, names, _ in libraries]),
        encoding="utf-8",
    )
    written = ",".join(name for name, _, _ in libraries)
    log.info("[decompile] externs=%s files=%s", len(libraries), written)
    print(f"[decompile] externs={len(libraries)} files={written}", flush=True)
    return len(libraries)
