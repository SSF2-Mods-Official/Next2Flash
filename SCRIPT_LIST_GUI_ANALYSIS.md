# ActionScript Panel Script List Management — Code Analysis

## Main File
**[app/assets/js/actionscript-panel.js](app/assets/js/actionscript-panel.js)** — Complete AS3 script GUI management

## Overview
This file implements a GUI panel that displays and manages:
1. **Source Scripts** — editable `.as` files loaded from N2D projects
2. **Bytecode Classes** — read-only AS3 classes parsed from SWF DoABC tags
3. **SymbolClass Mappings** — library character → AS3 class mappings

---

## 1. Scripts Array & State Management

**Lines 33-42: Core State**
```javascript
var scripts = []; // {name, path, source}  — editable
var abcClasses = []; // {name, pkg, superName, tagIdx} — parsed from DoABC
var rawGlobalTags = []; // raw from N2D (legacy)
var structuredGlobals = {}; // new structured fields: abcBlocks, protectFromImport, etc.
var activeScript = null; // index into scripts[]
```

Each **script object** contains:
- `name`: Display name (e.g., "Idle.as")
- `path`: Full path (e.g., "gameandwatch_fla/Idle.as")
- `source`: Source code text (editable)

---

## 2. Scripts Fetched from API Response

**Lines 645-669: Loading Scripts from N2D JSON**
```javascript
if (Array.isArray(json.scripts) && json.scripts.length > 0) {
  _log.info('Found', json.scripts.length, 'source scripts');
  scripts = json.scripts.map(function (s) {
    return {
      name: s.name || (s.path || 'unknown').split('/').pop(),
      path: s.path || s.name || 'unknown',
      source: s.source || s.content || ''
    };
  });
  saveScriptsToStorage();
}
```

Also extracts ABC classes from `rawGlobalTags`:
```javascript
if (Array.isArray(json.rawGlobalTags) && json.rawGlobalTags.length > 0) {
  _log.info('Found', json.rawGlobalTags.length, 'rawGlobalTags');
  rawGlobalTags = json.rawGlobalTags;
  extractAbcClasses();
}
```

---

## 3. Script List Rendering (`renderScriptList()`)

**Lines 1483-1680: Complete list rendering with search/filter**

### Section A: Source Scripts (Lines 1490-1505)
```javascript
var filtered = scripts.filter(function (s) {
  if (!q) return true;
  return (s.name + ' ' + s.path + ' ' + (s.source || '')).toLowerCase().indexOf(q) >= 0;
});
if (filtered.length > 0 || (!q && scripts.length === 0)) {
  html += '<div class="as-section-header">Source Scripts (' + filtered.length + ')</div>';
  filtered.forEach(function (s) {
    var idx = scripts.indexOf(s);  // ✓ CORRECT: finds actual index in scripts[]
    var ac = (activeScript === idx) ? ' active' : '';
    html += '<div class="as-script-item' + ac + '" data-type="source" data-index="' + idx + '">' +
      '<div class="as-script-icon source"></div>' +
      '<span class="as-script-name" title="' + esc(s.path) + '">' + esc(s.name) + '</span>' +
      '<span class="as-script-tag">AS3</span>' +
      '<span class="as-script-delete" data-index="' + idx + '" title="Delete">&times;</span></div>';
    hasResults = true;
  });
}
```

### Section B: ABC Classes (Lines 1511-1527)
```javascript
var filteredAbc = abcClasses.filter(function (c) {
  if (!q) return true;
  return (c.name + ' ' + c.pkg + ' ' + c.superName).toLowerCase().indexOf(q) >= 0;
});
if (filteredAbc.length > 0) {
  html += '<div class="as-section-header">Bytecode Classes (' + filteredAbc.length + ')</div>';
  filteredAbc.forEach(function (c, i) {  // ◄─ i is index in FILTERED array
    var fullName = c.pkg ? c.pkg + '.' + c.name : c.name;
    var extendsText = c.superName ? ' extends ' + c.superName : '';
    html += '<div class="as-script-item" data-type="abc" data-index="' + i + '">' +  // ◄─ BUG!
      '<div class="as-script-icon bytecode"></div>' +
      '<span class="as-script-name" title="' + esc(fullName + extendsText) + '">' + esc(fullName) +
      '</span>' +
      '<span class="as-script-tag">bytecode</span></div>';
    hasResults = true;
  });
}
```

### **🐛 OFF-BY-ONE BUG DETECTED**
**Line 1519 uses `i` (filtered array index) instead of actual `abcClasses` index**
- When searching/filtering: clicking on any ABC class **except the first** opens wrong class
- Replace with: `var actualIdx = abcClasses.indexOf(c);` then use `actualIdx` in `data-index`

### Section C: Event Wiring (Lines 1559-1567)
```javascript
var items = elScriptList.querySelectorAll('.as-script-item');
for (var i = 0; i < items.length; i++) {
  items[i].addEventListener('click', onItemClick);
  items[i].addEventListener('dblclick', onItemDblClick);
}
var dels = elScriptList.querySelectorAll('.as-script-delete');
for (var j = 0; j < dels.length; j++) {
  dels[j].addEventListener('click', onDeleteScript);
}
```

---

## 4. Click Event Handlers

### `onItemClick()` — Lines 1599-1612
```javascript
function onItemClick(e) {
  if (e.target.classList.contains('as-script-delete')) return;
  var el = e.currentTarget;
  var type = el.getAttribute('data-type');
  var idx = parseInt(el.getAttribute('data-index'), 10);

  if (type === 'source' && !isNaN(idx) && idx < scripts.length) {
    openScriptInEditor(idx);
  } else if (type === 'abc' && !isNaN(idx) && idx < abcClasses.length) {
    showAbcClassInfo(idx);  // ◄─ Receives wrong index if filtered
  } else if (type === 'sym') {
    showSymbolClassInfo(el);
  }
}
```

