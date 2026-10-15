"""The bundled FFDec / Flex lite toolchain resolves to real files."""

import json
import os
import subprocess

from toolchain_home import aflex_lite_dir, asconfigc_jar, ffdec_jar, java_exe


def test_ffdec_jar_exists():
    jar = ffdec_jar()
    assert jar and os.path.isfile(jar)


def test_java_and_flex_lite_exist():
    java = java_exe()
    lite = aflex_lite_dir()
    assert java and os.path.isfile(java)
    assert lite and os.path.isfile(os.path.join(lite, "bin", "mxmlc.bat"))
    assert os.path.isfile(os.path.join(lite, "bin", "adl.exe"))


def test_java_runtime_is_jlink():
    java = java_exe()
    assert java and os.path.isfile(java)
    proc = subprocess.run(
        [java, "--list-modules"],
        capture_output=True,
        text=True,
        check=True,
    )
    names = {line.split("@", 1)[0] for line in proc.stdout.splitlines() if line.strip()}
    assert "java.desktop" in names
    assert "java.se" not in names
    assert "jdk.internal.vm.compiler" not in names


def test_release_keeps_english_locale():
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    package = os.path.join(app_dir, "electron", "package.json")
    with open(package, encoding="utf-8") as handle:
        data = json.load(handle)
    assert data["build"]["electronLanguages"] == ["en-US"]


def test_asconfigc_jar_exists():
    jar = asconfigc_jar()
    assert jar and os.path.isfile(jar)
