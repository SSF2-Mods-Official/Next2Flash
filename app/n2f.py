#!/usr/bin/env python3
"""
n2f — Next2Flash unified command-line tool.

Every operation available in the GUI can be done from this CLI:

  n2f convert   input.swf  [-o output.n2d]     SWF/SSF -> N2D
  n2f project   input.swf  [-o output_dir]     SWF -> editable project folder
  n2f compile   input.n2d  [-o output.swf]     N2D/folder -> SWF
  n2f decompile input.swf  [--class X | --all]  AS3 bytecode -> source
  n2f info      input.n2d                       Show project metadata
  n2f server    [--port 5000]                   Start the HTTP server
  n2f profiler  [--port 5000] [--seconds 30]    Capture perf data from a running server
  n2f open      [input.n2d]                     Launch desktop app (optionally with a file)

Each sub-command maps directly to its GUI equivalent so automation
scripts can do anything the editor UI can do, without needing a display.
"""

from __future__ import annotations

import argparse
import json
import logging
import msgpack
import os
import sys
import time

log = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ═══════════════════════════════════════════════════════════════════════════
#  convert  —  SWF/SSF -> N2D
# ═══════════════════════════════════════════════════════════════════════════

def cmd_convert(args):
    """Convert a .swf or .ssf file into a .n2d project file."""
    log.info("cmd_convert: input=%s output=%s", args.input, args.output)
    sys.path.insert(0, SCRIPT_DIR)
    import swf_to_n2d as mod

    swf_path = args.input
    if not os.path.isfile(swf_path):
        print(f"Error: file not found: {swf_path}", file=sys.stderr)
        return 1

    name = os.path.splitext(os.path.basename(swf_path))[0]
    output = args.output or name + ".n2d"

    t0 = time.time()
    step = lambda msg: print(f"[{time.time()-t0:6.1f}s] {msg}", flush=True)

    step("Parsing SWF binary...")
    with open(swf_path, "rb") as f:
        swf_data = f.read()
    header, tags = mod.parse_swf(swf_data)
    step(f"SWF: {header['width']}x{header['height']} @ {header['fps']}fps, "
         f"{header['frameCount']} frames, {len(tags)} tags")

    step("Building n2d project...")
    builder = mod.N2DBuilder(header, name=name)
    builder.catalog_swf_tags(tags)

    step("Decompiling AS3 scripts...")
    scripts, frame_scripts = mod.decompile_all_scripts(builder.global_raw_tags)
    builder.frame_scripts = frame_scripts
    if scripts:
        builder.scripts.extend(scripts)
    step(f"  {len(scripts)} scripts, {len(frame_scripts)} frame-script classes")

    step("Building library entries...")
    builder.build_all()

    step("Building main timeline...")
    builder.build_main_timeline(tags)

    step("Generating .n2d output...")
    n2d = builder.to_n2d_json()
    mod.save_n2d(n2d, output)
    step(f"DONE: {output} ({os.path.getsize(output):,} bytes)")
    return 0


# ═══════════════════════════════════════════════════════════════════════════
#  project  —  SWF -> Project Folder (editable PNG/WAV/AS)
# ═══════════════════════════════════════════════════════════════════════════

def cmd_project(args):
    """Convert a SWF into an editable project folder with PNG/WAV/AS files."""
    log.info("cmd_project: input=%s output=%s", args.input, args.output)
    sys.path.insert(0, SCRIPT_DIR)
    import swf_to_n2d as mod

    swf_path = args.input
    if not os.path.isfile(swf_path):
        print(f"Error: file not found: {swf_path}", file=sys.stderr)
        return 1

    name = os.path.splitext(os.path.basename(swf_path))[0]
    output_dir = args.output or name

    t0 = time.time()
    step = lambda msg: print(f"[{time.time()-t0:6.1f}s] {msg}", flush=True)

    step("Parsing SWF binary...")
    with open(swf_path, "rb") as f:
        swf_data = f.read()
    header, tags = mod.parse_swf(swf_data)
    step(f"SWF: {header['width']}x{header['height']} @ {header['fps']}fps, "
         f"{header['frameCount']} frames, {len(tags)} tags")

    step("Building n2d project...")
    builder = mod.N2DBuilder(header, name=name)
    builder.catalog_swf_tags(tags)

    step("Decompiling AS3 scripts...")
    scripts, frame_scripts = mod.decompile_all_scripts(builder.global_raw_tags)
    builder.frame_scripts = frame_scripts
    if scripts:
        builder.scripts.extend(scripts)
    step(f"  {len(scripts)} scripts, {len(frame_scripts)} frame-script classes")

    step("Building library entries...")
    builder.build_all()

    step("Building main timeline...")
    builder.build_main_timeline(tags)

    step("Generating project folder...")
    n2d = builder.to_n2d_json()
    mod.save_project_folder(n2d, output_dir)
    step(f"DONE: project folder at {output_dir}")
    return 0


