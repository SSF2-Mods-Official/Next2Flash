#!/usr/bin/env python3
"""
Test suite for cycle_detector.py

Tests Bug Fix #2: Circular sprite reference detection
Ensures circular sprite dependencies are caught before causing infinite recursion.
"""

import pytest
import struct
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cycle_detector import (
    detect_sprite_cycles,
    build_sprite_dependency_map,
    validate_swf_sprites
)
from swf_constants import (
    TAG_DEFINE_SPRITE,
    TAG_PLACE_OBJECT2,
    TAG_PLACE_OBJECT3,
    TAG_END
)
from swf_to_n2d import SWFTag


def make_define_sprite_tag(sprite_id: int, nested_tags_data: bytes) -> SWFTag:
    """Helper to create DefineSprite tag."""
    # DefineSprite: [charID:UI16][frameCount:UI16][...nested tags][End]
    data = struct.pack('<HH', sprite_id, 1) + nested_tags_data
    return SWFTag(TAG_DEFINE_SPRITE, data, 0)


def make_place_object2_tag(char_id: int, depth: int = 1) -> bytes:
    """Helper to create PlaceObject2 tag data."""
    # PlaceObject2: [flags:UI8][depth:UI16][charID:UI16]...
    # flags: 0x02 = hasCharacter
    flags = 0x02
    tag_header = struct.pack('<H', (TAG_PLACE_OBJECT2 << 6) | 5)  # 5 bytes
    tag_data = struct.pack('<BHH', flags, depth, char_id)
    return tag_header + tag_data


def make_end_tag() -> bytes:
    """Helper to create End tag."""
    return struct.pack('<H', (TAG_END << 6) | 0)


def test_simple_cycle():
    """Bug Fix #2: Detect simple A→B→A cycle."""
    dependencies = {
        1: [2],  # Sprite 1 contains sprite 2
        2: [1]   # Sprite 2 contains sprite 1 (CYCLE!)
    }
    
    with pytest.raises(ValueError, match="Circular sprite reference detected: 1 → 2 → 1"):
        detect_sprite_cycles(1, dependencies, set(), [])


def test_complex_cycle():
    """Detect complex A→B→C→A cycle."""
    dependencies = {
        1: [2],
        2: [3],
        3: [1]  # Cycle back to start
    }
    
    with pytest.raises(ValueError, match="1 → 2 → 3 → 1"):
        detect_sprite_cycles(1, dependencies, set(), [])


def test_self_reference():
    """Detect sprite referencing itself (A→A)."""
    dependencies = {
        1: [1]  # Self-reference
    }
    
    with pytest.raises(ValueError, match="1 → 1"):
        detect_sprite_cycles(1, dependencies, set(), [])


def test_no_cycle_linear():
    """Linear dependency chain (A→B→C) should pass."""
    dependencies = {
        1: [2],
        2: [3],
        3: []  # Terminal node
    }
    
    # Should not raise
    detect_sprite_cycles(1, dependencies, set(), [])


def test_no_cycle_dag():
    """Diamond DAG (A→B,C; B→D; C→D) should pass."""
    dependencies = {
        1: [2, 3],
        2: [4],
        3: [4],
        4: []
    }
    
    # Should not raise
    visited = set()
    for sprite_id in [1, 2, 3, 4]:
        if sprite_id not in visited:
            detect_sprite_cycles(sprite_id, dependencies, visited, [])


def test_disconnected_cycle():
    """Cycle in disconnected component should be caught."""
    dependencies = {
        1: [2],
        2: [],      # Component 1 (no cycle)
        10: [11],
        11: [10]    # Component 2 (CYCLE!)
    }
    
    # Sprite 1 should pass
    visited = set()
    detect_sprite_cycles(1, dependencies, visited, [])
    
    # Sprite 10 should fail
    with pytest.raises(ValueError, match="10 → 11 → 10"):
        detect_sprite_cycles(10, dependencies, set(), [])


