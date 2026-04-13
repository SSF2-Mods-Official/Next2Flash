# Export Edits Survival Checklist

Track which user edits survive the SWF export round-trip.

## Legend
- ✅ Edits survive export
- ❌ Edits silently lost (rawTagBody passthrough wins)
- 🔧 Fix in progress
- ⬜ Not yet reviewed
- N/A Not editable in tool

---

## Text (DefineEditText — tag 37)
| Property | Survives? | Notes |
|----------|-----------|-------|
| text content | ❌ | rawTagBody passthrough; rebuild path exists |
| font name | ❌ | same |
| font size | ❌ | same |
| font color | ❌ | same |
| alignment | ❌ | same |
| bold/italic | ❌ | same |
| leading | ❌ | same |
| letterSpacing | ❌ | same |
| leftMargin | ❌ | same |
| rightMargin | ❌ | same |
| multiline | ❌ | same |
| wordWrap | ❌ | same |
| border | ❌ | same |
| scroll | ❌ | same |
| bounds | ❌ | same |

**Fix**: Clear `rawTagBody` for text entries during merge when any property differs from disk.

## Text (DefineText — tags 11, 33)
| Property | Survives? | Notes |
|----------|-----------|-------|
| text content | ❌ | rawTagBody passthrough; rebuild path exists |
| font/size/color | ❌ | same |

**Fix**: Same as EditText — clear rawTagBody during merge.

## Shape (tags 2, 22, 32, 83)
| Property | Survives? | Notes |
|----------|-----------|-------|
| recodes (fill/stroke/path) | ❌ | rawTagBody passthrough; rebuild path exists |
| bounds | ❌ | same |

**Fix**: Clear `rawTagBody` for shape entries during merge when `recodes` differ.

## MorphShape (tags 46, 84)
| Property | Survives? | Notes |
|----------|-----------|-------|
| startRecodes | ❌ | rawTagBody passthrough; rebuild path exists |
| endRecodes | ❌ | same |

**Fix**: Clear `rawTagBody` for morphshape entries during merge when recodes differ.

## Container / MovieClip (tag 39)
| Property | Survives? | Notes |
|----------|-----------|-------|
| layers / placement | ✅ | Always rebuilds from JSON; ignores rawTagBody |
| totalFrame | ✅ | same |
| labels | ✅ | same |
| actions / scripts | ✅ | same |

No fix needed.

## Bitmap (tags 6, 8, 9, 20, 21, 35, 36)
| Property | Survives? | Notes |
|----------|-----------|-------|
| pixel data (externalFile) | ✅ | Merge rebuilds rawTagBody from disk file when externalFile set |
| pixel data (no externalFile) | ❌ | rawTagBody passthrough; rebuild path exists from `buffer` |

**Fix**: Clear `rawTagBody` for bitmap entries during merge when `buffer` differs or is present in editor blob.

## Sound (tag 14)
| Property | Survives? | Notes |
|----------|-----------|-------|
| audio data (externalFile) | ✅ | Merge rebuilds rawTagBody from disk file |
| audio data (no externalFile) | ❌ | rawTagBody passthrough |

**Fix**: Same pattern as bitmap.

## Font (tags 48, 75)
| Property | Survives? | Notes |
|----------|-----------|-------|
| glyph data | N/A | Not editable; no rebuild path; rawTagBody mandatory |
| font name | N/A | same |

No fix possible without writing font rebuild code. Keep rawTagBody.

## Button (tag 34)
| Property | Survives? | Notes |
|----------|-----------|-------|
| button records | N/A | Not editable; no rebuild path; rawTagBody mandatory |
| actions | N/A | same |

No fix possible without writing button rebuild code. Keep rawTagBody.

---

## Implementation Plan

### Phase 1 — Text (highest priority)
- [ ] In `server.py` merge: detect text property changes → clear rawTagBody/rawTagType
- [ ] Verify `text_converter.build_define_edit_text()` rebuild produces valid SWF
- [ ] Verify DefineText rebuild path works
- [ ] Test: edit text in tool → export → open in JPEXS → confirm new text

### Phase 2 — Shape / MorphShape
- [ ] In `server.py` merge: detect recodes changes → clear rawTagBody/rawTagType
- [ ] Verify shape rebuild from recodes produces valid SWF
- [ ] Verify morphshape rebuild produces valid SWF
- [ ] Test: edit shape in tool → export → verify in Flash Player

### Phase 3 — Bitmap / Sound (without externalFile)
- [ ] In `server.py` merge: detect buffer changes → clear rawTagBody/rawTagType
- [ ] Verify bitmap rebuild from buffer produces valid SWF
- [ ] Verify sound rebuild from buffer produces valid SWF

### Phase 4 — Font / Button (future)
- [ ] Write font rebuild code (DefineFont2/3 from glyph data)
- [ ] Write button rebuild code (DefineButton2 from records)
- [ ] Remove rawTagBody dependency for these types

---

## Merge Strategy Reference

**Current** (`server.py`): rawTagBody unconditionally preserved from disk.

**Target**: For types with rebuild paths (text, shape, morphshape, bitmap, sound):
1. Compare editor properties vs disk properties
2. If any editable property changed → delete rawTagBody + rawTagType
3. Export falls through to rebuild path → edits survive

For types without rebuild paths (font, button):
- Keep rawTagBody always (no alternative)