# ═══════════════════════════════════════════════════════════════════════════
#  compile  —  N2D -> SWF
# ═══════════════════════════════════════════════════════════════════════════

def cmd_compile(args):
    """Compile a .n2d project file or project folder back into a .swf."""
    log.info("cmd_compile: input=%s output=%s", args.input, args.output)
    sys.path.insert(0, SCRIPT_DIR)
    import compile_n2d as mod

    n2d_path = args.input
    if not os.path.isfile(n2d_path) and not os.path.isdir(n2d_path):
        print(f"Error: file or folder not found: {n2d_path}", file=sys.stderr)
        return 1

    if os.path.isdir(n2d_path):
        name = os.path.basename(n2d_path.rstrip('/\\'))
    else:
        name = os.path.splitext(os.path.basename(n2d_path))[0]
    output = args.output or name + ".swf"
    _default_shared = os.path.join(SCRIPT_DIR, "shared")
    shared = args.shared or (_default_shared if os.path.isdir(_default_shared) else None)

    t0 = time.time()
    print(f"Compiling {n2d_path} -> {output} ...", flush=True)

    compiler = mod.N2DCompiler(
        n2d_path=n2d_path,
        shared_dir=shared,
        output_path=output,
        sdk_path=args.sdk,
    )
    compiler.compile()

    print(f"DONE in {time.time()-t0:.1f}s: {output} ({os.path.getsize(output):,} bytes)")
    return 0


# ═══════════════════════════════════════════════════════════════════════════
#  decompile  —  AS3 bytecode -> source
# ═══════════════════════════════════════════════════════════════════════════

def cmd_decompile(args):
    """Decompile AS3 bytecode from a SWF file."""
    log.info("cmd_decompile: input=%s", args.input)
    sys.path.insert(0, SCRIPT_DIR)
    from as3_decompiler.cli import main as decompiler_main

    # Forward to the existing decompiler CLI
    sys.argv = ["as3_decompiler", args.input]
    if args.list_classes:
        sys.argv.append("--list")
    elif args.class_name:
        sys.argv.extend(["--class", args.class_name])
    elif args.all:
        sys.argv.append("--all")
    if args.outdir:
        sys.argv.extend(["--outdir", args.outdir])
    if args.verbose:
        sys.argv.append("--verbose")

    return decompiler_main()


# ═══════════════════════════════════════════════════════════════════════════
#  info  —  Inspect an N2D project
# ═══════════════════════════════════════════════════════════════════════════

def cmd_info(args):
    """Display metadata about an N2D project file."""
    log.debug("cmd_info: input=%s", args.input)
    n2d_path = args.input
    if not os.path.isfile(n2d_path):
        print(f"Error: file not found: {n2d_path}", file=sys.stderr)
        return 1

    file_size = os.path.getsize(n2d_path)
    print(f"File: {n2d_path} ({file_size:,} bytes)")

    # Try ZIP format first (PK magic)
    with open(n2d_path, "rb") as f:
        magic = f.read(2)

    data = None
    if magic == b"PK":
        import zipfile
        with zipfile.ZipFile(n2d_path, "r") as zf:
            # Try MessagePack first, fall back to JSON
            if 'project.msgpack' in zf.namelist():
                print('Format: MessagePack (binary)')
                with zf.open("project.msgpack") as pf:
                    data = msgpack.unpackb(pf.read(), raw=False)
            else:
                print('Format: JSON (legacy)')
                with zf.open("project.json") as pf:
                    data = json.loads(pf.read())
    else:
        import zlib
        with open(n2d_path, "rb") as f:
            raw = f.read()
        try:
            decompressed = zlib.decompress(raw)
            # The data may be URI-encoded. Try decoding as latin-1 first.
            text = decompressed.decode("latin-1")
            # Quick check: if starts with %7B or { it's JSON (possibly encoded)
            if text.startswith("%"):
                import urllib.parse
                # For huge files, unquote_to_bytes is faster
                decoded = urllib.parse.unquote_to_bytes(text)
                data = json.loads(decoded)
            else:
                data = json.loads(text)
        except Exception:
            try:
                data = json.loads(raw)
            except Exception:
                pass

    if not data:
        print("Error: could not parse N2D file", file=sys.stderr)
        return 1

    # Scene info
    stage = data.get("stage", {})
    print(f"Stage: {stage.get('width', '?')}x{stage.get('height', '?')} "
          f"@ {stage.get('fps', '?')}fps, bg={stage.get('bgColor', '?')}")

    # Libraries
    libs = data.get("libraries", [])
    type_counts = {}
    for lib in libs:
        t = lib.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    print(f"Libraries: {len(libs)} total")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")

    # Timeline
    tl = data.get("timeline", data.get("scene", {}))
    if isinstance(tl, dict):
        layers = tl.get("layers", [])
        total_frames = 0
        for layer in layers:
            frames = layer.get("frames", [])
            for fr in frames:
                fn = fr.get("frame", 0)
                if fn > total_frames:
                    total_frames = fn
        print(f"Timeline: {len(layers)} layers, ~{total_frames + 1} frames")

    # Scripts
    scripts = data.get("scripts", [])
    if scripts:
        print(f"AS3 Scripts: {len(scripts)}")

    # SWF roundtrip fields
    if data.get("swfVersion"):
        print(f"SWF version: {data['swfVersion']}")
    if data.get("rawGlobalTags"):
        print(f"Raw global tags: {len(data['rawGlobalTags'])}")
    if data.get("rootTimelineDefIds"):
        print(f"Root timeline def IDs: {len(data['rootTimelineDefIds'])}")

    if args.json:
        # Dump full JSON (minus large binary fields)
        slim = {k: v for k, v in data.items() if k != "libraries"}
        slim["libraries_summary"] = type_counts
        print(json.dumps(slim, indent=2))

    return 0


