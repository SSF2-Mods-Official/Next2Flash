"""Recover decompiler output for ABC shell classes (0 traits, empty cinit).

Some shipped SWFs (including SSF2) contain class stubs whose methods were
stripped or never emitted as traits.  We recover editable source by:

1. Scanning call sites (getlex Class + callprop*) for required method names.
2. Loading a matching .as from reference source roots when the on-disk file
   is a complete implementation (not another stub).
"""

from __future__ import annotations

import logging
import os
import re
from typing import Dict, List, Optional, Set

log = logging.getLogger(__name__)

from .method_decompiler import _ru30, _skip_operands
from .opcodes import OP_CALLPROPVOID, OP_CALLPROPERTY, OP_GETLEX

_CLASS_DECL_RE = re.compile(r"\bclass\s+(\w+)")
_FUNC_DECL_RE = re.compile(r"\bfunction\s+(\w+)")


def is_shell_class(abc, class_idx: int) -> bool:
    inst = abc.instances[class_idx]
    cls = abc.classes[class_idx]
    if inst.traits or cls.traits:
        return False
    cinit = abc.method_bodies.get(cls.cinit)
    iinit = abc.method_bodies.get(inst.iinit)
    cinit_len = len(cinit.code) if cinit else 0
    iinit_len = len(iinit.code) if iinit else 0
    return cinit_len <= 6 and iinit_len <= 12


def find_called_methods(abc, class_name: str, package: str = "") -> Set[str]:
    """Methods invoked as ClassName.method(...) or getlex Class; callprop method."""
    full = f"{package}.{class_name}" if package else class_name
    names: Set[str] = set()
    pending = False
    for body in abc.method_bodies.values():
        code = body.code
        p = 0
        while p < len(code):
            op = code[p]
            p += 1
            if op == OP_GETLEX:
                idx, p = _ru30(code, p)
                mn = abc.mn_name(idx)
                mn_full = abc.mn_full(idx)
                pending = mn == class_name or mn_full == full
            elif pending and op in (OP_CALLPROPVOID, OP_CALLPROPERTY):
                idx, p = _ru30(code, p)
                _argc, p = _ru30(code, p)
                names.add(abc.mn_name(idx))
                pending = False
            else:
                p = _skip_operands(op, code, p)
    return names


def _reference_roots() -> List[str]:
    roots: List[str] = []
    env = os.environ.get("N2F_DECOMPILER_REFERENCE_ROOTS", "")
    if env:
        roots.extend(p.strip() for p in env.split(os.pathsep) if p.strip())
    default = (
        r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1"
    )
    if os.path.isdir(default):
        roots.append(default)
    return roots


def _is_substantial_source(source: str, class_name: str) -> bool:
    lines = [
        ln
        for ln in source.splitlines()
        if ln.strip() and not ln.strip().startswith("//")
    ]
    if len(lines) <= 12:
        return False
    if f"function {class_name}" not in source and source.count("function ") <= 1:
        return False
    return True


def load_reference_class_source(package: str, class_name: str) -> Optional[str]:
    rel = os.path.join(*package.split("."), f"{class_name}.as") if package else f"{class_name}.as"
    for root in _reference_roots():
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
        except OSError:
            continue
        if _is_substantial_source(source, class_name):
            log.info("shell_recovery: loaded reference %s from %s", rel, path)
            marker = "// @n2f-shell-recovered\n"
            if not source.lstrip().startswith("// @n2f-shell-recovered"):
                source = marker + source
            return source
    return None


def embed_metadata_for_asset_class(class_name: str, package: str) -> Optional[str]:
    """Infer [Embed] for Flex ByteArrayAsset helper classes (SSF2 pattern)."""
    asset_map: Dict[str, str] = {
        "ProfanityFilter_wordfilter": "/ProfanityFilter_wordfilter.json",
        "ResourceManager_manifestJSON": "/ResourceManager_manifestJSON.json",
        "CountryRegionData_countryRegionDataJSON": "/CountryRegionData_countryRegionDataJSON.json",
    }
    rel = asset_map.get(class_name)
    if not rel:
        return None
    return (
        f'    [Embed(source="{rel}", mimeType="application/octet-stream")]\n'
    )


def recover_class_source(abc, class_idx: int, class_name: str, package: str) -> Optional[str]:
    if not is_shell_class(abc, class_idx):
        return None
    ref = load_reference_class_source(package, class_name)
    if ref:
        return ref
    called = find_called_methods(abc, class_name, package)
    if not called:
        return None
    log.warning(
        "shell_recovery: %s.%s is a shell (calls: %s) but no reference source found",
        package,
        class_name,
        ", ".join(sorted(called)[:8]),
    )
    return None
