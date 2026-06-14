#!/usr/bin/env python3
"""Decompiler postprocess: imports and activation artifacts."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from as3_decompiler.helpers import canonical_import_fqn
from as3_decompiler.postprocess import finalize_decompiled_source


def test_canonical_import_fqn_air_desktop():
    assert canonical_import_fqn(
        "flash.events.NativeWindowDisplayStateEvent"
    ) == "flash.desktop.NativeWindowDisplayStateEvent"


def test_finalize_strips_activation_and_fixes_imports():
    src = """package com.example {
    import flash.events.NativeWindowDisplayStateEvent;
    public class Foo {
        public function bar():void {
            var _local_1:* = __activation__;
            trace(_local_1);
        }
    }
}"""
    out = finalize_decompiled_source(src)
    assert "__activation__" not in out
    assert "flash.desktop.NativeWindowDisplayStateEvent" in out
    assert "flash.events.NativeWindowDisplayStateEvent" not in out
