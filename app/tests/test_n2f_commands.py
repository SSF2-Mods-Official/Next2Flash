"""n2f --help lists every command the wiki says is the CLI."""

import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
N2F = APP / "n2f.py"

REQUIRED = (
    "convert",
    "project",
    "compile",
    "patch",
    "decompile",
    "info",
    "server",
    "profiler",
    "open",
    "toolchain",
    "fla",
    "ffdec",
    "mxmlc",
    "asconfig",
)


def test_help_lists_documented_commands():
    proc = subprocess.run(
        [sys.executable, str(N2F), "--help"],
        cwd=str(APP),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    text = proc.stdout
    missing = [name for name in REQUIRED if name not in text]
    assert not missing, "n2f --help is missing: " + ", ".join(missing)
