"""Normalize decompiler output before it is stored in N2D or compiled."""

from __future__ import annotations

import re
from typing import List, Set

from .helpers import _IMPORT_FQN_CORRECTIONS
from .method_decompiler import _strip_activation_artifacts

_ACTIVATION_VAR = re.compile(
    r'^\s*(?:var\s+)?(_local_\d+)\s*:[^=]*=\s*__activation__\s*;?\s*$'
)
_AIR_POLICY_FILE = re.compile(
    r'^(\s*)(Security\.loadPolicyFile\s*\(\s*MGNClient\.POLICY_FILE\s*\)\s*;)',
    re.MULTILINE,
)
_LOCAL_SLOT_ASSIGN = re.compile(
    r'^(\s*)(_local_\d+)\.slot(\d+)\s*=\s*(.+);\s*$'
)
_LOCAL_SLOT_USE = re.compile(r'(_local_\d+)\.slot(\d+)')


def _fix_local_slot_patterns(source: str) -> str:
    """Rewrite compiler activation slots leaked as _local_N.slotK."""
    slot_vars: dict[tuple[str, str], str] = {}
    out: List[str] = []
    for ln in source.splitlines():
        m = _LOCAL_SLOT_ASSIGN.match(ln)
        if m:
            ind, loc, idx, rhs = m.group(1), m.group(2), m.group(3), m.group(4)
            key = (loc, idx)
            if key not in slot_vars:
                slot_vars[key] = f'_actSlot{idx}'
            vname = slot_vars[key]
            tm = re.match(r'^new\s+([\w.]+)', rhs.strip())
            typ = tm.group(1) if tm else '*'
            ln = f'{ind}var {vname}:{typ} = {rhs};'
        else:
            for (loc, idx), vname in slot_vars.items():
                ln = re.sub(
                    rf'\b{re.escape(loc)}\.slot{re.escape(idx)}\b',
                    vname,
                    ln,
                )
        out.append(ln)
    return '\n'.join(out)


def finalize_decompiled_source(source: str) -> str:
    """Apply decompiler output fixes (imports, activation artifacts)."""
    if not source:
        return source
    for wrong, right in _IMPORT_FQN_CORRECTIONS.items():
        source = source.replace(f'import {wrong};', f'import {right};')
    source = _AIR_POLICY_FILE.sub(
        r'\1// \2  // Disabled — AIR security sandbox',
        source,
    )
    if _LOCAL_SLOT_USE.search(source):
        source = _fix_local_slot_patterns(source)
    if '__activation__' not in source:
        return source + ('\n' if source.endswith('\n') else '')
    lines = source.splitlines()
    dropped_regs: Set[str] = set()
    out: List[str] = []
    for ln in lines:
        st = ln.strip()
        m = _ACTIVATION_VAR.match(st)
        if m:
            dropped_regs.add(m.group(1))
            continue
        if dropped_regs and any(
            re.search(r'\b' + re.escape(r) + r'\b', ln) for r in dropped_regs
        ):
            continue
        if '__activation__' in ln:
            continue
        out.append(ln)
    # method-level pass for any block that survived line-wise cleanup
    body = '\n'.join(out)
    if '__activation__' in body:
        stmts = _strip_activation_artifacts(body.split('\n'))
        body = '\n'.join(stmts)
    return body + ('\n' if source.endswith('\n') else '')
