"""The published app is a small launcher plus one runtime folder."""

import json
import os
import subprocess
import tempfile

import pytest

from app_icon import _ico_images, main as icon_main, set_windows_exe_icon, write_ico

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_launcher_starts_runtime_exe():
    path = os.path.join(ROOT, "app", "electron", "launcher.cs")
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    assert 'Path.Combine(baseDir, "runtime")' in text
    assert 'Path.Combine(runtime, "Next2Flash.exe")' in text


def test_icon_png_is_the_app_icon():
    png = os.path.join(ROOT, "app", "icon.png")
    assert os.path.isfile(png)
    package_path = os.path.join(ROOT, "app", "electron", "package.json")
    with open(package_path, encoding="utf-8") as handle:
        package = json.load(handle)
    assert package["build"]["win"]["icon"] == "../icon.png"
    assert "icon.png" in package["build"]["extraResources"][0]["filter"]
    main = os.path.join(ROOT, "app", "electron", "main.js")
    with open(main, encoding="utf-8") as handle:
        text = handle.read()
    assert "const APP_ICON = path.join(APP_DIR, 'icon.png')" in text
    assert "icon: APP_ICON" in text
    publish = os.path.join(ROOT, "publish.bat")
    with open(publish, encoding="utf-8") as handle:
        script = handle.read()
    assert "app\\lib\\app_icon.py" in script
    assert "/win32icon:" in script


def test_icon_cli_writes_ico_without_an_exe():
    png = os.path.join(ROOT, "app", "icon.png")
    with tempfile.TemporaryDirectory() as folder:
        ico = os.path.join(folder, "icon.ico")
        assert icon_main([png, ico]) == 0
        assert os.path.isfile(ico)


def test_exe_icon_comes_from_png():
    csc = os.path.join(
        os.environ.get("WINDIR", r"C:\Windows"),
        "Microsoft.NET",
        "Framework64",
        "v4.0.30319",
        "csc.exe",
    )
    if not os.path.isfile(csc):
        pytest.skip("csc.exe is not installed")
    source = os.path.join(ROOT, "app", "electron", "launcher.cs")
    png = os.path.join(ROOT, "app", "icon.png")
    with tempfile.TemporaryDirectory() as folder:
        exe = os.path.join(folder, "Next2Flash.exe")
        ico = os.path.join(folder, "icon.ico")
        compiled = subprocess.run(
            [
                csc,
                "/nologo",
                "/target:winexe",
                "/optimize+",
                "/out:" + exe,
                "/reference:System.Windows.Forms.dll",
                source,
            ],
            capture_output=True,
            text=True,
        )
        assert compiled.returncode == 0, compiled.stdout + compiled.stderr
        write_ico(png, ico)
        set_windows_exe_icon(exe, ico)
        blob = _ico_images(ico)[-1][1]
        with open(exe, "rb") as handle:
            stamped = handle.read()
        assert blob in stamped


def test_publish_writes_runtime_folder():
    path = os.path.join(ROOT, "publish.bat")
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    assert '"%RELEASE%\\runtime"' in text
    assert "launcher.cs" in text


def test_launcher_compiles():
    csc = os.path.join(
        os.environ.get("WINDIR", r"C:\Windows"),
        "Microsoft.NET",
        "Framework64",
        "v4.0.30319",
        "csc.exe",
    )
    if not os.path.isfile(csc):
        pytest.skip("csc.exe is not installed")
    source = os.path.join(ROOT, "app", "electron", "launcher.cs")
    with tempfile.TemporaryDirectory() as folder:
        out = os.path.join(folder, "Next2Flash.exe")
        proc = subprocess.run(
            [
                csc,
                "/nologo",
                "/target:winexe",
                "/optimize+",
                "/out:" + out,
                "/reference:System.Windows.Forms.dll",
                source,
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        with open(out, "rb") as handle:
            assert handle.read(2) == b"MZ"
