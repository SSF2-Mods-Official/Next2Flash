#!/usr/bin/env python3
"""
swf_constants.py — SWF and Next2D Format Constants

Centralized definitions of SWF tag IDs, shape commands, blend modes,
and other magic numbers used throughout the codebase.

This eliminates duplicate constant definitions and provides type-safe
enums for better IDE support and error checking.
"""

from enum import IntEnum


# ══════════════════════════════════════════════════════════════════════
#  SWF TAG IDS
# ══════════════════════════════════════════════════════════════════════

class SWFTag(IntEnum):
    """SWF tag type identifiers."""
    END = 0
    SHOW_FRAME = 1
    DEFINE_SHAPE = 2
    FREE_CHARACTER = 3
    PLACE_OBJECT = 4
    REMOVE_OBJECT = 5
    DEFINE_BITS = 6
    DEFINE_BUTTON = 7
    JPEG_TABLES = 8
    SET_BACKGROUND_COLOR = 9
    DEFINE_FONT = 10
    DEFINE_TEXT = 11
    DO_ACTION = 12
    DEFINE_FONT_INFO = 13
    DEFINE_SOUND = 14
    START_SOUND = 15
    STOP_SOUND = 16
    DEFINE_BUTTON_SOUND = 17
    SOUND_STREAM_HEAD = 18
    SOUND_STREAM_BLOCK = 19
    DEFINE_BITS_LOSSLESS = 20
    DEFINE_BITS_JPEG2 = 21
    DEFINE_SHAPE2 = 22
    DEFINE_BUTTON_CXFORM = 23
    PROTECT = 24
    PATHS_ARE_POSTSCRIPT = 25
    PLACE_OBJECT2 = 26
    REMOVE_OBJECT2 = 28
    SYNC_FRAME = 29
    FREE_ALL = 31
    DEFINE_SHAPE3 = 32
    DEFINE_TEXT2 = 33
    DEFINE_BUTTON2 = 34
    DEFINE_BITS_JPEG3 = 35
    DEFINE_BITS_LOSSLESS2 = 36
    DEFINE_EDIT_TEXT = 37
    DEFINE_VIDEO = 38
    DEFINE_SPRITE = 39
    NAME_CHARACTER = 40
    PRODUCT_INFO = 41
    GENERATOR_TEXT = 42
    FRAME_LABEL = 43
    DEFINE_MORPH_SHAPE = 46
    GENERATE_FRAME = 47
    DEFINE_FONT2 = 48
    GENERATOR_COMMAND = 49
    DEFINE_COMMAND_OBJ = 50
    CHARACTER_SET = 51
    EXTERNAL_FONT = 52
    EXPORT_ASSETS = 56
    IMPORT_ASSETS = 57
    ENABLE_DEBUGGER = 58
    DO_INIT_ACTION = 59
    DEFINE_VIDEO_STREAM = 60
    VIDEO_FRAME = 61
    DEFINE_FONT_INFO2 = 62
    DEBUG_ID = 63
    ENABLE_DEBUGGER2 = 64
    SCRIPT_LIMITS = 65
    SET_TAB_INDEX = 66
    FILE_ATTRIBUTES = 69
    PLACE_OBJECT3 = 70
    IMPORT_ASSETS2 = 71
    DO_ABC = 72
    DEFINE_FONT_ALIGN_ZONES = 73
    CSM_TEXT_SETTINGS = 74
    DEFINE_FONT3 = 75
    SYMBOL_CLASS = 76
    METADATA = 77
    DEFINE_SCALING_GRID = 78
    DO_ABC2 = 82
    DEFINE_SHAPE4 = 83
    DEFINE_MORPH_SHAPE2 = 84
    DEFINE_SCENE_AND_FRAME_LABEL_DATA = 86
    DEFINE_BINARY_DATA = 87
    DEFINE_FONT_NAME = 88
    START_SOUND2 = 89
    DEFINE_BITS_JPEG4 = 90
    DEFINE_FONT4 = 91


