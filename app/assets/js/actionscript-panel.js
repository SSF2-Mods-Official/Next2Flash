/**
 * ActionScript Panel — Enhanced AS tab for Next2D Animation Tool
 *
 * Features:
 *   1. Parses DoABC bytecode to show individual AS3 class names
 *   2. Lists editable source scripts from N2D project scripts[]
 *   3. Search/filter across all scripts
 *   4. "Add New Script" dialog with templates
 *   5. Ace editor (with textarea fallback) for editing source scripts
 *   6. Expand-to-floating-window for side-by-side editing
 *   7. Full N2D round-trip: scripts, rawGlobalTags, swfVersion, per-library
 *      metadata (swfCharId, fontData, buttonData, etc.) are captured on
 *      load and re-injected into every Ctrl+Shift+S save.
 *
 * Opens via file:///  or through the Tauri converter app.
 */

(function () {
  'use strict';

  var _log = window.__N2F_DEBUG ? window.__N2F_DEBUG.logger('ASPanel') : { trace:function(){},debug:function(){},info:function(){},warn:function(){},error:function(){},time:function(){},timeEnd:function(){},group:function(){},groupEnd:function(){} };

  /* ================================================================== */
  /*  SWF Tag Constants                                                  */
  /* ================================================================== */
  var DOABC_TAG = 82; // DoABC2 (flags + name + abc data)
  var DOABC1_TAG = 72; // DoABC  (abc data only)
  var SYMCLASS_TAG = 76;

  /* ================================================================== */
  /*  State                                                              */
  /* ================================================================== */
  var scripts = []; // {name, path, source}  — editable
  var _projectScriptsLoaded = false; // true once scripts are loaded from current project
  var abcClasses = []; // {name, pkg, superName, tagIdx} — parsed from DoABC
  var rawGlobalTags = []; // raw from N2D (legacy)
  var structuredGlobals = {}; // new structured fields: abcBlocks, protectFromImport, etc.
  var roundtripData = null; // swfVersion, swfCompressed, rootTimelineDefIds, per-lib metadata
  var originalN2DJson = null; // full parsed JSON from loaded N2D (in-memory, for fallback)
  var scriptsModified = false; // true when user has edited any script source
  var aceEditor = null;
  var fallbackTA = null; // textarea fallback when Ace is unavailable
  var activeScript = null; // index into scripts[]
  var searchQuery = '';
  var floatingWindows = {};
  var scriptPollTimer = null;
  var importInterceptionInstalled = false;
  var editorDragState = null;

  /* ================================================================== */
  /*  DOM refs                                                           */
  /* ================================================================== */
  var elScriptList, elSearch, elAddBtn, elEditorContainer,
    elEditorDiv, elEditorFilename, elEditorClose, elEditorExpand,
    elFrameScriptBox;

  /* ================================================================== */
  /*  Init                                                               */
  /* ================================================================== */
  function init() {
    _log.debug('AS Panel initializing');

    /* ----- Ensure AS panel DOM elements exist ----- */
    var jsArea = document.getElementById('controller-area-js');
    if (jsArea && !document.getElementById('as-script-list')) {
      var toolbar = document.createElement('div');
      toolbar.id = 'as-panel-toolbar';
      toolbar.innerHTML =
        '<div class="as-search-area"><i></i>' +
        '<input type="text" id="as-search" placeholder="Search scripts…" autocomplete="off"></div>' +
        '<button id="as-add-script-btn">+ New Script</button>';
      jsArea.insertBefore(toolbar, jsArea.firstChild);

      var list = document.createElement('div');
      list.id = 'as-script-list';
      jsArea.insertBefore(list, toolbar.nextSibling);

      var ec = document.createElement('div');
      ec.id = 'as-editor-container';
      ec.className = 'none';
      ec.innerHTML =
        '<div id="as-editor-header"><span id="as-editor-filename"></span>' +
        '<span id="as-editor-expand" title="Open in new tab">\u21F1</span>' +
        '<span id="as-editor-close" title="Close">&times;</span></div>' +
        '<div id="as-editor"></div>';
      jsArea.appendChild(ec);
      _log.info('AS Panel: created missing DOM elements');
    }

    elScriptList = document.getElementById('as-script-list');
    elSearch = document.getElementById('as-search');
    elAddBtn = document.getElementById('as-add-script-btn');
    elEditorContainer = document.getElementById('as-editor-container');
    elEditorDiv = document.getElementById('as-editor');
    elEditorFilename = document.getElementById('as-editor-filename');
    elEditorClose = document.getElementById('as-editor-close');
    elEditorExpand = document.getElementById('as-editor-expand');
    elFrameScriptBox = document.getElementById('javascript-internal-list-box');

    if (!elScriptList || !elSearch || !elAddBtn) {
      _log.warn('UI elements not found, retrying in 1s…');
      return setTimeout(init, 1000);
    }

    _log.info('Initialized — Ace available:', typeof ace !== 'undefined');

    elSearch.addEventListener('input', function (e) {
      searchQuery = e.target.value;
      renderScriptList();
    });
    elAddBtn.addEventListener('click', showNewScriptDialog);
    if (elEditorClose) elEditorClose.addEventListener('click', closeEditor);
    var editorHeader = document.getElementById('as-editor-header');
    if (editorHeader) editorHeader.addEventListener('mousedown', beginEditorDrag);
    if (elEditorContainer) {
      elEditorContainer.addEventListener('keydown', onEditorKeyCapture, true);
      elEditorContainer.addEventListener('keypress', onEditorKeyCapture, true);
      elEditorContainer.addEventListener('keyup', onEditorKeyCapture, true);
    }
    document.addEventListener('mousemove', onEditorDragMove);
    document.addEventListener('mouseup', endEditorDrag);
    // Keep editing inside the ActionScript panel to avoid split-state issues.
    if (elEditorExpand) {
      elEditorExpand.style.display = 'none';
      elEditorExpand.removeAttribute('title');
    }

    injectStyles();
    interceptN2DLoads();
    interceptN2DSave();
    monitorProjectLoad();
    loadRoundtripFromStorage();
    window.addEventListener('message', onFloatingWindowMessage);
    window.addEventListener('resize', function () {
      resizeEditorArea();
    });

    // Clear stale scripts from localStorage — start blank until a file is loaded
    scripts = [];
    abcClasses = [];
    rawGlobalTags = [];
    structuredGlobals = {};
    activeScript = null;
    try {
      localStorage.removeItem('n2d_as_scripts');
    } catch (e) {}

    renderScriptList();
  }

  /* ================================================================== */
  /*  CSS                                                                */
  /* ================================================================== */
  function injectStyles() {
    var s = document.createElement('style');
    s.textContent =
      '#as-panel-toolbar{display:flex;align-items:center;gap:4px;padding:4px 6px;border-bottom:1px solid #444;background:#2a2a2a;flex-shrink:0}' +
      '.as-search-area{display:flex;align-items:center;flex:1;background:#1a1a1a;border-radius:3px;padding:0 6px}' +
      '.as-search-area i{width:14px;height:14px;opacity:.5;background:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 16 16\' fill=\'%23ccc\'%3E%3Cpath d=\'M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85zm-5.242.156a5 5 0 1 1 0-10 5 5 0 0 1 0 10z\'/%3E%3C/svg%3E") center/contain no-repeat}' +
      '#as-search{flex:1;background:transparent;border:none;color:#ccc;font:11px/1.4 Arial,sans-serif;padding:4px 6px;outline:none}' +
      '#as-search::placeholder{color:#666}' +
      '#as-add-script-btn{padding:3px 10px;background:#3a6;color:#fff;border:none;border-radius:3px;cursor:pointer;font:bold 11px/1.4 Arial,sans-serif;white-space:nowrap;user-select:none}' +
      '#as-add-script-btn:hover{background:#4b7}' +
      '#as-script-list{flex-shrink:0;max-height:25vh;overflow-y:auto;border-bottom:1px solid #444}' +
      '.as-script-item{display:flex;align-items:center;padding:5px 8px;cursor:pointer;border-bottom:1px solid #333;user-select:none}' +
      '.as-script-item:hover{background:#383838}' +
      '.as-script-item.active{background:#2a4a6a}' +
      '.as-script-icon{width:16px;height:16px;margin-right:8px;flex-shrink:0}' +
      '.as-script-icon.source{background:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 16 16\' fill=\'%2390caf9\'%3E%3Cpath d=\'M4 1h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2zm1 3v1h6V4H5zm0 2.5v1h4v-1H5zm0 2.5v1h5V9H5z\'/%3E%3C/svg%3E") center/contain no-repeat}' +
      '.as-script-icon.bytecode{background:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 16 16\' fill=\'%23ff9800\'%3E%3Cpath d=\'M4 1h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2zm2 4L4 7l2 2 .7-.7L5.4 7l1.3-1.3L6 5zm4 0l-.7.7L10.6 7l-1.3 1.3.7.7 2-2-2-2z\'/%3E%3C/svg%3E") center/contain no-repeat}' +
      '.as-script-name{flex:1;font:11px/1.4 Arial,sans-serif;color:#ddd;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}' +
      '.as-script-tag{font:9px/1.2 Arial,sans-serif;color:#888;margin-left:6px;padding:1px 5px;background:#333;border-radius:2px;flex-shrink:0}' +
      '.as-script-delete{margin-left:6px;color:#f55;cursor:pointer;font-size:14px;opacity:0;transition:opacity .15s;flex-shrink:0}' +
      '.as-script-item:hover .as-script-delete{opacity:1}' +
      '.as-no-results{padding:12px;text-align:center;color:#666;font:11px/1.6 Arial,sans-serif}' +
      '.as-section-header{padding:4px 8px;font:bold 10px/1.4 Arial,sans-serif;color:#888;text-transform:uppercase;letter-spacing:.5px;background:#222;border-bottom:1px solid #333}' +
      '#as-editor-container{display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden}' +
      '#as-editor-container.none{display:none}' +
      '#as-editor-container.as-floating-window{position:fixed!important;left:56px;top:184px;width:58vw;height:58vh;z-index:9999;background:#1f1f1f;border:1px solid #4a4a4a;box-shadow:0 12px 40px rgba(0,0,0,.5);display:flex!important}' +
      '#as-editor-header{display:flex;align-items:center;padding:4px 8px;background:#2a2a2a;border-bottom:1px solid #444;flex-shrink:0}' +
      '#as-editor-container.as-floating-window #as-editor-header{cursor:move}' +
      '#as-editor-filename{flex:1;font:bold 11px/1.4 Arial,sans-serif;color:#90caf9;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}' +
      '#as-editor-close{cursor:pointer;color:#888;font-size:18px;line-height:1;padding:0 4px;margin-left:8px}' +
      '#as-editor-close:hover{color:#fff}' +
      '#as-editor-expand{cursor:pointer;color:#888;font-size:14px;line-height:1;padding:2px 4px;margin-left:4px;border:1px solid transparent;border-radius:3px;transition:all .15s}' +
      '#as-editor-expand:hover{color:#90caf9;border-color:#555;background:#333}' +
      '#as-editor-expand svg{width:14px;height:14px;vertical-align:middle}' +
      '#as-editor{flex:1;min-height:0;position:relative;overflow:hidden}' +
      '#as-editor.ace_editor{position:relative!important;width:100%!important;height:100%!important}' +
      '#as-editor .ace_gutter{will-change:transform;-webkit-backface-visibility:hidden;backface-visibility:hidden}' +
      '#as-editor .ace_gutter-layer{will-change:transform;-webkit-backface-visibility:hidden;backface-visibility:hidden}' +
      '#as-editor .ace_scroller{will-change:transform;-webkit-backface-visibility:hidden;backface-visibility:hidden}' +
      '#as-editor .ace_content{will-change:transform;-webkit-backface-visibility:hidden;backface-visibility:hidden}' +
      '#as-editor .ace_text-layer{will-change:transform;-webkit-backface-visibility:hidden;backface-visibility:hidden}' +
      '#as-editor-fallback{width:100%;height:100%;background:#272822;color:#f8f8f2;border:none;padding:8px;font:13px/1.5 "Courier New",monospace;resize:none;outline:none;box-sizing:border-box;position:absolute;top:0;left:0}' +
      '#javascript-internal-list-box{height:auto!important;max-height:30vh!important;flex-shrink:0!important;flex-grow:0!important;border:none!important}' +
      '#as-panel-toolbar{flex-shrink:0}' +
      '#as-new-script-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.6);z-index:100000;display:flex;align-items:center;justify-content:center}' +
      '#as-new-script-dialog{background:#2a2a2a;border:1px solid #555;border-radius:6px;padding:20px;min-width:360px;box-shadow:0 8px 32px rgba(0,0,0,.5)}' +
      '#as-new-script-dialog h3{margin:0 0 12px;font:bold 14px/1.4 Arial,sans-serif;color:#ddd}' +
      '#as-new-script-dialog label{display:block;font:11px/1.6 Arial,sans-serif;color:#aaa;margin-bottom:4px}' +
      '#as-new-script-dialog input,#as-new-script-dialog select{width:100%;padding:6px 8px;background:#1a1a1a;border:1px solid #555;border-radius:3px;color:#ddd;font:12px/1.4 monospace;margin-bottom:12px;box-sizing:border-box}' +
      '#as-new-script-dialog .dialog-buttons{display:flex;justify-content:flex-end;gap:8px;margin-top:4px}' +
      '#as-new-script-dialog .dialog-buttons button{padding:6px 16px;border:none;border-radius:3px;cursor:pointer;font:12px/1.4 Arial,sans-serif}' +
      '#as-new-script-dialog .btn-cancel{background:#444;color:#ccc}' +
      '#as-new-script-dialog .btn-cancel:hover{background:#555}' +
      '#as-new-script-dialog .btn-create{background:#3a6;color:#fff}' +
      '#as-new-script-dialog .btn-create:hover{background:#4b7}';
    document.head.appendChild(s);
  }

  function onEditorKeyCapture(e) {
    if (!elEditorContainer || elEditorContainer.classList.contains('none')) return;
    // Prevent timeline/canvas global shortcuts from consuming editor keys.
    e.stopPropagation();
  }

  function beginEditorDrag(e) {
    if (!elEditorContainer || !elEditorContainer.classList.contains('as-floating-window')) return;
    if (e.button !== 0) return;
    if (e.target && (e.target.id === 'as-editor-close' || e.target.id === 'as-editor-expand')) return;
    var rect = elEditorContainer.getBoundingClientRect();
    editorDragState = {
      dx: e.clientX - rect.left,
      dy: e.clientY - rect.top
    };
    e.preventDefault();
  }

  function onEditorDragMove(e) {
    if (!editorDragState || !elEditorContainer) return;
    var vw = window.innerWidth || document.documentElement.clientWidth || 0;
    var vh = window.innerHeight || document.documentElement.clientHeight || 0;
    var w = elEditorContainer.offsetWidth || 0;
    var h = elEditorContainer.offsetHeight || 0;
    var left = e.clientX - editorDragState.dx;
    var top = e.clientY - editorDragState.dy;
    left = Math.max(8, Math.min(left, Math.max(8, vw - w - 8)));
    top = Math.max(8, Math.min(top, Math.max(8, vh - h - 8)));
    elEditorContainer.style.left = left + 'px';
    elEditorContainer.style.top = top + 'px';
    e.preventDefault();
  }

  function endEditorDrag() {
    editorDragState = null;
  }

  /* ================================================================== */
  /*  ABC Bytecode Parser — extract class names from DoABC tags          */
  /* ================================================================== */

  /** Read a variable-length unsigned 30-bit int (u30/u32 in AVM2). */
  function readU30(body, off) {
    var result = 0,
      shift = 0,
      b;
    for (var i = 0; i < 5; i++) {
      b = body.charCodeAt(off++) & 0xff;
      result |= (b & 0x7f) << shift;
      if (!(b & 0x80)) break;
      shift += 7;
    }
    return {
      v: result >>> 0,
      o: off
    };
  }

  /** Read little-endian u16. */
  function readU16(body, off) {
    return ((body.charCodeAt(off + 1) & 0xff) << 8) | (body.charCodeAt(off) & 0xff);
  }

  /**
   * Parse the ABC constant pool + class table from a DoABC body string.
   * Returns array of {name, pkg, superName}.
   */
  function parseAbcClasses(body, abcStart) {
    var off = abcStart;
    var classes = [];

    try {
      // minor_version(u16), major_version(u16)
      off += 4;

      // ── int pool ──
      var r = readU30(body, off);
      off = r.o;
      var intCount = r.v;
      for (var i = 1; i < intCount; i++) {
        r = readU30(body, off);
        off = r.o; // skip each s32
      }

      // ── uint pool ──
      r = readU30(body, off);
      off = r.o;
      var uintCount = r.v;
      for (var i = 1; i < uintCount; i++) {
        r = readU30(body, off);
        off = r.o;
      }

      // ── double pool ──
      r = readU30(body, off);
      off = r.o;
      var doubleCount = r.v;
      if (doubleCount > 1) {
        off += (doubleCount - 1) * 8; // each double = 8 bytes
      }

      // ── string pool ──
      r = readU30(body, off);
      off = r.o;
      var stringCount = r.v;
      var strings = ['']; // index 0 = empty
      for (var i = 1; i < stringCount; i++) {
        r = readU30(body, off);
        off = r.o;
        var len = r.v;
        var s = '';
        for (var j = 0; j < len; j++) {
          s += String.fromCharCode(body.charCodeAt(off + j) & 0xff);
        }
        // Try to decode as UTF-8
        try {
          s = decodeURIComponent(escape(s));
        } catch (e) {
          /* keep raw */ }
        strings.push(s);
        off += len;
      }

      // ── namespace pool ──
      r = readU30(body, off);
      off = r.o;
      var nsCount = r.v;
      var namespaces = [{
        kind: 0,
        name: ''
      }]; // index 0
      for (var i = 1; i < nsCount; i++) {
        var kind = body.charCodeAt(off++) & 0xff;
        r = readU30(body, off);
        off = r.o;
        namespaces.push({
          kind: kind,
          name: strings[r.v] || ''
        });
      }

      // ── ns_set pool ──
      r = readU30(body, off);
      off = r.o;
      var nsSetCount = r.v;
      for (var i = 1; i < nsSetCount; i++) {
        r = readU30(body, off);
        off = r.o;
        var cnt = r.v;
        for (var j = 0; j < cnt; j++) {
          r = readU30(body, off);
          off = r.o;
        }
      }

      // ── multiname pool ──
      r = readU30(body, off);
      off = r.o;
      var mnCount = r.v;
      var multinames = [null]; // index 0
      for (var i = 1; i < mnCount; i++) {
        var mnKind = body.charCodeAt(off++) & 0xff;
        var mn = {
          kind: mnKind,
          ns: '',
          name: ''
        };
        switch (mnKind) {
          case 0x07: // QName
          case 0x0D: // QNameA
            r = readU30(body, off);
            off = r.o;
            mn.ns = namespaces[r.v] ? namespaces[r.v].name : '';
            r = readU30(body, off);
            off = r.o;
            mn.name = strings[r.v] || '';
            break;
          case 0x0F: // RTQName
          case 0x10: // RTQNameA
            r = readU30(body, off);
            off = r.o;
            mn.name = strings[r.v] || '';
            break;
          case 0x11: // RTQNameL
          case 0x12: // RTQNameLA
            break;
          case 0x09: // Multiname
          case 0x0E: // MultinameA
            r = readU30(body, off);
            off = r.o;
            mn.name = strings[r.v] || '';
            r = readU30(body, off);
            off = r.o;
            break;
          case 0x1B: // MultinameL
          case 0x1C: // MultinameLA
            r = readU30(body, off);
            off = r.o;
            break;
          case 0x1D: // TypeName (generic)
            r = readU30(body, off);
            off = r.o;
            var r2 = readU30(body, off);
            off = r2.o;
            var paramCount = r2.v;
            for (var j = 0; j < paramCount; j++) {
              r2 = readU30(body, off);
              off = r2.o;
            }
            break;
          default:
            // Unknown kind — bail out of multiname parsing
            _log.warn('Unknown multiname kind:', mnKind, 'at offset', off);
            multinames.push(mn);
            return classes;
        }
        multinames.push(mn);
      }

      // ── method pool (skip) ──
      r = readU30(body, off);
      off = r.o;
      var methodCount = r.v;
      for (var i = 0; i < methodCount; i++) {
        r = readU30(body, off);
        off = r.o; // param_count
        var paramCnt = r.v;
        r = readU30(body, off);
        off = r.o; // return_type
        for (var j = 0; j < paramCnt; j++) {
          r = readU30(body, off);
          off = r.o; // param_type
        }
        r = readU30(body, off);
        off = r.o; // name
        var flags = body.charCodeAt(off++) & 0xff;
        if (flags & 0x08) { // HAS_OPTIONAL
          r = readU30(body, off);
          off = r.o;
          var optCount = r.v;
          for (var j = 0; j < optCount; j++) {
            r = readU30(body, off);
            off = r.o; // val
            off++; // kind
          }
        }
        if (flags & 0x80) { // HAS_PARAM_NAMES
          for (var j = 0; j < paramCnt; j++) {
            r = readU30(body, off);
            off = r.o;
          }
        }
      }

      // ── metadata pool (skip) ──
      r = readU30(body, off);
      off = r.o;
      var metadataCount = r.v;
      for (var i = 0; i < metadataCount; i++) {
        r = readU30(body, off);
        off = r.o; // name
        r = readU30(body, off);
        off = r.o; // item_count
        var itemCnt = r.v;
        for (var j = 0; j < itemCnt; j++) {
          r = readU30(body, off);
          off = r.o; // key
          r = readU30(body, off);
          off = r.o; // value
        }
      }

      // ── instance_info[] — THIS is what we want ──
      r = readU30(body, off);
      off = r.o;
      var classCount = r.v;

      for (var i = 0; i < classCount; i++) {
        r = readU30(body, off);
        off = r.o;
        var nameIdx = r.v;
        r = readU30(body, off);
        off = r.o;
        var superIdx = r.v;
        var instFlags = body.charCodeAt(off++) & 0xff;

        if (instFlags & 0x08) { // CONSTANT_ClassProtectedNs
          r = readU30(body, off);
          off = r.o; // protectedNs
        }

        r = readU30(body, off);
        off = r.o;
        var intfCount = r.v;
        for (var j = 0; j < intfCount; j++) {
          r = readU30(body, off);
          off = r.o;
        }

        r = readU30(body, off);
        off = r.o; // iinit (method index)

        // traits
        r = readU30(body, off);
        off = r.o;
        var traitCount = r.v;
        for (var j = 0; j < traitCount; j++) {
          off = skipTrait(body, off);
        }

        var mn = multinames[nameIdx];
        var superMn = superIdx > 0 ? multinames[superIdx] : null;
        if (mn) {
          classes.push({
            name: mn.name || ('Class_' + i),
            pkg: mn.ns || '',
            superName: superMn ? (superMn.ns ? superMn.ns + '.' : '') + superMn.name : ''
          });
        }
      }
    } catch (e) {
      _log.warn('ABC parse error at offset', off, ':', e.message);
    }

    return classes;
  }

  /** Skip a single trait_info structure, return new offset. */
  function skipTrait(body, off) {
    var r = readU30(body, off);
    off = r.o; // name
    var kindByte = body.charCodeAt(off++) & 0xff;
    var kind = kindByte & 0x0f;
    var attrs = (kindByte >> 4) & 0x0f;

    switch (kind) {
      case 0: // Slot
      case 6: // Const
        r = readU30(body, off);
        off = r.o; // slot_id
        r = readU30(body, off);
        off = r.o; // type_name
        r = readU30(body, off);
        off = r.o; // vindex
        if (r.v !== 0) off++; // vkind
        break;
      case 1: // Method
      case 2: // Getter
      case 3: // Setter
        r = readU30(body, off);
        off = r.o; // disp_id
        r = readU30(body, off);
        off = r.o; // method
        break;
      case 4: // Class
        r = readU30(body, off);
        off = r.o; // slot_id
        r = readU30(body, off);
        off = r.o; // classi
        break;
      case 5: // Function
        r = readU30(body, off);
        off = r.o; // slot_id
        r = readU30(body, off);
        off = r.o; // function
        break;
    }
    if (attrs & 0x04) { // ATTR_Metadata
      r = readU30(body, off);
      off = r.o;
      var mc = r.v;
      for (var j = 0; j < mc; j++) {
        r = readU30(body, off);
        off = r.o;
      }
    }
    return off;
  }

  /**
   * Parse all DoABC tags in rawGlobalTags and populate abcClasses[].
   */
  function extractAbcClasses() {
    _log.debug('Extracting ABC classes from', rawGlobalTags.length, 'global tags');
    abcClasses = [];
    rawGlobalTags.forEach(function (tag, tagIdx) {
      if (tag.tagType !== DOABC_TAG && tag.tagType !== DOABC1_TAG) return;

      var body = tag.body;
      if (!body || body.length < 10) return;

      var abcStart = 0;
      var tagName = '';

      if (tag.tagType === DOABC_TAG) {
        // DoABC2: 4 bytes flags + null-terminated name + abc data
        abcStart = 4;
        var nameChars = [];
        for (var i = 4; i < Math.min(body.length, 260); i++) {
          var c = body.charCodeAt(i) & 0xff;
          if (c === 0) {
            abcStart = i + 1;
            break;
          }
          nameChars.push(String.fromCharCode(c));
        }
        tagName = nameChars.join('');
      }

      _log.info('Parsing DoABC tag "' + tagName + '" (' + body.length + ' bytes)');

      var parsed = parseAbcClasses(body, abcStart);
      parsed.forEach(function (cls) {
        cls.tagIdx = tagIdx;
        cls.tagName = tagName;
        abcClasses.push(cls);
      });

      _log.info('Found', parsed.length, 'ABC classes in tag "' + tagName + '"');
    });
  }

  /* ================================================================== */
  /*  Intercept N2D file loads                                           */
  /* ================================================================== */
  function interceptN2DLoads() {
    if (importInterceptionInstalled) return;
    importInterceptionInstalled = true;
    // Use delegated listener so interception still works when inputs are
    // created after this panel initializes.
    document.addEventListener('change', onAnyFileInputChange, true);
    hookFileInput('tools-load-file-input');
    hookFileInput('library-menu-import-swf-timeline-input');
    _log.info('Import interception installed');
  }

  function onAnyFileInputChange(e) {
    var target = e && e.target;
    if (!target || (target.id !== 'tools-load-file-input' &&
      target.id !== 'library-menu-import-swf-timeline-input')) {
      return;
    }
    onImportInputChange(target);
  }

  function hookFileInput(inputId) {
    var input = document.getElementById(inputId);
    if (!input) {
      _log.debug('Import input not found at init:', inputId);
      return;
    }
    input.addEventListener('change', function () {
      onImportInputChange(input);
    }, true);
  }

  function onImportInputChange(input) {
    if (!input || !input.files || !input.files.length) return;
    var file = input.files[0];
    var lower = (file.name || '').toLowerCase();
    if (lower.endsWith('.swf')) {
      _log.info('Detected SWF import start:', file.name);
      beginProjectLoad('swf:' + file.name);
      return;
    }
    if (!lower.endsWith('.n2d')) return;
    _log.info('Intercepting N2D load:', file.name);
    parseN2DFile(file);
  }

  function beginProjectLoad(reason) {
    _log.info('Project load reset:', reason || 'unknown');
    scripts = [];
    _projectScriptsLoaded = false;
    abcClasses = [];
    rawGlobalTags = [];
    structuredGlobals = {};
    roundtripData = null;
    scriptsModified = false;
    activeScript = null;
    if (elEditorContainer) elEditorContainer.classList.add('none');
    saveScriptsToStorage();
    renderScriptList();
    clearNext2dToolData();
  }

  function clearNext2dToolData() {
    try {
      var req = indexedDB.open('next2d-tool');
      req.onsuccess = function (e) {
        var db = e.target.result;
        var stores = Array.from(db.objectStoreNames || []);
        if (!stores.length) {
          db.close();
          return;
        }
        var tx = db.transaction(stores, 'readwrite');
        stores.forEach(function (sn) {
          try {
            tx.objectStore(sn).clear();
          } catch (ex) {
            _log.warn('Skipping clear for store:', sn, ex);
          }
        });
        tx.oncomplete = function () {
          _log.info('Cleared next2d-tool IndexedDB stores:', stores.length);
          db.close();
        };
        tx.onerror = function () {
          _log.warn('Failed clearing next2d-tool IndexedDB');
          db.close();
        };
      };
      req.onerror = function () {
        _log.warn('Unable to open next2d-tool IndexedDB for clear');
      };
    } catch (e) {
      _log.warn('IndexedDB clear failed:', e);
    }
  }

  function parseN2DFile(file) {
    beginProjectLoad('n2d:' + file.name);
    // Keep previousOriginal for merging rootTimelineDefIds on tool reloads
    var previousOriginal = originalN2DJson;

    var reader = new FileReader();
    reader.onload = function (e) {
      var data = new Uint8Array(e.target.result);
      decompressN2D(data).then(function (json) {
        if (!json) return;

        // If this N2D is from a tool reload (no rootTimelineDefIds) but
        // we have it from the original server import, restore it.
        if (!json.rootTimelineDefIds && previousOriginal && previousOriginal.rootTimelineDefIds) {
          json.rootTimelineDefIds = previousOriginal.rootTimelineDefIds;
          _log.info('Restored rootTimelineDefIds from previous session:',
            json.rootTimelineDefIds.length, 'ids');
        }
        // Same for root totalFrame
        if (previousOriginal && previousOriginal.rootTotalFrame !== undefined) {
          if (Array.isArray(json.libraries)) {
            json.libraries.forEach(function (lib) {
              if (lib && lib.id === 0 && (lib.totalFrame === undefined || lib.totalFrame === 1)) {
                lib.totalFrame = previousOriginal.rootTotalFrame;
              }
            });
          }
        }

        // Store full parsed JSON for fallback during export
        originalN2DJson = json;
        // Only save to IDB if we have rootTimelineDefIds
        // (don't overwrite good import data with tool's stripped reload)
        if (json.rootTimelineDefIds) {
          saveOriginalN2DToIDB(json);
        }

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
          _projectScriptsLoaded = true;
        }
        if (Array.isArray(json.rawGlobalTags) && json.rawGlobalTags.length > 0) {
          _log.info('Found', json.rawGlobalTags.length, 'rawGlobalTags');
          rawGlobalTags = json.rawGlobalTags;
          extractAbcClasses();
        }
        // Load structured global fields
        structuredGlobals = {};
        ['abcBlocks', 'protectFromImport', 'metadata', 'sceneAndFrameLabels',
         'soundStream', 'importAssets'].forEach(function (key) {
          if (json[key] !== undefined) {
            structuredGlobals[key] = json[key];
          }
        });
        captureRoundtripData(json);
        renderScriptList();
      }).catch(function (ex) {
        _log.error('N2D parse failed:', ex);
      });
    };
    reader.readAsArrayBuffer(file);
  }

  function decompressN2D(data) {
    // Detect ZIP-based N2D format (PK magic bytes)
    if (data.length >= 4 && data[0] === 0x50 && data[1] === 0x4B) {
      if (typeof JSZip !== 'undefined') {
        return JSZip.loadAsync(data.buffer).then(function (zip) {
          // Try MessagePack format first (preferred)
          if (zip.file('project.msgpack')) {
            _log.info('Loading MessagePack format (binary)');
            return zip.file('project.msgpack').async('uint8array').then(function (msgpackData) {
              // Check if @msgpack/msgpack is available
              if (typeof MessagePack !== 'undefined' && MessagePack.decode) {
                try {
                  var decoded = MessagePack.decode(msgpackData);
                  _log.info('MessagePack decoded successfully');
                  return decoded;
                } catch (e) {
                  _log.error('MessagePack decode failed:', e);
                  return null;
                }
              } else {
                _log.error('MessagePack library not loaded, cannot decode .msgpack format');
                return null;
              }
            });
          }
          // Fall back to JSON format (legacy)
          _log.info('Loading JSON format (legacy)');
          return zip.file('project.json').async('string');
        }).then(function (result) {
          // If result is already an object (from MessagePack), return it
          if (typeof result === 'object') return result;
          // Otherwise parse JSON
          try {
            return JSON.parse(result);
          } catch (e) {
            return null;
          }
        }).catch(function (err) {
          _log.error('ZIP parse failed:', err);
          return null;
        });
      }
      _log.warn('ZIP N2D but JSZip not available');
      return Promise.resolve(null);
    }
    // Legacy zlib-compressed format
    if (typeof DecompressionStream !== 'undefined') {
      return decompressWithStream(data).catch(function () {
        return tryPlainText(data);
      });
    }
    return Promise.resolve(tryPlainText(data));
  }

  function decompressWithStream(data) {
    var ds = new DecompressionStream('deflate');
    var w = ds.writable.getWriter();
    w.write(data);
    w.close();
    return new Response(ds.readable).text().then(function (text) {
      try {
        return JSON.parse(decodeURIComponent(text));
      } catch (e) {
        return JSON.parse(text);
      }
    });
  }

  function tryPlainText(data) {
    try {
      var text = new TextDecoder().decode(data);
      try {
        return JSON.parse(decodeURIComponent(text));
      } catch (e) {
        return JSON.parse(text);
      }
    } catch (e) {
      return null;
    }
  }

  /* ================================================================== */
  /*  Roundtrip data capture & save interception                          */
  /* ================================================================== */

  /** Per-library fields that the tool's toJSON() strips but we must preserve. */
  var ROUNDTRIP_LIB_FIELDS = ['swfCharId',
    'inBitmap', 'grid', 'bitmapId',
    'rawSoundStreamHead', 'mode', 'totalFrame',
    'fontData', 'fontTagType', 'fontAuxTags',
    'buttonData', 'binaryDataBody', 'soundFormat', 'buttonAuxTags',
    'soundStreamParsed'
  ];

  /**
   * Keys to EXCLUDE when computing a library content hash.
   * These are roundtrip-only fields or tool UI state — not user-visible content.
   */
  var CONTENT_SKIP_KEYS = {
    swfCharId: true,
    inBitmap: true,
    grid: true,
    bitmapId: true,
    rawSoundStreamHead: true,
    soundStreamParsed: true,
    mode: true,
    currentFrame: true,
    leftFrame: true,
    fontData: true,
    fontTagType: true,
    fontAuxTags: true,
    buttonData: true,
    binaryDataBody: true,
    soundFormat: true,
    buttonAuxTags: true
  };

  /**
   * Deterministic JSON.stringify with sorted keys, so that the same
   * logical object always produces the same string regardless of
   * property insertion order.
   */
  function stableStringify(val) {
    if (val === null || val === undefined) return 'null';
    if (typeof val === 'boolean') return val ? 'true' : 'false';
    if (typeof val === 'number') return isFinite(val) ? String(val) : 'null';
    if (typeof val === 'string') {
      // For very large strings (bitmap buffers), use a size + sample fingerprint
      if (val.length > 5000) {
        return '"L' + val.length + ':' + val.substring(0, 200) +
          ':' + val.substring(val.length - 200) + '"';
      }
      return JSON.stringify(val);
    }
    if (Array.isArray(val)) {
      // For very large arrays, fingerprint rather than full traverse
      if (val.length > 5000) {
        var head = val.slice(0, 50).map(stableStringify).join(',');
        var tail = val.slice(-50).map(stableStringify).join(',');
        return '[L' + val.length + ':' + head + ':' + tail + ']';
      }
      return '[' + val.map(stableStringify).join(',') + ']';
    }
    if (typeof val === 'object') {
      var keys = Object.keys(val).sort();
      return '{' + keys.map(function (k) {
        return JSON.stringify(k) + ':' + stableStringify(val[k]);
      }).join(',') + '}';
    }
    return String(val);
  }

  /** djb2 hash — fast, deterministic 31-bit hash of a string. */
  function djb2Hash(str) {
    var hash = 5381;
    for (var i = 0; i < str.length; i++) {
      hash = ((hash << 5) + hash + str.charCodeAt(i)) & 0x7FFFFFFF;
    }
    return hash;
  }

  /**
   * Compute a content fingerprint for a library, excluding roundtrip
   * and UI-state fields.  Used to detect whether the user has edited
   * a library's visual data since it was loaded.
   */
  function computeLibContentHash(lib) {
    var filtered = {};
    for (var k in lib) {
      if (lib.hasOwnProperty(k) && !CONTENT_SKIP_KEYS[k] && k.charAt(0) !== '_') {
        filtered[k] = lib[k];
      }
    }
    return djb2Hash(stableStringify(filtered));
  }

  /**
   * Capture all roundtrip-relevant fields from an N2D JSON so they
   * can be re-injected when the user saves.
   */
  function captureRoundtripData(json) {
    roundtripData = {};

    // Log ALL top-level keys for debugging
    _log.debug('N2D JSON keys:', Object.keys(json).join(', '));

    // Top-level SWF metadata fields
    ['swfVersion', 'swfCompressed', 'rootTimelineDefIds', 'version',
      'characterId'
    ].forEach(function (key) {
      if (json[key] !== undefined) roundtripData[key] = json[key];
    });

    // Per-library roundtrip fields
    var libMeta = {};
    if (Array.isArray(json.libraries)) {
      json.libraries.forEach(function (lib) {
        var meta = {};
        var has = false;
        ROUNDTRIP_LIB_FIELDS.forEach(function (f) {
          if (lib[f] !== undefined) {
            meta[f] = lib[f];
            has = true;
          }
        });

        // Deep capture: layer-level custom fields for containers
        if (lib.type === 'container' && Array.isArray(lib.layers)) {
          var layerCustom = captureLayerCustomFields(lib.layers);
          if (layerCustom) {
            meta._layerCustom = layerCustom;
            has = true;
          }
        }

        // Content hash for edit detection
        meta._contentHash = computeLibContentHash(lib);
        has = true;

        if (has) libMeta[lib.id] = meta;
      });
    }
    if (Object.keys(libMeta).length > 0) roundtripData.libraries = libMeta;

    saveRoundtripToStorage();
    _log.debug('Captured roundtrip data:',
      Object.keys(roundtripData).join(', '));
  }

  /**
   * Capture custom fields nested inside layers, characters, and places.
   * Returns a compact structure keyed by layer name, or null if nothing custom.
   */
  function captureLayerCustomFields(layers) {
    var result = {};
    var hasAny = false;
    for (var i = 0; i < layers.length; i++) {
      var layer = layers[i];
      var layerData = {};
      var layerHas = false;

      // swfDepth on the layer itself
      if (layer.swfDepth !== undefined) {
        layerData.swfDepth = layer.swfDepth;
        layerHas = true;
      }

      // Per-character: reinstated, and per-place: ratio
      if (Array.isArray(layer.characters)) {
        var charCustom = [];
        var charHasAny = false;
        for (var c = 0; c < layer.characters.length; c++) {
          var ch = layer.characters[c];
          var cd = {};
          if (ch.reinstated !== undefined) {
            cd.reinstated = ch.reinstated;
          }
          // Per-place ratio
          if (Array.isArray(ch.places)) {
            var placeRatios = [];
            var hasRatio = false;
            for (var p = 0; p < ch.places.length; p++) {
              if (ch.places[p].ratio !== undefined) {
                placeRatios.push({
                  idx: p,
                  ratio: ch.places[p].ratio
                });
                hasRatio = true;
              }
            }
            if (hasRatio) cd.placeRatios = placeRatios;
          }
          charCustom.push(cd);
          if (cd.reinstated !== undefined || cd.placeRatios) charHasAny = true;
        }
        if (charHasAny) {
          layerData.charCustom = charCustom;
          layerHas = true;
        }
      }

      if (layerHas) {
        // Key by layer index (position-stable)
        result[i] = layerData;
        hasAny = true;
      }
    }
    return hasAny ? result : null;
  }

  /* ================================================================== */
  /*  IndexedDB helpers — reliable storage for large roundtrip data      */
  /* ================================================================== */
  var IDB_NAME = 'n2d-as-roundtrip';
  var IDB_VERSION = 1;
  var IDB_STORE = 'data';

  function openIDB() {
    return new Promise(function (resolve, reject) {
      var req = indexedDB.open(IDB_NAME, IDB_VERSION);
      req.onupgradeneeded = function (e) {
        e.target.result.createObjectStore(IDB_STORE);
      };
      req.onsuccess = function (e) {
        resolve(e.target.result);
      };
      req.onerror = function () {
        reject(req.error);
      };
    });
  }

  function saveToIDB(key, value) {
    _log.debug('IDB save:', key);
    openIDB().then(function (db) {
      var tx = db.transaction(IDB_STORE, 'readwrite');
      tx.objectStore(IDB_STORE).put(value, key);
      tx.oncomplete = function () {
        db.close();
      };
      tx.onerror = function () {
        db.close();
      };
    }).catch(function (e) {
      _log.error('IDB save error:', e);
    });
  }

  function loadFromIDB(key) {
    _log.debug('IDB load:', key);
    return openIDB().then(function (db) {
      return new Promise(function (resolve) {
        var tx = db.transaction(IDB_STORE, 'readonly');
        var req = tx.objectStore(IDB_STORE).get(key);
        req.onsuccess = function () {
          resolve(req.result || null);
        };
        req.onerror = function () {
          resolve(null);
        };
        tx.oncomplete = function () {
          db.close();
        };
      });
    }).catch(function () {
      return null;
    });
  }

  /**
   * Save critical fields from the original N2D to IndexedDB for
   * cross-session recovery (page reload without re-import).
   */
  function saveOriginalN2DToIDB(json) {
    // Read-modify-write: merge new fields into existing IDB data
    // so we never accidentally clobber rootTimelineDefIds
    loadFromIDB('originalN2D').then(function (existing) {
      var critical = existing || {};
      if (json.rootTimelineDefIds) critical.rootTimelineDefIds = json.rootTimelineDefIds;
      if (json.swfVersion !== undefined) critical.swfVersion = json.swfVersion;
      if (json.swfCompressed !== undefined) critical.swfCompressed = json.swfCompressed;
      if (json.version !== undefined) critical.version = json.version;
      if (json.characterId !== undefined) critical.characterId = json.characterId;
      // Root container totalFrame
      if (Array.isArray(json.libraries)) {
        json.libraries.forEach(function (lib) {
          if (lib && lib.id === 0 && lib.totalFrame !== undefined) {
            critical.rootTotalFrame = lib.totalFrame;
          }
        });
      }
      saveToIDB('originalN2D', critical);
    }).catch(function () {
      // IDB read failed — write fresh
      var critical = {};
      if (json.rootTimelineDefIds) critical.rootTimelineDefIds = json.rootTimelineDefIds;
      if (json.swfVersion !== undefined) critical.swfVersion = json.swfVersion;
      if (json.swfCompressed !== undefined) critical.swfCompressed = json.swfCompressed;
      saveToIDB('originalN2D', critical);
    });
  }

  function saveRoundtripToStorage() {
    // Save to IndexedDB (large data, reliable)
    saveToIDB('roundtrip', roundtripData);
    // Also try localStorage (fast sync access on reload)
    try {
      localStorage.setItem('n2d_roundtrip', JSON.stringify(roundtripData || {}));
    } catch (e) {
      _log.warn('localStorage full for roundtrip:', e.name);
    }
  }

  function loadRoundtripFromStorage() {
    // Try localStorage first (sync, fast)
    try {
      var s = localStorage.getItem('n2d_roundtrip');
      if (s) {
        var data = JSON.parse(s);
        if (data && data.rootTimelineDefIds) {
          roundtripData = data;
          _log.debug('Loaded roundtrip from localStorage, keys:',
            Object.keys(data).join(', '));
          return;
        }
        // localStorage data exists but lacks rootTimelineDefIds — stale
        if (data && Object.keys(data).length > 0) {
          _log.warn('localStorage roundtrip data is stale (no rootTimelineDefIds)');
          roundtripData = data; // Use as partial fallback
        }
      }
    } catch (e) {
      /* ignore parse errors */ }

    // Try IndexedDB (async, larger storage, more reliable)
    loadFromIDB('roundtrip').then(function (data) {
      if (data) {
        // Only overwrite if parseN2DFile hasn't already run
        if (!roundtripData || !roundtripData.rootTimelineDefIds) {
          roundtripData = data;
          _log.debug('Loaded roundtrip from IndexedDB, keys:',
            Object.keys(data).join(', '));
        }
      }
    }).catch(function () {});

    // Also try to restore original N2D critical fields from IndexedDB
    loadFromIDB('originalN2D').then(function (data) {
      if (data) {
        if (!originalN2DJson) {
          originalN2DJson = data;
        } else if (!originalN2DJson.rootTimelineDefIds && data.rootTimelineDefIds) {
          // Merge rootTimelineDefIds into existing originalN2DJson
          originalN2DJson.rootTimelineDefIds = data.rootTimelineDefIds;
        }
        if (data.rootTotalFrame !== undefined && !originalN2DJson.rootTotalFrame) {
          originalN2DJson.rootTotalFrame = data.rootTotalFrame;
        }
        // Also ensure roundtripData has rootTimelineDefIds
        if (data.rootTimelineDefIds && roundtripData && !roundtripData.rootTimelineDefIds) {
          roundtripData.rootTimelineDefIds = data.rootTimelineDefIds;
          _log.debug('Merged rootTimelineDefIds into roundtripData from IDB');
        }
        _log.debug('Loaded original N2D critical fields from IndexedDB,',
          'rootTimelineDefIds:', data.rootTimelineDefIds ? data.rootTimelineDefIds.length + ' ids' : 'none');
      }
    }).catch(function () {});
  }

  function hasRoundtripData() {
    return scripts.length > 0 || rawGlobalTags.length > 0 ||
      Object.keys(structuredGlobals).length > 0 ||
      (roundtripData && Object.keys(roundtripData).length > 0);
  }

  /**
   * Intercept the #save-anchor click so we can inject roundtrip fields
   * into the N2D file before it downloads.
   *
   * The tool's save flow:
   *   1. workspace.toJSON() → JSON string (missing our custom fields)
   *   2. zlib worker compresses it
   *   3. Worker posts back compressed buffer
   *   4. Tool creates blob URL, sets it on #save-anchor, calls anchor.click()
   *
   * We override anchor.click() to: fetch blob → inflate → inject → deflate → download.
   */
  function interceptN2DSave() {
    var anchor = document.getElementById('save-anchor');
    if (!anchor) {
      _log.warn('save-anchor not found, save interception disabled');
      return;
    }

    var origClick = HTMLAnchorElement.prototype.click;

    anchor.click = function () {
      // Only intercept .n2d saves when we have roundtrip data
      if (!this.download || !this.download.endsWith('.n2d') || !hasRoundtripData()) {
        return origClick.call(this);
      }

      var self = this;
      var blobUrl = this.href;
      var downloadName = this.download;

      _log.info('Intercepting N2D save to inject roundtrip data…');

      // Ensure current editor content is captured
      if (activeScript !== null && activeScript < scripts.length) {
        scripts[activeScript].source = getEditorValue();
      }

      fetch(blobUrl)
        .then(function (r) {
          return r.arrayBuffer();
        })
        .then(function (buf) {
          return inflateBuffer(new Uint8Array(buf));
        })
        .then(function (text) {
          var json;
          try {
            json = JSON.parse(decodeURIComponent(text));
          } catch (ex) {
            json = JSON.parse(text);
          }

          // Inject all roundtrip fields
          injectRoundtripFields(json);

          // Recompress: JSON → URI-encode → deflate
          var encoded = encodeURIComponent(JSON.stringify(json));
          var arr = new Uint8Array(encoded.length);
          for (var i = 0; i < encoded.length; i++) arr[i] = encoded.charCodeAt(i);
          return deflateBuffer(arr).then(function (compressed) {
            return {
              compressed: compressed,
              name: downloadName
            };
          });
        })
        .then(function (result) {
          var blob = new Blob([result.compressed], {
            type: 'text/plain'
          });
          var url = URL.createObjectURL(blob);
          var a = document.createElement('a');
          a.href = url;
          a.download = result.name;
          document.body.appendChild(a);
          origClick.call(a);
          document.body.removeChild(a);
          setTimeout(function () {
            URL.revokeObjectURL(url);
          }, 5000);

          var parts = [];
          if (scripts.length) parts.push(scripts.length + ' scripts');
          if (rawGlobalTags.length) parts.push(rawGlobalTags.length + ' SWF tags');
          if (roundtripData && roundtripData.libraries)
            parts.push(Object.keys(roundtripData.libraries).length + ' lib metadata');
          _log.info('N2D saved with roundtrip:', parts.join(', '));
          toast('Saved with ' + parts.join(' + '));
        })
        .catch(function (ex) {
          _log.error('Save injection failed, falling back:', ex);
          origClick.call(self);
        });
    };
  }

  /**
   * Inject scripts, rawGlobalTags, and other SWF roundtrip fields into
   * the workspace JSON produced by the tool's save().
   */
  function injectRoundtripFields(json) {
    // 1) Source scripts
    if (scripts.length > 0) {
      json.scripts = scripts.map(function (s) {
        return {
          name: s.name,
          path: s.path,
          source: s.source
        };
      });
    }

    // 1b) If scripts were edited, set flag so compiler recompiles from source
    //     instead of using raw DoABC passthrough.  Also strip DoABC tags from
    //     rawGlobalTags so the compiler falls through to the mxmlc path.
    if (scriptsModified) {
      json.scriptsModified = true;
      _log.info('Scripts modified — stripping DoABC for recompilation');
    }

    // 2) Raw global SWF tags (DoABC, SymbolClass, etc.)
    if (rawGlobalTags.length > 0) {
      json.rawGlobalTags = rawGlobalTags;
    }

    // 2b) Structured global fields
    if (structuredGlobals) {
      ['abcBlocks', 'protectFromImport', 'metadata', 'sceneAndFrameLabels',
       'soundStream', 'importAssets'].forEach(function (key) {
        if (structuredGlobals[key] !== undefined) {
          json[key] = structuredGlobals[key];
        }
      });
    }

    // 3) Top-level SWF metadata
    if (roundtripData) {
      ['swfVersion', 'swfCompressed', 'rootTimelineDefIds',
        'version', 'characterId'
      ].forEach(function (key) {
        if (roundtripData[key] !== undefined && json[key] === undefined) {
          json[key] = roundtripData[key];
        }
      });

      // 4) Per-library roundtrip fields (fontData, buttonData, etc.)
      if (roundtripData.libraries && Array.isArray(json.libraries)) {
        json.libraries.forEach(function (lib) {
          var meta = roundtripData.libraries[lib.id];
          if (meta) {
            Object.keys(meta).forEach(function (k) {
              if (k === '_layerCustom' || k === '_contentHash') return;
              var isCritical = (k === 'swfCharId' || k === 'fontData' || k === 'fontTagType' ||
                k === 'fontAuxTags' || k === 'totalFrame' ||
                k === 'buttonData' || k === 'binaryDataBody' || k === 'soundFormat' || k === 'buttonAuxTags');
              if (lib[k] === undefined || (isCritical && !lib[k] && meta[k])) {
                lib[k] = meta[k];
              }
            });

            // 5) Deep re-inject: layer/character/place custom fields
            if (meta._layerCustom && Array.isArray(lib.layers)) {
              injectLayerCustomFields(lib.layers, meta._layerCustom);
            }
          }
        });
      }
    }

    // 6) Fallback: if critical fields still missing, try originalN2DJson
    //    (covers page-reload scenarios where localStorage was stale/truncated)
    if (!json.rootTimelineDefIds && originalN2DJson && originalN2DJson.rootTimelineDefIds) {
      json.rootTimelineDefIds = originalN2DJson.rootTimelineDefIds;
      _log.info('Restored rootTimelineDefIds from in-memory original N2D:',
        json.rootTimelineDefIds.length, 'ids');
    }
    if (json.swfVersion === undefined && originalN2DJson && originalN2DJson.swfVersion !== undefined) {
      json.swfVersion = originalN2DJson.swfVersion;
    }

    // 7) Inject root container totalFrame if missing or defaulted
    if (Array.isArray(json.libraries)) {
      var origSource = originalN2DJson || (roundtripData || {});
      json.libraries.forEach(function (lib) {
        if (lib && lib.id === 0) {
          // Try originalN2DJson first, then roundtripData
          var origTotalFrame = null;
          if (originalN2DJson && Array.isArray(originalN2DJson.libraries)) {
            originalN2DJson.libraries.forEach(function (origLib) {
              if (origLib && origLib.id === 0 && origLib.totalFrame !== undefined) {
                origTotalFrame = origLib.totalFrame;
              }
            });
          }
          // Also check roundtripData per-lib metadata
          if (origTotalFrame === null && roundtripData && roundtripData.libraries && roundtripData.libraries[0]) {
            origTotalFrame = roundtripData.libraries[0].totalFrame;
          }
          if (origTotalFrame !== null && origTotalFrame !== undefined && lib.totalFrame !== origTotalFrame) {
            _log.debug('Restored root totalFrame:', origTotalFrame,
              '(was ' + lib.totalFrame + ')');
            lib.totalFrame = origTotalFrame;
          }
        }
      });
    }
  }

  /**
   * Re-inject swfDepth, reinstated, and ratio into layers/characters/places.
   */
  function injectLayerCustomFields(layers, layerCustom) {
    for (var i = 0; i < layers.length; i++) {
      var saved = layerCustom[i];
      if (!saved) continue;

      var layer = layers[i];

      // swfDepth
      if (saved.swfDepth !== undefined && layer.swfDepth === undefined) {
        layer.swfDepth = saved.swfDepth;
      }

      // Per-character custom fields
      if (saved.charCustom && Array.isArray(layer.characters)) {
        for (var c = 0; c < Math.min(saved.charCustom.length, layer.characters.length); c++) {
          var cd = saved.charCustom[c];
          var ch = layer.characters[c];

          // reinstated
          if (cd.reinstated !== undefined && ch.reinstated === undefined) {
            ch.reinstated = cd.reinstated;
          }

          // per-place ratio
          if (cd.placeRatios && Array.isArray(ch.places)) {
            for (var r = 0; r < cd.placeRatios.length; r++) {
              var pr = cd.placeRatios[r];
              if (pr.idx < ch.places.length && ch.places[pr.idx].ratio === undefined) {
                ch.places[pr.idx].ratio = pr.ratio;
              }
            }
          }
        }
      }
    }
  }

  /** Inflate a zlib-compressed Uint8Array, returning the text via a Promise. */
  function inflateBuffer(data) {
    var ds = new DecompressionStream('deflate');
    var w = ds.writable.getWriter();
    w.write(data);
    w.close();
    return new Response(ds.readable).text();
  }

  /** Deflate text/bytes to a zlib-compressed Uint8Array via a Promise. */
  function deflateBuffer(data) {
    var cs = new CompressionStream('deflate');
    var w = cs.writable.getWriter();
    w.write(data);
    w.close();
    return new Response(cs.readable).arrayBuffer().then(function (buf) {
      return new Uint8Array(buf);
    });
  }

  /* ================================================================== */
  /*  Fallback: IndexedDB polling                                        */
  /* ================================================================== */
  function monitorProjectLoad() {
    loadScriptsFromStorage();
    if (scriptPollTimer) clearInterval(scriptPollTimer);
    scriptPollTimer = setInterval(checkForScripts, 5000);
  }

  function saveScriptsToStorage() {
    try {
      localStorage.setItem('n2d_as_scripts', JSON.stringify(scripts));
    } catch (e) {
      /* ignore */ }
  }

  function loadScriptsFromStorage() {
    try {
      var s = localStorage.getItem('n2d_as_scripts');
      if (s) {
        scripts = JSON.parse(s);
        renderScriptList();
      }
    } catch (e) {
      /* ignore */ }
  }

  function checkForScripts() {
    if (_projectScriptsLoaded) return;
    try {
      var req = indexedDB.open('next2d-tool');
      req.onsuccess = function (e) {
        var db = e.target.result;
        _log.debug('Polling next2d-tool stores:', db.objectStoreNames.length);
        Array.from(db.objectStoreNames).forEach(function (sn) {
          try {
            var tx = db.transaction(sn, 'readonly');
            tx.objectStore(sn).getAll().onsuccess = function (ev) {
              (ev.target.result || []).forEach(function (rec) {
                if (rec && typeof rec === 'object') {
                  if (Array.isArray(rec.scripts)) mergeScripts(rec.scripts);
                  if (Array.isArray(rec.rawGlobalTags) && rec.rawGlobalTags.length) {
                    _log.info('Loaded rawGlobalTags from IDB poll:', rec.rawGlobalTags.length);
                    rawGlobalTags = rec.rawGlobalTags;
                    extractAbcClasses();
                    renderScriptList();
                  }
                }
              });
            };
          } catch (ex) {
            /* skip */ }
        });
        db.close();
      };
    } catch (e) {
      /* ignore */ }
  }

  function mergeScripts(newScripts) {
    // Once a project's scripts are loaded (from file or first IDB poll),
    // block any further IDB polling from adding stale data from other projects.
    if (_projectScriptsLoaded) {
      _log.debug('Skipping mergeScripts because project scripts already loaded');
      return;
    }
    var existing = {};
    scripts.forEach(function (s) {
      existing[s.path] = true;
    });
    var added = 0;
    newScripts.forEach(function (s) {
      if (s && s.path && !existing[s.path]) {
        scripts.push({
          name: s.name || s.path.split('/').pop(),
          path: s.path,
          source: s.source || ''
        });
        existing[s.path] = true;
        added++;
      }
    });
    if (added) {
      _log.info('Merged scripts from IDB poll:', added, 'added from', newScripts.length);
      _projectScriptsLoaded = true;
      saveScriptsToStorage();
      renderScriptList();
    }
  }

  /* ================================================================== */
  /*  Render script list                                                 */
  /* ================================================================== */
  function renderScriptList() {
    if (!elScriptList) return;

    var html = '';
    var q = searchQuery.toLowerCase().trim();
    var hasResults = false;

    // ─── Source Scripts (editable) ───
    // Filter: only show scripts that aren't linkage-generated
    var filtered = scripts.filter(function (s) {
      // POLICY: never show linkage-generated scripts in the GUI
      if (s.scriptOrigin === 'linkage-generated') return false;
      if (!q) return true;
      return (s.name + ' ' + s.path + ' ' + (s.source || '')).toLowerCase().indexOf(q) >= 0;
    });
    if (filtered.length > 0 || (!q && scripts.length === 0)) {
      html += '<div class="as-section-header">Source Scripts (' + filtered.length + ')</div>';
      filtered.forEach(function (s) {
        var idx = scripts.indexOf(s);
        var ac = (activeScript === idx) ? ' active' : '';
        var originTag = s.scriptOrigin ? ' [' + s.scriptOrigin + ']' : '';
        html += '<div class="as-script-item' + ac + '" data-type="source" data-index="' + idx + '">' +
          '<div class="as-script-icon source"></div>' +
          '<span class="as-script-name" title="' + esc(s.path) + '">' + esc(s.name) + '</span>' +
          '<span class="as-script-tag">AS3</span>' +
          (s.scriptOrigin ? '<span class="as-script-note">' + esc(originTag) + '</span>' : '') +
          '<span class="as-script-delete" data-index="' + idx + '" title="Delete">&times;</span></div>';
        hasResults = true;
      });
    }

    // ─── ABC classes (parsed from bytecode, read-only) ───
    var filteredAbc = abcClasses.filter(function (c) {
      if (!q) return true;
      return (c.name + ' ' + c.pkg + ' ' + c.superName).toLowerCase().indexOf(q) >= 0;
    });
    if (filteredAbc.length > 0) {
      html += '<div class="as-section-header">Bytecode Classes (' + filteredAbc.length + ')</div>';
      filteredAbc.forEach(function (c, i) {
        var fullName = c.pkg ? c.pkg + '.' + c.name : c.name;
        var extendsText = c.superName ? ' extends ' + c.superName : '';
        // FIX: Use abcClasses.indexOf(c) instead of i to get correct index in full array
        var actualIndex = abcClasses.indexOf(c);
        html += '<div class="as-script-item" data-type="abc" data-index="' + actualIndex + '">' +
          '<div class="as-script-icon bytecode"></div>' +
          '<span class="as-script-name" title="' + esc(fullName + extendsText) + '">' + esc(fullName) +
          '</span>' +
          '<span class="as-script-tag">bytecode</span></div>';
        hasResults = true;
      });
    }

    // ─── SymbolClass mappings ───
    var symEntries = rawGlobalTags.filter(function (t) {
      return t.tagType === SYMCLASS_TAG;
    });
    if (symEntries.length > 0 && (!q || 'symbolclass'.indexOf(q) >= 0 || 'symbol'.indexOf(q) >= 0)) {
      html += '<div class="as-section-header">SymbolClass Mappings</div>';
      symEntries.forEach(function (t) {
        var symbols = parseSymbolClass(t.body);
        symbols.forEach(function (sym) {
          if (q && (sym.name + ' ' + sym.charId).toLowerCase().indexOf(q) < 0) return;
          html += '<div class="as-script-item" data-type="sym" data-sym-name="' + esc(sym.name) +
            '" data-sym-charid="' + sym.charId + '">' +
            '<div class="as-script-icon bytecode"></div>' +
            '<span class="as-script-name" title="charId=' + sym.charId + '">' +
            esc(sym.name || '(document class)') +
            ' <span style="color:#666">\u2192 #' + sym.charId + '</span></span>' +
            '<span class="as-script-tag">symbol</span></div>';
          hasResults = true;
        });
      });
    }

    if (!hasResults) {
      html += q ?
        '<div class="as-no-results">No scripts matching "' + esc(q) + '"</div>' :
        '<div class="as-no-results">No scripts yet.<br>Click <b>+ New Script</b> to create one,<br>or load an N2D project with scripts.</div>';
    }

    elScriptList.innerHTML = html;

    // Wire events
    var items = elScriptList.querySelectorAll('.as-script-item');
    for (var i = 0; i < items.length; i++) {
      items[i].addEventListener('click', onItemClick);
      items[i].addEventListener('dblclick', onItemDblClick);
    }
    var dels = elScriptList.querySelectorAll('.as-script-delete');
    for (var j = 0; j < dels.length; j++) {
      dels[j].addEventListener('click', onDeleteScript);
    }
  }

  /** Parse a SymbolClass tag body into [{charId, name}]. */
  function parseSymbolClass(body) {
    var results = [];
    if (!body || body.length < 4) return results;
    try {
      var count = readU16(body, 0);
      var off = 2;
      for (var i = 0; i < count && off < body.length; i++) {
        var charId = readU16(body, off);
        off += 2;
        var nameChars = [];
        while (off < body.length) {
          var c = body.charCodeAt(off++) & 0xff;
          if (c === 0) break;
          nameChars.push(String.fromCharCode(c));
        }
        results.push({
          charId: charId,
          name: nameChars.join('')
        });
      }
    } catch (e) {
      /* best effort */ }
    return results;
  }

  /* ================================================================== */
  /*  Event handlers                                                     */
  /* ================================================================== */
  function onItemClick(e) {
    if (e.target.classList.contains('as-script-delete')) return;
    var el = e.currentTarget;
    var type = el.getAttribute('data-type');
    var idx = parseInt(el.getAttribute('data-index'), 10);

    if (type === 'source' && !isNaN(idx) && idx < scripts.length) {
      openScriptInEditor(idx);
    } else if (type === 'abc' && !isNaN(idx) && idx < abcClasses.length) {
      showAbcClassInfo(idx);
    } else if (type === 'sym') {
      showSymbolClassInfo(el);
    }
  }

  function onItemDblClick(e) {
    if (e.target.classList.contains('as-script-delete')) return;
    var el = e.currentTarget;
    var type = el.getAttribute('data-type');
    var idx = parseInt(el.getAttribute('data-index'), 10);

    if (type === 'source' && !isNaN(idx) && idx < scripts.length) {
      // Double-click should still stay in-panel.
      _log.debug('Double-click opening script in panel:', scripts[idx].name, 'index:', idx);
      openScriptInEditor(idx);
    }
  }

  function onDeleteScript(e) {
    e.stopPropagation();
    var idx = parseInt(e.currentTarget.getAttribute('data-index'), 10);
    if (isNaN(idx) || idx >= scripts.length) return;
    if (confirm('Delete "' + scripts[idx].name + '"?')) {
      scripts.splice(idx, 1);
      if (activeScript === idx) closeEditor();
      else if (activeScript > idx) activeScript--;
      saveScriptsToStorage();
      renderScriptList();
    }
  }

  function showSymbolClassInfo(el) {
    var symName = el.getAttribute('data-sym-name') || '';
    var charId = el.getAttribute('data-sym-charid') || '';

    // Try to find a matching source script by class name
    var matchIdx = -1;
    for (var i = 0; i < scripts.length; i++) {
      var s = scripts[i];
      var sName = (s.name || '').replace(/\.as$/i, '');
      var sPath = (s.path || '').replace(/\.as$/i, '').replace(/\//g, '.');
      if (sName === symName || sPath === symName) {
        matchIdx = i;
        break;
      }
    }
    if (matchIdx >= 0) {
      openScriptInEditor(matchIdx);
      return;
    }

    // No source — show mapping info in the editor area
    var info = '// SymbolClass Mapping\n' +
      '// Name:    ' + (symName || '(document class)') + '\n' +
      '// CharId:  #' + charId + '\n' +
      '//\n' +
      '// This symbol maps the library character #' + charId + '\n' +
      '// to the AS3 class "' + symName + '".\n' +
      '//\n' +
      '// No decompiled source was found for this class.\n' +
      '// If you need the source, re-import the SWF with the server running.';

    activeScript = null;
    elEditorContainer.classList.remove('none');
    if (elEditorFilename) elEditorFilename.textContent = symName || '(document class)';
    createEditor();
    setEditorValue(info);
    if (aceEditor) aceEditor.setReadOnly(true);
    renderScriptList();
    resizeEditorArea();
    setTimeout(resizeEditorArea, 50);
  }

  function showAbcClassInfo(idx) {
    var c = abcClasses[idx];
    var full = c.pkg ? c.pkg + '.' + c.name : c.name;

    // Try to find a matching decompiled source script and open it
    var matchIdx = -1;
    for (var i = 0; i < scripts.length; i++) {
      var s = scripts[i];
      // Match by class name (filename without .as) or full path
      var sName = (s.name || '').replace(/\.as$/i, '');
      var sPath = (s.path || '').replace(/\.as$/i, '').replace(/\//g, '.');
      if (sName === c.name || sPath === full) {
        matchIdx = i;
        break;
      }
    }
    if (matchIdx >= 0) {
      openScriptInEditor(matchIdx);
      return;
    }

    // No decompiled source found — show info
    alert(
      'AS3 Class: ' + full + '\n' +
      'Extends: ' + (c.superName || '(none)') + '\n\n' +
      'No decompiled source found for this class.\n' +
      'Try re-importing the SWF with the server running.'
    );
  }

  /* ================================================================== */
  /*  Editor — Ace with textarea fallback                                */
  /* ================================================================== */
  function createEditor() {
    if (aceEditor) return true;
    if (fallbackTA) return true;

    // Try Ace first
    if (typeof ace !== 'undefined') {
      try {
        _log.debug('Creating Ace editor');
        aceEditor = ace.edit('as-editor');
        aceEditor.setTheme('ace/theme/monokai');
        aceEditor.session.setMode('ace/mode/actionscript');
        aceEditor.session.setUseWorker(false);
        aceEditor.setOptions({
          enableBasicAutocompletion: true,
          enableSnippets: false,
          enableLiveAutocompletion: true,
          fontSize: '12px',
          showPrintMargin: false,
          wrap: true,
          showFoldWidgets: false
        });
        aceEditor.commands.addCommand({
          name: 'saveScript',
          bindKey: {
            win: 'Ctrl-S',
            mac: 'Command-S'
          },
          exec: saveCurrentScript
        });
        aceEditor.commands.addCommand({
          name: 'findInScript',
          bindKey: {
            win: 'Ctrl-F',
            mac: 'Command-F'
          },
          exec: function (ed) {
            if (ace.config && ace.config.loadModule) {
              ace.config.loadModule('ace/ext/searchbox', function (sb) {
                if (sb && sb.Search) sb.Search(ed);
              });
            }
          }
        });
        _log.info('Ace editor created successfully');
        return true;
      } catch (e) {
        _log.error('Ace init failed:', e);
        aceEditor = null;
      }
    }

    // Fallback: textarea
    _log.info('Using textarea fallback (Ace not available)');
    fallbackTA = document.createElement('textarea');
    fallbackTA.id = 'as-editor-fallback';
    fallbackTA.spellcheck = false;
    fallbackTA.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveCurrentScript();
      }
      // Tab indentation support
      if (e.key === 'Tab') {
        e.preventDefault();
        var start = fallbackTA.selectionStart;
        var end = fallbackTA.selectionEnd;
        fallbackTA.value = fallbackTA.value.substring(0, start) + '    ' + fallbackTA.value.substring(end);
        fallbackTA.selectionStart = fallbackTA.selectionEnd = start + 4;
      }
    });
    elEditorDiv.appendChild(fallbackTA);
    return true;
  }

  function saveCurrentScript() {
    if (activeScript === null || activeScript >= scripts.length) return;
    _log.info('Saving script:', scripts[activeScript].name);
    scripts[activeScript].source = getEditorValue();
    scriptsModified = true;
    saveScriptsToStorage();
    toast('Saved: ' + scripts[activeScript].name);
  }

  function getEditorValue() {
    if (aceEditor) return aceEditor.getValue();
    if (fallbackTA) return fallbackTA.value;
    return '';
  }

  function setEditorValue(text) {
    if (aceEditor) {
      aceEditor.setValue(text, -1);
      return;
    }
    if (fallbackTA) {
      fallbackTA.value = text;
      return;
    }
  }

  /** Resize the Ace editor to fit its container.
   *  CSS handles the layout (#controller-area-js has height:100%
   *  and display:flex), so we just need to tell Ace to recalculate. */
  function resizeEditorArea() {
    if (aceEditor) aceEditor.resize();
  }

  /** Force a hard repaint of the Ace editor to fix GPU compositing artifacts.
   *  Temporarily toggles visibility on the gutter/scroller to force Chrome
   *  to re-rasterize GPU tiles for the 1M-px virtual layers. */
  function forceAceRepaint() {
    if (!aceEditor) return;
    var el = document.getElementById('as-editor');
    if (!el) return;
    var gutter = el.querySelector('.ace_gutter');
    var scroller = el.querySelector('.ace_scroller');
    if (gutter) {
      gutter.style.visibility = 'hidden';
    }
    if (scroller) {
      scroller.style.visibility = 'hidden';
    }
    // Force reflow then restore
    void el.offsetHeight;
    requestAnimationFrame(function () {
      if (gutter) {
        gutter.style.visibility = '';
      }
      if (scroller) {
        scroller.style.visibility = '';
      }
      aceEditor.renderer.updateFull(true);
    });
  }

  function focusEditor() {
    if (aceEditor) {
      resizeEditorArea();
      setTimeout(function () {
        resizeEditorArea();
        forceAceRepaint();
        aceEditor.focus();
      }, 50);
      // Second repaint pass in case layout settled late
      setTimeout(function () {
        forceAceRepaint();
      }, 300);
    } else if (fallbackTA) {
      setTimeout(function () {
        fallbackTA.focus();
      }, 100);
    }
  }

  function openScriptInEditor(index) {
    _log.trace('Opening script in editor:', scripts[index] ? scripts[index].name : index);
    if (index < 0 || index >= scripts.length) return;

    // Unified path: use the same core editor modal as frame scripts.
    if (window.__N2F_EditorBridge && typeof window.__N2F_EditorBridge.openSourceScript === 'function') {
      activeScript = index;
      var unifiedScript = scripts[index];
      var opened = window.__N2F_EditorBridge.openSourceScript(unifiedScript, function (newSource) {
        if (index >= 0 && index < scripts.length) {
          scripts[index].source = newSource;
          scriptsModified = true;
          saveScriptsToStorage();
          renderScriptList();
        }
      });
      if (opened) {
        if (elEditorContainer) {
          elEditorContainer.classList.add('none');
          elEditorContainer.classList.remove('as-floating-window');
        }
        renderScriptList();
        return;
      }
    }

    // Save current before switching
    if (activeScript !== null && activeScript < scripts.length) {
      scripts[activeScript].source = getEditorValue();
      saveScriptsToStorage();
    }

    activeScript = index;
    var script = scripts[index];

    // Keep source scripts in an in-page floating editor window.
    elEditorContainer.classList.add('as-floating-window');

    // Show container FIRST so editor has dimensions
    elEditorContainer.classList.remove('none');

    if (elEditorFilename) elEditorFilename.textContent = script.path || script.name;

    // Create editor (Ace or fallback)
    createEditor();

    // Set content
    setEditorValue(script.source || '');
    if (aceEditor) aceEditor.setReadOnly(false);

    focusEditor();
    renderScriptList();
  }

  /** External-tab mode is disabled; keep everything in the panel editor. */
  function openScriptInNewTab(index) {
    _log.info('External editor tab disabled; opening in panel instead');
    openScriptInEditor(index);
  }

  function closeEditor() {
    _log.trace('Closing editor');
    if (window.__N2F_EditorBridge && typeof window.__N2F_EditorBridge.closeEditor === 'function') {
      window.__N2F_EditorBridge.closeEditor();
    }
    if (activeScript !== null && activeScript < scripts.length) {
      scripts[activeScript].source = getEditorValue();
      saveScriptsToStorage();
    }
    activeScript = null;
    elEditorContainer.classList.remove('as-floating-window');
    elEditorContainer.classList.add('none');
    renderScriptList();
  }

  /* ================================================================== */
  /*  Expand to floating window                                          */
  /* ================================================================== */
  function onExpandToTab() {
    if (activeScript === null || activeScript >= scripts.length) {
      toast('No script open to expand', true);
      return;
    }
    openScriptInEditor(activeScript);
    toast('Editor is pinned to ActionScript panel');
  }

  function getAceBasePath() {
    var tags = document.querySelectorAll('script[src*="ace"]');
    for (var i = 0; i < tags.length; i++) {
      var src = tags[i].getAttribute('src');
      if (src && src.indexOf('ace.js') >= 0) return src.replace(/ace\.js.*$/, '');
    }
    return './assets/js/';
  }

  function buildFloatingHTML(script, aceBase) {
    return '<!DOCTYPE html><html><head><title>' + esc(script.name) + ' \u2014 N2D Editor</title>' +
      '<style>html,body{margin:0;padding:0;height:100%;overflow:hidden;background:#1e1e1e;color:#ccc;font-family:Arial,sans-serif}' +
      '#bar{display:flex;align-items:center;padding:6px 12px;background:#2a2a2a;border-bottom:1px solid #444}' +
      '#fname{flex:1;font:bold 13px/1.4 Arial,sans-serif;color:#90caf9}' +
      '#save-btn{padding:4px 14px;background:#3a6;color:#fff;border:none;border-radius:3px;cursor:pointer;font:bold 12px Arial;margin-right:8px}' +
      '#save-btn:hover{background:#4b7}#status{font:11px Arial;color:#888}' +
      '#editor{position:absolute;top:38px;left:0;right:0;bottom:0}' +
      '#editor-ta{width:100%;height:100%;background:#272822;color:#f8f8f2;border:none;padding:8px;font:13px/1.5 "Courier New",monospace;resize:none;outline:none;box-sizing:border-box}' +
      '</style></head><body>' +
      '<div id="bar"><span id="fname">' + esc(script.path || script.name) + '</span>' +
      '<button id="save-btn">Save (Ctrl+S)</button><span id="status">Ready</span></div>' +
      '<div id="editor"></div>' +
      '<script src="' + aceBase + 'ace.js"></' + 'script>' +
      '<script src="' + aceBase + 'ext-language_tools.js"></' + 'script>' +
      '<script src="' + aceBase + 'ext-searchbox.js"></' + 'script>' +
      '<script src="' + aceBase + 'mode-actionscript.js"></' + 'script>' +
      '<script>' +
      '(function(){' +
      'var path=' + JSON.stringify(script.path) + ';' +
      'var src=' + JSON.stringify(script.source || '') + ';' +
      'var statusEl=document.getElementById("status");' +
      'var editor,ta,isDirty=false;' +
      'try{editor=ace.edit("editor");editor.setTheme("ace/theme/monokai");' +
      'editor.session.setMode("ace/mode/actionscript");' +
      'editor.session.setUseWorker(false);' +
      'editor.setOptions({enableBasicAutocompletion:true,enableSnippets:false,enableLiveAutocompletion:true,fontSize:"13px",showPrintMargin:false,wrap:true,showFoldWidgets:false});' +
      'editor.setValue(src,-1);editor.focus();' +
      'editor.on("change",function(){isDirty=true;statusEl.textContent="Modified";statusEl.style.color="#f0ad4e";});' +
      'editor.commands.addCommand({name:"save",bindKey:{win:"Ctrl-S",mac:"Command-S"},exec:save});' +
      'editor.commands.addCommand({name:"find",bindKey:{win:"Ctrl-F",mac:"Command-F"},exec:function(e){ace.config.loadModule("ace/ext/searchbox",function(s){s.Search(e);});}});' +
      '}catch(e){' +
      'ta=document.createElement("textarea");ta.id="editor-ta";ta.value=src;ta.spellcheck=false;' +
      'document.getElementById("editor").appendChild(ta);ta.focus();' +
      'ta.addEventListener("input",function(){isDirty=true;statusEl.textContent="Modified";statusEl.style.color="#f0ad4e";});' +
      'ta.addEventListener("keydown",function(e){if((e.ctrlKey||e.metaKey)&&e.key==="s"){e.preventDefault();save();}});' +
      '}' +
      'function save(){' +
      'var val=editor?editor.getValue():ta.value;' +
      'if(window.opener&&!window.opener.closed){window.opener.postMessage({type:"n2d-as-script-save",path:path,source:val},"*");}' +
      'isDirty=false;statusEl.textContent="Saved";statusEl.style.color="#2ecc71";' +
      'setTimeout(function(){statusEl.textContent="Ready";statusEl.style.color="#888";},2000);' +
      '}' +
      'document.getElementById("save-btn").addEventListener("click",save);' +
      'window.addEventListener("beforeunload",function(){if(isDirty)save();});' +
      'window.addEventListener("message",function(e){' +
      'if(e.data&&e.data.type==="n2d-as-script-update"&&e.data.path===path){' +
      'if(editor)editor.setValue(e.data.source,-1);else if(ta)ta.value=e.data.source;isDirty=false;}});' +
      '})();</' + 'script></body></html>';
  }

  function _saveScriptToDisk(path, source) {
    fetch('/api/save-script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: path, source: source })
    }).then(function (r) {
      if (!r.ok) r.json().then(function (j) {
        _log.warn('save-script failed:', j.error || r.status);
      });
    }).catch(function (e) {
      _log.warn('save-script network error:', e);
    });
  }

  function onFloatingWindowMessage(e) {
    if (!e.data || e.data.type !== 'n2d-as-script-save') return;
    for (var i = 0; i < scripts.length; i++) {
      if (scripts[i].path === e.data.path) {
        scripts[i].source = e.data.source;
        saveScriptsToStorage();
        if (activeScript === i) setEditorValue(e.data.source);
        _saveScriptToDisk(e.data.path, e.data.source);
        toast('Saved: ' + scripts[i].name);
        break;
      }
    }
  }

  /* ================================================================== */
  /*  New Script Dialog                                                  */
  /* ================================================================== */
  function showNewScriptDialog() {
    _log.debug('Showing new script dialog');
    var ov = document.createElement('div');
    ov.id = 'as-new-script-overlay';
    ov.innerHTML =
      '<div id="as-new-script-dialog">' +
      '<h3>New ActionScript File</h3>' +
      '<label for="as-new-name">File Name:</label>' +
      '<input type="text" id="as-new-name" placeholder="MyClass.as" autofocus>' +
      '<label for="as-new-package">Package (optional):</label>' +
      '<input type="text" id="as-new-package" placeholder="com.example">' +
      '<label for="as-new-template">Template:</label>' +
      '<select id="as-new-template">' +
      '<option value="class">Class</option>' +
      '<option value="movieclip">MovieClip Subclass</option>' +
      '<option value="sprite">Sprite Subclass</option>' +
      '<option value="bitmapdata">BitmapData Subclass</option>' +
      '<option value="sound">Sound Subclass</option>' +
      '<option value="empty">Empty File</option>' +
      '</select>' +
      '<div class="dialog-buttons">' +
      '<button class="btn-cancel" id="as-new-cancel">Cancel</button>' +
      '<button class="btn-create" id="as-new-create">Create</button>' +
      '</div></div>';

    document.body.appendChild(ov);
    var nameIn = document.getElementById('as-new-name');
    var pkgIn = document.getElementById('as-new-package');
    var tplSel = document.getElementById('as-new-template');
    setTimeout(function () {
      nameIn.focus();
    }, 100);

    document.getElementById('as-new-cancel').addEventListener('click', function () {
      ov.remove();
    });
    ov.addEventListener('click', function (e) {
      if (e.target === ov) ov.remove();
    });
    nameIn.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') document.getElementById('as-new-create').click();
      if (e.key === 'Escape') ov.remove();
    });

    document.getElementById('as-new-create').addEventListener('click', function () {
      var name = nameIn.value.trim();
      if (!name) {
        nameIn.style.borderColor = '#f55';
        nameIn.focus();
        return;
      }
      if (!name.toLowerCase().endsWith('.as')) name += '.as';

      var pkg = pkgIn.value.trim();
      var cls = name.replace(/\.as$/i, '');
      var path = pkg ? pkg.replace(/\./g, '/') + '/' + name : name;

      if (scripts.some(function (s) {
          return s.path === path;
        })) {
        alert('"' + path + '" already exists.');
        return;
      }

      var source = genTemplate(tplSel.value, cls, pkg);
      scripts.push({
        name: name,
        path: path,
        source: source
      });
      saveScriptsToStorage();
      renderScriptList();
      ov.remove();
      openScriptInEditor(scripts.length - 1);
      toast('Created: ' + path);
    });
  }

  function genTemplate(tpl, cls, pkg) {
    var p = pkg ? 'package ' + pkg : 'package';
    switch (tpl) {
      case 'movieclip':
        return p + ' {\n    import flash.display.MovieClip;\n\n    public class ' + cls +
          ' extends MovieClip {\n        public function ' + cls + '() { super(); }\n    }\n}\n';
      case 'sprite':
        return p + ' {\n    import flash.display.Sprite;\n\n    public class ' + cls +
          ' extends Sprite {\n        public function ' + cls + '() { super(); }\n    }\n}\n';
      case 'bitmapdata':
        return p + ' {\n    import flash.display.BitmapData;\n\n    public class ' + cls +
          ' extends BitmapData {\n        public function ' + cls + '(w:int=1,h:int=1) { super(w,h); }\n    }\n}\n';
      case 'sound':
        return p + ' {\n    import flash.media.Sound;\n\n    public class ' + cls +
          ' extends Sound {\n        public function ' + cls + '() { super(); }\n    }\n}\n';
      case 'empty':
        return '';
      default:
        return p + ' {\n    public class ' + cls + ' {\n        public function ' + cls + '() {}\n    }\n}\n';
    }
  }

  /* ================================================================== */
  /*  Helpers                                                            */
  /* ================================================================== */
  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function toast(msg, isErr) {
    var old = document.getElementById('as-panel-toast');
    if (old) old.remove();
    var el = document.createElement('div');
    el.id = 'as-panel-toast';
    el.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:100001;max-width:360px;' +
      'padding:10px 18px;border-radius:5px;font:12px/1.5 Arial,sans-serif;color:#fff;' +
      'box-shadow:0 4px 12px rgba(0,0,0,.3);transition:opacity .3s;' +
      'background:' + (isErr ? '#e74c3c' : '#2ecc71');
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(function () {
      el.style.opacity = '0';
      setTimeout(function () {
        el.remove();
      }, 300);
    }, isErr ? 5000 : 3000);
  }

  /* ================================================================== */
  /*  Public API                                                         */
  /* ================================================================== */
  window.__n2d_as_panel = {
    getScripts: function () {
      return scripts.slice();
    },
    setScripts: function (s) {
      scripts = s || [];
      saveScriptsToStorage();
      renderScriptList();
    },
    addScript: function (n, p, s) {
      scripts.push({
        name: n,
        path: p,
        source: s || ''
      });
      saveScriptsToStorage();
      renderScriptList();
    },
    setRawGlobalTags: function (t) {
      rawGlobalTags = t || [];
      extractAbcClasses();
      renderScriptList();
    },
    getRoundtripData: function () {
      return roundtripData;
    },
    setRoundtripData: function (d) {
      roundtripData = d || {};
      saveRoundtripToStorage();
    },
    hasRoundtripData: hasRoundtripData,
    getOriginalN2DJson: function () {
      return originalN2DJson;
    },
    /**
     * Inject all roundtrip fields into a parsed N2D JSON object.
     * Captures current editor content first so unsaved edits are included.
     * Auto-detects unsaved script changes and sets scriptsModified flag.
     * Used by next2flash-integration.js during Export-to-SWF.
     */
    injectRoundtripFields: function (json) {
      // Capture current editor content before injection
      if (activeScript !== null && activeScript < scripts.length) {
        var currentValue = getEditorValue();
        // Detect unsaved changes → mark scripts as modified
        if (currentValue !== scripts[activeScript].source) {
          scriptsModified = true;
          _log.info('Detected unsaved editor changes in',
            scripts[activeScript].name, '— marking scriptsModified');
        }
        scripts[activeScript].source = currentValue;
      }
      injectRoundtripFields(json);
    }
  };

  /* ================================================================== */
  /*  Boot                                                               */
  /* ================================================================== */
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
