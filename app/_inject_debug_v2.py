"""
Comprehensive debug trace injection for fox_fresh.swf.

Injects traces into:
1. SSF2Character.endAttack — args
2. SSF2Character.setState — arg
3. SSF2GameObject.stancePlayFrame — arg
4. SSF2API.getCharacter — return value null check
5. fox_fla.fox_combo_36.frame1 — self null check
6. fox_fla.fox_combo_36.frame8 — endAttack trace
7. fox_fla.fox_DashA_37.frame1 — self null check
8. FoxExt.initialize — confirm init fires
9. fox.fox() constructor — confirm main MC constructed

Output: fox_debug.swf
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))

from as3_decompiler.abc_editor import ABCEditor, Assembler, disassemble, NS_Package
from as3_decompiler.abc_parser import ABCFile, TRAIT_Method, TRAIT_Getter, TRAIT_Setter
from as3_decompiler.abc_patcher import serialize_abc, _parse_instructions
from as3_decompiler.swf_patcher import (
    read_swf_full, write_swf_from_tags,
    _extract_abc_data_from_tag, _build_doabc2_tag_body,
    TAG_DOABC, TAG_DOABC2,
)

RT_SWF = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"
OUT_SWF = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_debug.swf"


def find_method_idx(editor, class_name, method_name):
    ci = editor.find_class(class_name)
    if ci is None:
        print(f"  WARNING: class '{class_name}' not found")
        return None
    methods = editor.get_class_methods(ci)
    key = f"method:{method_name}"
    if key not in methods:
        print(f"  WARNING: method '{method_name}' not found in {class_name}")
        print(f"  Available: {sorted(methods.keys())}")
        return None
    return methods[key]


def dump_method(editor, method_idx, label=""):
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        print(f"  {label}: NO METHOD BODY for method[{method_idx}]")
        return
    print(f"  {label}: method[{method_idx}] max_stack={body.max_stack} "
          f"local_count={body.local_count} "
          f"scope={body.init_scope_depth}-{body.max_scope_depth}")
    text = disassemble(editor.abc, body.code)
    for line in text.split('\n'):
        print(f"    {line}")


def _find_mn(editor, name):
    """Find a QName multiname index for a given name in the Package namespace."""
    abc = editor.abc
    for i, (kind, data) in enumerate(abc.multinames):
        if kind == 0x07 and data:
            ns_idx, name_idx = data
            if (0 < name_idx < len(abc.strings) and abc.strings[name_idx] == name
                    and 0 < ns_idx < len(abc.namespaces)):
                ns_kind, ns_name_idx = abc.namespaces[ns_idx]
                if ns_kind == 0x16:  # NS_Package
                    return i
    return None


def _emit_print(asm, ssf2api_mn, print_mn, msg_str_idx):
    """Emit: getlex SSF2API; pushstring msg; callpropvoid print,1"""
    asm.emit('getlex', ssf2api_mn)
    asm.emit('pushstring', msg_str_idx)
    asm.emit('callpropvoid', print_mn, 1)


def _emit_print_with_local(asm, ssf2api_mn, print_mn, prefix_str_idx, local_idx):
    """Emit: getlex SSF2API; pushstring prefix; getlocal_N; add; callpropvoid print,1"""
    asm.emit('getlex', ssf2api_mn)
    asm.emit('pushstring', prefix_str_idx)
    if local_idx <= 3:
        asm.emit(f'getlocal_{local_idx}')
    else:
        asm.emit('getlocal', local_idx)
    asm.emit('add')
    asm.emit('callpropvoid', print_mn, 1)


def inject_simple_trace(editor, class_name, method_name, message, ssf2api_mn, print_mn):
    """Inject a simple SSF2API.print(message) after pushscope."""
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
    _emit_print(asm, ssf2api_mn, print_mn, msg_str)
    
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
    print(f"  Patched {class_name}.{method_name} with trace: {message}")
    return True


def inject_trace_with_arg(editor, class_name, method_name, prefix, arg_local, ssf2api_mn, print_mn):
    """Inject SSF2API.print(prefix + arg_local) after pushscope."""
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
    _emit_print_with_local(asm, ssf2api_mn, print_mn, prefix_str, arg_local)
    
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
    print(f"  Patched {class_name}.{method_name} with trace: {prefix}<arg{arg_local}>")
    return True


def inject_getcharacter_trace(editor, ssf2api_mn, print_mn):
    """Inject a null-check trace into SSF2API.getCharacter().
    
    Original:
      getlocal_0 / pushscope
      getlocal_1 / istype MovieClip / ...
      if isReady: return m_api.getCharacter(arg)
      else: return null
    
    We add after pushscope:
      SSF2API.print("GETCHAR called, isReady=" + SSF2API.isReady())
    
    And before each returnvalue, print what's being returned.
    
    Actually, simpler: just trace entry with the argument type.
    """
    method_idx = find_method_idx(editor, "SSF2API", "getCharacter")
    if method_idx is None:
        return False
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        return False
    
    print(f"\n--- SSF2API.getCharacter ---")
    dump_method(editor, method_idx, "BEFORE")
    
    # For static methods, there's no meaningful getlocal_0/pushscope in same way.
    # Let's just add a traceat the start.
    # Static method: getlocal_0 pushes the global object, pushscope adds it.
    
    instructions = _parse_instructions(body.code)
    msg_str = editor.ensure_string("*** GETCHAR called")
    
    asm = Assembler()
    asm.emit('getlocal_0')
    asm.emit('pushscope')
    _emit_print(asm, ssf2api_mn, print_mn, msg_str)
    
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
    dump_method(editor, method_idx, "AFTER")
    return True


def inject_frame_script_traces(editor, class_name, frame_methods, ssf2api_mn, print_mn):
    """Inject traces into frame script methods of a stance MC class.
    
    Frame scripts are special: they don't have getlocal_0/pushscope at the start
    because they're called as frame scripts (via addFrameScript), not as regular methods.
    
    Actually, frame script bodies DO start with getlocal_0/pushscope in the ABC.
    Let's verify and patch them.
    """
    ci = editor.find_class(class_name)
    if ci is None:
        print(f"  WARNING: class '{class_name}' not found")
        return 0
    
    methods = editor.get_class_methods(ci)
    patched = 0
    
    for fname, message in frame_methods:
        key = f"method:{fname}"
        if key not in methods:
            print(f"  WARNING: {class_name}.{fname} not found")
            continue
        
        method_idx = methods[key]
        body = editor.abc.method_bodies.get(method_idx)
        if body is None:
            print(f"  No body for {class_name}.{fname}")
            continue
        
        print(f"\n--- {class_name}.{fname} ---")
        dump_method(editor, method_idx, "BEFORE")
        
        instructions = _parse_instructions(body.code)
        msg_str = editor.ensure_string(message)
        
        asm = Assembler()
        asm.emit('getlocal_0')
        asm.emit('pushscope')
        _emit_print(asm, ssf2api_mn, print_mn, msg_str)
        
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
        dump_method(editor, method_idx, "AFTER")
        patched += 1
    
    return patched


def main():
    print("=== COMPREHENSIVE DEBUG TRACE INJECTION ===\n")
    
    swf_info = read_swf_full(RT_SWF)
    tags = swf_info['tags']
    
    abc_tag_idx = None
    for i, (tag_type, body) in enumerate(tags):
        if tag_type in (TAG_DOABC, TAG_DOABC2):
            abc_tag_idx = i
            break
    
    tag_type, tag_body = tags[abc_tag_idx]
    block_name, abc_data = _extract_abc_data_from_tag(tag_type, tag_body)
    print(f"ABC block '{block_name}': {len(abc_data)} bytes")
    
    editor = ABCEditor(abc_data)
    classes = editor.list_classes()
    print(f"Classes: {len(classes)}")
    print(f"  fox_fla classes: {[c for c in classes if 'fox_fla' in c][:5]}...")
    
    ssf2api_mn = _find_mn(editor, "SSF2API")
    print_mn = _find_mn(editor, "print")
    print(f"SSF2API mn={ssf2api_mn}, print mn={print_mn}")
    
    if ssf2api_mn is None or print_mn is None:
        print("ERROR: Can't find SSF2API/print multinames")
        return
    
    total_patched = 0
    
    # 1. SSF2Character wrapper methods
    print("\n=== Wrapper method traces ===")
    for method, prefix in [
        ("endAttack", "*** ENDATTACK: "),
        ("setState", "*** SETSTATE: "),
        ("switchAttack", "*** SWITCHATTACK: "),
    ]:
        if inject_trace_with_arg(editor, "SSF2Character", method, prefix, 1, ssf2api_mn, print_mn):
            total_patched += 1
    
    if inject_trace_with_arg(editor, "SSF2GameObject", "stancePlayFrame", "*** STANCEPLAY: ", 1, ssf2api_mn, print_mn):
        total_patched += 1
    
    if inject_simple_trace(editor, "SSF2Character", "toIdle", "*** TOIDLE", ssf2api_mn, print_mn):
        total_patched += 1
    
    # 2. FoxExt.initialize
    print("\n=== FoxExt traces ===")
    if inject_simple_trace(editor, "FoxExt", "initialize", "*** FOX INIT ***", ssf2api_mn, print_mn):
        total_patched += 1
    
    # 3. SSF2API.getCharacter - trace entry
    print("\n=== SSF2API.getCharacter trace ===")
    if inject_getcharacter_trace(editor, ssf2api_mn, print_mn):
        total_patched += 1
    
    # 4. Frame script traces for fox_combo_36 (jab combo - always triggered in gameplay)
    print("\n=== fox_combo_36 frame script traces ===")
    combo_traces = [
        ("frame1", "*** COMBO F1: entered (self setup)"),
        ("frame8", "*** COMBO F8: endAttack call"),
        ("frame9", "*** COMBO F9: hit2 start"),
        ("frame16", "*** COMBO F16: endAttack call 2"),
        ("frame17", "*** COMBO F17: hit3/rapid start"),
        ("frame40", "*** COMBO F40: finish"),
        ("frame41", "*** COMBO F41: endAttack finish"),
    ]
    total_patched += inject_frame_script_traces(
        editor, "fox_fla.fox_combo_36", combo_traces, ssf2api_mn, print_mn)
    
    # 5. Frame script traces for fox_DashA_37 (dash attack - easy to test)
    print("\n=== fox_DashA_37 frame script traces ===")
    dasha_traces = [
        ("frame1", "*** DASHA F1: entered"),
        ("frame14", "*** DASHA F14: sound/decay"),
        ("frame21", "*** DASHA F21: endAttack"),
    ]
    total_patched += inject_frame_script_traces(
        editor, "fox_fla.fox_DashA_37", dasha_traces, ssf2api_mn, print_mn)
    
    # 6. Frame script traces for fox_tiltS_38 (side tilt)
    print("\n=== fox_tiltS_38 frame script traces ===")
    tilts_traces = [
        ("frame1", "*** TILTS F1: entered"),
        ("frame13", "*** TILTS F13: endAttack"),
    ]
    total_patched += inject_frame_script_traces(
        editor, "fox_fla.fox_tiltS_38", tilts_traces, ssf2api_mn, print_mn)
    
    # 7. Main fox constructor
    print("\n=== fox constructor trace ===")
    # The fox class constructor is the "iinit" - we already trace via frame1
    # Let's trace the main fox frame1 which sets xframe="stand"
    fox_traces = [
        ("frame1", "*** FOX MAIN F1: stand"),
    ]
    total_patched += inject_frame_script_traces(
        editor, "fox", fox_traces, ssf2api_mn, print_mn)
    
    # 8. fox_idle_14 traces - to see if idle enters
    print("\n=== fox_idle_14 frame script traces ===")
    idle_traces = [
        ("frame1", "*** IDLE F1: entered"),
    ]
    total_patched += inject_frame_script_traces(
        editor, "fox_fla.fox_idle_14", idle_traces, ssf2api_mn, print_mn)
    
    # 9. fox_hurt_103 - to see hurt behavior
    print("\n=== fox_hurt_103 frame script traces ===")
    hurt_traces = [
        ("frame1", "*** HURT F1: entered"),
        ("frame9", "*** HURT F9: done1, stop"),
        ("frame10", "*** HURT F10: stancePlayFrame done1"),
    ]
    total_patched += inject_frame_script_traces(
        editor, "fox_fla.fox_hurt_103", hurt_traces, ssf2api_mn, print_mn)
    
    print(f"\n=== Total: {total_patched} methods patched ===")
    
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
    in_size = os.path.getsize(RT_SWF)
    print(f"\nWrote {OUT_SWF}: {out_size:,} bytes (original: {in_size:,})")
    print("\nReplace fox.ssf with fox_debug.swf and look for '***' messages in game console.")


if __name__ == '__main__':
    main()