**Issues:**
- Line 1608: Bounds check `idx < abcClasses.length` can pass with wrong index due to bug above

### `onItemDblClick()` — Lines 1614-1623
```javascript
function onItemDblClick(e) {
  if (e.target.classList.contains('as-script-delete')) return;
  var el = e.currentTarget;
  var type = el.getAttribute('data-type');
  var idx = parseInt(el.getAttribute('data-index'), 10);

  if (type === 'source' && !isNaN(idx) && idx < scripts.length) {
    _log.debug('Double-click opening script in new tab:', scripts[idx].name, 'index:', idx);
    openScriptInNewTab(idx);
  }
}
```

### `onDeleteScript()` — Lines 1626-1637
```javascript
function onDeleteScript(e) {
  e.stopPropagation();
  var idx = parseInt(e.currentTarget.getAttribute('data-index'), 10);
  if (isNaN(idx) || idx >= scripts.length) return;
  if (confirm('Delete "' + scripts[idx].name + '"?')) {
    scripts.splice(idx, 1);
    if (activeScript === idx) closeEditor();
    else if (activeScript > idx) activeScript--;  // ✓ Correctly adjusts active index
    saveScriptsToStorage();
    renderScriptList();
  }
}
```

---

## 5. Opening Scripts in Editor

### `openScriptInEditor(index)` — Lines 1867-1895
```javascript
function openScriptInEditor(index) {
  _log.trace('Opening script in editor:', scripts[index] ? scripts[index].name : index);
  // Save current before switching
  if (activeScript !== null && activeScript < scripts.length) {
    scripts[activeScript].source = getEditorValue();
    saveScriptsToStorage();
  }

  activeScript = index;
  var script = scripts[index];

  // Show container FIRST so editor has dimensions
  elEditorContainer.classList.remove('none');

  if (elEditorFilename) elEditorFilename.textContent = script.path || script.name;

  // Create editor (Ace or textarea fallback)
  createEditor();
  setEditorValue(script.source || '');
  if (aceEditor) aceEditor.setReadOnly(false);

  focusEditor();
  renderScriptList();
}
```

---

## 6. API Response Integration

### Load Handler — Lines 600-670
The GUI intercepts the N2D file load and extracts scripts from the JSON response:

```javascript
// File load handler triggers decompressN2D()
// which extracts json.scripts[] array
scripts = json.scripts.map(function (s) {
  return {
    name: s.name || (s.path || 'unknown').split('/').pop(),
    path: s.path || s.name || 'unknown',
    source: s.source || s.content || ''
  };
});
```

### Save Handler — Lines 1231-1251 (`injectDataBeforeExport()`)
```javascript
function injectDataBeforeExport() {
  var json = originalN2DJson;
  
  // 1) Source scripts
  if (scripts.length > 0) {
    json.scripts = scripts.map(function (s) {
      return {name: s.name, path: s.path, source: s.source};
    });
  }
  
  // 1b) If scripts were edited, set flag for recompilation
  if (scriptsModified && json.scripts && json.scripts.length > 0) {
    json.scriptsModified = true;  // ◄─ Signals backend to recompile from source
    _log.info('Scripts modified — stripping DoABC for recompilation');
  }
  
  return json;
}
```

---

## 7. Search/Filter

**Lines 1490-1494: Source Script Filter**
```javascript
var filtered = scripts.filter(function (s) {
  if (!q) return true;
  return (s.name + ' ' + s.path + ' ' + (s.source || '')).toLowerCase().indexOf(q) >= 0;
});
```

Searches across name, path, and source code. Uses `scripts.indexOf(s)` to preserve correct indices.

---

## 8. Key Code Patterns

### Creating New Script
Lines 2093-2122
```javascript
scripts.forEach(function (s) {
  if (s.name === newName || s.path === newName) {
    // Already exists
    scripts.push({name: newName, path: newName, source: '// New script\n'});
    renderScriptList();
    openScriptInEditor(scripts.length - 1);
  }
});
```

### Checking for Modifications  
Lines 2033-2039
```javascript
for (var i = 0; i < scripts.length; i++) {
  if (scripts[i].path === e.data.path) {
    scripts[i].source = e.data.source;
    scriptsModified = true;  // Mark for recompile
    saveScriptsToStorage();
    toast('Saved: ' + scripts[i].name);
  }
}
```

---

## Issues Summary

| Issue | Location | Severity | Notes |
|-------|----------|----------|-------|
| **ABC Class Off-by-One Bug** | Line 1519 in `renderScriptList()` | 🔴 High | Using filtered array index instead of actual `abcClasses` index; clicking filtered ABC classes opens wrong one |
| **No bounds check on filtered items** | Line 1561 | 🟡 Medium | Event wiring doesn't validate items match current data state |
| **Storage/IDB consistency** | Throughout | 🟡 Medium | Multiple storage mechanisms (localStorage, IDB) can drift |

---

## How Scripts Flow Through the System

```
1. User loads N2D file
   ↓
2. decompressN2D() extracts project.json
   ↓
3. Scripts extracted: json.scripts[] → scripts[] variable
   ↓
4. renderScriptList() displays them with event listeners
   ↓
5. Click → onItemClick() → openScriptInEditor(idx)
   ↓
6. User edits in Ace editor
   ↓
7. Ctrl+S calls saveCurrentScript()
   ↓
8. injectDataBeforeExport() puts scripts back into JSON
   ↓
9. Backend compiles if scriptsModified=true
```

