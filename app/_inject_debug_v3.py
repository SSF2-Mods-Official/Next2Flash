"""
Targeted debug trace injection v3.
Focus: inject state/controls diagnostics AROUND endAttack calls in stance MCs.

Patches frame methods to print:
  - inState(IDLE), inState(ATTACKING) BEFORE endAttack
  - getControls() BUTTON2 (attack button) status
  - Same checks AFTER endAttack

Also patches SSF2Character.endAttack and stancePlayFrame as before.
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))

from as3_decompiler.abc_editor import ABCEditor, Assembler, disassemble
from as3_decompiler.abc_parser import ABCFile, TRAIT_Method, TRAIT_Getter, TRAIT_Setter
from as3_decompiler.abc_patcher import serialize_abc, _parse_instructions
from as3_decompiler.swf_patcher import (
    read_swf_full, write_swf_from_tags,
    _extract_abc_data_from_tag, _build_doabc2_tag_body,
    TAG_DOABC, TAG_DOABC2,
)

RT_SWF = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"
OUT_SWF = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_debug.swf"


def _find_mn(editor, name):
    """Find a QName multiname index for a given name in the Package namespace."""
    abc = editor.abc
    for i, (kind, data) in enumerate(abc.multinames):
        if kind == 0x07 and data:  # QName
            ns_idx, name_idx = data
            if (0 < name_idx < len(abc.strings) and abc.strings[name_idx] == name
                    and 0 < ns_idx < len(abc.namespaces)):
                ns_kind, ns_name_idx = abc.namespaces[ns_idx]
                if ns_kind == 0x16:  # NS_Package
                    return i
    return None


def _find_any_mn(editor, name):
    """Find ANY multiname for a given name."""
    abc = editor.abc
    for i, (kind, data) in enumerate(abc.multinames):
        if kind == 0x07 and data:  # QName
            ns_idx, name_idx = data
            if 0 < name_idx < len(abc.strings) and abc.strings[name_idx] == name:
                return i
    return None


def find_method_idx(editor, class_name, method_name):
    ci = editor.find_class(class_name)
    if ci is None:
        print(f"  WARNING: class '{class_name}' not found")
        return None
    methods = editor.get_class_methods(ci)
    key = f"method:{method_name}"
    if key not in methods:
        # Try static
        key2 = f"static:method:{method_name}"
        if key2 in methods:
            return methods[key2]
        print(f"  WARNING: method '{method_name}' not found in {class_name}")
        return None
    return methods[key]


def dump_method(editor, method_idx, label=""):
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        print(f"  {label}: NO METHOD BODY")
        return
    text = disassemble(editor.abc, body.code)
    print(f"  {label}: method[{method_idx}] stack={body.max_stack} locals={body.local_count}")
    for line in text.split('\n')[:15]:
        print(f"    {line}")
    if len(text.split('\n')) > 15:
        print(f"    ... ({len(text.split(chr(10)))} total lines)")


def inject_simple_trace(editor, class_name, method_name, message, mns):
    """Add trace at start of method."""
    method_idx = find_method_idx(editor, class_name, method_name)
    if method_idx is None:
        return False
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        return False
    
    msg_str = editor.ensure_string(message)
    instructions = _parse_instructions(body.code)
    
    asm = Assembler()
    asm.emit('getlocal_0')
    asm.emit('pushscope')
    asm.emit('getlex', mns['SSF2API'])
    asm.emit('pushstring', msg_str)
    asm.emit('callpropvoid', mns['print'], 1)
    
    skipped = 0
    for start, end, op, operands in instructions:
        if skipped < 2:
            if op in (0xD0, 0x30):
                skipped += 1
                continue
        asm.emit_raw(op, operands)
    
    code = asm.assemble()
    editor.replace_method_body(method_idx, code=code,
        max_stack=max(body.max_stack, 3),
        local_count=body.local_count,
        init_scope_depth=body.init_scope_depth,
        max_scope_depth=body.max_scope_depth)
    return True


def inject_trace_with_arg(editor, class_name, method_name, prefix, arg_local, mns):
    """Add trace at start of method with string concat of arg."""
    method_idx = find_method_idx(editor, class_name, method_name)
    if method_idx is None:
        return False
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        return False
    
    prefix_str = editor.ensure_string(prefix)
    instructions = _parse_instructions(body.code)
    
    asm = Assembler()
    asm.emit('getlocal_0')
    asm.emit('pushscope')
    asm.emit('getlex', mns['SSF2API'])
    asm.emit('pushstring', prefix_str)
    if arg_local <= 3:
        asm.emit(f'getlocal_{arg_local}')
    else:
        asm.emit('getlocal', arg_local)
    asm.emit('add')
    asm.emit('callpropvoid', mns['print'], 1)
    
    skipped = 0
    for start, end, op, operands in instructions:
        if skipped < 2:
            if op in (0xD0, 0x30):
                skipped += 1
                continue
        asm.emit_raw(op, operands)
    
    code = asm.assemble()
    editor.replace_method_body(method_idx, code=code,
        max_stack=max(body.max_stack, 4),
        local_count=body.local_count,
        init_scope_depth=body.init_scope_depth,
        max_scope_depth=body.max_scope_depth)
    return True


def rewrite_dasha_frame21(editor, mns):
    """Rewrite fox_DashA_37.frame21 with full diagnostics.
    
    Original:
        this.self.setXSpeed(this.self.getXSpeed() * 0.5);
        this.self.endAttack();
    
    New version:
        SSF2API.print("*** DASHA-F21 PRE: isATTACK=" + this.self.inState(9) + " isIDLE=" + this.self.inState(0));
        this.self.setXSpeed(this.self.getXSpeed() * 0.5);
        this.self.endAttack();
        SSF2API.print("*** DASHA-F21 POST: isATTACK=" + this.self.inState(9) + " isIDLE=" + this.self.inState(0));
        var c:Object = this.self.getControls();
        SSF2API.print("*** DASHA-F21 CONTROLS: B2=" + c.BUTTON2 + " LEFT=" + c.LEFT + " RIGHT=" + c.RIGHT);
    """
    method_idx = find_method_idx(editor, "fox_fla.fox_DashA_37", "frame21")
    if method_idx is None:
        return False
    
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        return False
    
    print(f"\n--- Rewriting fox_DashA_37.frame21 ---")
    dump_method(editor, method_idx, "BEFORE")
    
    # We need multinames for: self, setXSpeed, getXSpeed, endAttack, inState, getControls
    # Plus property names: BUTTON2, LEFT, RIGHT
    # These should all exist in the pool already since other code uses them
    self_mn = _find_any_mn(editor, "self")
    setXSpeed_mn = _find_any_mn(editor, "setXSpeed")
    getXSpeed_mn = _find_any_mn(editor, "getXSpeed")
    endAttack_mn = _find_any_mn(editor, "endAttack")
    inState_mn = _find_any_mn(editor, "inState")
    getControls_mn = _find_any_mn(editor, "getControls")
    
    # Ensure string pool entries
    str_pre = editor.ensure_string("*** DASHA-F21 PRE: isATTACK=")
    str_idle_eq = editor.ensure_string(" isIDLE=")
    str_post = editor.ensure_string("*** DASHA-F21 POST: isATTACK=")
    str_ctrl = editor.ensure_string("*** DASHA-F21 CONTROLS: B2=")
    str_left = editor.ensure_string(" LEFT=")
    str_right = editor.ensure_string(" RIGHT=")
    
    # Property multinames for controls object
    BUTTON2_mn = _find_any_mn(editor, "BUTTON2")
    LEFT_mn = _find_any_mn(editor, "LEFT")
    RIGHT_mn = _find_any_mn(editor, "RIGHT")
    
    print(f"  Multinames: self={self_mn}, setXSpeed={setXSpeed_mn}, getXSpeed={getXSpeed_mn}")
    print(f"  endAttack={endAttack_mn}, inState={inState_mn}, getControls={getControls_mn}")
    print(f"  BUTTON2={BUTTON2_mn}, LEFT={LEFT_mn}, RIGHT={RIGHT_mn}")
    
    if any(x is None for x in [self_mn, setXSpeed_mn, getXSpeed_mn, endAttack_mn, 
                                 inState_mn, getControls_mn]):
        print("  ERROR: Missing multinames!")
        return False
    
    asm = Assembler()
    
    # getlocal_0 + pushscope
    asm.emit('getlocal_0')
    asm.emit('pushscope')
    
    # --- PRE-ENDATTACK diagnostics ---
    # SSF2API.print("*** DASHA-F21 PRE: isATTACK=" + this.self.inState(9) + " isIDLE=" + this.self.inState(0))
    asm.emit('getlex', mns['SSF2API'])
    asm.emit('pushstring', str_pre)
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 9)  # CState.ATTACKING
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('pushstring', str_idle_eq)
    asm.emit('add')
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 0)  # CState.IDLE
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('callpropvoid', mns['print'], 1)
    
    # --- Original code: this.self.setXSpeed(this.self.getXSpeed() * 0.5) ---
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('callproperty', getXSpeed_mn, 0)
    asm.emit('pushdouble', editor.ensure_double(0.5))
    asm.emit('multiply')
    asm.emit('callpropvoid', setXSpeed_mn, 1)
    
    # --- Original code: this.self.endAttack() ---
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('callpropvoid', endAttack_mn, 0)
    
    # --- POST-ENDATTACK diagnostics ---
    # SSF2API.print("*** DASHA-F21 POST: isATTACK=" + this.self.inState(9) + " isIDLE=" + this.self.inState(0))
    asm.emit('getlex', mns['SSF2API'])
    asm.emit('pushstring', str_post)
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 9)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('pushstring', str_idle_eq)
    asm.emit('add')
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 0)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('callpropvoid', mns['print'], 1)
    
    # --- Controls check ---
    # var c = this.self.getControls();
    # SSF2API.print("*** DASHA-F21 CONTROLS: B2=" + c.BUTTON2 + " LEFT=" + c.LEFT + " RIGHT=" + c.RIGHT)
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('callproperty', getControls_mn, 0)
    asm.emit('coerce_a')
    asm.emit('setlocal', 4)  # store in local 4 (new local for controls)
    
    if BUTTON2_mn and LEFT_mn and RIGHT_mn:
        asm.emit('getlex', mns['SSF2API'])
        asm.emit('pushstring', str_ctrl)
        asm.emit('getlocal', 4)
        asm.emit('getproperty', BUTTON2_mn)
        asm.emit('add')
        asm.emit('pushstring', str_left)
        asm.emit('add')
        asm.emit('getlocal', 4)
        asm.emit('getproperty', LEFT_mn)
        asm.emit('add')
        asm.emit('pushstring', str_right)
        asm.emit('add')
        asm.emit('getlocal', 4)
        asm.emit('getproperty', RIGHT_mn)
        asm.emit('add')
        asm.emit('callpropvoid', mns['print'], 1)
    
    asm.emit('returnvoid')
    
    code = asm.assemble()
    editor.replace_method_body(method_idx, code=code,
        max_stack=10,
        local_count=max(body.local_count, 5),  # need local 4 for controls
        init_scope_depth=body.init_scope_depth,
        max_scope_depth=body.max_scope_depth)
    
    dump_method(editor, method_idx, "AFTER")
    return True


def rewrite_tilts_frame13(editor, mns):
    """Rewrite fox_tiltS_38.frame13 with diagnostics.
    
    Original:
        this.self.endAttack();
    
    New:
        SSF2API.print("*** TILTS-F13 PRE: isATTACK=" + this.self.inState(9) + " isIDLE=" + this.self.inState(0));
        this.self.endAttack();
        SSF2API.print("*** TILTS-F13 POST: isATTACK=" + this.self.inState(9) + " isIDLE=" + this.self.inState(0));
    """
    method_idx = find_method_idx(editor, "fox_fla.fox_tiltS_38", "frame13")
    if method_idx is None:
        return False
    
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        return False
    
    print(f"\n--- Rewriting fox_tiltS_38.frame13 ---")
    dump_method(editor, method_idx, "BEFORE")
    
    self_mn = _find_any_mn(editor, "self")
    endAttack_mn = _find_any_mn(editor, "endAttack")
    inState_mn = _find_any_mn(editor, "inState")
    
    str_pre = editor.ensure_string("*** TILTS-F13 PRE: isATTACK=")
    str_idle_eq = editor.ensure_string(" isIDLE=")
    str_post = editor.ensure_string("*** TILTS-F13 POST: isATTACK=")
    
    asm = Assembler()
    asm.emit('getlocal_0')
    asm.emit('pushscope')
    
    # PRE
    asm.emit('getlex', mns['SSF2API'])
    asm.emit('pushstring', str_pre)
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 9)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('pushstring', str_idle_eq)
    asm.emit('add')
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 0)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('callpropvoid', mns['print'], 1)
    
    # endAttack
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('callpropvoid', endAttack_mn, 0)
    
    # POST
    asm.emit('getlex', mns['SSF2API'])
    asm.emit('pushstring', str_post)
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 9)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('pushstring', str_idle_eq)
    asm.emit('add')
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 0)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('callpropvoid', mns['print'], 1)
    
    asm.emit('returnvoid')
    
    code = asm.assemble()
    editor.replace_method_body(method_idx, code=code,
        max_stack=10,
        local_count=body.local_count,
        init_scope_depth=body.init_scope_depth,
        max_scope_depth=body.max_scope_depth)
    
    dump_method(editor, method_idx, "AFTER")
    return True


def rewrite_combo_frame8(editor, mns):
    """Rewrite fox_combo_36.frame8 with diagnostics (same pattern).
    
    Original:
        this.self.endAttack();
    """
    method_idx = find_method_idx(editor, "fox_fla.fox_combo_36", "frame8")
    if method_idx is None:
        return False
    
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        return False
    
    print(f"\n--- Rewriting fox_combo_36.frame8 ---")
    
    self_mn = _find_any_mn(editor, "self")
    endAttack_mn = _find_any_mn(editor, "endAttack")
    inState_mn = _find_any_mn(editor, "inState")
    getControls_mn = _find_any_mn(editor, "getControls")
    BUTTON2_mn = _find_any_mn(editor, "BUTTON2")
    
    str_pre = editor.ensure_string("*** COMBO-F8 PRE: isATTACK=")
    str_idle_eq = editor.ensure_string(" isIDLE=")
    str_post = editor.ensure_string("*** COMBO-F8 POST: isATTACK=")
    str_ctrl = editor.ensure_string(" B2=")
    
    asm = Assembler()
    asm.emit('getlocal_0')
    asm.emit('pushscope')
    
    # PRE
    asm.emit('getlex', mns['SSF2API'])
    asm.emit('pushstring', str_pre)
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 9)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('pushstring', str_idle_eq)
    asm.emit('add')
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 0)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('callpropvoid', mns['print'], 1)
    
    # endAttack
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('callpropvoid', endAttack_mn, 0)
    
    # POST with controls check
    asm.emit('getlex', mns['SSF2API'])
    asm.emit('pushstring', str_post)
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 9)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    asm.emit('pushstring', str_idle_eq)
    asm.emit('add')
    asm.emit('getlocal_0')
    asm.emit('getproperty', self_mn)
    asm.emit('pushbyte', 0)
    asm.emit('callproperty', inState_mn, 1)
    asm.emit('add')
    if BUTTON2_mn:
        asm.emit('pushstring', str_ctrl)
        asm.emit('add')
        asm.emit('getlocal_0')
        asm.emit('getproperty', self_mn)
        asm.emit('callproperty', getControls_mn, 0)
        asm.emit('getproperty', BUTTON2_mn)
        asm.emit('add')
    asm.emit('callpropvoid', mns['print'], 1)
    
    asm.emit('returnvoid')
    
    code = asm.assemble()
    editor.replace_method_body(method_idx, code=code,
        max_stack=10,
        local_count=body.local_count,
        init_scope_depth=body.init_scope_depth,
        max_scope_depth=body.max_scope_depth)
    return True


def main():
    print("=== DEBUG TRACE INJECTION V3 ===\n")
    
    swf_info = read_swf_full(RT_SWF)
    tags = swf_info['tags']
    
    abc_tag_idx = None
    for i, (tag_type, body) in enumerate(tags):
        if tag_type in (TAG_DOABC, TAG_DOABC2):
            abc_tag_idx = i
            break
    
    tag_type, tag_body = tags[abc_tag_idx]
    block_name, abc_data = _extract_abc_data_from_tag(tag_type, tag_body)
    print(f"ABC: {len(abc_data)} bytes")
    
    editor = ABCEditor(abc_data)
    
    # Find common multinames
    mns = {
        'SSF2API': _find_mn(editor, "SSF2API"),
        'print': _find_mn(editor, "print"),
    }
    print(f"SSF2API mn={mns['SSF2API']}, print mn={mns['print']}")
    
    total = 0
    
    # 1. Wrapper traces (same as v2)
    print("\n=== Wrapper traces ===")
    for method, prefix in [
        ("endAttack", "*** ENDATTACK: "),
        ("stancePlayFrame", "*** STANCEPLAY: "),
    ]:
        cls = "SSF2Character" if method == "endAttack" else "SSF2GameObject"
        if inject_trace_with_arg(editor, cls, method, prefix, 1, mns):
            total += 1
            print(f"  Patched {cls}.{method}")
    
    if inject_simple_trace(editor, "FoxExt", "initialize", "*** FOX INIT ***", mns):
        total += 1
        print("  Patched FoxExt.initialize")
    
    # 2. Fox main frame1 trace
    print("\n=== Fox main traces ===")
    ci = editor.find_class("fox")
    if ci is not None:
        methods = editor.get_class_methods(ci)
        key = "method:frame1"
        if key in methods:
            method_idx = methods[key]
            body = editor.abc.method_bodies.get(method_idx)
            if body:
                msg_str = editor.ensure_string("*** FOX MAIN F1: stand")
                instructions = _parse_instructions(body.code)
                asm = Assembler()
                asm.emit('getlocal_0')
                asm.emit('pushscope')
                asm.emit('getlex', mns['SSF2API'])
                asm.emit('pushstring', msg_str)
                asm.emit('callpropvoid', mns['print'], 1)
                skipped = 0
                for s, e, op, operands in instructions:
                    if skipped < 2 and op in (0xD0, 0x30):
                        skipped += 1
                        continue
                    asm.emit_raw(op, operands)
                code = asm.assemble()
                editor.replace_method_body(method_idx, code=code,
                    max_stack=max(body.max_stack, 3),
                    local_count=body.local_count,
                    init_scope_depth=body.init_scope_depth,
                    max_scope_depth=body.max_scope_depth)
                total += 1
                print("  Patched fox.frame1")
    
    # 3. KEY: Rewrite endAttack frame scripts with full diagnostics
    print("\n=== Frame script rewrites with state diagnostics ===")
    if rewrite_dasha_frame21(editor, mns):
        total += 1
    if rewrite_tilts_frame13(editor, mns):
        total += 1
    if rewrite_combo_frame8(editor, mns):
        total += 1
    
    # 4. Simple traces for stance frame1 entries
    print("\n=== Stance frame1 traces ===")
    stance_traces = [
        ("fox_fla.fox_combo_36", "frame1", "*** COMBO F1"),
        ("fox_fla.fox_DashA_37", "frame1", "*** DASHA F1"),
        ("fox_fla.fox_tiltS_38", "frame1", "*** TILTS F1"),
        ("fox_fla.fox_idle_14", "frame1", "*** IDLE F1"),
        ("fox_fla.fox_hurt_103", "frame1", "*** HURT F1"),
    ]
    for cls, method, msg in stance_traces:
        if inject_simple_trace(editor, cls, method, msg, mns):
            total += 1
            print(f"  Patched {cls}.{method}")
    
    print(f"\n=== Total: {total} methods patched ===")
    
    # Serialize
    new_abc = editor.serialize()
    print(f"New ABC: {len(new_abc)} bytes (was {len(abc_data)})")
    
    if tag_type == TAG_DOABC2:
        new_tag_body = _build_doabc2_tag_body(block_name, new_abc, flags=1)
    else:
        new_tag_body = new_abc
    
    tags[abc_tag_idx] = (tag_type, new_tag_body)
    write_swf_from_tags(swf_info, OUT_SWF)
    
    out_size = os.path.getsize(OUT_SWF)
    print(f"\nWrote {OUT_SWF}: {out_size:,} bytes")
    print("\nKey traces to look for:")
    print("  *** DASHA-F21 PRE/POST: isATTACK=true/false isIDLE=true/false")
    print("  *** DASHA-F21 CONTROLS: B2=true/false LEFT=true/false RIGHT=true/false")
    print("  *** TILTS-F13 PRE/POST: same format")
    print("  *** COMBO-F8 PRE/POST: same format + B2=")


if __name__ == '__main__':
    main()