# Legacy tag references (for backward compatibility)
TAG_END = SWFTag.END
TAG_SHOW_FRAME = SWFTag.SHOW_FRAME
TAG_DEFINE_SHAPE = SWFTag.DEFINE_SHAPE
TAG_DEFINE_SHAPE2 = SWFTag.DEFINE_SHAPE2
TAG_DEFINE_SHAPE3 = SWFTag.DEFINE_SHAPE3
TAG_DEFINE_SHAPE4 = SWFTag.DEFINE_SHAPE4
TAG_PLACE_OBJECT = SWFTag.PLACE_OBJECT
TAG_PLACE_OBJECT2 = SWFTag.PLACE_OBJECT2
TAG_PLACE_OBJECT3 = SWFTag.PLACE_OBJECT3
TAG_REMOVE_OBJECT = SWFTag.REMOVE_OBJECT
TAG_REMOVE_OBJECT2 = SWFTag.REMOVE_OBJECT2
TAG_DEFINE_BITS = SWFTag.DEFINE_BITS
TAG_DEFINE_BITS_JPEG2 = SWFTag.DEFINE_BITS_JPEG2
TAG_DEFINE_BITS_JPEG3 = SWFTag.DEFINE_BITS_JPEG3
TAG_DEFINE_BITS_JPEG4 = SWFTag.DEFINE_BITS_JPEG4
TAG_DEFINE_BITS_LOSSLESS = SWFTag.DEFINE_BITS_LOSSLESS
TAG_DEFINE_BITS_LOSSLESS2 = SWFTag.DEFINE_BITS_LOSSLESS2
TAG_DEFINE_SPRITE = SWFTag.DEFINE_SPRITE
TAG_FRAME_LABEL = SWFTag.FRAME_LABEL
TAG_DO_ACTION = SWFTag.DO_ACTION
TAG_DO_INIT_ACTION = SWFTag.DO_INIT_ACTION
TAG_EXPORT_ASSETS = SWFTag.EXPORT_ASSETS
TAG_DEFINE_SOUND = SWFTag.DEFINE_SOUND
TAG_DEFINE_TEXT = SWFTag.DEFINE_TEXT
TAG_DEFINE_TEXT2 = SWFTag.DEFINE_TEXT2
TAG_DEFINE_EDIT_TEXT = SWFTag.DEFINE_EDIT_TEXT
TAG_DEFINE_MORPH_SHAPE = SWFTag.DEFINE_MORPH_SHAPE
TAG_DEFINE_MORPH_SHAPE2 = SWFTag.DEFINE_MORPH_SHAPE2
TAG_SYMBOL_CLASS = SWFTag.SYMBOL_CLASS
TAG_DO_ABC = SWFTag.DO_ABC
TAG_DO_ABC2 = SWFTag.DO_ABC2
TAG_FILE_ATTRIBUTES = SWFTag.FILE_ATTRIBUTES
TAG_SET_BACKGROUND_COLOR = SWFTag.SET_BACKGROUND_COLOR
TAG_DEFINE_FONT3 = SWFTag.DEFINE_FONT3
TAG_DEFINE_BUTTON2 = SWFTag.DEFINE_BUTTON2
TAG_START_SOUND = SWFTag.START_SOUND
TAG_START_SOUND2 = SWFTag.START_SOUND2
TAG_DEFINE_SCALING_GRID = SWFTag.DEFINE_SCALING_GRID
TAG_JPEG_TABLES = SWFTag.JPEG_TABLES
TAG_DEFINE_BUTTON_SOUND = SWFTag.DEFINE_BUTTON_SOUND
TAG_DEFINE_BUTTON_CXFORM = SWFTag.DEFINE_BUTTON_CXFORM
TAG_DEFINE_FONT2 = SWFTag.DEFINE_FONT2
TAG_IMPORT_ASSETS = SWFTag.IMPORT_ASSETS
TAG_IMPORT_ASSETS2 = SWFTag.IMPORT_ASSETS2
TAG_DEFINE_BINARY_DATA = SWFTag.DEFINE_BINARY_DATA


# ══════════════════════════════════════════════════════════════════════
#  NEXT2D SHAPE COMMANDS (Recodes)
# ══════════════════════════════════════════════════════════════════════

class ShapeCommand(IntEnum):
    """Next2D shape recode command opcodes."""
    MOVE_TO = 0
    CURVE_TO = 1
    LINE_TO = 2
    CUBIC = 3
    ARC = 4
    FILL_STYLE = 5
    STROKE_STYLE = 6
    END_FILL = 7
    END_STROKE = 8
    BEGIN_PATH = 9
    GRADIENT_FILL = 10
    GRADIENT_STROKE = 11
    CLOSE_PATH = 12
    BITMAP_FILL = 13
    BITMAP_STROKE = 14


# Legacy command references (for backward compatibility)
MOVE_TO = ShapeCommand.MOVE_TO
CURVE_TO = ShapeCommand.CURVE_TO
LINE_TO = ShapeCommand.LINE_TO
CUBIC = ShapeCommand.CUBIC
ARC = ShapeCommand.ARC
FILL_STYLE = ShapeCommand.FILL_STYLE
STROKE_STYLE = ShapeCommand.STROKE_STYLE
END_FILL = ShapeCommand.END_FILL
END_STROKE = ShapeCommand.END_STROKE
BEGIN_PATH = ShapeCommand.BEGIN_PATH
GRADIENT_FILL = ShapeCommand.GRADIENT_FILL
GRADIENT_STROKE = ShapeCommand.GRADIENT_STROKE
CLOSE_PATH = ShapeCommand.CLOSE_PATH
BITMAP_FILL = ShapeCommand.BITMAP_FILL
BITMAP_STROKE = ShapeCommand.BITMAP_STROKE

