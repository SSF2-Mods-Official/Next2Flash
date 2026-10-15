"""Locate the Flash toolchain owned by Next2Flash.

FFDec (JPEXS), the Flex/AIR lite SDK, asconfigc, and a
JRE live under the repo-root ``toolchain/`` folder. ``n2f`` resolves
these paths instead of shipping a second copy.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Optional

_here = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(_here) if os.path.basename(_here) == "lib" else _here
REPO_ROOT = os.path.dirname(APP_DIR)


def toolchain_dir() -> str:
    env = os.environ.get("N2F_TOOLCHAIN")
    if env and os.path.isdir(env):
        return os.path.abspath(env)

    candidates = [os.path.join(REPO_ROOT, "toolchain")]
    web = os.environ.get("N2F_WEB_ROOT")
    if web:
        candidates.append(os.path.join(os.path.dirname(web), "toolchain"))
    candidates.append(os.path.join(os.getcwd(), "toolchain"))
    for candidate in candidates:
        if os.path.isdir(candidate):
            return candidate
    return candidates[0]


def ffdec_dir() -> Optional[str]:
    path = os.path.join(toolchain_dir(), "ffdec")
    if os.path.isfile(os.path.join(path, "ffdec.jar")):
        return path
    return None


def ffdec_jar() -> Optional[str]:
    directory = ffdec_dir()
    if not directory:
        return None
    jar = os.path.join(directory, "ffdec.jar")
    return jar if os.path.isfile(jar) else None


def java_exe() -> Optional[str]:
    name = "java.exe" if os.name == "nt" else "java"
    candidates = [
        os.path.join(toolchain_dir(), "jre", "bin", name),
    ]
    java_home = os.environ.get("JAVA_HOME") or os.environ.get("JRE_HOME")
    if java_home:
        candidates.append(os.path.join(java_home, "bin", name))
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return shutil.which("java")


def aflex_lite_dir() -> Optional[str]:
    path = os.path.join(toolchain_dir(), "aflex_lite")
    for name in ("mxmlc.bat", "mxmlc"):
        if os.path.isfile(os.path.join(path, "bin", name)):
            return path
    return None


def asconfigc_jar() -> Optional[str]:
    jar = os.path.join(toolchain_dir(), "asconfigc", "asconfigc.jar")
    if os.path.isfile(jar):
        return jar
    env = os.environ.get("ASCONFIGC_JAR")
    if env and os.path.isfile(env):
        return env
    return None


def describe() -> dict:
    return {
        "toolchain": toolchain_dir(),
        "ffdec": ffdec_dir(),
        "java": java_exe(),
        "aflex_lite": aflex_lite_dir(),
        "asconfigc": asconfigc_jar(),
    }


def _quote_worker_arg(arg: str) -> str:
    if arg == "" or any(ch.isspace() or ch == '"' for ch in arg):
        return '"' + arg.replace('"', "") + '"'
    return arg


def run_ffdec(args: list[str]) -> int:
    """Run bundled FFDec. Identifier commands go through the warm-worker jar."""
    java = java_exe()
    directory = ffdec_dir()
    jar = ffdec_jar()
    if not java or not directory or not jar:
        print(
            "FFDec toolchain is missing. Expected toolchain/ffdec/ffdec.jar "
            "and toolchain/jre/bin/java.exe.",
            file=sys.stderr,
        )
        return 1

    args = [a for a in args if a != "--"]
    if not args:
        args = ["-help"]

    worker = os.path.join(directory, "ffdec-worker.jar")
    if args[0] == "--worker" and os.path.isfile(worker):
        return _serve_ffdec_worker(java, directory, jar, worker)
    custom = args[0].lower() in {"-identdump", "-identrewrite", "-untypestance", "-placeedit"}
    if custom and os.path.isfile(worker):
        return _run_ffdec_worker(java, directory, jar, worker, args)

    completed = subprocess.run(
        [java, "-Djava.awt.headless=true", "-jar", jar, *args],
        cwd=directory,
    )
    return int(completed.returncode or 0)


def _worker_command(java: str, directory: str, jar: str, worker: str) -> list[str]:
    lib_glob = os.path.join(directory, "lib", "*")
    classpath = os.pathsep.join([worker, jar, lib_glob])
    return [
        java,
        "-Xmx2048m",
        "-Djava.awt.headless=true",
        "-Dn2f.fastFla=true",
        "-Dn2f.worker=true",
        "-cp",
        classpath,
        "next2flash.ffdec.FfdecWorker",
    ]


def _serve_ffdec_worker(java: str, directory: str, jar: str, worker: str) -> int:
    """Stay open and let the caller talk to the FFDec worker on stdin/stdout."""
    proc = subprocess.Popen(
        _worker_command(java, directory, jar, worker),
        cwd=directory,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    return int(proc.wait() or 0)


def _run_ffdec_worker(java: str, directory: str, jar: str, worker: str, args: list[str]) -> int:
    proc = subprocess.Popen(
        _worker_command(java, directory, jar, worker),
        cwd=directory,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    assert proc.stdin and proc.stdout
    ready = proc.stdout.readline().strip()
    if ready != "READY":
        proc.kill()
        err = proc.stderr.read() if proc.stderr else ""
        print(err or f"FFDec worker failed to start ({ready!r})", file=sys.stderr)
        return 1

    line = " ".join(_quote_worker_arg(arg) for arg in args)
    proc.stdin.write(line + "\nEXIT\n")
    proc.stdin.flush()
    proc.stdin.close()
    status = 1
    for raw in proc.stdout:
        text = raw.strip()
        if text == "OK":
            status = 0
        elif text.startswith("ERR "):
            print(text[4:], file=sys.stderr)
            status = 1
        elif text not in {"BYE", "READY", ""}:
            print(text)
    proc.wait(timeout=30)
    return status


def run_mxmlc(args: list[str]) -> int:
    args = [a for a in args if a != "--"]
    sdk = aflex_lite_dir()
    java = java_exe()
    if not sdk:
        print("Flex lite SDK not found at toolchain/aflex_lite.", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env["FLEX_HOME"] = sdk
    jar = os.path.join(sdk, "lib", "mxmlc.jar")
    if java and os.path.isfile(jar):
        completed = subprocess.run([java, "-jar", jar, *args], cwd=sdk, env=env)
        return int(completed.returncode or 0)

    bat = os.path.join(sdk, "bin", "mxmlc.bat" if os.name == "nt" else "mxmlc")
    if not os.path.isfile(bat):
        print(f"mxmlc not found in {sdk}", file=sys.stderr)
        return 1
    completed = subprocess.run([bat, *args], cwd=sdk, env=env)
    return int(completed.returncode or 0)


def run_asconfig(project: str, sdk: Optional[str] = None, debug: bool = False) -> int:
    java = java_exe()
    jar = asconfigc_jar()
    sdk_path = sdk or aflex_lite_dir()
    if not java or not jar or not sdk_path:
        print(
            "asconfigc needs toolchain/jre, toolchain/asconfigc/asconfigc.jar, "
            "and toolchain/aflex_lite.",
            file=sys.stderr,
        )
        return 1
    if not os.path.isfile(project):
        print(f"Project not found: {project}", file=sys.stderr)
        return 1
    command = [java, "-jar", jar, "--sdk", sdk_path, "--project", os.path.abspath(project)]
    if debug:
        command.append("--debug=true")
    completed = subprocess.run(
        command,
        cwd=os.path.dirname(os.path.abspath(project)),
    )
    return int(completed.returncode or 0)