def test_build_dependency_map():
    """Build dependency map from real SWFTag objects."""
    # Create sprite 1 that contains sprite 2
    nested_data = make_place_object2_tag(char_id=2, depth=1) + make_end_tag()
    sprite1 = make_define_sprite_tag(sprite_id=1, nested_tags_data=nested_data)
    
    # Create sprite 2 (empty)
    sprite2 = make_define_sprite_tag(sprite_id=2, nested_tags_data=make_end_tag())
    
    tags = [sprite1, sprite2]
    deps = build_sprite_dependency_map(tags)
    
    assert 1 in deps
    assert 2 in deps[1]


def test_build_dependency_map_multiple_children():
    """Sprite with multiple children."""
    # Sprite 1 contains sprites 2 and 3
    nested_data = (
        make_place_object2_tag(char_id=2, depth=1) +
        make_place_object2_tag(char_id=3, depth=2) +
        make_end_tag()
    )
    sprite1 = make_define_sprite_tag(sprite_id=1, nested_tags_data=nested_data)
    
    tags = [sprite1]
    deps = build_sprite_dependency_map(tags)
    
    assert deps[1] == [2, 3]


def test_validate_swf_sprites_valid():
    """Valid SWF with no cycles should pass."""
    # Sprite 1 → sprite 2 (no cycle)
    nested_data = make_place_object2_tag(char_id=2, depth=1) + make_end_tag()
    sprite1 = make_define_sprite_tag(sprite_id=1, nested_tags_data=nested_data)
    sprite2 = make_define_sprite_tag(sprite_id=2, nested_tags_data=make_end_tag())
    
    tags = [sprite1, sprite2]
    
    # Should not raise
    validate_swf_sprites(tags)


def test_validate_swf_sprites_with_cycle():
    """SWF with cycle should fail validation."""
    # Sprite 1 → sprite 2
    nested1 = make_place_object2_tag(char_id=2, depth=1) + make_end_tag()
    sprite1 = make_define_sprite_tag(sprite_id=1, nested_tags_data=nested1)
    
    # Sprite 2 → sprite 1 (CYCLE!)
    nested2 = make_place_object2_tag(char_id=1, depth=1) + make_end_tag()
    sprite2 = make_define_sprite_tag(sprite_id=2, nested_tags_data=nested2)
    
    tags = [sprite1, sprite2]
    
    with pytest.raises(ValueError, match="Circular sprite reference"):
        validate_swf_sprites(tags)


def test_empty_tags():
    """Empty tag list should pass."""
    validate_swf_sprites([])


def test_multiple_independent_sprites():
    """Multiple independent sprites should all be checked."""
    # Sprite 1 → sprite 2
    nested1 = make_place_object2_tag(char_id=2, depth=1) + make_end_tag()
    sprite1 = make_define_sprite_tag(sprite_id=1, nested_tags_data=nested1)
    sprite2 = make_define_sprite_tag(sprite_id=2, nested_tags_data=make_end_tag())
    
    # Sprite 10 → sprite 11
    nested10 = make_place_object2_tag(char_id=11, depth=1) + make_end_tag()
    sprite10 = make_define_sprite_tag(sprite_id=10, nested_tags_data=nested10)
    sprite11 = make_define_sprite_tag(sprite_id=11, nested_tags_data=make_end_tag())
    
    tags = [sprite1, sprite2, sprite10, sprite11]
    
    validate_swf_sprites(tags)


def test_long_cycle():
    """Long cycle (A→B→C→D→E→A) should be detected."""
    dependencies = {
        1: [2],
        2: [3],
        3: [4],
        4: [5],
        5: [1]  # Long cycle
    }
    
    with pytest.raises(ValueError, match="1 → 2 → 3 → 4 → 5 → 1"):
        detect_sprite_cycles(1, dependencies, set(), [])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
