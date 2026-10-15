"""Export a SWF's scripts through FFDec and rewrite them so mxmlc accepts them.

The SWF path is an argument. Nothing in here names a particular game file.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger("next2flash")

FLASH_UTILS_TYPES = (
    "ByteArray", "Timer", "Endian", "Proxy", "IDataInput", "IDataOutput",
    "IExternalizable", "CompressionAlgorithm", "Dictionary",
)
FLASH_UTILS_FUNCS = (
    "getTimer", "getDefinitionByName", "getQualifiedClassName",
    "getQualifiedSuperclassName", "describeType", "setTimeout", "clearTimeout",
    "setInterval", "clearInterval", "escapeMultiByte", "unescapeMultiByte",
    "getAliasName",
)

RE_WHILE_TRUE = re.compile(r"while\s*\(\s*true\s*\)")
RE_OR_EQ = re.compile(r"^(\s*)([^/\n]*?)\|\|=", re.M)
RE_INDEX = re.compile(r"(?<![\w.])((?:this\.)?[A-Za-z_][\w.]*)\[([A-Za-z_]\w*)\]")
RE_EMBED = re.compile(r"""\[Embed\s*\(\s*source\s*=\s*(['"])([^'"]+)\1""", re.I)
RE_IMPORT_UTILS_STAR = re.compile(r"^(\s*)import\s+flash\.utils\.\*\s*;\s*$", re.M)
RE_NEW_FLASH_DICT = re.compile(r"\bnew\s+Dictionary\s*\(\s*(true|false)\s*\)")
RE_NEW_EMPTY_DICT = re.compile(r"\bnew\s+Dictionary\s*\(\s*\)")
RE_AS_DICT = re.compile(r"\bas\s+Dictionary\b")
RE_IMPORT_FLASH_DICT = re.compile(r"^[ \t]*import flash\.utils\.Dictionary;\r?\n", re.M)
RE_STAR_IMPORT = re.compile(r"import\s+(?!flash\.utils\b)[\w.]+\.\*\s*;")
RE_IMPORT_CUSTOM_UTIL_DICT = re.compile(r"import\s+(?!flash\.)[\w.]+\.util\.Dictionary\s*;")
# Some projects store SWF payloads under another file extension.
SWF_ALIAS_EXTENSIONS = (".ssf",)


def find_scripts_root(export_dir: Path) -> Path:
    if (export_dir / "com").is_dir():
        return export_dir
    nested = [p for p in export_dir.rglob("com") if p.is_dir() and p.name == "com"]
    nested.sort(key=lambda p: (0 if "scripts" in p.parts else 1, len(p.parts)))
    if not nested:
        raise FileNotFoundError(f"No com/ package under {export_dir}")
    return nested[0].parent


def skip_string_comment(text: str, i: int) -> int | None:
    n = len(text)
    c = text[i]
    if c == "/" and i + 1 < n:
        nxt = text[i + 1]
        if nxt == "/":
            j = text.find("\n", i + 2)
            return n if j < 0 else j + 1
        if nxt == "*":
            j = text.find("*/", i + 2)
            return n if j < 0 else j + 2
    if c in "'\"":
        quote = c
        j = i + 1
        while j < n:
            if text[j] == "\\":
                j += 2
                continue
            if text[j] == quote:
                return j + 1
            j += 1
        return n
    return None


def matching_brace(text: str, open_idx: int) -> int:
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        skipped = skip_string_comment(text, i)
        if skipped is not None:
            i = skipped
            continue
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"unbalanced brace at {open_idx}")


def code_without_strings(text: str) -> str:
    out = list(text)
    i = 0
    n = len(text)
    while i < n:
        skipped = skip_string_comment(text, i)
        if skipped is not None:
            for k in range(i, skipped):
                out[k] = "\n" if text[k] == "\n" else " "
            i = skipped
            continue
        i += 1
    return "".join(out)


def fix_or_assign(text: str) -> tuple[str, int]:
    count = 0
    lines = text.splitlines(keepends=True)
    out = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("//") or "||=" not in line or "||=" not in code_without_strings(line):
            out.append(line)
            continue
        match = RE_OR_EQ.search(line)
        if not match:
            out.append(line)
            continue
        indent, lhs = match.group(1), match.group(2).rstrip()
        line = line[: match.start()] + f"{indent}{lhs} = {lhs} ||" + line[match.end() :]
        count += 1
        out.append(line)
    return "".join(out), count


def fix_flash_utils_star(text: str) -> tuple[str, int]:
    match = RE_IMPORT_UTILS_STAR.search(text)
    if not match:
        return text, 0
    indent = match.group(1)
    masked = RE_IMPORT_UTILS_STAR.sub("", code_without_strings(text))
    names = [name for name in FLASH_UTILS_TYPES + FLASH_UTILS_FUNCS if re.search(rf"\b{name}\b", masked)]
    replacement = "".join(f"{indent}import flash.utils.{name};\n" for name in names)
    text = RE_IMPORT_UTILS_STAR.sub(replacement, text, count=1)
    package = ""
    pkg = re.search(r"package\s+([\w.]+)", text)
    if pkg:
        package = pkg.group(1)
    collide = package.endswith(".util") or RE_IMPORT_CUSTOM_UTIL_DICT.search(text) is not None
    if collide:
        text = RE_NEW_FLASH_DICT.sub(r"new flash.utils.Dictionary(\1)", text)
        text = RE_NEW_EMPTY_DICT.sub("new flash.utils.Dictionary()", text)
        if "flash.utils.Dictionary" in text:
            text = RE_AS_DICT.sub("as flash.utils.Dictionary", text)
    return text, 1


def fix_dictionary_clash(text: str) -> tuple[str, int]:
    """Drop import flash.utils.Dictionary when a star import also defines Dictionary.

    mxmlc then reports both classes for an unqualified Dictionary. Flash
    constructions stay qualified. A custom Dictionary(SomeClass) keeps the short name.
    """
    if not RE_IMPORT_FLASH_DICT.search(text) or not RE_STAR_IMPORT.search(text):
        return text, 0
    text = RE_NEW_FLASH_DICT.sub(r"new flash.utils.Dictionary(\1)", text)
    text = RE_NEW_EMPTY_DICT.sub("new flash.utils.Dictionary()", text)
    text = RE_AS_DICT.sub("as flash.utils.Dictionary", text)
    text = RE_IMPORT_FLASH_DICT.sub("", text, count=1)
    return text, 1


def first_unsafe_index(body: str) -> tuple[str, str] | None:
    masked = code_without_strings(body)
    increments = set(re.findall(
        r"\b([A-Za-z_]\w*)\s*(?:\+\+|\+=\s*1)|(?:\+\+)\s*([A-Za-z_]\w*)",
        masked,
    ))
    inc_names = {a or b for a, b in increments}
    if not inc_names:
        return None
    for match in RE_INDEX.finditer(masked):
        arr, idx = match.group(1), match.group(2)
        if idx not in inc_names:
            continue
        prefix = masked[: match.start()]
        bound = re.compile(
            rf"{re.escape(idx)}\s*(?:<|>=)\s*{re.escape(arr)}\.length|"
            rf"{re.escape(arr)}\.length\s*(?:>|<=)\s*{re.escape(idx)}"
        )
        if bound.search(prefix):
            continue
        return arr, idx
    return None


def fix_while_true_bounds(text: str) -> tuple[str, int]:
    edits = []
    for match in RE_WHILE_TRUE.finditer(text):
        i = match.end()
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text) or text[i] != "{":
            continue
        try:
            close = matching_brace(text, i)
        except ValueError:
            continue
        body = text[i + 1 : close]
        hit = first_unsafe_index(body)
        if not hit:
            continue
        arr, idx = hit
        if re.search(rf"if\s*\(\s*{re.escape(idx)}\s*>=\s*{re.escape(arr)}\.length\s*\)", body[:200]):
            continue
        nl = body.find("\n")
        indent = "         "
        if nl >= 0:
            rest = body[nl + 1 :]
            indent = rest[: len(rest) - len(rest.lstrip(" \t"))] or indent
        guard = (
            f"\n{indent}if({idx} >= {arr}.length)\n{indent}{{\n"
            f"{indent}   break;\n{indent}}}\n"
        )
        edits.append((i + 1, guard))
    if not edits:
        return text, 0
    out = text
    for pos, guard in reversed(edits):
        out = out[:pos] + guard + out[pos:]
    return out, len(edits)


def fix_embed_swf_alias_names(text: str) -> tuple[str, int]:
    count = 0

    def repl(match: re.Match) -> str:
        nonlocal count
        quote, src = match.group(1), match.group(2)
        if src.lower().endswith(SWF_ALIAS_EXTENSIONS):
            count += 1
            src = src[:-4] + ".swf"
        return f"[Embed(source={quote}{src}{quote}"

    return RE_EMBED.sub(repl, text), count


def fix_embeds(export_dir: Path, scripts_root: Path) -> int:
    names = []
    for path in scripts_root.rglob("*.as"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in RE_EMBED.finditer(text):
            names.append(match.group(2).replace("\\", "/").rsplit("/", 1)[-1])
    if not names:
        return 0
    assets = scripts_root / "_assets"
    assets.mkdir(exist_ok=True)
    bins = []
    seen = set()
    for root in (export_dir, scripts_root, scripts_root.parent):
        if not root.exists():
            continue
        for path in root.rglob("*.bin"):
            key = path.resolve()
            if key in seen:
                continue
            seen.add(key)
            bins.append(path)
    by_name = {path.name: path for path in bins}
    copied = 0
    for name in names:
        dest = assets / name
        src = by_name.get(name)
        if src is None:
            for cand in bins:
                if cand.name.endswith(name) or name.endswith(cand.name):
                    src = cand
                    break
        if src is None or dest.resolve() == src.resolve():
            continue
        shutil.copy2(src, dest)
        copied += 1
    return copied


def ensure_flash_dictionary_import(text: str) -> str:
    """Add import flash.utils.Dictionary when the file uses the type and does not import it."""
    if re.search(r"\bclass\s+Dictionary\b", text) or not re.search(r"\bDictionary\b", text):
        return text
    if RE_IMPORT_FLASH_DICT.search(text) or RE_IMPORT_UTILS_STAR.search(text):
        return text
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if re.match(r"\s*import ", line):
            indent = re.match(r"\s*", line).group(0) or "   "
            lines.insert(i, f"{indent}import flash.utils.Dictionary;\n")
            return "".join(lines)
    return re.sub(
        r"(package[^{]*\{\s*\n)",
        r"\1   import flash.utils.Dictionary;\n",
        text,
        count=1,
    )


def strip_embed_metadata(text: str) -> str:
    """Drop [Embed] lines. The exported asset SWF is often missing, and an extern library does not need the art."""
    return "".join(line for line in text.splitlines(keepends=True) if "[Embed(" not in line)


def prepare_compiler_sources(scripts_root: str | Path) -> int:
    """Rewrite decompiled scripts so compc can build an extern SWC. Returns how many files changed."""
    root = Path(scripts_root)
    changed = 0
    for path in root.rglob("*.as"):
        original = path.read_text(encoding="utf-8", errors="replace")
        text = ensure_flash_dictionary_import(strip_embed_metadata(original))
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed += 1
    log.info("[decompile] compiler-sources dir=%s changed=%s", root, changed)
    return changed


def apply_mxmlc_fixes(export_dir: str | Path) -> int:
    """Rewrite exported .as files. Returns how many files changed."""
    root = Path(export_dir)
    scripts_root = find_scripts_root(root)
    changed = 0
    for path in scripts_root.rglob("*.as"):
        original = path.read_text(encoding="utf-8", errors="replace")
        text = original
        text, _ = fix_flash_utils_star(text)
        text, _ = fix_dictionary_clash(text)
        text, _ = fix_or_assign(text)
        text, _ = fix_while_true_bounds(text)
        text, _ = fix_embed_swf_alias_names(text)
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed += 1
    copied = fix_embeds(root, scripts_root)
    log.info(
        "[decompile] dir=%s files=%s embeds=%s",
        scripts_root,
        changed,
        copied,
    )
    return changed


def export_script_files(swf_path: str, out_dir: str) -> int:
    """FFDec script+binaryData export, then the mxmlc cleanup. Does not write externs."""
    from toolchain_home import ffdec_jar, java_exe

    java = java_exe()
    jar = ffdec_jar()
    if not java or not jar:
        print("FFDec toolchain is missing.", flush=True)
        return 1
    if not os.path.isfile(swf_path):
        print(f"SWF not found: {swf_path}", flush=True)
        return 1
    dest = Path(out_dir)
    dest.mkdir(parents=True, exist_ok=True)
    log.info("[decompile] input=%s wrote=%s", os.path.basename(swf_path), dest)
    completed = subprocess.run(
        [
            java,
            "-Xmx4096m",
            "-Djava.awt.headless=true",
            "-jar",
            jar,
            "-config",
            "autoDeobfuscate=0,parallelSpeedUp=1",
            "-export",
            "script,binaryData",
            str(dest),
            os.path.abspath(swf_path),
        ],
        cwd=os.path.dirname(jar),
    )
    code = int(completed.returncode or 0)
    if code != 0:
        return code
    try:
        apply_mxmlc_fixes(dest)
    except FileNotFoundError as exc:
        print(str(exc), flush=True)
        return 1
    return 0


def export_scripts(swf_path: str, out_dir: str) -> int:
    """FFDec script+binaryData export, then the mxmlc cleanup and extern SWCs."""
    from toolchain_home import ffdec_jar, java_exe

    if not java_exe() or not ffdec_jar():
        print("FFDec toolchain is missing.", flush=True)
        return 1
    if not os.path.isfile(swf_path):
        print(f"SWF not found: {swf_path}", flush=True)
        return 1
    dest = Path(out_dir)
    dest.mkdir(parents=True, exist_ok=True)
    held = hold_externs(dest)
    code = export_script_files(swf_path, str(dest))
    if code != 0:
        restore_externs(dest, held)
        return code
    restore_externs(dest, held)
    from swf_externs import write_externs

    write_externs(swf_path, str(dest))
    return 0


def hold_externs(dest: Path) -> Path | None:
    """Move out/externs aside. FFDec export clears the output folder."""
    externs = dest / "externs"
    if not externs.is_dir():
        return None
    import tempfile

    held = Path(tempfile.mkdtemp(prefix="n2f-externs-"))
    shutil.move(str(externs), str(held / "externs"))
    return held


def restore_externs(dest: Path, held: Path | None) -> None:
    if held is None:
        return
    externs = dest / "externs"
    if externs.exists():
        shutil.rmtree(externs)
    shutil.move(str(held / "externs"), str(externs))
    held.rmdir()
