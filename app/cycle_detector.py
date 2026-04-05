#!/usr/bin/env python3
"""
cycle_detector.py — Detect circular sprite references in SWF files

Problem: Circular sprites (e.g., sprite A contains sprite B, sprite B contains
sprite A) cause infinite recursion and browser freeze when rendering.

Solution: Build dependency graph and detect cycles using depth-first search.

Usage:
    from cycle_detector import validate_swf_sprites
    
    header, tags = parse_swf(swf_data)
    validate_swf_sprites(tags)  # Raises ValueError if cycles detected
"""

import struct
from typing import List, Set, Dict

from swf_constants import (
    TAG_DEFINE_SPRITE,
    TAG_PLACE_OBJECT2,
    TAG_PLACE_OBJECT3
)


def detect_sprite_cycles(
    sprite_id: int,
    dependencies: Dict[int, List[int]],
    visited: Set[int] = None,
    path: List[int] = None
) -> None:
    """
    Detect circular references in sprite dependencies using DFS.
    
    Args:
        sprite_id: Current sprite ID being checked
        dependencies: Map of sprite_id → [child_sprite_ids]
        visited: Set of already-visited sprites (prevents re-checking)
        path: Current DFS path (for cycle detection)
    
    Raises:
        ValueError: If circular reference detected, includes cycle path
    
    Example:
        >>> deps = {1: [2], 2: [3], 3: [1]}  # Cycle: 1→2→3→1
        >>> detect_sprite_cycles(1, deps, set(), [])
        ValueError: Circular sprite reference detected: 1 → 2 → 3 → 1
    """
    if visited is None:
        visited = set()
    if path is None:
        path = []
    
    # Cycle detected: sprite appears in current path
    if sprite_id in path:
        cycle_path = " → ".join(str(s) for s in path) + f" → {sprite_id}"
        raise ValueError(f"Circular sprite reference detected: {cycle_path}")
    
    # Already checked this sprite (from different path)
    if sprite_id in visited:
        return
    
    # Mark as visited
    visited.add(sprite_id)
    path.append(sprite_id)
    
    # Recurse into children
    if sprite_id in dependencies:
        for child_id in dependencies[sprite_id]:
            detect_sprite_cycles(child_id, dependencies, visited, path)
    
    # Backtrack
    path.pop()


def build_sprite_dependency_map(tags: List) -> Dict[int, List[int]]:
    """
    Build sprite dependency map from raw SWF tags.
    
    Parses DefineSprite tags and extracts PlaceObject references to
    build a dict mapping sprite ID → list of child sprite IDs.
    
    Args:
        tags: List of SWFTag objects (from parse_swf())
    
    Returns:
        Dict mapping sprite_id → [child_sprite_ids]
    
    Example:
        >>> build_sprite_dependency_map(tags)
        {1: [2, 3], 2: [4], 3: [], 4: []}
    """
    dependencies = {}
    
    for tag in tags:
        # Check if this is a DefineSprite tag
        if tag.tag_type == TAG_DEFINE_SPRITE:
            # Parse sprite ID from binary data
            # DefineSprite format: [charID:UI16][frameCount:UI16][...nested tags]
            if len(tag.data) < 2:
                continue
            
            sprite_id = struct.unpack_from('<H', tag.data, 0)[0]
            
            # Parse nested tags to find PlaceObject references
            child_ids = []
            
            # Parse all nested tags (starting at offset 4)
            if len(tag.data) > 4:
                nested_tags = _parse_nested_tags(tag.data, 4)
                
                for nested_tag in nested_tags:
                    if nested_tag.tag_type in (TAG_PLACE_OBJECT2, TAG_PLACE_OBJECT3):
                        char_id = _extract_char_id_from_place_object(nested_tag)
                        if char_id is not None and char_id != 0:
                            child_ids.append(char_id)
            
            dependencies[sprite_id] = child_ids
    
    return dependencies


def _parse_nested_tags(data: bytes, offset: int) -> List:
    """
    Parse nested SWF tags from DefineSprite.
    
    Returns list of SWFTag-like objects with tag_type and data.
    """
    from swf_to_n2d import SWFTag
    
    tags = []
    pos = offset
    
    while pos < len(data) - 1:
        # Read tag header
        tag_code_and_length = struct.unpack_from('<H', data, pos)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        
        pos += 2
        
        # Long form
        if tag_length == 0x3F:
            if pos + 4 > len(data):
                break
            tag_length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        
        # Extract tag data
        if pos + tag_length > len(data):
            break
        
        tag_data = data[pos:pos + tag_length]
        tags.append(SWFTag(tag_type, tag_data, pos))
        
        pos += tag_length
        
        # Stop at End tag
        if tag_type == 0:
            break
    
    return tags


def _extract_char_id_from_place_object(tag) -> int:
    """
    Extract character ID from PlaceObject2/3 tag.
    
    Returns None if no character ID present (move-only placement).
    """
    if not tag.data or len(tag.data) < 3:
        return None
    
    # PlaceObject2/3 format:
    # [flags:UI8][depth:UI16][charID:UI16 (if hasCharacter)]...
    flags = tag.data[0]
    has_character = bool(flags & 0x02)
    
    if not has_character:
        return None
    
    # CharID is at offset 3 (after flags + depth)
    if len(tag.data) < 5:
        return None
    
    char_id = struct.unpack_from('<H', tag.data, 3)[0]
    return char_id


def validate_swf_sprites(tags: List) -> None:
    """
    Validate all sprites in SWF have no circular references.
    
    Args:
        tags: List of SWF tags (from parse_swf())
    
    Raises:
        ValueError: If any circular reference detected
    
    Usage:
        >>> from swf_to_n2d import parse_swf
        >>> header, tags = parse_swf(swf_data)
        >>> validate_swf_sprites(tags)  # Raises if cycles exist
    """
    dependencies = build_sprite_dependency_map(tags)
    
    # Check all sprites (including those not referenced)
    visited = set()
    for sprite_id in dependencies:
        if sprite_id not in visited:
            detect_sprite_cycles(sprite_id, dependencies, visited, [])
