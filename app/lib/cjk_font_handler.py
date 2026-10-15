#!/usr/bin/env python3
"""
cjk_font_handler.py — CJK (Chinese/Japanese/Korean) font embedding support

Problem: CJK characters don't render (show as empty boxes) because:
  - Standard DefineFont tags only embed limited glyph ranges
  - SWF text system defaults to ASCII/Latin-1 (codepages)
  - Missing Unicode support for large CJK character sets

Solution: Detect CJK text and use DefineFont3/DefineFont4 with full embedding.

Usage:
    from cjk_font_handler import has_cjk_chars, FontEmbeddingMode
    
    text = "Hello 你好 こんにちは"
    
    if has_cjk_chars(text):
        mode = FontEmbeddingMode.DEFINE_FONT3
        # Use full Unicode embedding
    else:
        mode = FontEmbeddingMode.DEFINE_FONT
        # Use standard embedding
"""

import re
from enum import IntEnum
from typing import Set


class FontEmbeddingMode(IntEnum):
    """Font embedding modes for different text types."""
    DEFINE_FONT = 10      # Standard font (ASCII/Latin-1)
    DEFINE_FONT2 = 48     # Extended font with layout
    DEFINE_FONT3 = 75     # Full Unicode support (for CJK)
    DEFINE_FONT4 = 91     # CFF font (OpenType)


# CJK Unicode ranges
CJK_RANGES = [
    (0x4E00, 0x9FFF),    # CJK Unified Ideographs (Common)
    (0x3400, 0x4DBF),    # CJK Unified Ideographs Extension A
    (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
    (0x2A700, 0x2B73F),  # CJK Unified Ideographs Extension C
    (0x2B740, 0x2B81F),  # C JK Unified Ideographs Extension D
    (0x2B820, 0x2CEAF),  # CJK Unified Ideographs Extension E
    (0x3040, 0x309F),    # Hiragana (Japanese)
    (0x30A0, 0x30FF),    # Katakana (Japanese)
    (0xAC00, 0xD7AF),    # Hangul Syllables (Korean)
    (0x1100, 0x11FF),    # Hangul Jamo (Korean)
    (0x3130, 0x318F),    # Hangul Compatibility Jamo (Korean)
    (0x2E80, 0x2EFF),    # CJK Radicals Supplement
    (0x31C0, 0x31EF),    # CJK Strokes
    (0x3200, 0x32FF),    # Enclosed CJK Letters and Months
    (0x3300, 0x33FF),    # CJK Compatibility
    (0xF900, 0xFAFF),    # CJK Compatibility Ideographs
    (0xFE30, 0xFE4F),    # CJK Compatibility Forms
    (0xFF00, 0xFFEF),    # Halfwidth and Fullwidth Forms
]


def is_cjk_char(char: str) -> bool:
    """
    Check if a single character is CJK.
    
    Args:
        char: Single character to check
    
    Returns:
        True if character is in CJK Unicode ranges
    
    Example:
        >>> is_cjk_char('你')
        True
        >>> is_cjk_char('A')
        False
    """
    if not char:
        return False
    
    code = ord(char)
    return any(start <= code <= end for start, end in CJK_RANGES)


def has_cjk_chars(text: str) -> bool:
    """
    Check if text contains any CJK characters.
    
    Args:
        text: Text to check
    
    Returns:
        True if text contains at least one CJK character
    
    Example:
        >>> has_cjk_chars("Hello World")
        False
        >>> has_cjk_chars("Hello 你好")
        True
        >>> has_cjk_chars("こんにちは")
        True
        >>> has_cjk_chars("안녕하세요")
        True
    """
    if not text:
        return False
    
    return any(is_cjk_char(char) for char in text)


def extract_cjk_chars(text: str) -> Set[str]:
    """
    Extract all unique CJK characters from text.
    
    Useful for determining which glyphs need to be embedded.
    
    Args:
        text: Text to analyze
    
    Returns:
        Set of unique CJK characters
    
    Example:
        >>> extract_cjk_chars("你好世界 Hello")
        {'你', '好', '世', '界'}
    """
    return {char for char in text if is_cjk_char(char)}


def get_char_ranges(text: str) -> Set[tuple]:
    """
    Get all Unicode ranges needed for text.
    
    Returns set of (start, end) tuples for ranges that contain
    characters from the input text.
    
    Args:
        text: Text to analyze
    
    Returns:
        Set of (start, end) range tuples needed
    
    Example:
        >>> get_char_ranges("Hello 你好")
        {(0x4E00, 0x9FFF)}  # CJK Unified Ideographs range
    """
    if not text:
        return set()
    
    needed_ranges = set()
    for char in text:
        code = ord(char)
        for start, end in CJK_RANGES:
            if start <= code <= end:
                needed_ranges.add((start, end))
                break
    
    return needed_ranges


def estimate_glyph_count(text: str) -> int:
    """
    Estimate number of glyphs needed for text.
    
    For CJK text, this can be large (thousands of glyphs).
    Used to determine whether to use subset or full font embedding.
    
    Args:
        text: Text to analyze
    
    Returns:
        Estimated glyph count
    
    Notes:
        - ASCII: ~128 glyphs
        - Latin Extended: +256 glyphs
        - CJK (minimal): unique chars in text
        - CJK (full): 20,000+ glyphs per range
    """
    if not has_cjk_chars(text):
        # Non-CJK: just count unique chars + ASCII base
        return min(256, len(set(text)) + 128)
    
    # CJK: count unique CJK chars
    cjk_chars = extract_cjk_chars(text)
    non_cjk_chars = set(text) - cjk_chars
    
    return len(cjk_chars) + len(non_cjk_chars) + 128  # +128 for ASCII base


def select_font_embedding_mode(text: str, prefer_subset: bool = True) -> FontEmbeddingMode:
    """
    Select appropriate font embedding mode for text.
    
    Args:
        text: Text to be rendered
        prefer_subset: If True, use subset embedding for CJK (smaller file)
                      If False, use full font embedding (better compatibility)
    
    Returns:
        FontEmbeddingMode enum value
    
    Example:
        >>> select_font_embedding_mode("Hello World")
        <FontEmbeddingMode.DEFINE_FONT: 10>
        >>> select_font_embedding_mode("你好")
        <FontEmbeddingMode.DEFINE_FONT3: 75>
    """
    if not has_cjk_chars(text):
        # Standard ASCII/Latin text
        return FontEmbeddingMode.DEFINE_FONT
    
    # CJK text requires full Unicode support
    glyph_count = estimate_glyph_count(text)
    
    if prefer_subset and glyph_count < 500:
        # Small subset: DefineFont3 with explicit glyph list
        return FontEmbeddingMode.DEFINE_FONT3
    else:
        # Large set or full embedding: DefineFont4 (CFF/OpenType)
        return FontEmbeddingMode.DEFINE_FONT4


# Language detection helpers
def is_chinese(text: str) -> bool:
    """Check if text is primarily Chinese."""
    return any(0x4E00 <= ord(char) <= 0x9FFF for char in text)


def is_japanese(text: str) -> bool:
    """Check if text is primarily Japanese."""
    return any(
        (0x3040 <= ord(char) <= 0x309F) or  # Hiragana
        (0x30A0 <= ord(char) <= 0x30FF)     # Katakana
        for char in text
    )


def is_korean(text: str) -> bool:
    """Check if text is primarily Korean."""
    return any(
        (0xAC00 <= ord(char) <= 0xD7AF) or  # Hangul Syllables
        (0x1100 <= ord(char) <= 0x11FF)     # Hangul Jamo
        for char in text
    )