# ═══════════════════════════════════════════════════════════════════════════
#  server  —  Start the HTTP conversion server
# ═══════════════════════════════════════════════════════════════════════════

def cmd_server(args):
    """Start the Next2Flash HTTP server."""
    log.info("cmd_server: host=%s port=%d", args.host, args.port)
    sys.path.insert(0, SCRIPT_DIR)
    sys.argv = ["server.py", "--port", str(args.port), "--host", args.host]
    if args.no_browser:
        sys.argv.append("--no-browser")
    import server
    server.main()
    return 0


# ═══════════════════════════════════════════════════════════════════════════
#  profiler  —  Capture performance data from a running server
# ═══════════════════════════════════════════════════════════════════════════

def cmd_profiler(args):
    """Capture profiler data from a running Next2Flash instance.

    Polls the server's /api/profile endpoint and prints live stats,
    or connects to the profiler-instrument.js ring buffer via CDP.
    """
    log.info("cmd_profiler: host=%s port=%d seconds=%d", args.host, args.port, args.seconds)
    import urllib.request
    import urllib.error

    base = f"http://{args.host}:{args.port}"
    duration = args.seconds
    output = args.output

    print(f"Polling profiler at {base} for {duration}s ...")

    # Check server is alive
    try:
        urllib.request.urlopen(f"{base}/api/health", timeout=3)
    except Exception:
        print(f"Error: server not reachable at {base}", file=sys.stderr)
        print("Start the app first, or run: n2f server", file=sys.stderr)
        return 1

    # Poll the profile log endpoint
    collected = []
    t_end = time.time() + duration
    interval = 2
    while time.time() < t_end:
        try:
            with open(os.path.join(SCRIPT_DIR, "_profile.log"), "r") as f:
                lines = f.readlines()
                if lines:
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            collected.append(line)
                            print(line)
        except FileNotFoundError:
            pass
        time.sleep(interval)

    if output:
        with open(output, "w") as f:
            f.write("\n".join(collected))
        print(f"\nSaved {len(collected)} samples to {output}")
    else:
        print(f"\nCaptured {len(collected)} profiler samples")

    return 0


# ═══════════════════════════════════════════════════════════════════════════
#  open  —  Launch the desktop app
# ═══════════════════════════════════════════════════════════════════════════

def cmd_open(args):
    """Launch the Next2Flash desktop application."""
    log.info("cmd_open")
    import subprocess

    # Find the exe
    candidates = [
        os.path.join(SCRIPT_DIR, "src-tauri", "target", "release", "next2flash.exe"),
        os.path.join(SCRIPT_DIR, "src-tauri", "target", "debug", "next2flash.exe"),
    ]
    exe = None
    for c in candidates:
        if os.path.isfile(c):
            exe = c
            break

    if not exe:
        print("Error: next2flash.exe not found. Build with: cd src-tauri && cargo build", file=sys.stderr)
        return 1

    cmd = [exe]
    print(f"Launching {exe} ...")
    proc = subprocess.Popen(cmd)

    if args.wait:
        proc.wait()
        return proc.returncode

    print(f"PID: {proc.pid}")
    return 0


