#!/usr/bin/env python3
"""
Test suite for cjk_font_handler.py

Tests Bug Fix #3: CJK font embedding
Ensures CJK characters are detected and proper font embedding is used.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cjk_font_handler import (
    is_cjk_char,
    has_cjk_chars,
    extract_cjk_chars,
    get_char_ranges,
    estimate_glyph_count,
    select_font_embedding_mode,
    is_chinese,
    is_japanese,
    is_korean,
    FontEmbeddingMode
)


def test_is_cjk_char_chinese():
    """Bug Fix #3: Detect Chinese characters."""
    assert is_cjk_char('你')
    assert is_cjk_char('好')
    assert is_cjk_char('世')
    assert is_cjk_char('界')


def test_is_cjk_char_japanese():
    """Detect Japanese characters (Hiragana/Katakana)."""
    assert is_cjk_char('あ')  # Hiragana
    assert is_cjk_char('ア')  # Katakana
    assert is_cjk_char('ん')  # Hiragana
    assert is_cjk_char('ン')  # Katakana


def test_is_cjk_char_korean():
    """Detect Korean characters (Hangul)."""
    assert is_cjk_char('안')
    assert is_cjk_char('녕')
    assert is_cjk_char('하')
    assert is_cjk_char('세')


def test_is_cjk_char_non_cjk():
    """Non-CJK characters should return False."""
    assert not is_cjk_char('A')
    assert not is_cjk_char('z')
    assert not is_cjk_char('0')
    assert not is_cjk_char(' ')
    assert not is_cjk_char('!')
    assert not is_cjk_char('é')  # Latin extended


def test_has_cjk_chars_chinese():
    """Detect Chinese in mixed text."""
    assert has_cjk_chars("Hello 你好")
    assert has_cjk_chars("你好世界")
    assert has_cjk_chars("123你好ABC")


def test_has_cjk_chars_japanese():
    """Detect Japanese in mixed text."""
    assert has_cjk_chars("こんにちは")
    assert has_cjk_chars("Hello こんにちは")
    assert has_cjk_chars("カタカナ")


def test_has_cjk_chars_korean():
    """Detect Korean in mixed text."""
    assert has_cjk_chars("안녕하세요")
    assert has_cjk_chars("Hello 안녕")


def test_has_cjk_chars_no_cjk():
    """Pure ASCII/Latin text should return False."""
    assert not has_cjk_chars("Hello World")
    assert not has_cjk_chars("123 ABC xyz")
    assert not has_cjk_chars("Café résumé")  # Latin extended


def test_has_cjk_chars_empty():
    """Empty string should return False."""
    assert not has_cjk_chars("")
    assert not has_cjk_chars(None)


def test_extract_cjk_chars():
    """Extract only CJK characters."""
    result = extract_cjk_chars("Hello 你好世界 World")
    assert result == {'你', '好', '世', '界'}


def test_extract_cjk_chars_duplicates():
    """Duplicate CJK chars should appear once."""
    result = extract_cjk_chars("你好你好你")
    assert result == {'你', '好'}


def test_extract_cjk_chars_no_cjk():
    """No CJK chars should return empty set."""
    result = extract_cjk_chars("Hello World")
    assert result == set()


def test_get_char_ranges_chinese():
    """Get Unicode ranges for Chinese text."""
    ranges = get_char_ranges("你好")
    # Should include CJK Unified Ideographs range
    assert (0x4E00, 0x9FFF) in ranges


def test_get_char_ranges_japanese():
    """Get Unicode ranges for Japanese text."""
    ranges = get_char_ranges("あア")
    # Should include Hiragana and Katakana
    assert (0x3040, 0x309F) in ranges  # Hiragana
    assert (0x30A0, 0x30FF) in ranges  # Katakana


def test_get_char_ranges_korean():
    """Get Unicode ranges for Korean text."""
    ranges = get_char_ranges("안녕")
    # Should include Hangul Syllables
    assert (0xAC00, 0xD7AF) in ranges


def test_estimate_glyph_count_ascii():
    """ASCII text should have small glyph count."""
    count = estimate_glyph_count("Hello World")
    assert count < 300  # ASCII + unique chars


def test_estimate_glyph_count_cjk():
    """CJK text should account for each character."""
    count = estimate_glyph_count("你好世界")
    assert count >= 4  # At least 4 CJK chars


def test_select_font_embedding_mode_ascii():
    """ASCII text should use standard font."""
    mode = select_font_embedding_mode("Hello World")
    assert mode == FontEmbeddingMode.DEFINE_FONT


def test_select_font_embedding_mode_cjk():
    """CJK text should use DefineFont3/4."""
    mode = select_font_embedding_mode("你好")
    assert mode in [FontEmbeddingMode.DEFINE_FONT3, FontEmbeddingMode.DEFINE_FONT4]


def test_select_font_embedding_mode_prefer_subset():
    """Small CJK set with prefer_subset should use DefineFont3."""
    mode = select_font_embedding_mode("你好", prefer_subset=True)
    # Small set (2 chars) should use subset
    assert mode == FontEmbeddingMode.DEFINE_FONT3


def test_is_chinese():
    """Detect Chinese text."""
    assert is_chinese("你好")
    assert is_chinese("世界")
    assert not is_chinese("こんにちは")
    assert not is_chinese("Hello")


def test_is_japanese():
    """Detect Japanese text."""
    assert is_japanese("こんにちは")
    assert is_japanese("カタカナ")
    assert not is_japanese("你好")
    assert not is_japanese("Hello")


def test_is_korean():
    """Detect Korean text."""
    assert is_korean("안녕하세요")
    assert not is_korean("你好")
    assert not is_korean("こんにちは")
    assert not is_korean("Hello")


def test_mixed_cjk():
    """Mixed CJK scripts."""
    text = "你好こんにちは안녕"
    
    assert has_cjk_chars(text)
    assert is_chinese(text)
    assert is_japanese(text)
    assert is_korean(text)
    
    cjk_chars = extract_cjk_chars(text)
    assert len(cjk_chars) > 0


def test_edge_case_surrogate_pairs():
    """Handle characters outside BMP (surrogate pairs)."""
    # CJK Extension B character (requires surrogate pair in UTF-16)
    char = '\U00020000'  # First char in CJK Extension B
    
    assert is_cjk_char(char)
    assert has_cjk_chars(char)


def test_performance_large_text():
    """Large text should be processed efficiently."""
    # 1000 repeated Chinese text
    text = "你好世界" * 1000
    
    assert has_cjk_chars(text)
    
    cjk_chars = extract_cjk_chars(text)
    assert cjk_chars == {'你', '好', '世', '界'}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
