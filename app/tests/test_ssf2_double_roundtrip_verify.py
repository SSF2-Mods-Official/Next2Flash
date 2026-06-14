"""Tests for SWF→N2D→SWF→N2D verification helpers."""

from ssf2_runner import (
    _find_unqualified_calls,
    compare_abc_inventories,
    compare_n2d_inventories,
    format_verify_report_summary,
)


def test_find_unqualified_calls_detects_logger():
    src = """
package com.mcleodgaming.ssf2.util {
    public class Utils {
        public static function init():void {
            Logger("hello");
        }
    }
}
"""
    calls = _find_unqualified_calls(src)
    assert "Logger" in calls


def test_compare_n2d_inventories_line_regression():
    before = {
        "com/foo/Utils.as": {
            "nonEmptyLines": 200,
            "functions": 40,
            "shellRecovered": True,
        },
        "com/foo/Gone.as": {"nonEmptyLines": 10, "functions": 1},
    }
    after = {
        "com/foo/Utils.as": {"nonEmptyLines": 8, "functions": 1},
    }
    diff = compare_n2d_inventories(before, after)
    assert "com/foo/Gone.as" in diff["missingAfterCompile"]
    assert diff["lineRegressions"][0]["path"] == "com/foo/Utils.as"


def test_compare_abc_inventories_trait_regression():
    before = {
        "com.foo.Utils": {"name": "Utils", "traitCount": 80},
        "com.foo.Removed": {"name": "Removed", "traitCount": 10},
    }
    after = {
        "com.foo.Utils": {"name": "Utils", "traitCount": 2},
    }
    diff = compare_abc_inventories(before, after)
    assert "com.foo.Removed" in diff["missingClasses"]
    assert diff["traitRegressions"][0]["fullName"] == "com.foo.Utils"


def test_format_verify_report_summary():
    text = format_verify_report_summary({
        "import1Count": 421,
        "import2Count": 418,
        "reimportMs": 120000,
        "n2dDiff": {"missingAfterCompile": ["Logger.as"], "lineRegressions": []},
        "abcDiff": {"missingClasses": [], "traitRegressions": []},
        "missingRuntimeSymbols": [{"symbol": "Logger", "referencedFrom": "Utils.as"}],
        "warnings": ["Unresolved runtime symbol Logger (from Utils.as)"],
    })
    assert "SWF→N2D→SWF→N2D" in text
    assert "Logger" in text