# ═══════════════════════════════════════════════════════════════════════════
#  Main argument parser
# ═══════════════════════════════════════════════════════════════════════════

def main():
    log.debug("n2f main: argv=%s", sys.argv)
    parser = argparse.ArgumentParser(
        prog="n2f",
        description="Next2Flash CLI — all editor operations from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  n2f convert game.swf                     # SWF -> N2D
  n2f convert game.swf -o game.n2d         # SWF -> N2D (named output)
  n2f project game.swf                     # SWF -> project folder (PNG/WAV/AS)
  n2f project game.swf -o my_project/      # SWF -> named project folder
  n2f compile game.n2d                     # N2D -> SWF
  n2f compile game.n2d -o game.swf         # N2D -> SWF (named output)
  n2f compile my_project/                  # Project folder -> SWF
  n2f decompile game.swf --list            # List AS3 classes
  n2f decompile game.swf --all -d out/     # Decompile all classes
  n2f info game.n2d                        # Show project metadata
  n2f server --port 5000                   # Start HTTP server
  n2f profiler --seconds 60               # Capture 60s of profiler data
  n2f open                                 # Launch desktop app
""",
    )

    sub = parser.add_subparsers(dest="command", help="Command to run")

    # ── convert ────────────────────────────────────────────────────
    p = sub.add_parser("convert", help="Convert SWF/SSF to N2D",
                       aliases=["swf2n2d", "import"])
    p.add_argument("input", help="Input .swf or .ssf file")
    p.add_argument("-o", "--output", help="Output .n2d path")
    p.set_defaults(func=cmd_convert)

    # ── project ────────────────────────────────────────────────────
    p = sub.add_parser("project", help="Import SWF into editable project folder",
                       aliases=["extract"])
    p.add_argument("input", help="Input .swf file")
    p.add_argument("-o", "--output", help="Output folder path (default: SWF name)")
    p.set_defaults(func=cmd_project)

    # ── compile ────────────────────────────────────────────────────
    p = sub.add_parser("compile", help="Compile N2D/project folder to SWF",
                       aliases=["n2d2swf", "export"])
    p.add_argument("input", help="Input .n2d file or project folder")
    p.add_argument("-o", "--output", help="Output .swf path")
    p.add_argument("--shared", help="Path to shared AS3 source directory")
    p.add_argument("--sdk", help="Path to Flex/AIR SDK")
    p.set_defaults(func=cmd_compile)

    # ── decompile ──────────────────────────────────────────────────
    p = sub.add_parser("decompile", help="Decompile AS3 from SWF",
                       aliases=["as3"])
    p.add_argument("input", help="Input .swf file")
    p.add_argument("-l", "--list", dest="list_classes", action="store_true",
                   help="List class names")
    p.add_argument("-c", "--class", dest="class_name",
                   help="Decompile a specific class")
    p.add_argument("-a", "--all", action="store_true",
                   help="Decompile all classes")
    p.add_argument("-d", "--outdir", help="Output directory for --all")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_decompile)

    # ── info ───────────────────────────────────────────────────────
    p = sub.add_parser("info", help="Show N2D project info",
                       aliases=["inspect"])
    p.add_argument("input", help="Input .n2d file")
    p.add_argument("--json", action="store_true",
                   help="Also dump JSON metadata")
    p.set_defaults(func=cmd_info)

    # ── server ─────────────────────────────────────────────────────
    p = sub.add_parser("server", help="Start HTTP conversion server",
                       aliases=["serve"])
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--no-browser", action="store_true")
    p.set_defaults(func=cmd_server)

    # ── profiler ───────────────────────────────────────────────────
    p = sub.add_parser("profiler", help="Capture profiler data",
                       aliases=["perf", "profile"])
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--seconds", type=int, default=30,
                   help="Duration to capture (default: 30)")
    p.add_argument("-o", "--output", help="Save data to file")
    p.set_defaults(func=cmd_profiler)

    # ── open ───────────────────────────────────────────────────────
    p = sub.add_parser("open", help="Launch desktop app",
                       aliases=["launch", "gui"])
    p.add_argument("--wait", action="store_true",
                   help="Wait for app to exit")
    p.set_defaults(func=cmd_open)

    args = parser.parse_args()

    # ── Configure logging so all debug calls print to terminal ──
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stdout,
    )

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