# Also export as CMD_ prefix (legacy support)
CMD_MOVE_TO = ShapeCommand.MOVE_TO
CMD_CURVE_TO = ShapeCommand.CURVE_TO
CMD_LINE_TO = ShapeCommand.LINE_TO
CMD_CUBIC = ShapeCommand.CUBIC
CMD_ARC = ShapeCommand.ARC
CMD_FILL_STYLE = ShapeCommand.FILL_STYLE
CMD_STROKE_STYLE = ShapeCommand.STROKE_STYLE
CMD_END_FILL = ShapeCommand.END_FILL
CMD_END_STROKE = ShapeCommand.END_STROKE
CMD_BEGIN_PATH = ShapeCommand.BEGIN_PATH
CMD_GRADIENT_FILL = ShapeCommand.GRADIENT_FILL
CMD_GRADIENT_STROKE = ShapeCommand.GRADIENT_STROKE
CMD_CLOSE_PATH = ShapeCommand.CLOSE_PATH
CMD_BITMAP_FILL = ShapeCommand.BITMAP_FILL
CMD_BITMAP_STROKE = ShapeCommand.BITMAP_STROKE


# ══════════════════════════════════════════════════════════════════════
#  BLEND MODES
# ══════════════════════════════════════════════════════════════════════

class BlendMode(IntEnum):
    """SWF blend mode identifiers."""
    NORMAL = 1
    LAYER = 2
    MULTIPLY = 3
    SCREEN = 4
    LIGHTEN = 5
    DARKEN = 6
    DIFFERENCE = 7
    ADD = 8
    SUBTRACT = 9
    INVERT = 10
    ALPHA = 11
    ERASE = 12
    OVERLAY = 13
    HARDLIGHT = 14


# Next2D blend mode names (SWF ID → Next2D string)
NEXT2D_BLEND_MAP = {
    1: "normal",
    2: "layer",
    3: "multiply",
    4: "screen",
    5: "lighten",
    6: "darken",
    7: "difference",
    8: "add",
    9: "subtract",
    10: "invert",
    11: "alpha",
    12: "erase",
    13: "overlay",
    14: "hardlight",
}

# Reverse map: Next2D string → SWF ID
SWF_BLEND_MAP = {v: k for k, v in NEXT2D_BLEND_MAP.items()}

# Legacy blend mode constants (for backward compatibility)
SWF_BLEND_NORMAL = BlendMode.NORMAL
SWF_BLEND_LAYER = BlendMode.LAYER
SWF_BLEND_MULTIPLY = BlendMode.MULTIPLY
SWF_BLEND_SCREEN = BlendMode.SCREEN
SWF_BLEND_LIGHTEN = BlendMode.LIGHTEN
SWF_BLEND_DARKEN = BlendMode.DARKEN
SWF_BLEND_DIFFERENCE = BlendMode.DIFFERENCE
SWF_BLEND_ADD = BlendMode.ADD
SWF_BLEND_SUBTRACT = BlendMode.SUBTRACT
SWF_BLEND_INVERT = BlendMode.INVERT
SWF_BLEND_ALPHA = BlendMode.ALPHA
SWF_BLEND_ERASE = BlendMode.ERASE
SWF_BLEND_OVERLAY = BlendMode.OVERLAY
SWF_BLEND_HARDLIGHT = BlendMode.HARDLIGHT


# ══════════════════════════════════════════════════════════════════════
#  STYLE ENUMS
# ══════════════════════════════════════════════════════════════════════

class CapStyle(IntEnum):
    """SWF line cap styles."""
    ROUND = 0
    NONE = 1
    SQUARE = 2


class JoinStyle(IntEnum):
    """SWF line join styles."""
    ROUND = 0
    BEVEL = 1
    MITER = 2


class GradientType(IntEnum):
    """SWF gradient types."""
    LINEAR = 0
    RADIAL = 1


class SpreadMode(IntEnum):
    """SWF gradient spread modes (internal encoding)."""
    PAD = 0
    REFLECT = 1
    REPEAT = 2


class InterpolationMode(IntEnum):
    """SWF gradient interpolation."""
    RGB = 0
    LINEAR_RGB = 1


# ══════════════════════════════════════════════════════════════════════
#  SOUND FORMATS
# ══════════════════════════════════════════════════════════════════════

class SoundFormat(IntEnum):
    """SWF sound format identifiers."""
    ADPCM = 1
    MP3 = 2
    PCM = 3
    PCM_LE = 3  # Alias
    NELLYMOSER_16K = 4
    NELLYMOSER_8K = 5
    NELLYMOSER = 6
    SPEEX = 11


class SoundRate(IntEnum):
    """SWF sound sampling rates."""
    RATE_5_5K = 0
    RATE_11K = 1
    RATE_22K = 2
    RATE_44K = 3


# ══════════════════════════════════════════════════════════════════════
#  FILE ATTRIBUTES FLAGS
# ══════════════════════════════════════════════════════════════════════

class FileAttributes(IntEnum):
    """SWF file attributes flags (bitfield)."""
    USE_DIRECT_BLIT = 0x40
    USE_GPU = 0x20
    HAS_METADATA = 0x10
    ACTIONSCRIPT3 = 0x08
    USE_NETWORK = 0x01


# ══════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════

# Twips per pixel (SWF uses 20 twips = 1 pixel)
TWIPS_PER_PIXEL = 20

# Maximum SWF version supported
MAX_SWF_VERSION = 40

# Default frame rate
DEFAULT_FRAME_RATE = 24.0

# Default stage dimensions
DEFAULT_STAGE_WIDTH = 550
DEFAULT_STAGE_HEIGHT = 400
