"""Inject SSF2API.print() debug traces into key methods of fox_fresh.swf.

Patches:
  - SSF2Character.endAttack → prints "ENDATTACK(<arg1>,<arg2>)"
  - SSF2Character.setState → prints "SETSTATE(<stateId>)"
  - SSF2GameObject.setState → prints "GO.SETSTATE(<stateId>)"
  - SSF2Character.toIdle → prints "TOIDLE"

Then writes fox_debug.swf for runtime testing.
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
    """Find the method_idx for a named method in a class."""
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
    """Disassemble and print a method body."""
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


def _find_existing_ssf2api_mn(editor):
    """Find the existing SSF2API multiname index (used by getlex in setState)."""
    # SSF2API is QName(ns=Package(""), "SSF2API") — find it in the pool
    abc = editor.abc
    for i, (kind, data) in enumerate(abc.multinames):
        if kind == 0x07 and data:  # QName
            ns_idx, name_idx = data
            if (0 < name_idx < len(abc.strings) and abc.strings[name_idx] == "SSF2API"
                    and 0 < ns_idx < len(abc.namespaces)):
                ns_kind, ns_name_idx = abc.namespaces[ns_idx]
                if ns_kind == 0x16:  # NS_Package
                    return i
    return None


def _find_existing_print_mn(editor):
    """Find the existing 'print' multiname index (used by callpropvoid in setState)."""
    abc = editor.abc
    for i, (kind, data) in enumerate(abc.multinames):
        if kind == 0x07 and data:  # QName
            ns_idx, name_idx = data
            if (0 < name_idx < len(abc.strings) and abc.strings[name_idx] == "print"
                    and 0 < ns_idx < len(abc.namespaces)):
                ns_kind, ns_name_idx = abc.namespaces[ns_idx]
                if ns_kind == 0x16:  # NS_Package
                    return i
    return None


def _emit_print_trace(asm, ssf2api_mn, print_mn, msg_str_idx):
    """Emit: getlex SSF2API; pushstring msg; callpropvoid print,1
    
    Uses getlex (like the original code) instead of findpropstrict+getproperty.
    getlex works the same way the existing SSF2API references do.
    """
    asm.emit('getlex', ssf2api_mn)
    asm.emit('pushstring', msg_str_idx)
    asm.emit('callpropvoid', print_mn, 1)


def _emit_print_trace_with_arg(asm, ssf2api_mn, print_mn, prefix_str_idx, arg_local=1):
    """Emit: getlex SSF2API; pushstring prefix; getlocal_N; add; callpropvoid print,1"""
    asm.emit('getlex', ssf2api_mn)
    asm.emit('pushstring', prefix_str_idx)
    if arg_local == 0:
        asm.emit('getlocal_0')
    elif arg_local == 1:
        asm.emit('getlocal_1')
    elif arg_local == 2:
        asm.emit('getlocal_2')
    elif arg_local == 3:
        asm.emit('getlocal_3')
    else:
        asm.emit('getlocal', arg_local)
    asm.emit('add')  # string concat
    asm.emit('callpropvoid', print_mn, 1)


def inject_print_before_delegate(editor, class_name, method_name, trace_msg):
    """Inject SSF2API.print(trace_msg) after the initial pushscope.
    
    The original code starts with: getlocal_0 / pushscope / ...
    We emit: getlocal_0 / pushscope / <print trace> / <rest of original>
    This ensures 'this' is on the scope chain so getlex SSF2API resolves.
    """
    method_idx = find_method_idx(editor, class_name, method_name)
    if method_idx is None:
        return False
    
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        print(f"  No body for {class_name}.{method_name}")
        return False
    
    print(f"\n--- Patching {class_name}.{method_name} ---")
    dump_method(editor, method_idx, "BEFORE")
    
    instructions = _parse_instructions(body.code)
    
    ssf2api_mn = _find_existing_ssf2api_mn(editor)
    print_mn = _find_existing_print_mn(editor)
    if ssf2api_mn is None or print_mn is None:
        print(f"  ERROR: Can't find SSF2API (mn={ssf2api_mn}) or print (mn={print_mn}) in pool")
        return False
    
    msg_str = editor.ensure_string(trace_msg)
    
    asm = Assembler()
    
    # Emit getlocal_0 + pushscope first (from original code)
    asm.emit('getlocal_0')
    asm.emit('pushscope')
    
    # Now the print trace (scope chain has 'this', so getlex works)
    _emit_print_trace(asm, ssf2api_mn, print_mn, msg_str)
    
    # Replay original, SKIPPING first getlocal_0 + pushscope
    skipped = 0
    for start, end, op, operands in instructions:
        if skipped < 2:
            # Skip getlocal_0 (0xD0) and pushscope (0x30)
            if op in (0xD0, 0x30):
                skipped += 1
                continue
        asm.emit_raw(op, operands)
    
    code = asm.assemble()
    
    editor.replace_method_body(
        method_idx,
        code=code,
        max_stack=max(body.max_stack, 3),  # getlex pushes 1, pushstring +1, add uses 2
        local_count=body.local_count,
        init_scope_depth=body.init_scope_depth,
        max_scope_depth=body.max_scope_depth,
    )
    
    dump_method(editor, method_idx, "AFTER")
    return True


def inject_print_with_arg(editor, class_name, method_name, trace_prefix, arg_local=1):
    """Inject SSF2API.print(trace_prefix + arg) after the initial pushscope.
    
    Prints the prefix concatenated with the first argument.
    """
    method_idx = find_method_idx(editor, class_name, method_name)
    if method_idx is None:
        return False
    
    body = editor.abc.method_bodies.get(method_idx)
    if body is None:
        print(f"  No body for {class_name}.{method_name}")
        return False
    
    print(f"\n--- Patching {class_name}.{method_name} (with arg) ---")
    dump_method(editor, method_idx, "BEFORE")
    
    instructions = _parse_instructions(body.code)
    
    ssf2api_mn = _find_existing_ssf2api_mn(editor)
    print_mn = _find_existing_print_mn(editor)
    if ssf2api_mn is None or print_mn is None:
        print(f"  ERROR: Can't find SSF2API or print in pool")
        return False
    
    prefix_str = editor.ensure_string(trace_prefix)
    
    asm = Assembler()
    
    # Emit getlocal_0 + pushscope first
    asm.emit('getlocal_0')
    asm.emit('pushscope')
    
    # Now the print trace with arg
    _emit_print_trace_with_arg(asm, ssf2api_mn, print_mn, prefix_str, arg_local)
    
    # Replay original, SKIPPING first getlocal_0 + pushscope
    skipped = 0
    for start, end, op, operands in instructions:
        if skipped < 2:
            if op in (0xD0, 0x30):
                skipped += 1
                continue
        asm.emit_raw(op, operands)
    
    code = asm.assemble()
    
    editor.replace_method_body(
        method_idx,
        code=code,
        max_stack=max(body.max_stack, 4),
        local_count=body.local_count,
        init_scope_depth=body.init_scope_depth,
        max_scope_depth=body.max_scope_depth,
    )
    
    dump_method(editor, method_idx, "AFTER")
    return True


def main():
    print("=== INJECTING DEBUG TRACES ===\n")
    print(f"Input:  {RT_SWF}")
    print(f"Output: {OUT_SWF}")
    
    # Step 1: Read the SWF
    print("\nReading SWF...")
    swf_info = read_swf_full(RT_SWF)
    tags = swf_info['tags']
    
    # Find the ABC block
    abc_tag_idx = None
    for i, (tag_type, body) in enumerate(tags):
        if tag_type in (TAG_DOABC, TAG_DOABC2):
            abc_tag_idx = i
            break
    
    if abc_tag_idx is None:
        print("ERROR: No DoABC tag found!")
        return
    
    tag_type, tag_body = tags[abc_tag_idx]
    block_name, abc_data = _extract_abc_data_from_tag(tag_type, tag_body)
    print(f"Found ABC block '{block_name}': {len(abc_data)} bytes")
    
    # Step 2: Create editor
    editor = ABCEditor(abc_data)
    
    # List classes for verification
    print(f"Classes: {len(editor.list_classes())}")
    
    # Step 3: Inject traces
    patched = 0
    
    # endAttack — most critical: tells when attack animation signals completion
    if inject_print_with_arg(editor, "SSF2Character", "endAttack", "*** ENDATTACK: "):
        patched += 1
    
    # setState — tracks state transitions
    if inject_print_with_arg(editor, "SSF2Character", "setState", "*** CHAR.SETSTATE: "):
        patched += 1
    
    # toIdle — tracks idle transition
    if inject_print_before_delegate(editor, "SSF2Character", "toIdle", "*** TO_IDLE ***"):
        patched += 1
    
    # switchAttack — tracks attack switching  
    if inject_print_with_arg(editor, "SSF2Character", "switchAttack", "*** SWITCH_ATTACK: "):
        patched += 1
        
    # stancePlayFrame on SSF2GameObject — if it exists
    # This is the key method called by frame scripts to change animation frames
    stpf_idx = find_method_idx(editor, "SSF2GameObject", "stancePlayFrame")
    if stpf_idx is not None:
        body = editor.abc.method_bodies.get(stpf_idx)
        if body:
            print(f"\n--- Patching SSF2GameObject.stancePlayFrame (with arg) ---")
            dump_method(editor, stpf_idx, "BEFORE")
            
            instructions = _parse_instructions(body.code)
            ssf2api_mn = _find_existing_ssf2api_mn(editor)
            print_mn = _find_existing_print_mn(editor)
            prefix_str = editor.ensure_string("*** STANCE_PLAY: ")
            
            asm = Assembler()
            # Emit getlocal_0 + pushscope first
            asm.emit('getlocal_0')
            asm.emit('pushscope')
            # Print trace
            _emit_print_trace_with_arg(asm, ssf2api_mn, print_mn, prefix_str, 1)
            # Replay original, skipping first getlocal_0 + pushscope
            skipped = 0
            for start, end, op, operands in instructions:
                if skipped < 2:
                    if op in (0xD0, 0x30):
                        skipped += 1
                        continue
                asm.emit_raw(op, operands)
            code = asm.assemble()
            editor.replace_method_body(
                stpf_idx, code=code,
                max_stack=max(body.max_stack, 4),
                local_count=body.local_count,
                init_scope_depth=body.init_scope_depth,
                max_scope_depth=body.max_scope_depth,
            )
            dump_method(editor, stpf_idx, "AFTER")
            patched += 1
    
    if patched == 0:
        print("\nERROR: No methods were patched!")
        return
    
    print(f"\n=== Patched {patched} methods ===")
    
    # Step 4: Serialize
    print("\nSerializing modified ABC...")
    new_abc = editor.serialize()
    print(f"New ABC: {len(new_abc)} bytes (was {len(abc_data)} bytes)")
    
    # Step 5: Rebuild the DoABC tag
    if tag_type == TAG_DOABC2:
        new_tag_body = _build_doabc2_tag_body(block_name, new_abc, flags=1)
    else:
        new_tag_body = new_abc
    
    # Step 6: Replace the tag in the SWF
    tags[abc_tag_idx] = (tag_type, new_tag_body)
    
    # Step 7: Write the new SWF
    print(f"Writing {OUT_SWF}...")
    write_swf_from_tags(swf_info, OUT_SWF)
    
    out_size = os.path.getsize(OUT_SWF)
    in_size = os.path.getsize(RT_SWF)
    print(f"Done! {out_size:,} bytes (original: {in_size:,} bytes)")
    print(f"\nDebug SWF: {OUT_SWF}")
    print("Replace fox.ssf/fox.swf with this file and test.")
    print("Look for '***' prefixed messages in the game's output/console.")


if __name__ == '__main__':
    main()
