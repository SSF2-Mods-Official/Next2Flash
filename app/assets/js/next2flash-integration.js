/**
 * Next2Flash Integration — Server-backed SWF conversion for the Next2D tool.
 *
 * When running under the Next2Flash server (http://localhost:5000), this
 * module adds:
 *   - "Convert SWF → N2D" via the server's /api/swf-to-n2d endpoint
 *   - "Export as SWF" via the server's /api/n2d-to-swf endpoint
 *   - Status indicators showing server connectivity
 *
 * The UI is injected as buttons in the toolbar area.
 */

(function () {
  'use strict';

  // _log: routes to browser devtools via __N2F_DEBUG, and also forwards
  // INFO/WARN/ERROR to the server console via _serverLog (hoisted below).
  var _log = (function () {
    var base = window.__N2F_DEBUG ? window.__N2F_DEBUG.logger('Integration')
      : {trace:function(){},debug:function(){},info:function(){},warn:function(){},error:function(){},time:function(){},timeEnd:function(){},group:function(){},groupEnd:function(){}};
    function _fwd(lvl, args) {
      try {
        _serverLog(lvl, Array.prototype.map.call(args, function (a) {
          return (a == null) ? String(a) : (typeof a === 'object') ? JSON.stringify(a) : String(a);
        }).join(' '));
      } catch (e) { /* ignore */ }
    }
    return {
      trace:    function () { base.trace    && base.trace.apply(base, arguments); },
      debug:    function () { base.debug    && base.debug.apply(base, arguments); },
      info:     function () { base.info     && base.info.apply(base, arguments);  _fwd('INFO',  arguments); },
      warn:     function () { base.warn     && base.warn.apply(base, arguments);  _fwd('WARN',  arguments); },
      error:    function () { base.error    && base.error.apply(base, arguments); _fwd('ERROR', arguments); },
      time:     function () { base.time     && base.time.apply(base, arguments); },
      timeEnd:  function () { base.timeEnd  && base.timeEnd.apply(base, arguments); },
      group:    function () { base.group    && base.group.apply(base, arguments); },
      groupEnd: function () { base.groupEnd && base.groupEnd.apply(base, arguments); },
    };
  })();

  var API_BASE = '';  // same origin when served by Next2Flash server
  var serverOnline = false;
  var _importedN2DBlob = null;  // stored for fallback during export
  var _currentProjectName = '';  // user-chosen project name from import popup
  var _isDirty = false;          // unsaved changes since last save
  var _autosaveTimer = null;     // setInterval handle for background autosave
  var _autosaveWorker = null;    // persistent worker for off-thread serialization
  var _dirtyPollTimer = null;    // setInterval for watching workspace revision
  var _lastRevision = 0;         // workspace revision snapshot
  var _recentProjects = [];      // cached recent project list from server
  var _recentImports = [];       // cached recent imports list from server

  /* ------------------------------------------------------------------ */
  /*  Document title & dirty state helpers                               */
  /* ------------------------------------------------------------------ */
  function _setDocumentTitle(name, dirty) {
    if (name === '') { document.title = 'Next2Flash'; return; }
    var n = (name !== undefined && name !== null) ? name : (_currentProjectName || 'Untitled');
    document.title = (dirty ? '\u2022 ' : '') + n + ' \u2014 Next2Flash';
  }
  function _markDirty() {
    if (!_isDirty) { _isDirty = true; _setDocumentTitle(undefined, true); }
  }
  function _markClean() {
    _isDirty = false; _setDocumentTitle(undefined, false);
  }
  function _startDirtyPoll() {
    if (_dirtyPollTimer) return;
    _dirtyPollTimer = setInterval(function () {
      if (!_currentProjectDir) return;
      try {
        var ws = window.Util && window.Util.$currentWorkSpace && window.Util.$currentWorkSpace();
        if (!ws) return;
        var rev = (ws._$revision ? ws._$revision.length : 0);
        if (rev !== _lastRevision) { _lastRevision = rev; _markDirty(); }
      } catch (e) { /* ignore */ }
    }, 2000);
  }

  function _stopDirtyPoll() {
    if (_dirtyPollTimer) { clearInterval(_dirtyPollTimer); _dirtyPollTimer = null; }
  }

  /* ================================================================== */
  /*  Init                                                               */
  /* ================================================================== */
  function init() {
    // Try immediately, then retry a few times (sidecar may need time to start)
    var isTauri = !!(window.__TAURI__ || window.__NEXT2FLASH_DESKTOP__);
    var attempts = 0;
    var maxAttempts = isTauri ? 10 : 2;
    var delay = 600;

    function updateApiBase() {
      // Re-check on every attempt — Rust eval() may arrive late
      if (window.__NEXT2FLASH_SERVER_URL__ && API_BASE !== window.__NEXT2FLASH_SERVER_URL__) {
        API_BASE = window.__NEXT2FLASH_SERVER_URL__;
        _log.info('Server URL detected:', API_BASE);
      }
    }

    function tryConnect() {
      updateApiBase();
      // In Tauri, skip if we don't have a server URL yet (wait for eval)
      if (isTauri && !API_BASE && attempts < maxAttempts - 1) {
        attempts++;
        _log.debug('Waiting for server URL... (' + attempts + '/' + maxAttempts + ')');
        setTimeout(tryConnect, delay);
        return;
      }
      checkServer().then(function (online) {
        serverOnline = online;
        if (online) {
          injectUI();
          _log.info('Server connected — SWF conversion available');
        } else if (++attempts < maxAttempts) {
          _log.debug('Server not ready, retrying in', delay, 'ms... (' + attempts + '/' + maxAttempts + ')');
          setTimeout(tryConnect, delay);
          delay = Math.min(delay * 1.5, 3000);
        } else {
          _log.warn('No server detected — running in static mode');
        }
      });
    }
    tryConnect();
  }

  function checkServer() {
    _log.trace('Checking server health:', API_BASE + '/api/health');
    return fetch(API_BASE + '/api/health', { method: 'GET' })
      .then(function (r) { return r.ok; })
      .catch(function () { return false; });
  }

  /* ================================================================== */
  /*  Inject UI                                                          */
  /* ================================================================== */
  function injectUI() {
    _log.debug('Injecting toolbar UI');
    // Add styles
    var style = document.createElement('style');
    style.textContent = [
      '#n2f-toolbar { display:flex; flex-direction:column; align-items:stretch; gap:4px; padding:8px;',
      '  position:fixed; bottom:10px; right:10px; z-index:100000;',
      '  background:rgba(30,30,30,.92); border:1px solid #444;',
      '  border-radius:6px;',
      '  box-shadow:0 2px 12px rgba(0,0,0,.4); }',
      '#n2f-toolbar .n2f-header { display:flex; align-items:center; gap:4px; padding-bottom:2px; }',
      '#n2f-toolbar .n2f-btn { display:inline-flex; align-items:center; gap:4px;',
      '  padding:4px 10px; border:1px solid #555; border-radius:4px; cursor:pointer;',
      '  font:bold 11px/1.4 Arial,sans-serif; color:#ccc; background:#333;',
      '  transition:background .15s, border-color .15s; white-space:nowrap; }',
      '#n2f-toolbar .n2f-btn:hover { background:#444; border-color:#7af; }',
      '#n2f-toolbar .n2f-btn:disabled { opacity:.45; cursor:default; pointer-events:none; }',
      '#n2f-toolbar .n2f-btn.primary { background:#2a6; border-color:#2a6; color:#fff; }',
      '#n2f-toolbar .n2f-btn.primary:hover { background:#3b7; border-color:#3b7; }',
      '#n2f-toolbar .n2f-dot { width:8px; height:8px; border-radius:50%; background:#2ecc71;',
      '  display:inline-block; margin-right:2px; }',
      '#n2f-toolbar .n2f-label { font:11px/1.4 Arial,sans-serif; color:#888; }',
      '#n2f-progress { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);',
      '  z-index:320000; background:#222; color:#ccc; border:1px solid #555; border-radius:8px;',
      '  padding:24px 32px; font:13px/1.6 Arial,sans-serif; text-align:center;',
      '  box-shadow:0 8px 32px rgba(0,0,0,.5); min-width:320px; }',
      '#n2f-progress-bar-track { width:100%; height:8px; background:#333; border-radius:4px;',
      '  overflow:hidden; margin:12px 0 8px; }',
      '#n2f-progress-bar { height:100%; width:0%; background:linear-gradient(90deg,#4fc3f7,#7af);',
      '  border-radius:4px; transition:width .3s ease; }',
      '#n2f-progress-bar.indeterminate { width:30%;',
      '  animation:n2f-indeterminate 1.5s ease-in-out infinite; }',
      '@keyframes n2f-indeterminate { 0%{margin-left:0;width:30%} 50%{margin-left:35%;width:30%} 100%{margin-left:70%;width:30%} }',
      '#n2f-progress-pct { font-size:11px; color:#888; margin-top:2px; }',
      '#n2f-overlay { display:none; position:fixed; top:0; left:0; right:0; bottom:0;',
      '  z-index:310000; background:rgba(0,0,0,.4); }',
      '#n2f-name-modal { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);',
      '  z-index:330000; background:#222; color:#ccc; border:1px solid #555; border-radius:8px;',
      '  padding:24px 32px; font:13px/1.6 Arial,sans-serif; text-align:center;',
      '  box-shadow:0 8px 32px rgba(0,0,0,.5); min-width:320px; }',
      '#n2f-name-modal h3 { margin:0 0 12px; font-size:15px; color:#eee; }',
      '#n2f-name-modal input { width:100%; box-sizing:border-box; padding:8px 10px; margin-bottom:16px;',
      '  background:#333; border:1px solid #555; border-radius:4px; color:#eee;',
      '  font:13px Arial,sans-serif; outline:none; }',
      '#n2f-name-modal input:focus { border-color:#7af; }',
      '#n2f-name-modal .n2f-modal-buttons { display:flex; gap:8px; justify-content:center; }',
      '#n2f-name-modal .n2f-btn { min-width:80px; justify-content:center; }',
      '#n2f-name-modal .n2f-label-row { text-align:left; font-size:11px; color:#aaa; margin-bottom:3px; }',
      '#n2f-name-modal .n2f-dir-row { display:flex; gap:6px; margin-bottom:16px; align-items:center; }',
      '#n2f-name-modal .n2f-dir-row input { flex:1; box-sizing:border-box; padding:8px 10px;',
      '  background:#333; border:1px solid #555; border-radius:4px; color:#eee;',
      '  font:13px Arial,sans-serif; outline:none; }',
      '#n2f-name-modal .n2f-dir-row input:focus { border-color:#7af; }',
      '#n2f-name-error { color:#f66; font-size:11px; margin:-10px 0 8px; display:none; text-align:left; }',
      '#n2f-name-overwrite { display:none; margin-top:8px; border-color:#e80; color:#e80; }',
      '#n2f-name-overwrite.confirm { border-color:#e33; color:#e33; font-weight:bold; }',
      '#n2f-name-overwrite:hover { background:#3a1a00; }',
      '#n2f-name-overwrite.confirm:hover { background:#3a0000; }',
      /* Welcome screen */
      '#n2f-welcome { display:none; position:fixed; top:0; left:0; right:0; bottom:0;',
      '  z-index:300000; background:#111; align-items:center; justify-content:center; }',
      '#n2f-welcome-box { width:860px; max-width:95vw; max-height:93vh; overflow-y:auto;',
      '  padding:44px; position:relative; }',
      '#n2f-welcome-close { position:absolute; top:8px; right:12px; background:none; border:none;',
      '  color:#444; font-size:22px; cursor:pointer; padding:4px 8px; border-radius:4px; line-height:1; }',
      '#n2f-welcome-close:hover { background:#222; color:#aaa; }',
      '#n2f-welcome-brand { text-align:center; margin-bottom:36px; }',
      '#n2f-welcome-brand h1 { font:bold 34px/1 Arial,sans-serif; color:#7af; margin:0; }',
      '#n2f-welcome-brand p { font:13px Arial,sans-serif; color:#555; margin:8px 0 0; }',
      '#n2f-welcome-actions { display:flex; gap:16px; justify-content:center; margin-bottom:40px; }',
      '.n2f-wcard { background:#1e1e1e; border:1px solid #333; border-radius:10px;',
      '  padding:22px 16px; text-align:center; cursor:pointer; width:148px;',
      '  transition:background .18s,border-color .18s,transform .14s; }',
      '.n2f-wcard:hover { background:#252525; border-color:#7af; transform:translateY(-3px); }',
      '.n2f-wcard-icon { font-size:32px; margin-bottom:10px; }',
      '.n2f-wcard-title { font:bold 13px Arial,sans-serif; color:#ddd; margin-bottom:5px; }',
      '.n2f-wcard-desc { font:11px Arial,sans-serif; color:#666; }',
      '#n2f-welcome-recents { display:flex; gap:28px; }',
      '.n2f-recents-col { flex:1; min-width:0; max-height:280px; overflow-y:auto; }',
      '.n2f-recents-hdr { font:bold 10px Arial,sans-serif; color:#555; text-transform:uppercase;',
      '  letter-spacing:.8px; margin-bottom:10px; padding-bottom:6px;',
      '  border-bottom:1px solid #222; }',
      '.n2f-recent-item { display:flex; align-items:center; padding:7px 8px; border-radius:4px;',
      '  cursor:pointer; transition:background .12s; }',
      '.n2f-recent-item:hover { background:#1e1e1e; }',
      '.n2f-ri-info { min-width:0; flex:1; }',
      '.n2f-ri-name { font:bold 12px Arial,sans-serif; color:#bbb; overflow:hidden;',
      '  text-overflow:ellipsis; white-space:nowrap; }',
      '.n2f-ri-path { font:10px Arial,sans-serif; color:#444; overflow:hidden;',
      '  text-overflow:ellipsis; white-space:nowrap; margin-top:1px; }',
      '.n2f-ri-actions { display:flex; gap:2px; margin-left:6px; flex-shrink:0; opacity:0; transition:opacity .12s; }',
      '.n2f-recent-item:hover .n2f-ri-actions { opacity:1; }',
      '.n2f-ri-btn { background:none; border:none; color:#555; cursor:pointer; font-size:12px;',
      '  padding:2px 5px; border-radius:3px; line-height:1; }',
      '.n2f-ri-btn:hover { background:#2a2a2a; color:#aaa; }',
      '.n2f-recent-empty { font:italic 11px Arial,sans-serif; color:#333; padding:6px 8px; }',
      /* Error dialog */
      '#n2f-export-error-overlay { display:none; position:fixed; top:0; left:0; right:0; bottom:0;',
      '  z-index:340000; background:rgba(0,0,0,.55); }',
      '#n2f-export-error { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);',
      '  z-index:340001; background:#1a1a1a; color:#ccc; border:1px solid #c33; border-radius:8px;',
      '  padding:28px 32px; font:13px/1.6 Arial,sans-serif; box-shadow:0 8px 32px rgba(0,0,0,.7);',
      '  min-width:420px; max-width:700px; max-height:80vh; flex-direction:column; gap:14px; }',
      '#n2f-export-error h3 { margin:0; font-size:16px; color:#f77; display:flex; align-items:center; gap:8px; }',
      '#n2f-export-error .n2f-err-msg { background:#111; border:1px solid #333; border-radius:4px;',
      '  padding:12px; font:11px/1.5 monospace; color:#e99; overflow-y:auto; max-height:280px;',
      '  white-space:pre-wrap; word-break:break-all; user-select:text; }',
      '#n2f-export-error .n2f-err-hint { font:11px Arial,sans-serif; color:#666; line-height:1.5; }',
      '#n2f-export-error .n2f-err-buttons { display:flex; gap:8px; }',
    ].join('\n');
    document.head.appendChild(style);

    // Create toolbar
    var toolbar = document.createElement('div');
    toolbar.id = 'n2f-toolbar';
    toolbar.innerHTML =
      '<div class="n2f-header"><span class="n2f-dot"></span>' +
      '<span class="n2f-label">Next2Flash</span></div>' +
      '<button class="n2f-btn" id="n2f-import-swf" title="Import SWF into editable project folder (PNG/WAV/AS)">' +
        '\u{1F4E5} Import SWF</button>' +
      '<button class="n2f-btn" id="n2f-open-project" title="Open a saved .n2d project folder">' +
        '\u{1F4C2} Open Project</button>' +
      '<button class="n2f-btn" id="n2f-refresh-assets" title="Refresh external assets from project folder" disabled>' +
        '\u{1F504} Refresh Assets</button>' +
      '<button class="n2f-btn" id="n2f-import-asset" title="Import image/audio files into the active project assets/ folder">' +
        '\u{1F5BC} Import Asset</button>' +
      '<button class="n2f-btn" id="n2f-save-project" title="Save project (prompts for name/location if new)">' +
        '\u{1F4BE} Save Project</button>' +
      '<button class="n2f-btn primary" id="n2f-export-swf" title="Export current project as SWF">' +
        '\u{1F4E4} Export SWF</button>' +
      '<button class="n2f-btn" id="n2f-ssf2-roundtrip" title="Import PSB SSF2.swf, compile roundtrip, deploy, launch ADL debugger">' +
        '\u{1F3AE} SSF2 Roundtrip + ADL</button>' +
      '<input type="file" id="n2f-swf-input" accept=".swf,.ssf" style="display:none">' +
      '<input type="file" id="n2f-n2d-input" accept=".n2d" style="display:none">' +
      '<input type="file" id="n2f-asset-input" accept="image/*,audio/*" multiple style="display:none">';

    // Insert as fixed-position toolbar at top of page
    document.body.appendChild(toolbar);

    // Overlay + progress dialog
    var overlay = document.createElement('div');
    overlay.id = 'n2f-overlay';
    document.body.appendChild(overlay);

    var progress = document.createElement('div');
    progress.id = 'n2f-progress';
    progress.innerHTML = '<div id="n2f-status">Processing...</div>' +
      '<div id="n2f-progress-bar-track"><div id="n2f-progress-bar" class="indeterminate"></div></div>' +
      '<div id="n2f-progress-pct"></div>';
    document.body.appendChild(progress);

    // Project name modal
    var nameModal = document.createElement('div');
    nameModal.id = 'n2f-name-modal';
    nameModal.innerHTML =
      '<h3>Enter Project Name</h3>' +
      '<div class="n2f-label-row">Project Name</div>' +
      '<input type="text" id="n2f-name-input" placeholder="Project name" autocomplete="off">' +
      '<div class="n2f-label-row">Save Location</div>' +
      '<div class="n2f-dir-row">' +
        '<input type="text" id="n2f-dir-input" placeholder="Default (server converted/ folder)">' +
        '<button class="n2f-btn" id="n2f-dir-browse" style="display:none">Browse...</button>' +
      '</div>' +
      '<div id="n2f-name-error"></div>' +
      '<div class="n2f-modal-buttons">' +
        '<button class="n2f-btn primary" id="n2f-name-ok">OK</button>' +
        '<button class="n2f-btn" id="n2f-name-overwrite">Overwrite?</button>' +
        '<button class="n2f-btn" id="n2f-name-cancel">Cancel</button>' +
      '</div>';
    document.body.appendChild(nameModal);

    // Welcome screen
    var welcome = document.createElement('div');
    welcome.id = 'n2f-welcome';
    welcome.innerHTML =
      '<div id="n2f-welcome-box">' +
        '<button id="n2f-welcome-close">\u00d7</button>' +
        '<div id="n2f-welcome-brand"><h1>Next2Flash</h1><p>SWF Animation Studio</p></div>' +
        '<div id="n2f-welcome-actions">' +
          '<div class="n2f-wcard" id="n2f-wc-new">' +
            '<div class="n2f-wcard-icon">\ud83d\udcc4</div>' +
            '<div class="n2f-wcard-title">New Project</div>' +
            '<div class="n2f-wcard-desc">Start from scratch</div>' +
          '</div>' +
          '<div class="n2f-wcard" id="n2f-wc-import">' +
            '<div class="n2f-wcard-icon">\ud83d\udce5</div>' +
            '<div class="n2f-wcard-title">Import SWF</div>' +
            '<div class="n2f-wcard-desc">Edit an existing SWF</div>' +
          '</div>' +
          '<div class="n2f-wcard" id="n2f-wc-open">' +
            '<div class="n2f-wcard-icon">\ud83d\udcc2</div>' +
            '<div class="n2f-wcard-title">Open Project</div>' +
            '<div class="n2f-wcard-desc">Load a saved .n2d project</div>' +
          '</div>' +
        '</div>' +
        '<div id="n2f-welcome-recents">' +
          '<div class="n2f-recents-col">' +
            '<div class="n2f-recents-hdr">Recent Projects</div>' +
            '<div id="n2f-recent-projects"><div class="n2f-recent-empty">Loading\u2026</div></div>' +
          '</div>' +
          '<div class="n2f-recents-col">' +
            '<div class="n2f-recents-hdr">Recent Imports</div>' +
            '<div id="n2f-recent-imports"><div class="n2f-recent-empty">Loading\u2026</div></div>' +
          '</div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(welcome);

    // Wire events
    document.getElementById('n2f-import-swf').addEventListener('click', onImportSWF);
    document.getElementById('n2f-open-project').addEventListener('click', onOpenProject);
    document.getElementById('n2f-refresh-assets').addEventListener('click', onRefreshAssets);
    document.getElementById('n2f-import-asset').addEventListener('click', onImportAsset);
    document.getElementById('n2f-save-project').addEventListener('click', onSaveProject);
    document.getElementById('n2f-export-swf').addEventListener('click', onExportSWF);
    var ssf2Btn = document.getElementById('n2f-ssf2-roundtrip');
    if (ssf2Btn) {
      ssf2Btn.style.display = window.n2fElectron ? '' : 'none';
      ssf2Btn.addEventListener('click', onSsf2RoundtripAndAdl);
    }
    if (window.n2fElectron && window.n2fElectron.onSsf2AdlError) {
      window.n2fElectron.onSsf2AdlError(function (payload) {
        var msg = (payload && payload.message) || 'ADL error';
        _log.error('SSF2 ADL:', msg);
        _showExportError(msg);
      });
    }
    document.getElementById('n2f-swf-input').addEventListener('change', onSWFFileSelected);
    document.getElementById('n2f-n2d-input').addEventListener('change', onN2DFileSelected);
    document.getElementById('n2f-asset-input').addEventListener('change', onAssetFileSelected);
    document.getElementById('n2f-welcome-close').addEventListener('click', _hideWelcomeScreen);
    document.getElementById('n2f-wc-new').addEventListener('click', function () {
      _onNewProject();
    });
    document.getElementById('n2f-wc-import').addEventListener('click', function () {
      onImportSWF();
    });
    document.getElementById('n2f-wc-open').addEventListener('click', function () {
      onOpenProject();
    });

    // Warn before leaving the page if there are unsaved changes
    window.onbeforeunload = function (e) {
      if (_isDirty && _currentProjectDir) {
        e.preventDefault();
        e.returnValue = 'You have unsaved changes. Leave without saving?';
        return e.returnValue;
      }
    };

    // Wire Electron menu events
    if (window.n2fElectron) {
      window.n2fElectron.onMenuSave(onSaveProject);
      window.n2fElectron.onMenuExportSWF(onExportSWF);
      window.n2fElectron.onImportSWF(function (swfPath) { _importSWFByPath(swfPath); });
      if (window.n2fElectron.onMenuUndo) {
        window.n2fElectron.onMenuUndo(function () {
          var ws = Util.$currentWorkSpace();
          if (ws) ws.undo();
        });
      }
      if (window.n2fElectron.onMenuSsf2RoundtripAdl) {
        window.n2fElectron.onMenuSsf2RoundtripAdl(onSsf2RoundtripAndAdl);
      }
      if (window.n2fElectron.onMenuRedo) {
        window.n2fElectron.onMenuRedo(function () {
          var ws = Util.$currentWorkSpace();
          if (ws) ws.redo();
        });
      }
      if (window.n2fElectron.onMenuOpenRecent) {
        window.n2fElectron.onMenuOpenRecent(function () { _showWelcomeScreen(); });
      }
      _log.info('Electron bridge detected — native menu/dialogs active');
    }

    // Forward console.error calls to the server console so errors from
    // tool source code appear in the N2F Server Console window.
    (function () {
      var _orig = console.error;
      console.error = function () {
        _orig.apply(console, arguments);
        try {
          _serverLog('ERROR', Array.prototype.map.call(arguments, function (a) {
            return (a instanceof Error) ? (a.stack || a.message) :
              (a == null) ? String(a) :
              (typeof a === 'object') ? JSON.stringify(a) : String(a);
          }).join(' '));
        } catch (e) { /* ignore */ }
      };
    })();

    // Forward uncaught JS errors and unhandled promise rejections to the server console.
    window.onerror = function (msg, src, line, col, err) {
      _serverLog('ERROR', 'Uncaught: ' + msg +
        ' @ ' + (src || '?') + ':' + (line || 0) +
        (err && err.stack ? '\n' + err.stack : ''));
      return false;
    };
    window.addEventListener('unhandledrejection', function (e) {
      var r = e.reason;
      _serverLog('ERROR', 'UnhandledRejection: ' +
        (r ? (r.stack || r.message || String(r)) : 'unknown'));
    });

    // Intercept the + tab button to open New Project dialog instead of blank workspace.
    document.addEventListener('n2f:add-tab-requested', function (e) {
      e.preventDefault();
      _onNewProject();
    });

    // Home button: show welcome screen.
    document.addEventListener('n2f:show-welcome', function () {
      _showWelcomeScreen();
    });

    // When the last tab is closed, show the welcome screen.
    document.addEventListener('n2f:no-workspaces', function () {
      _stopAutosave();
      _stopDirtyPoll();
      _currentProjectDir = '';
      _currentProjectName = '';
      _isDirty = false;
      _setDocumentTitle('', false);
      _showWelcomeScreen();
    });

    // Show welcome screen when no project is loaded
    _showWelcomeScreen();
  }

  /* ================================================================== */
  /*  Import SWF                                                         */
  /* ================================================================== */
  /**
   * Show a styled modal prompting user for a project name and optional save location.
   * Returns a Promise that resolves with { name, saveDir } or null if cancelled.
   */
  function _promptProjectName(defaultName) {
    return new Promise(function (resolve) {
      var modal = document.getElementById('n2f-name-modal');
      var overlay = document.getElementById('n2f-overlay');
      var input = document.getElementById('n2f-name-input');
      var dirInput = document.getElementById('n2f-dir-input');
      var dirBrowse = document.getElementById('n2f-dir-browse');
      var okBtn = document.getElementById('n2f-name-ok');
      var cancelBtn = document.getElementById('n2f-name-cancel');
      var overwriteBtn = document.getElementById('n2f-name-overwrite');
      var errEl = document.getElementById('n2f-name-error');

      var _overwriteStep = 0; // 0=hidden, 1=first shown, 2=confirmed

      input.value = defaultName || '';
      dirInput.value = '';
      if (errEl) { errEl.textContent = ''; errEl.style.display = 'none'; }
      if (overwriteBtn) { overwriteBtn.style.display = 'none'; overwriteBtn.textContent = 'Overwrite?'; overwriteBtn.classList.remove('confirm'); }

      // Show native folder-picker button only in Electron
      if (window.n2fElectron) {
        dirBrowse.style.display = 'inline-flex';
        dirInput.readOnly = true;
        dirInput.style.cursor = 'default';
      } else {
        dirBrowse.style.display = 'none';
        dirInput.readOnly = false;
        dirInput.style.cursor = '';
      }

      function onBrowse() {
        window.n2fElectron.openFileDialog({ properties: ['openDirectory'] })
          .then(function (result) {
            if (!result.canceled && result.filePaths && result.filePaths.length > 0) {
              dirInput.value = result.filePaths[0];
            }
          });
      }

      modal.style.display = 'block';
      overlay.style.display = 'block';
      input.focus();
      input.select();

      function cleanup() {
        modal.style.display = 'none';
        overlay.style.display = 'none';
        okBtn.removeEventListener('click', onOk);
        cancelBtn.removeEventListener('click', onCancel);
        if (overwriteBtn) overwriteBtn.removeEventListener('click', onOverwrite);
        input.removeEventListener('keydown', onKey);
        input.removeEventListener('input', onInput);
        dirInput.removeEventListener('input', onInput);
        dirBrowse.removeEventListener('click', onBrowse);
      }
      function onInput() {
        if (errEl) { errEl.textContent = ''; errEl.style.display = 'none'; }
        // Reset overwrite prompt if the user edits the name
        if (overwriteBtn) { overwriteBtn.style.display = 'none'; overwriteBtn.textContent = 'Overwrite?'; overwriteBtn.classList.remove('confirm'); }
        _overwriteStep = 0;
      }
      function onOverwrite() {
        if (_overwriteStep === 1) {
          // Second click — confirm
          if (errEl) {
            errEl.textContent = '\u26a0 This will permanently delete the existing project folder. Click again to confirm.';
            errEl.style.display = 'block';
          }
          overwriteBtn.textContent = '\u2620 Yes, delete & replace';
          overwriteBtn.classList.add('confirm');
          _overwriteStep = 2;
        } else if (_overwriteStep === 2) {
          // Third click — execute
          var nameVal = input.value.trim() || defaultName;
          var dirVal = dirInput.value.trim() || null;
          cleanup();
          resolve({ name: nameVal, saveDir: dirVal, overwrite: true });
        }
      }
      function onOk() {
        var nameVal = input.value.trim() || defaultName;
        var dirVal = dirInput.value.trim() || null;
        var url = API_BASE + '/api/check-project-name?name=' + encodeURIComponent(nameVal);
        if (dirVal) url += '&saveDir=' + encodeURIComponent(dirVal);
        fetch(url)
          .then(function (r) { return r.ok ? r.json() : { exists: false }; })
          .then(function (data) {
            if (data.exists) {
              if (errEl) {
                errEl.textContent = '\u26a0 A project named \u201c' + nameVal + '\u201d already exists. Rename it, or click \u201cOverwrite?\u201d to replace it.';
                errEl.style.display = 'block';
              }
              if (overwriteBtn) {
                overwriteBtn.style.display = 'inline-flex';
                _overwriteStep = 1;
              }
            } else {
              cleanup();
              resolve({ name: nameVal, saveDir: dirVal });
            }
          })
          .catch(function () {
            // Server unreachable — proceed anyway
            cleanup();
            resolve({ name: nameVal, saveDir: dirVal });
          });
      }
      function onCancel() {
        cleanup();
        resolve(null);
      }
      function onKey(e) {
        if (e.key === 'Enter') onOk();
        else if (e.key === 'Escape') onCancel();
      }
      okBtn.addEventListener('click', onOk);
      cancelBtn.addEventListener('click', onCancel);
      if (overwriteBtn) overwriteBtn.addEventListener('click', onOverwrite);
      input.addEventListener('keydown', onKey);
      input.addEventListener('input', onInput);
      dirInput.addEventListener('input', onInput);
      dirBrowse.addEventListener('click', onBrowse);
    });
  }

  function onImportSWF() {
    _log.debug('Import SWF button clicked');
    // Electron: use native file dialog + path-based import (no upload)
    if (window.n2fElectron) {
      window.n2fElectron.showOpenSWFDialog().then(function (swfPath) {
        if (!swfPath) return;
        _importSWFByPath(swfPath);
      });
      return;
    }
    document.getElementById('n2f-swf-input').click();
  }

  /**
   * Electron fast path: import SWF by filesystem path — no HTTP upload.
   * Server reads the file directly from disk.
   */
  function _importSWFByPath(swfPath) {
    var fileName = swfPath.split(/[\\/]/).pop();
    var defaultName = fileName.replace(/\.\w+$/, '');

    _promptProjectName(defaultName).then(function (result) {
      if (result === null) return;
      _doImportSWFByPath(swfPath, fileName, result.name, result.saveDir, result.overwrite);
    });
  }

  function _doImportSWFByPath(swfPath, fileName, projectName, saveDir, overwrite) {
    _log.info('Importing SWF by path:', swfPath, 'as:', projectName, saveDir ? ('-> ' + saveDir) : '(default location)');
    showProgress('Sending SWF path to server...', 5);

    var reqBody = { swfPath: swfPath, lazy: true, projectName: projectName };
    if (saveDir) reqBody.saveDir = saveDir;
    if (overwrite) reqBody.overwrite = true;

    fetch(API_BASE + '/api/import-swf-path', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqBody),
    })
      .then(function (r) {
        updateProgress('Server reading SWF file...', 15);
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Server error'); });
        updateProgress('Parsing SWF tags & shapes...', 30);
        var name = r.headers.get('X-N2D-Name') || fileName.replace(/\.\w+$/, '');
        var libs = r.headers.get('X-N2D-Libraries') || '?';
        var scripts = r.headers.get('X-N2D-Scripts') || '0';
        var projDir = r.headers.get('X-Project-Dir') || '';
        var fontsHeader = r.headers.get('X-N2D-Fonts') || '';
        var fonts = null;
        if (fontsHeader) { try { fonts = JSON.parse(fontsHeader); } catch(e) {} }
        updateProgress('Downloading N2D project data (' + libs + ' libraries)...', 50);
        return r.blob().then(function (blob) {
          updateProgress('Project downloaded (' + formatBytes(blob.size) + ')...', 70);
          return { blob: blob, name: name, libs: libs, scripts: scripts, projDir: projDir, fonts: fonts };
        });
      })
      .then(function (result) {
        updateProgress('Registering fonts & preparing editor...', 80);
        _currentProjectDir = result.projDir;
        _log.info('Project created at:', _currentProjectDir);

        var refreshBtn = document.getElementById('n2f-refresh-assets');
        if (refreshBtn) refreshBtn.disabled = false;
        var saveBtn = document.getElementById('n2f-save-project');
        if (saveBtn) saveBtn.disabled = false;

        // Register @font-face rules BEFORE feeding the project to the tool
        _registerEmbeddedFonts(result.fonts);

        _importedN2DBlob = result.blob.slice(0);
        _saveImportedBlobToIDB(_importedN2DBlob);
        updateProgress('Loading project into editor...', 90);
        _currentProjectName = projectName;
        _setDocumentTitle(projectName, false);
        _markClean();
        _startAutosave();
        _startDirtyPoll();
        _addRecentImport(swfPath, fileName);
        _addRecentProject(result.projDir, projectName);
        _feedN2DToTool(result.blob, projectName);

        updateProgress('Finalizing...', 98);
        hideProgress();
        _hideWelcomeWhenTabReady();
        toast('Project created: ' + projectName + ' (' + result.libs + ' libraries, ' + result.scripts + ' scripts)\nFolder: ' + _currentProjectDir);

        // Start background hydration of lazy libraries
        _startBackgroundHydration(result.libs);
      })
      .catch(function (err) {
        hideProgress();
        _hideWelcomeScreen();
        _log.error('SWF import failed:', err.message);
        toast('Import failed: ' + err.message, true);
      });
  }

  /**
   * Start background hydration of lazy library stubs.
   * After the skeleton project is loaded, this streams full data from the server.
   */
  var _activeHydrator = null;
  function _startBackgroundHydration(libCount) {
    var expectedLibs = parseInt(libCount) || 0;
    var POLL_INTERVAL = 250;
    var MAX_WAIT = 30000;
    var waited = 0;
    var wsCountBefore = (window.Util && window.Util.$workSpaces) ? window.Util.$workSpaces.length : 0;

    _log.info('[Lazy] Starting hydration poll: expectedLibs=' + expectedLibs + ' wsCountBefore=' + wsCountBefore);

    function waitForRepo() {
      var Util = window.Util;
      if (!Util || !Util.$workSpaces || Util.$workSpaces.length === 0) {
        if (waited < MAX_WAIT) {
          waited += POLL_INTERVAL;
          return setTimeout(waitForRepo, POLL_INTERVAL);
        }
        _log.warn('[Lazy] No workspace found after ' + MAX_WAIT + 'ms');
        return;
      }

      // Wait for a NEW workspace to appear (the one loading our N2D file)
      if (Util.$workSpaces.length <= wsCountBefore && waited < MAX_WAIT) {
        if (waited % 2000 < POLL_INTERVAL) {
          _log.info('[Lazy] Waiting for new workspace: ' + Util.$workSpaces.length + ' workspaces (' + waited + 'ms)');
        }
        waited += POLL_INTERVAL;
        return setTimeout(waitForRepo, POLL_INTERVAL);
      }

      // Target the specific workspace that was just loaded (wsCountBefore is the
      // index of the new workspace), not the currently-active one — which may have
      // changed if the user switched tabs while the import was running.
      var ws = Util.$workSpaces[wsCountBefore] || (Util.$currentWorkSpace && Util.$currentWorkSpace());
      if (!ws && Util.$workSpaces.length) {
        ws = Util.$workSpaces[Util.$workSpaces.length - 1];
      }
      var repo = ws && ws._$project && ws._$project.repository;
      if (!repo) {
        if (waited < MAX_WAIT) {
          waited += POLL_INTERVAL;
          return setTimeout(waitForRepo, POLL_INTERVAL);
        }
        _log.warn('[Lazy] No repository found after ' + MAX_WAIT + 'ms');
        return;
      }

      // Wait until the tool finishes populating all libraries from the skeleton N2D
      var currentCount = 0;
      try { currentCount = repo.getAll().length; } catch(e) {}
      if (expectedLibs > 0 && currentCount < expectedLibs && waited < MAX_WAIT) {
        if (waited % 2000 < POLL_INTERVAL) {
          _log.info('[Lazy] Waiting for repo: ' + currentCount + '/' + expectedLibs + ' libs (' + waited + 'ms)');
        }
        waited += POLL_INTERVAL;
        return setTimeout(waitForRepo, POLL_INTERVAL);
      }

      _log.info('[Lazy] Repo ready: ' + currentCount + '/' + expectedLibs + ' libs after ' + waited + 'ms');
      _serverLog('INFO', '[Lazy] Repo ready: ' + currentCount + '/' + expectedLibs + ' libs after ' + waited + 'ms');
      beginHydration(repo);
    }

    function beginHydration(repo) {
      try {
        // Create hydrator with bulk fetch
        if (_activeHydrator) {
          _activeHydrator.abort();
          _log.info('[Lazy] Aborted previous hydrator');
        }
        _activeHydrator = new BackgroundHydrator('/api/lazy');

        function logHydrationSnapshot(tag) {
          try {
            var libs = Array.from(repo.getAll());
            var lazyCount = 0;
            var bitmapCount = 0;
            var bitmapMissingBuffer = 0;
            var lazyTypeCounts = {};
            for (var li = 0; li < libs.length; li++) {
              var lib = libs[li];
              if (!lib) continue;
              var isBitmapLike = !!lib.imageType || (typeof lib.width === 'number' && typeof lib.height === 'number' && lib.type === 4);
              if (lib._$lazy) {
                lazyCount++;
                var typeKey = String(lib.type != null ? lib.type : 'unknown');
                lazyTypeCounts[typeKey] = (lazyTypeCounts[typeKey] || 0) + 1;
              }
              if (isBitmapLike) {
                bitmapCount++;
                if (!lib._$buffer || !lib._$buffer.length) {
                  bitmapMissingBuffer++;
                }
              }
            }

            var stageArea = document.getElementById('stage-area');
            var displayObjects = stageArea ? stageArea.querySelectorAll('.display-object').length : -1;
            var canvases = stageArea ? stageArea.querySelectorAll('canvas').length : -1;

            var msg = '[LazyDiag] ' + tag
              + ' libs=' + libs.length
              + ' lazy=' + lazyCount
              + ' bitmaps=' + bitmapCount
              + ' missingBitmapBuffers=' + bitmapMissingBuffer
              + ' lazyTypeCounts=' + JSON.stringify(lazyTypeCounts)
              + ' stageDisplayObjects=' + displayObjects
              + ' stageCanvases=' + canvases;
            _log.info(msg);
            _serverLog('INFO', msg);
          } catch (diagErr) {
            _serverLog('WARN', '[LazyDiag] snapshot failed: ' + (diagErr.message || diagErr));
          }
        }

        _log.info('[Lazy] Starting bulk background hydration...');
        _activeHydrator.hydrate(repo, function(hydrated, total) {
          if (hydrated % 200 === 0 || hydrated === total) {
            _log.info('[Lazy] Hydrated ' + hydrated + '/' + total + ' libraries');
          }
        }).then(function(result) {
          var hydrated = result && typeof result === 'object' ? result.hydrated : result;
          var unresolved = result && typeof result === 'object' ? result.unresolved : 0;
          var errors = result && typeof result === 'object' ? result.errors : 0;
          var summary = '[Lazy] Background hydration complete: hydrated=' + hydrated + ' unresolved=' + unresolved + ' errors=' + errors;
          _log.info(summary);
          _serverLog('INFO', summary);
          if (window.Util) {
            window.Util.$hydrationVersion = (window.Util.$hydrationVersion | 0) + 1;
            _log.info('[Lazy] Hydration version: ' + window.Util.$hydrationVersion);
            _serverLog('INFO', '[Lazy] Hydration version: ' + window.Util.$hydrationVersion);
          }
          logHydrationSnapshot('after-hydrate-before-clear');
          _activeHydrator = null;

          // Trigger canvas re-render now that all data is loaded
          try {
            _log.info('[Lazy] Triggering canvas re-render...');
            // Clear cached graphic buffers in chunks via requestIdleCallback
            // to avoid a 4+ second main-thread freeze on large projects
            var allLibs = Array.from(repo.getAll());
            var CHUNK = 200;
            var idx = 0;
            function clearChunk(deadline) {
              while (idx < allLibs.length && (typeof deadline === 'undefined' || deadline.timeRemaining() > 1)) {
                var lib = allLibs[idx++];
                if (lib._$graphicBuffer) lib._$graphicBuffer = null;
                if (lib._$cacheCanvas) lib._$cacheCanvas = null;
                if (lib._$bitmapCanvas) lib._$bitmapCanvas = null;
              }
              if (idx < allLibs.length) {
                requestIdleCallback(clearChunk, { timeout: 100 });
              } else {
                _log.info('[Lazy] Cleared caches for ' + allLibs.length + ' libraries');
                finishHydrationRender();
              }
            }
            function finishHydrationRender() {
              // Flush the WebGL texture cache so stale black textures are discarded
              try {
                var player = window.next2d && window.next2d.player;
                if (player && player.cacheStore) {
                  player.cacheStore.reset();
                  _log.info('[Lazy] WebGL cacheStore reset');
                  _serverLog('INFO', '[Lazy] WebGL cacheStore reset');
                }
              } catch (cacheErr) {
                _log.warn('[Lazy] cacheStore reset failed:', cacheErr.message);
              }

              // Force the actual canvas repaint so bitmaps appear.
              // Hydration can complete before the stage timeline is fully initialized,
              // so retry redraw briefly until the scene is ready.
              var maxAttempts = 12;
              function triggerHydrationRedraw(attempt) {
                var Util = window.Util;
                var stageArea = document.getElementById('stage-area');
                if (attempt === 1) {
                  console.warn('[N2F-Hydration] triggerHydrationRedraw starting (attempt 1)');
                }
                if (!Util || !Util.$currentWorkSpace) {
                  if (attempt === 1 || attempt === maxAttempts) {
                    console.warn('[N2F-Hydration] redraw attempt ' + attempt + ': Util not ready');
                    _serverLog('INFO', '[LazyDiag] redraw attempt ' + attempt + ': Util not ready');
                  }
                  if (attempt < maxAttempts) {
                    return setTimeout(function() { triggerHydrationRedraw(attempt + 1); }, 250);
                  }
                  _log.warn('[Lazy] Redraw skipped: Util not ready after retries');
                  _serverLog('WARN', '[Lazy] Redraw skipped: Util not ready after retries');
                  return;
                }

                var ws = Util.$currentWorkSpace();
                var scene = ws && ws.scene;
                if (!scene || !stageArea) {
                  if (attempt === 1 || attempt === maxAttempts) {
                    console.warn('[N2F-Hydration] redraw attempt ' + attempt + ': scene/stage not ready');
                    _serverLog('INFO', '[LazyDiag] redraw attempt ' + attempt + ': scene/stage not ready');
                  }
                  if (attempt < maxAttempts) {
                    return setTimeout(function() { triggerHydrationRedraw(attempt + 1); }, 250);
                  }
                  _log.warn('[Lazy] Redraw skipped: scene/stage not ready after retries');
                  _serverLog('WARN', '[Lazy] Redraw skipped: scene/stage not ready after retries');
                  return;
                }

                var hydrVer = window.Util ? (window.Util.$hydrationVersion | 0) : -1;
                var wsSeq   = (ws && ws.root && ws.root._$renderSeq) ? ws.root._$renderSeq : '?';
                _serverLog('INFO', '[LazyDiag] triggerHydrationRedraw attempt=' + attempt +
                  ' frame=' + (Util.$timelineFrame ? Util.$timelineFrame.currentFrame : '?') +
                  ' hydrVer=' + hydrVer + ' wsSeq=' + wsSeq);

                try {
                  if (typeof scene.cacheClear === 'function') {
                    scene.cacheClear();
                  } else if (scene._$layers) {
                    scene._$layers.forEach(function(layer) {
                      var chars = layer._$characters;
                      if (chars) {
                        for (var ci = 0; ci < chars.length; ci++) {
                          chars[ci].dispose();
                        }
                      }
                    });
                  }
                } catch (dispErr) {
                  _log.warn('[Lazy] Character cache clear failed:', dispErr.message);
                }

                var frame = Util.$timelineFrame && Util.$timelineFrame.currentFrame
                  ? Util.$timelineFrame.currentFrame
                  : 1;

                var wsSeqAfterClear = (ws && ws.root && ws.root._$renderSeq) ? ws.root._$renderSeq : '?';
                _serverLog('INFO', '[LazyDiag] before changeFrame frame=' + frame + ' seqAfterClear=' + wsSeqAfterClear);

                var renderPromise = null;
                try {
                  if (typeof scene.changeFrame === 'function') {
                    renderPromise = scene.changeFrame(frame);
                  } else if (Util.$baseController && Util.$baseController.reloadScreen) {
                    Util.$baseController.reloadScreen();
                  }
                } catch (renderErr) {
                  renderPromise = Promise.reject(renderErr);
                }

                Promise.resolve(renderPromise)
                  .then(function() {
                    var wsSeqFinal = (ws && ws.root && ws.root._$renderSeq) ? ws.root._$renderSeq : '?';
                    var stageChildren = stageArea ? stageArea.querySelectorAll('canvas').length : -1;
                    // If stage has no canvases the changeFrame was likely STALE (a newer
                    // render incremented _$renderSeq before our .then() ran).  Retry.
                    if (stageChildren === 0 && attempt < maxAttempts) {
                      console.warn('[N2F-Hydration] Stage empty after attempt ' + attempt + ' (likely stale render), retrying...');
                      return setTimeout(function() { triggerHydrationRedraw(attempt + 1); }, 250);
                    }
                    console.warn('[N2F-Hydration] Hydration redraw complete: ' + stageChildren + ' canvas(es) on stage (attempt ' + attempt + ')');
                    _log.info('[Lazy] Canvas re-render triggered at frame ' + frame + ' (attempt ' + attempt + ')');
                    _serverLog('INFO', '[Lazy] Canvas re-render triggered at frame ' + frame +
                      ' (attempt ' + attempt + ') seqFinal=' + wsSeqFinal + ' stageCanvases=' + stageChildren);
                    logHydrationSnapshot('after-rerender-immediate');
                    setTimeout(function() {
                      logHydrationSnapshot('after-rerender-1000ms');
                    }, 1000);
                  })
                  .catch(function(err) {
                    _log.warn('[Lazy] Re-render attempt failed:', err && err.message ? err.message : err);
                    if (attempt < maxAttempts) {
                      setTimeout(function() { triggerHydrationRedraw(attempt + 1); }, 250);
                    } else {
                      _serverLog('WARN', '[Lazy] Re-render failed after retries');
                    }
                  });
              }

              triggerHydrationRedraw(1);
            }
            requestIdleCallback(clearChunk, { timeout: 100 });
          } catch (renderErr) {
            _log.warn('[Lazy] Canvas re-render failed (non-fatal):', renderErr.message);
          }
        }).catch(function(err) {
          _log.error('[Lazy] Background hydration failed:', err);
          _activeHydrator = null;
        });
      } catch (e) {
        _log.error('[Lazy] Failed to start background hydration:', e);
      }
    }

    waitForRepo();
  }

  function onSWFFileSelected(e) {
    var file = e.target.files[0];
    if (!file) return;
    _log.info('SWF file selected:', file.name, formatBytes(file.size));
    e.target.value = '';  // reset for re-selecting same file

    var defaultName = file.name.replace(/\.\w+$/, '');
    _promptProjectName(defaultName).then(function (result) {
      if (result === null) return;
      _doSWFFileImport(file, result.name, result.saveDir, result.overwrite);
    });
  }

  function _doSWFFileImport(file, projectName, saveDir, overwrite) {
    if (window.N2FProfiler) {
      window.N2FProfiler.startSession('swf-import-client');
      window.N2FProfiler.size('swf_file', file.size);
      window.N2FProfiler.note('file: ' + file.name);
      window.N2FProfiler.startTimer('server_convert');
    }

    showProgress('Uploading SWF to server...\n' + file.name + ' (' + formatBytes(file.size) + ')', 5);

    var form = new FormData();
    form.append('file', file);
    form.append('projectName', projectName);
    if (saveDir) form.append('saveDir', saveDir);
    if (overwrite) form.append('overwrite', '1');

    fetch(API_BASE + '/api/swf-to-project', { method: 'POST', body: form })
      .then(function (r) {
        updateProgress('Server converting SWF to N2D format...', 20);
        if (window.N2FProfiler) window.N2FProfiler.stopTimer();
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Server error'); });
        updateProgress('Extracting shapes, bitmaps & sounds...', 35);
        var name = r.headers.get('X-N2D-Name') || file.name.replace('.swf', '');
        var libs = r.headers.get('X-N2D-Libraries') || '?';
        var scripts = r.headers.get('X-N2D-Scripts') || '0';
        var projDir = r.headers.get('X-Project-Dir') || '';
        var fontsHeader = r.headers.get('X-N2D-Fonts') || '';
        var fonts = null;
        if (fontsHeader) { try { fonts = JSON.parse(fontsHeader); } catch(e) {} }
        if (window.N2FProfiler) {
          window.N2FProfiler.count('libraries', parseInt(libs) || 0);
          window.N2FProfiler.count('scripts', parseInt(scripts) || 0);
          window.N2FProfiler.startTimer('read_blob');
        }
        updateProgress('Downloading N2D project (' + libs + ' libraries)...', 50);
        return r.blob().then(function (blob) {
          if (window.N2FProfiler) {
            window.N2FProfiler.stopTimer();
            window.N2FProfiler.size('n2d_blob', blob.size);
          }
          updateProgress('Project downloaded (' + formatBytes(blob.size) + ')...', 65);
          return { blob: blob, name: name, libs: libs, scripts: scripts, projDir: projDir, fonts: fonts };
        });
      })
      .then(function (result) {
        updateProgress('Registering fonts & preparing editor...', 75);
        _currentProjectDir = result.projDir;
        _log.info('Project created at:', _currentProjectDir);

        var refreshBtn = document.getElementById('n2f-refresh-assets');
        if (refreshBtn) refreshBtn.disabled = false;
        var saveBtn = document.getElementById('n2f-save-project');
        if (saveBtn) saveBtn.disabled = false;

        // Register @font-face rules BEFORE feeding the project to the tool
        _registerEmbeddedFonts(result.fonts);

        _importedN2DBlob = result.blob.slice(0);
        _saveImportedBlobToIDB(_importedN2DBlob);

        updateProgress('Loading project into editor...', 88);
        if (window.N2FProfiler) window.N2FProfiler.startTimer('load_into_tool');
        _currentProjectName = projectName;
        _setDocumentTitle(projectName, false);
        _markClean();
        _startAutosave();
        _startDirtyPoll();
        _addRecentImport(file.name || '', file.name || projectName);
        _addRecentProject(result.projDir, projectName);
        _feedN2DToTool(result.blob, projectName);

        // End session after a delay to capture loading time
        if (window.N2FProfiler) {
          setTimeout(function() {
            window.N2FProfiler.stopTimer();
            window.N2FProfiler.endSession('swf-import-client');
          }, 8000);
        }

        updateProgress('Finalizing...', 98);
        hideProgress();
        _hideWelcomeWhenTabReady();
        toast('Project created: ' + projectName + ' (' + result.libs + ' libraries, ' + result.scripts + ' scripts)\nFolder: ' + _currentProjectDir);
      })
      .catch(function (err) {
        hideProgress();
        _hideWelcomeScreen();
        if (window.N2FProfiler) window.N2FProfiler.endSession('swf-import-client');
        _log.error('SWF import failed:', err.message);
        toast('Import failed: ' + err.message, true);
      });
  }

  /* ================================================================== */
  /*  Project folder tracking                                            */
  /* ================================================================== */
  var _currentProjectDir = null;

  /* ================================================================== */
  /*  Open Existing Project                                              */
  /* ================================================================== */
  function onOpenProject() {
    _log.debug('Open N2D button clicked');
    document.getElementById('n2f-n2d-input').click();
  }

  function onN2DFileSelected(e) {
    var file = e.target.files[0];
    if (!file) return;
    _log.info('N2D file selected:', file.name, formatBytes(file.size));
    e.target.value = '';
    showProgress('Reading N2D file...\n' + file.name + ' (' + formatBytes(file.size) + ')', 5);
    _doOpenProjectBlob(file, file.name, null);
  }

  /**
   * POST a blob to /api/open-project, apply the result to the tool.
   * @param {Blob} blob       - The .n2d blob to upload.
   * @param {string} fileName - Used as fallback name if server doesn't return one.
   * @param {Function|null} onSuccess - Called with the result object after loading;
   *                                    receives {blob, name, libs, projDir}.
   */
  function _doOpenProjectBlob(blob, fileName, onSuccess) {
    var form = new FormData();
    form.append('file', blob instanceof File ? blob : new File([blob], fileName, { type: 'application/octet-stream' }));

    fetch(API_BASE + '/api/open-project', { method: 'POST', body: form })
      .then(function (r) {
        updateProgress('Server processing N2D file...', 25);
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Server error'); });
        var name = r.headers.get('X-N2D-Name') || fileName.replace(/\.n2d$/i, '');
        var libs = r.headers.get('X-N2D-Libraries') || '?';
        var projDir = r.headers.get('X-Project-Dir') || '';
        console.log('[N2F] open-project response headers:', {
          'X-N2D-Name': name,
          'X-N2D-Libraries': libs,
          'X-Project-Dir': projDir,
          'X-N2D-Scripts': r.headers.get('X-N2D-Scripts')
        });
        updateProgress('Downloading project data (' + libs + ' libraries)...', 50);
        return r.blob().then(function (b) {
          console.log('[N2F] received blob size:', b.size);
          updateProgress('Project downloaded (' + formatBytes(b.size) + ')...', 70);
          return { blob: b, name: name, libs: libs, projDir: projDir };
        });
      })
      .then(function (result) {
        updateProgress('Setting up project folder...', 80);
        if (result.projDir) {
          _currentProjectDir = result.projDir;
          console.log('[N2F] project dir set to:', _currentProjectDir);
          _log.info('Opened project at:', _currentProjectDir);
          var refreshBtn = document.getElementById('n2f-refresh-assets');
          if (refreshBtn) refreshBtn.disabled = false;
          var saveBtn = document.getElementById('n2f-save-project');
          if (saveBtn) saveBtn.disabled = false;
        } else {
          console.warn('[N2F] No X-Project-Dir returned — bitmaps were NOT overlaid by server');
        }

        _importedN2DBlob = result.blob.slice(0);
        _saveImportedBlobToIDB(_importedN2DBlob);

        updateProgress('Loading project into editor...', 90);
        _currentProjectName = result.name;
        _setDocumentTitle(result.name, false);
        _markClean();
        _startAutosave();
        _startDirtyPoll();
        if (result.projDir) _addRecentProject(result.projDir, result.name);
        _feedN2DToTool(result.blob, result.name);

        updateProgress('Finalizing...', 98);
        hideProgress();
        _hideWelcomeWhenTabReady();
        if (onSuccess) onSuccess(result);
        else toast('Opened: ' + result.name + ' (' + result.libs + ' libraries)');
      })
      .catch(function (err) {
        hideProgress();
        _hideWelcomeScreen();
        _log.error('Open N2D failed:', err.message);
        toast('Open failed: ' + err.message, true);
      });
  }

  /* ================================================================== */
  /*  Refresh Assets                                                     */
  /* ================================================================== */
  function onRefreshAssets() {
    _log.debug('Refresh Assets button clicked');
    if (!_currentProjectDir) {
      toast('No project folder loaded. Import a SWF as a project first.', true);
      return;
    }

    // Remember which in-app tab is currently active.
    // The tool creates a new tab when loading an N2D blob.
    var oldTabEl = document.querySelector('#view-tab-area .active[data-tab-id]');
    var oldTabId = oldTabEl ? oldTabEl.dataset.tabId : null;

    showProgress('Refreshing project from server...', 10);
    fetch(API_BASE + '/api/refresh-assets', { method: 'POST' })
      .then(function (r) {
        updateProgress('Refreshing external assets...', 35);
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Server error'); });
        var name = r.headers.get('X-N2D-Name') || _currentProjectDir.split(/[\\/]/).pop() || 'project';
        var libs = r.headers.get('X-N2D-Libraries') || '?';
        updateProgress('Downloading refreshed project data (' + libs + ' libraries)...', 60);
        return r.blob().then(function (b) {
          return { blob: b, name: name, libs: libs };
        });
      })
      .then(function (result) {
        updateProgress('Loading refreshed project into editor...', 85);
        _currentProjectName = result.name;
        _feedN2DToTool(result.blob, result.name);

        _importedN2DBlob = result.blob.slice(0);
        _saveImportedBlobToIDB(_importedN2DBlob);

        // Poll until the new tab becomes active in the DOM, then close the old one.
        var attempts = 0;
        function waitAndCloseOldTab() {
          var activeEl = document.querySelector('#view-tab-area .active[data-tab-id]');
          var activeId = activeEl ? activeEl.dataset.tabId : null;
          if (activeId !== null && activeId !== oldTabId) {
            // New workspace is loaded and active — safe to close old tab.
            if (oldTabId !== null) {
              var closeBtn = document.getElementById('tab-delete-id-' + oldTabId);
              if (closeBtn) {
                var origConfirm = window.confirm;
                window.confirm = function () { return true; };
                try { closeBtn.click(); } finally { window.confirm = origConfirm; }
              }
            }
            hideProgress();
            toast('Refreshed: ' + result.name + ' (' + result.libs + ' libraries)');
          } else if (++attempts < 100) {
            setTimeout(waitAndCloseOldTab, 100);
          } else {
            _log.warn('Refresh: timed out waiting for new tab');
            hideProgress();
            toast('Refreshed: ' + result.name + ' (old tab may still be open)');
          }
        }
        setTimeout(waitAndCloseOldTab, 100);
      })
      .catch(function (err) {
        hideProgress();
        _log.error('Refresh failed:', err.message);
        toast('Refresh failed: ' + err.message, true);
      });
  }

  /* ================================================================== */
  /*  Helper: Register @font-face rules for embedded SWF fonts          */
  /* ================================================================== */
  function _registerEmbeddedFonts(fontManifest) {
    if (!fontManifest || !fontManifest.length) return;
    // Remove any previous embedded-font stylesheet
    var prev = document.getElementById('n2f-embedded-fonts');
    if (prev) prev.remove();

    var css = '';
    for (var i = 0; i < fontManifest.length; i++) {
      var f = fontManifest[i];
      css += '@font-face { font-family: "' + f.faceName.replace(/"/g, '\\"') + '"; '
           + "src: url('" + API_BASE + '/api/font/' + f.id + "') format('truetype'); "
           + 'font-display: block; }\n';
    }
    var style = document.createElement('style');
    style.id = 'n2f-embedded-fonts';
    style.textContent = css;
    document.head.appendChild(style);
    console.log('[N2F] Registered ' + fontManifest.length + ' @font-face rule(s)');
    _serverLog('INFO', 'Registered ' + fontManifest.length + ' embedded @font-face rule(s)');

    // Preload fonts so they are ready when the canvas renders
    fontManifest.forEach(function (f) {
      document.fonts.load('20px "' + f.faceName + '"').then(function () {
        console.log('[N2F] Font preloaded: ' + f.faceName);
      }).catch(function (e) {
        console.warn('[N2F] Font preload failed for ' + f.faceName + ':', e);
      });
    });
  }

  /* ================================================================== */
  /*  Helper: Feed N2D blob to tool                                      */
  /* ================================================================== */
  function _feedN2DToTool(blob, name) {
    console.log('[N2F] _feedN2DToTool called, blob size:', blob.size, 'name:', name);
    var n2dFile = new File([blob], name + '.n2d', { type: 'application/octet-stream' });
    var fileInput = document.getElementById('tools-load-file-input');
    console.log('[N2F] tools-load-file-input element:', fileInput);
    if (fileInput) {
      // Clear the texture cache so updated bitmaps are rendered fresh.
      var cacheStore = window.next2d && window.next2d.player && window.next2d.player.cacheStore;
      console.log('[N2F] cacheStore:', cacheStore);
      try {
        if (cacheStore) {
          cacheStore.reset();
          console.log('[N2F] cacheStore.reset() called successfully');
        } else {
          console.warn('[N2F] cacheStore not available — textures will NOT be cleared');
        }
      } catch (e) {
        console.error('[N2F] cacheStore.reset() threw:', e);
      }
      var dt = new DataTransfer();
      dt.items.add(n2dFile);
      fileInput.files = dt.files;
      console.log('[N2F] dispatching change event on file input...');
      fileInput.dispatchEvent(new Event('change', { bubbles: true }));
      console.log('[N2F] change event dispatched');
      _serverLog('INFO', 'Fed N2D to native file input, size: ' + n2dFile.size);
    } else {
      console.error('[N2F] tools-load-file-input element not found!');
      _serverLog('ERROR', 'tools-load-file-input element not found');
      toast('Load failed: tool file input not found', true);
    }
  }

  /* ================================================================== */
  /*  Save Project                                                      */
  /* ================================================================== */

  /** Save a scratch (no project folder) project by prompting for name/location. */
  function _saveAsNewProject(projectName, saveDir) {
    _log.info('Save As new project:', projectName, saveDir || '(default location)');
    showProgress('Capturing editor state...', 10);
    saveProjectAsN2D()
      .then(function (n2dBlob) {
        updateProgress('Saving project to server (' + formatBytes(n2dBlob.size) + ')...', 50);
        var form = new FormData();
        form.append('n2d', n2dBlob, 'project.n2d');
        form.append('name', projectName);
        if (saveDir) form.append('saveDir', saveDir);
        return fetch(API_BASE + '/api/save-as-project', { method: 'POST', body: form });
      })
      .then(function (r) {
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Save failed'); });
        return r.json();
      })
      .then(function (result) {
        hideProgress();
        _currentProjectDir = result.projDir;
        _currentProjectName = projectName;
        _setDocumentTitle(projectName, false);
        _markClean();
        _startAutosave();
        _startDirtyPoll();
        _addRecentProject(result.projDir, projectName);
        var refreshBtn = document.getElementById('n2f-refresh-assets');
        if (refreshBtn) refreshBtn.removeAttribute('disabled');
        _log.info('Project saved as new folder:', _currentProjectDir);
        toast('Project saved: ' + result.projDir);
      })
      .catch(function (err) {
        hideProgress();
        _log.error('Save As new project failed:', err.message);
        toast('Save failed: ' + err.message, true);
      });
  }

  function onSaveProject() {
    if (!_currentProjectDir) {
      // No project folder yet — prompt for name/location and create one
      var defaultName = getProjectName() || 'untitled';
      _promptProjectName(defaultName).then(function (result) {
        if (!result) return;
        _saveAsNewProject(result.name, result.saveDir);
      });
      return;
    }
    _log.info('Save Project requested');
    showProgress('Capturing editor state...', 10);

    saveProjectAsN2D()
      .then(function (n2dBlob) {
        updateProgress('Uploading project to server (' + formatBytes(n2dBlob.size) + ')...', 40);
        var form = new FormData();
        form.append('n2d', n2dBlob, 'project.n2d');
        return fetch(API_BASE + '/api/save-project', { method: 'POST', body: form });
      })
      .then(function (r) {
        updateProgress('Server writing files to disk...', 75);
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Save failed'); });
        return r.json();
      })
      .then(function (result) {
        updateProgress('Save complete.', 100);
        hideProgress();
        _markClean();
        _addRecentProject(_currentProjectDir, _currentProjectName);
        _log.info('Project saved to:', result.folder);
        toast('Project saved to: ' + result.folder);
      })
      .catch(function (err) {
        hideProgress();
        _log.error('Save project failed:', err.message);
        toast('Save failed: ' + err.message, true);
      });
  }

  /* ================================================================== */
  /*  Collect editor text patches (lightweight, no full serialize)       */
  /* ================================================================== */

  /**
   * Iterate all library items in the current workspace and return an array
   * of text-field objects that the editor holds in memory.  Each item is the
   * full toObject() of a TextField instance — a small JSON blob (< 1 KB per
   * text field).  This avoids the V8 RangeError that kills JSON.stringify on
   * the whole 225 MB+ workspace by serialising only the tiny text subset.
   */
  function _collectTextPatches() {
    var Util = window.Util;
    if (!Util || !Util.$currentWorkSpace) return [];
    var ws = Util.$currentWorkSpace();
    if (!ws) return [];
    var repo = ws._$project && ws._$project.repository;
    if (!repo) return [];

    var patches = [];
    var allLibs = repo.getAll();
    for (var i = 0; i < allLibs.length; i++) {
      var lib = allLibs[i];
      if (lib && lib.type === 'text' && typeof lib.toObject === 'function') {
        patches.push(lib.toObject());
      }
    }
    _log.info('Collected ' + patches.length + ' text patches from editor');
    return patches;
  }

  /**
   * Collect current ActionScript scripts from the AS panel, including unsaved
   * editor text (captured by injectRoundtripFields). Returns null if panel is
   * unavailable or no scripts are present.
   */
  function _collectScriptPatches() {
    var panel = window.__n2d_as_panel;
    if (!panel || typeof panel.injectRoundtripFields !== 'function') {
      // Fallback for cases where AS panel instance is not active but scripts
      // are still persisted by actionscript-panel.js.
      try {
        var raw = localStorage.getItem('n2d_as_scripts');
        if (!raw) return null;
        var cached = JSON.parse(raw);
        if (!Array.isArray(cached) || !cached.length) return null;
        _log.info('Collected ' + cached.length + ' script patches from localStorage fallback');
        return {
          scripts: cached,
          // Assume modified when exporting from fallback cache so compiler
          // does not skip source refresh paths.
          scriptsModified: true
        };
      } catch (e) {
        _log.warn('Failed localStorage script fallback: ' + e.message);
        return null;
      }
    }

    try {
      var probe = {};
      panel.injectRoundtripFields(probe);
      var scripts = Array.isArray(probe.scripts) ? probe.scripts : [];
      var scriptsModified = !!probe.scriptsModified;
      if (!scripts.length && !scriptsModified) return null;
      _log.info('Collected ' + scripts.length + ' script patches from AS panel');
      return {
        scripts: scripts,
        scriptsModified: scriptsModified
      };
    } catch (ex) {
      _log.warn('Failed to collect script patches: ' + ex.message);
      return null;
    }
  }

  /* ================================================================== */
  /*  SSF2 roundtrip + ADL (Electron)                                    */
  /* ================================================================== */
  function onSsf2RoundtripAndAdl() {
    if (!window.n2fElectron) {
      toast('SSF2 ADL debug requires the Electron desktop app');
      return;
    }
    _log.info('SSF2 roundtrip + ADL requested');
    showProgress('Loading SSF2 debug settings...', 5);
    window.n2fElectron.ssf2ShowConsole();

    fetch(API_BASE + '/api/ssf2/config')
      .then(function (r) { return r.json(); })
      .then(function (cfgRes) {
        var cfg = (cfgRes && cfgRes.config) || {};
        updateProgress('Roundtrip: import + compile (may take several minutes)...', 15);
        return fetch(API_BASE + '/api/ssf2/roundtrip', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sourceSwf: cfg.sourceSwf,
            projectName: cfg.projectName || 'ssf2-roundtrip',
            adlRoot: cfg.adlRoot,
            gameRoot: cfg.gameRoot,
            deployToAdlRoot: cfg.deployToAdlRoot !== false,
            deployToGameRoot: cfg.deployToGameRoot !== false,
            overwriteProject: true,
          }),
        });
      })
      .then(function (r) {
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Roundtrip failed'); });
        return r.json();
      })
      .then(function (result) {
        if (result.projectDir) {
          _currentProjectDir = result.projectDir;
          var refreshBtn = document.getElementById('n2f-refresh-assets');
          if (refreshBtn) refreshBtn.removeAttribute('disabled');
        }
        var warns = (result.preflight && result.preflight.compare && result.preflight.compare.warnings) || [];
        if (warns.length) {
          _log.warn('SSF2 preflight warnings:\n' + warns.join('\n'));
        }
        updateProgress('Launching ADL...', 92);
        return fetch(API_BASE + '/api/ssf2/config')
          .then(function (r) { return r.json(); })
          .then(function (cfgRes) {
            var cfg = (cfgRes && cfgRes.config) || {};
            return window.n2fElectron.ssf2RunAdl({
              adlRoot: cfg.adlRoot,
              airSdk: cfg.airSdk,
              adlExtDir: cfg.adlExtDir,
              sourceSwf: cfg.sourceSwf,
            });
          })
          .then(function (adlRes) {
            hideProgress();
            var msg = 'Roundtrip SWF: ' + formatBytes(result.compile && result.compile.size);
            if (warns.length) {
              msg += ' (' + warns.length + ' preflight warning(s) — see SSF2 console)';
            }
            if (adlRes && adlRes.ok) {
              toast(msg + ' — ADL launched');
            } else {
              toast(msg + ' — ADL failed: ' + ((adlRes && adlRes.error) || 'unknown'));
            }
            _log.info('SSF2 roundtrip complete', result);
          });
      })
      .catch(function (err) {
        hideProgress();
        _log.error('SSF2 roundtrip failed:', err.message);
        _showExportError(err.message);
      });
  }

  /* ================================================================== */
  /*  Export SWF                                                         */
  /* ================================================================== */
  function onExportSWF() {
    _log.info('Export SWF requested');
    showProgress('Preparing project for SWF export...', 5);

    if (window.N2FProfiler) {
      window.N2FProfiler.startSession('swf-export-client');
      window.N2FProfiler.startTimer('prepare_export');
    }

    var name = getProjectName() || 'output';

    // When a project folder is active, capture the current editor state first
    // (so timeline edits like position/filter changes are included), save it
    // to the project folder, then compile from there.
    if (_currentProjectDir) {

      // ── ELECTRON PATH: try full editor blob capture, fall back to disk-only ──
      if (window.n2fElectron) {
        _log.info('Electron — attempting full export via editorBlob');
        window.n2fElectron.showSaveSWFDialog(name + '.swf').then(function (outputPath) {
          if (!outputPath) { hideProgress(); return; }

          function _electronDiskOnlyFallback() {
            updateProgress('Reading project from disk...', 30);
            var textPatches = _collectTextPatches();
            var scriptPatches = _collectScriptPatches();
            _log.info('Electron disk-only fallback with ' + textPatches.length + ' text patches');
            updateProgress('Compiling SWF from project files...', 45);
            return fetch(API_BASE + '/api/compile-disk', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                projectDir: _currentProjectDir,
                outputPath: outputPath,
                textPatches: textPatches,
                scriptPatches: scriptPatches
              }),
            })
              .then(function (r) {
                if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Compilation failed'); });
                return r.json();
              })
              .then(function (result) {
                updateProgress('Writing SWF to disk...', 90);
                hideProgress();
                _log.info('SWF compiled to:', result.swfPath, formatBytes(result.size));
                toast('Exported: ' + outputPath.split(/[\\/]/).pop() + ' (' + formatBytes(result.size) + ')');
              });
          }

          updateProgress('Serializing editor state...', 15);
          return _captureToolBlob()
            .then(function (rawBlob) {
              updateProgress('Uploading editor data to server...', 30);
              var form = new FormData();
              form.append('editorBlob', rawBlob, 'editor.bin');
              form.append('outputPath', outputPath);
              var scriptPatches = _collectScriptPatches();
              if (scriptPatches) {
                form.append('scriptPatches', JSON.stringify(scriptPatches));
              }
              updateProgress('Server compiling SWF...', 50);
              return fetch(API_BASE + '/api/save-and-compile', { method: 'POST', body: form })
                .then(function (r) {
                  updateProgress('Processing server response...', 75);
                  if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Compilation failed'); });
                  return r.json();
                })
                .then(function (result) {
                  updateProgress('SWF written to disk.', 95);
                  hideProgress();
                  _log.info('SWF compiled to:', result.swfPath, formatBytes(result.size));
                  toast('Exported: ' + outputPath.split(/[\\/]/).pop() + ' (' + formatBytes(result.size) + ')');
                });
            })
            .catch(function (captureErr) {
              _log.warn('editorBlob capture failed (' + captureErr.message + '), falling back to disk-only');
              return _electronDiskOnlyFallback();
            });
        }).catch(function (err) {
          hideProgress();
          if (window.N2FProfiler) window.N2FProfiler.endSession('swf-import-client');
          _log.error('SWF export failed:', err.message);
          _showExportError(err.message);
        });
        return;
      }

      // ── BROWSER PATH: use HTTP blob transfer ──
      _log.info('Project folder active — fast export via server-side merge');
      updateProgress('Serializing editor state...', 15);

      // Fast path: try to capture the tool blob, but if the tool's
      // internal JSON.stringify crashes (RangeError for huge projects),
      // fall back to compiling directly from disk data.
      function _sendCompileRequest(rawBlob) {
        updateProgress('Uploading data to server...', 35);
        var form = new FormData();
        if (rawBlob) {
          form.append('editorBlob', rawBlob, 'editor.bin');
          var scriptPatches = _collectScriptPatches();
          if (scriptPatches) {
            form.append('scriptPatches', JSON.stringify(scriptPatches));
          }
        } else {
          // Disk-only: tell server to compile from existing project.n2d
          // but include text patches so editor text edits are preserved
          form.append('diskOnly', '1');
          var patches = _collectTextPatches();
          if (patches.length) {
            form.append('textPatches', JSON.stringify(patches));
          }
          var scriptPatchesDisk = _collectScriptPatches();
          if (scriptPatchesDisk) {
            form.append('scriptPatches', JSON.stringify(scriptPatchesDisk));
          }
        }
        updateProgress('Server compiling SWF...', 50);
        return fetch(API_BASE + '/api/save-and-compile', { method: 'POST', body: form })
          .then(function (r) {
            updateProgress('Receiving compiled SWF...', 70);
            if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Compilation failed'); });
            return r.blob();
          })
          .then(function (blob) {
            updateProgress('Preparing download (' + formatBytes(blob.size) + ')...', 90);
            if (window.N2FProfiler) {
              window.N2FProfiler.stopTimer();
              window.N2FProfiler.size('output_swf', blob.size);
              window.N2FProfiler.endSession('swf-export-client');
            }
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = name + '.swf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            setTimeout(function () { URL.revokeObjectURL(url); }, 5000);
            _log.info('SWF export succeeded:', name + '.swf', formatBytes(blob.size));
            hideProgress();
            toast('Exported: ' + name + '.swf (' + formatBytes(blob.size) + ')');
          });
      }

      _captureToolBlob()
        .then(function (rawBlob) { return _sendCompileRequest(rawBlob); })
        .catch(function (err) {
          _log.warn('Tool save failed (' + err.message + '), compiling from disk');
          return _sendCompileRequest(null);
        })
        .catch(function (err) {
          hideProgress();
          if (window.N2FProfiler) window.N2FProfiler.endSession('swf-export-client');
          _log.error('SWF export failed:', err.message);
          _showExportError(err.message);
        });
      return;
    }

    // No project folder — require saving first so export can use the fast path.
    hideProgress();
    var defaultName = getProjectName() || 'untitled';
    _log.info('Export SWF: no project folder, prompting user to save first');
    _promptProjectName(defaultName).then(function (result) {
      if (!result) return; // user cancelled
      showProgress('Saving project...', 10);
      saveProjectAsN2D()
        .then(function (n2dBlob) {
          updateProgress('Creating project folder...', 35);
          var form = new FormData();
          form.append('n2d', n2dBlob, 'project.n2d');
          form.append('name', result.name);
          if (result.saveDir) form.append('saveDir', result.saveDir);
          return fetch(API_BASE + '/api/save-as-project', { method: 'POST', body: form });
        })
        .then(function (r) {
          if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Save failed'); });
          return r.json();
        })
        .then(function (saved) {
          _currentProjectDir = saved.projDir;
          _currentProjectName = result.name;
          var refreshBtn = document.getElementById('n2f-refresh-assets');
          if (refreshBtn) refreshBtn.removeAttribute('disabled');
          _log.info('Project saved, now exporting SWF from:', _currentProjectDir);
          hideProgress();
          // Re-invoke export — _currentProjectDir is now set, will use fast path
          onExportSWF();
        })
        .catch(function (err) {
          hideProgress();
          _log.error('Save before export failed:', err.message);
          _showExportError(err.message);
        });
    });
  }

  /**
   * Capture the raw tool save blob without any processing.
   * Returns the zlib-compressed blob straight from the tool's save pipeline.
   * This is fast because it avoids decompress/parse/merge/stringify/recompress.
   *
   * For large projects the tool's internal save may call encodeURIComponent on
   * Capture the current editor state as a lightweight zlib-compressed blob.
   *
   * Uses workspace.toJSON(true) — "light mode" — which serialises all layout
   * data (timelines, placeObjects, color transforms, new pencil shapes/recodes)
   * but OMITS bitmap/sound pixel buffers (the server already has those on disk).
   * This bypasses the tool's save pipeline entirely, avoiding:
   *   - The "Generating JSON" progress popup
   *   - The multi-second JSON.stringify of all bitmap pixel arrays
   *   - The zlib web-worker round-trip
   *
   * The resulting blob is zlib-compressed (deflate with zlib header) to match
   * what Python's zlib.decompress() expects on the server side.
   *
   * If the workspace API is unavailable, rejects so callers can fall back.
   */
  function _captureToolBlob() {
    return new Promise(function (resolve, reject) {
      var Util = window.Util;
      if (!Util || typeof Util.$currentWorkSpace !== 'function') {
        return reject(new Error('Next2D Util not available'));
      }
      var ws = Util.$currentWorkSpace();
      if (!ws || typeof ws.toJSON !== 'function') {
        return reject(new Error('No active workspace'));
      }

      // If a previous save left the progress dialog open/stuck, dismiss it
      // so that the progress overlay doesn't block the UI after export.
      if (Util.$saveProgress && Util.$saveProgress.active) {
        _log.warn('[N2F] dismissing stuck save-progress dialog before capture');
        try { Util.$saveProgress.end(); } catch (e) { /* ignore */ }
      }

      // Serialise: light=true → full layout data but no bitmap/sound pixel buffers.
      // The server preserves disk buffers via roundtrip_keys so nothing is lost.
      var jsonStr;
      try {
        jsonStr = ws.toJSON(true);
      } catch (ex) {
        _log.error('[N2F] workspace.toJSON(true) threw:', ex.message);
        return reject(ex);
      }

      // Compress: 'deflate' = zlib-wrapped DEFLATE understood by Python zlib.decompress()
      try {
        var bytes = new TextEncoder().encode(jsonStr);
        var cs = new CompressionStream('deflate');
        var writer = cs.writable.getWriter();
        writer.write(bytes);
        writer.close();
        new Response(cs.readable).arrayBuffer()
          .then(function (buf) {
            var blob = new Blob([buf], { type: 'application/octet-stream' });
            _log.info('[PERF] captured editor state (light): ' +
              (blob.size / 1024).toFixed(0) + 'KB  (json: ' +
              (jsonStr.length / 1024).toFixed(0) + 'KB)');
            resolve(blob);
          })
          .catch(reject);
      } catch (ex) {
        reject(ex);
      }
    });
  }

  /**
   * Capture the current project as an N2D blob with roundtrip data injected.
   * This triggers the tool's internal save pipeline, intercepts the result,
   * then decompresses → injects roundtrip fields → recompresses so the
   * Python compiler receives rawGlobalTags, scripts, etc.
   */
  function saveProjectAsN2D() {
    _log.debug('Capturing project as N2D blob');
    return new Promise(function (resolve, reject) {
      var anchor = document.getElementById('save-anchor');
      if (!anchor) return reject(new Error('save-anchor not found'));

      // Save the original click and override temporarily
      var origClick = anchor.click;
      var origHref = anchor.href;

      anchor.click = function () {
        // Intercept: grab the blob URL the tool just set
        var blobUrl = this.href;
        var _t0 = performance.now();
        _log.info('[PERF] tool internal save: ' + (_t0 - _tSave).toFixed(0) + 'ms');
        if (!blobUrl || !blobUrl.startsWith('blob:')) {
          anchor.click = origClick;
          return reject(new Error('No blob URL available'));
        }

        // Restore immediately
        anchor.click = origClick;

        fetch(blobUrl)
          .then(function (r) { return r.arrayBuffer(); })
          .then(function (buf) {
            _log.info('[PERF] fetch blob: ' + (performance.now() - _t0).toFixed(0) + 'ms, size=' + (buf.byteLength / 1048576).toFixed(1) + 'MB');
            var _t1 = performance.now();
            // Decompress the zlib-compressed N2D data
            var ds = new DecompressionStream('deflate');
            var writer = ds.writable.getWriter();
            writer.write(new Uint8Array(buf));
            writer.close();
            return new Response(ds.readable).text().then(function (text) {
              _log.info('[PERF] decompress: ' + (performance.now() - _t1).toFixed(0) + 'ms, size=' + (text.length / 1048576).toFixed(1) + 'MB');
              return text;
            });
          })
          .then(function (text) {
            var _t2 = performance.now();
            var json;
            try { json = JSON.parse(decodeURIComponent(text)); }
            catch (ex) { json = JSON.parse(text); }
            _log.info('[PERF] parse JSON: ' + (performance.now() - _t2).toFixed(0) + 'ms');

            // Inject roundtrip data (rawGlobalTags, scripts, etc.)
            var _t3 = performance.now();
            var panel = window.__n2d_as_panel;
            if (panel && typeof panel.injectRoundtripFields === 'function') {
              panel.injectRoundtripFields(json);
            } else {
              _log.warn('AS panel not available — export without roundtrip data');
            }
            _log.info('[PERF] injectRoundtripFields: ' + (performance.now() - _t3).toFixed(0) + 'ms');

            // Fallback: if critical fields still missing, re-parse stored N2D blob
            var blobSource = _importedN2DBlob
              ? Promise.resolve(_importedN2DBlob)
              : Promise.resolve(null); // IDB blob may be stale from a prior session; only use in-memory blob
            var _t4 = performance.now();
            var needsFallback = !json.rootTimelineDefIds
              || !json.scripts || json.scripts.length === 0
              || !json.rawGlobalTags || json.rawGlobalTags.length === 0;
            var fallback = needsFallback
              ? blobSource.then(function (blob) {
                  return blob ? _parseN2DBlob(blob) : null;
                })
              : Promise.resolve(null);

            return fallback.then(function (origJson) {
              _log.info('[PERF] fallback parse: ' + (performance.now() - _t4).toFixed(0) + 'ms, needed=' + needsFallback);
              if (origJson) {
                if (!json.rootTimelineDefIds && origJson.rootTimelineDefIds) {
                  json.rootTimelineDefIds = origJson.rootTimelineDefIds;
                  _log.info('Restored rootTimelineDefIds from stored blob:',
                    json.rootTimelineDefIds.length, 'ids');
                }
                if (json.swfVersion === undefined && origJson.swfVersion !== undefined) {
                  json.swfVersion = origJson.swfVersion;
                }
                // Restore scripts if missing
                if ((!json.scripts || json.scripts.length === 0) && origJson.scripts && origJson.scripts.length > 0) {
                  json.scripts = origJson.scripts;
                  _log.info('Restored scripts from blob:', json.scripts.length);
                }
                // Restore rawGlobalTags if missing
                if ((!json.rawGlobalTags || json.rawGlobalTags.length === 0) && origJson.rawGlobalTags && origJson.rawGlobalTags.length > 0) {
                  json.rawGlobalTags = origJson.rawGlobalTags;
                  _log.info('Restored rawGlobalTags from blob:', json.rawGlobalTags.length);
                }
                // Restore swfCompressed if missing
                if (json.swfCompressed === undefined && origJson.swfCompressed !== undefined) {
                  json.swfCompressed = origJson.swfCompressed;
                }
                // Restore critical library fields that may be missing
                if (Array.isArray(json.libraries) && Array.isArray(origJson.libraries)) {
                  var origMap = {};
                  origJson.libraries.forEach(function (lib) {
                    if (lib) origMap[lib.id] = lib;
                  });
                  var restored = 0;
                  var framesRestored = 0;
                  json.libraries.forEach(function (lib) {
                    if (!lib) return;
                    var orig = origMap[lib.id];
                    if (!orig) return;
                    // Restore fontData/buttonData/binaryDataBody if missing
                    ['fontData', 'fontTagType', 'fontAuxTags', 'buttonData',
                     'binaryDataBody', 'soundFormat', 'buttonAuxTags', 'swfCharId',
                     'rawBitmapFormat'
                    ].forEach(function (field) {
                      if (!lib[field] && orig[field]) lib[field] = orig[field];
                    });
                    if (orig.fontData || orig.buttonData || orig.binaryDataBody) restored++;
                    // Restore totalFrame for any container where tool returned 1 but original had more
                    if ((!lib.totalFrame || lib.totalFrame <= 1) && orig.totalFrame > 1) {
                      lib.totalFrame = orig.totalFrame;
                      framesRestored++;
                    }
                  });
                  if (restored > 0) {
                    _log.info('Restored critical fields from blob for', restored, 'libraries');
                  }
                  if (framesRestored > 0) {
                    _log.info('Restored totalFrame from blob for', framesRestored, 'libraries');
                  }
                }
              }

              // Diagnostic logging
              var libsTotal = Array.isArray(json.libraries) ? json.libraries.length : 0;
              _log.info('Injected roundtrip data:',
                libsTotal, 'libs,',
                'swfVersion=' + json.swfVersion,
                'rootTimeline=' + (json.rootTimelineDefIds || []).length + ' ids,',
                'rawGlobalTags=' + (json.rawGlobalTags || []).length,
                'scripts=' + (json.scripts || []).length,
                'scriptsModified=' + !!json.scriptsModified);

              // Re-encode and recompress
              var _t5 = performance.now();
              var jsonStr = JSON.stringify(json);
              _log.info('[PERF] JSON.stringify: ' + (performance.now() - _t5).toFixed(0) + 'ms, size=' + (jsonStr.length / 1048576).toFixed(1) + 'MB');
              var _t6 = performance.now();
              var arr = new TextEncoder().encode(jsonStr);
              _log.info('[PERF] TextEncoder: ' + (performance.now() - _t6).toFixed(0) + 'ms');

              var _t7 = performance.now();
              var cs = new CompressionStream('deflate');
              var cw = cs.writable.getWriter();
              cw.write(arr);
              cw.close();
              return new Response(cs.readable).arrayBuffer().then(function (buf) {
                _log.info('[PERF] compress: ' + (performance.now() - _t7).toFixed(0) + 'ms, size=' + (buf.byteLength / 1048576).toFixed(1) + 'MB');
                _log.info('[PERF] saveProjectAsN2D total: ' + (performance.now() - _t0).toFixed(0) + 'ms');
                return buf;
              });
            });
          })
          .then(function (compressed) {
            var blob = new Blob([new Uint8Array(compressed)], { type: 'application/octet-stream' });
            resolve(blob);
          })
          .catch(reject);
      };

      // Trigger the tool's save mechanism
      // The tool binds Ctrl+Shift+S to the tools-save element
      var _tSave = performance.now();
      var saveBtn = document.getElementById('tools-save');
      if (saveBtn) {
        saveBtn.click();
      } else {
        anchor.click = origClick;
        reject(new Error('tools-save button not found'));
      }
    });
  }

  function getProjectName() {
    // Prefer the stored project name from import
    if (_currentProjectName) return _currentProjectName;
    // Fall back to the tab area
    var tab = document.querySelector('#view-tab-area .active');
    if (tab) {
      var span = tab.querySelector('span');
      if (span && span.textContent) return span.textContent.trim();
    }
    return 'project';
  }

  /* ================================================================== */
  /*  N2D blob parsing helper (for export fallback)                      */
  /* ================================================================== */
  function _parseN2DBlobWithWorker(blob) {
    return blob.arrayBuffer().then(function (buf) {
      return new Promise(function (resolve, reject) {
        var worker;
        try {
          worker = new Worker('./assets/js/workers/swf-parse-worker.js');
        } catch (e) {
          _log.warn('[N2F] Parse worker creation failed, using fallback:', e.message);
          return resolve(_parseN2DBlobFallback(buf));
        }

        worker.onmessage = function (e) {
          var msg = e.data;
          worker.terminate();
          if (msg.type === 'parsed') {
            _log.info('[N2F] Parse Worker: decoded ' + msg.format + ' format');
            resolve(msg.data);
          } else if (msg.type === 'raw-blob') {
            // Legacy format — decode on main thread
            resolve(_parseN2DBlobFallback(msg.buffer));
          } else if (msg.type === 'error') {
            _log.warn('[N2F] Parse worker error, using fallback:', msg.message);
            resolve(_parseN2DBlobFallback(buf));
          }
        };

        worker.onerror = function (e) {
          worker.terminate();
          _log.warn('[N2F] Parse worker crashed, using fallback');
          resolve(_parseN2DBlobFallback(buf));
        };

        worker.postMessage({ type: 'parse', buffer: buf }, [buf]);
      });
    });
  }

  function _parseN2DBlobFallback(buf) {
    var bytes = new Uint8Array(buf);
    // Detect ZIP-based N2D format (PK magic bytes)
    if (bytes.length >= 4 && bytes[0] === 0x50 && bytes[1] === 0x4B) {
      return JSZip.loadAsync(buf).then(function (zip) {
        if (zip.file('project.msgpack')) {
          _log.info('[N2F] Loading MessagePack format (binary)');
          return zip.file('project.msgpack').async('uint8array').then(function (msgpackData) {
            if (typeof MessagePack !== 'undefined' && MessagePack.decode) {
              try {
                var decoded = MessagePack.decode(msgpackData);
                _log.info('[N2F] MessagePack decoded successfully');
                return decoded;
              } catch (e) {
                _log.error('[N2F] MessagePack decode failed:', e);
                return null;
              }
            } else {
              _log.error('[N2F] MessagePack library not loaded');
              return null;
            }
          });
        }
        _log.info('[N2F] Loading JSON format (legacy)');
        return zip.file('project.json').async('string');
      }).then(function (result) {
        if (typeof result === 'object') return result;
        try { return JSON.parse(result); }
        catch (e) { return null; }
      });
    }
    // Legacy zlib-compressed format
    var ds = new DecompressionStream('deflate');
    var writer = ds.writable.getWriter();
    writer.write(bytes);
    writer.close();
    return new Response(ds.readable).text().then(function (text) {
      try { return JSON.parse(decodeURIComponent(text)); }
      catch (e) { return JSON.parse(text); }
    });
  }

  function _parseN2DBlob(blob) {
    return _parseN2DBlobWithWorker(blob)
      .catch(function (err) {
        _log.warn('Failed to parse stored N2D blob:', err);
        return null;
      });
  }

  /* ================================================================== */
  /*  IDB storage for imported N2D blob                                  */
  /* ================================================================== */
  var _IDB_NAME = 'n2f-imported-blob';
  var _IDB_VERSION = 1;
  var _IDB_STORE = 'blobs';

  function _openBlobIDB() {
    return new Promise(function (resolve, reject) {
      var req = indexedDB.open(_IDB_NAME, _IDB_VERSION);
      req.onupgradeneeded = function (e) {
        e.target.result.createObjectStore(_IDB_STORE);
      };
      req.onsuccess = function (e) { resolve(e.target.result); };
      req.onerror = function () { reject(req.error); };
    });
  }

  function _saveImportedBlobToIDB(blob) {
    blob.arrayBuffer().then(function (buf) {
      _openBlobIDB().then(function (db) {
        var tx = db.transaction(_IDB_STORE, 'readwrite');
        tx.objectStore(_IDB_STORE).put(buf, 'importedN2D');
        tx.oncomplete = function () { db.close(); };
        tx.onerror = function () { db.close(); };
      }).catch(function (e) { _log.warn('IDB save error:', e); });
    });
  }

  function _loadImportedBlobFromIDB() {
    return _openBlobIDB().then(function (db) {
      return new Promise(function (resolve) {
        var tx = db.transaction(_IDB_STORE, 'readonly');
        var req = tx.objectStore(_IDB_STORE).get('importedN2D');
        req.onsuccess = function () {
          if (req.result) {
            var blob = new Blob([new Uint8Array(req.result)], { type: 'application/octet-stream' });
            _importedN2DBlob = blob;  // cache in memory
            _log.info('Loaded imported N2D blob from IDB:', blob.size, 'bytes');
            resolve(blob);
          } else {
            resolve(null);
          }
        };
        req.onerror = function () { resolve(null); };
        tx.oncomplete = function () { db.close(); };
      });
    }).catch(function () { return null; });
  }

  /* ================================================================== */
  /*  UI helpers                                                         */
  /* ================================================================== */
  function showProgress(msg, pct) {
    document.getElementById('n2f-overlay').style.display = 'block';
    document.getElementById('n2f-progress').style.display = 'block';
    document.getElementById('n2f-status').textContent = msg;
    _setProgressBar(pct);
  }

  function updateProgress(msg, pct) {
    document.getElementById('n2f-status').textContent = msg;
    _setProgressBar(pct);
  }

  function _setProgressBar(pct) {
    var bar = document.getElementById('n2f-progress-bar');
    var pctEl = document.getElementById('n2f-progress-pct');
    if (typeof pct === 'number' && pct >= 0) {
      bar.classList.remove('indeterminate');
      bar.style.width = Math.min(100, Math.max(0, pct)) + '%';
      pctEl.textContent = Math.round(pct) + '%';
    } else {
      bar.classList.add('indeterminate');
      bar.style.width = '';
      pctEl.textContent = '';
    }
  }

  function hideProgress() {
    document.getElementById('n2f-overlay').style.display = 'none';
    document.getElementById('n2f-progress').style.display = 'none';
  }

  /* ================================================================== */
  /*  Export error dialog                                                */
  /* ================================================================== */
  function _showExportError(message) {
    hideProgress();

    // Lazily create the overlay and dialog elements
    if (!document.getElementById('n2f-export-error')) {
      var ov = document.createElement('div');
      ov.id = 'n2f-export-error-overlay';
      document.body.appendChild(ov);

      var dlg = document.createElement('div');
      dlg.id = 'n2f-export-error';
      dlg.innerHTML =
        '<h3>\u274c Export Failed</h3>' +
        '<div class="n2f-err-msg" id="n2f-export-error-msg"></div>' +
        '<div class="n2f-err-hint" id="n2f-export-error-hint"></div>' +
        '<div class="n2f-err-buttons">' +
          '<button class="n2f-btn primary" id="n2f-export-error-dismiss">Dismiss</button>' +
          '<button class="n2f-btn" id="n2f-export-error-log">Open Server Log</button>' +
        '</div>';
      document.body.appendChild(dlg);

      document.getElementById('n2f-export-error-dismiss').addEventListener('click', _hideExportError);
      document.getElementById('n2f-export-error-overlay').addEventListener('click', _hideExportError);
      document.getElementById('n2f-export-error-log').addEventListener('click', function () {
        if (window.n2fElectron && window.n2fElectron.showServerConsole) {
          window.n2fElectron.showServerConsole();
        }
        _hideExportError();
      });
    }

    // Populate the message
    document.getElementById('n2f-export-error-msg').textContent = message;

    // Add a friendly hint for known errors
    var hint = '';
    if (message.indexOf('ObjectList') !== -1 || message.indexOf('mxmlc') !== -1) {
      hint = 'The AS3 compiler (mxmlc) encountered an error. This can happen when a project ' +
        'has many scripts and the compiler runs low on memory, or when a script contains ' +
        'syntax the compiler cannot parse. Check the Server Log for the full mxmlc output.';
    } else if (message.indexOf('Flex SDK not found') !== -1) {
      hint = 'The Flex SDK is required to compile AS3 scripts. Make sure flex_sdk/ is present ' +
        'in the app/ folder next to server.py.';
    }
    var hintEl = document.getElementById('n2f-export-error-hint');
    hintEl.textContent = hint;
    hintEl.style.display = hint ? '' : 'none';

    document.getElementById('n2f-export-error-overlay').style.display = 'block';
    document.getElementById('n2f-export-error').style.display = 'flex';
  }

  function _hideExportError() {
    var ov = document.getElementById('n2f-export-error-overlay');
    var dlg = document.getElementById('n2f-export-error');
    if (ov) ov.style.display = 'none';
    if (dlg) dlg.style.display = 'none';
  }

  function toast(msg, isErr) {
    var old = document.getElementById('n2f-toast');
    if (old) old.remove();
    var el = document.createElement('div');
    el.id = 'n2f-toast';
    el.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);' +
      'z-index:330001;max-width:500px;padding:12px 24px;border-radius:6px;' +
      'font:13px/1.5 Arial,sans-serif;color:#fff;' +
      'box-shadow:0 4px 16px rgba(0,0,0,.4);transition:opacity .3s;' +
      'background:' + (isErr ? '#e74c3c' : '#2ecc71');
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(function () {
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 300);
    }, isErr ? 6000 : 4000);

    // On error, open server console so user can see what went wrong
    if (isErr && window.n2fElectron && window.n2fElectron.showServerConsole) {
      window.n2fElectron.showServerConsole();
    }
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  /** Send a log message to the server so it prints in the terminal. */
  function _serverLog(level, message) {
    try {
      fetch(API_BASE + '/api/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level: level, message: message })
      }).catch(function () { /* ignore */ });
    } catch (e) { /* ignore */ }
  }

  /* ================================================================== */
  /*  Autosave                                                           */
  /* ================================================================== */
  function _startAutosave() {
    if (_autosaveTimer) return;
    _autosaveTimer = setInterval(_doAutosave, 60000);
    _log.info('Autosave started (every 60 s)');
  }

  function _stopAutosave() {
    if (_autosaveTimer) { clearInterval(_autosaveTimer); _autosaveTimer = null; }
  }

  function _doAutosave() {
    if (!_currentProjectDir || !_isDirty) return;
    var prog = document.getElementById('n2f-progress');
    if (prog && prog.style.display !== 'none') return; // busy

    // Build the project object on the main thread (plain JS objects — no stringify yet)
    var Util = window.Util;
    var ws = Util && Util.$currentWorkSpace && Util.$currentWorkSpace();
    if (!ws || !ws._$project) {
      _log.warn('Autosave: no active workspace, skipping');
      return;
    }

    var projectObj;
    try {
      var projectData = ws._$project.toObject(false);
      var uiData = ws._$uiState ? ws._$uiState.toObject() : {};
      projectObj = Object.assign({}, projectData, { setting: uiData });
    } catch (e) {
      _log.warn('Autosave: failed to build project object:', e.message);
      return;
    }

    // Inject roundtrip fields (scripts, rawGlobalTags, SWF metadata) on main thread
    // so live editor state is captured before passing to the worker
    var panel = window.__n2d_as_panel;
    if (panel && typeof panel.injectRoundtripFields === 'function') {
      try { panel.injectRoundtripFields(projectObj); } catch (e) { /* non-fatal */ }
    }

    _log.info('Autosave: serializing project in worker...');

    // Lazily create a persistent worker for serialize + compress
    if (!_autosaveWorker) {
      _autosaveWorker = new Worker('./assets/js/workers/autosave-worker.js');
      _autosaveWorker.onerror = function (e) {
        _log.warn('Autosave worker error:', e.message);
      };
    }

    _autosaveWorker.onmessage = function (e) {
      var msg = e.data;
      if (msg.type === 'error') {
        _log.warn('Autosave worker serialization error:', msg.message);
        return;
      }
      var blob = new Blob([msg.buffer], { type: 'application/octet-stream' });
      var form = new FormData();
      form.append('n2d', blob, 'project.n2d');
      fetch(API_BASE + '/api/save-project', { method: 'POST', body: form })
        .then(function (r) {
          if (!r.ok) throw new Error('Server rejected autosave');
          return r.json();
        })
        .then(function () {
          _markClean();
          _addRecentProject(_currentProjectDir, _currentProjectName);
          toast('Autosaved \u2713');
          _log.info('Autosave: done');
        })
        .catch(function (e) { _log.warn('Autosave failed:', e.message); });
    };

    // Transfer the plain object to the worker — JSON.stringify + deflate runs off-thread
    _autosaveWorker.postMessage({ type: 'serialize', obj: projectObj });
  }

  /* ================================================================== */
  /*  Welcome screen                                                     */
  /* ================================================================== */
  function _showWelcomeScreen() {
    var el = document.getElementById('n2f-welcome');
    if (!el) return;
    el.style.display = 'flex';
    // Hide the close button when there is no open project to return to.
    var closeBtn = document.getElementById('n2f-welcome-close');
    if (closeBtn) {
      closeBtn.style.display = (window.Util && window.Util.$workSpaces && window.Util.$workSpaces.length > 0) ? '' : 'none';
    }
    _loadRecents().then(function () { _renderRecentLists(); });
  }

  function _hideWelcomeScreen() {
    var el = document.getElementById('n2f-welcome');
    if (el) el.style.display = 'none';
  }

  /**
   * Delay hiding the welcome screen until a new tab appears in the editor,
   * so the user doesn't briefly see the old (tab-less) workspace.
   * Falls back to hiding after ~5 s if no tab appears.
   */
  function _hideWelcomeWhenTabReady() {
    var el = document.getElementById('n2f-welcome');
    if (!el || el.style.display === 'none') return; // already hidden
    var activeEl = document.querySelector('#view-tab-area .active[data-tab-id]');
    var oldTabId = activeEl ? activeEl.dataset.tabId : null;
    var attempts = 0;
    function poll() {
      var cur = document.querySelector('#view-tab-area .active[data-tab-id]');
      var curId = cur ? cur.dataset.tabId : null;
      if (curId !== null && curId !== oldTabId) {
        _hideWelcomeScreen();
      } else if (++attempts < 50) {
        setTimeout(poll, 100);
      } else {
        _hideWelcomeScreen(); // fallback after ~5 s
      }
    }
    setTimeout(poll, 50);
  }

  /* ================================================================== */
  /*  Recents                                                            */
  /* ================================================================== */
  function _loadRecents() {
    return fetch(API_BASE + '/api/recents')
      .then(function (r) { return r.ok ? r.json() : { projects: [], imports: [] }; })
      .then(function (data) {
        _recentProjects = data.projects || [];
        _recentImports = data.imports || [];
      })
      .catch(function () { _recentProjects = []; _recentImports = []; });
  }

  function _addRecentProject(projDir, name) {
    if (!projDir) return;
    fetch(API_BASE + '/api/add-recent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: 'project', path: projDir, name: name || projDir.split(/[\\/]/).pop() })
    }).then(function () {
      return _loadRecents().then(_renderRecentLists);
    }).catch(function () {});
  }

  function _addRecentImport(filePath, name) {
    if (!filePath) return;
    fetch(API_BASE + '/api/add-recent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: 'import', path: filePath, name: name || filePath.split(/[\\/]/).pop() })
    }).then(function () {
      return _loadRecents().then(_renderRecentLists);
    }).catch(function () {});
  }

  function _renderRecentLists() {
    _renderRecentList('n2f-recent-projects', _recentProjects, function (item) {
      _openRecentProject(item.path, item.name);
    });
    _renderRecentList('n2f-recent-imports', _recentImports, function (item) {
      _importRecentSWF(item.path, item.name);
    });
  }

  function _renderRecentList(containerId, items, onClick) {
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    if (!items || !items.length) {
      container.innerHTML = '<div class="n2f-recent-empty">No recent files</div>';
      return;
    }
    items.forEach(function (item) {
      var div = document.createElement('div');
      div.className = 'n2f-recent-item';
      div.title = item.path;
      var nameText = _escapeHtml(item.name || item.path.split(/[\\/]/).pop());
      var pathText = _escapeHtml(item.path);

      var info = document.createElement('div');
      info.className = 'n2f-ri-info';
      info.innerHTML =
        '<div class="n2f-ri-name">' + nameText + '</div>' +
        '<div class="n2f-ri-path">' + pathText + '</div>';
      info.addEventListener('click', function () { onClick(item); });

      var actions = document.createElement('div');
      actions.className = 'n2f-ri-actions';

      var revealBtn = document.createElement('button');
      revealBtn.className = 'n2f-ri-btn';
      revealBtn.title = 'Reveal in Explorer';
      revealBtn.textContent = '\ud83d\udcc2';
      revealBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        _revealPath(item.path);
      });

      var removeBtn = document.createElement('button');
      removeBtn.className = 'n2f-ri-btn';
      removeBtn.title = 'Remove from list';
      removeBtn.textContent = '\u2715';
      removeBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        _removeRecentItem(containerId, item.path);
      });

      actions.appendChild(revealBtn);
      actions.appendChild(removeBtn);
      div.appendChild(info);
      div.appendChild(actions);
      container.appendChild(div);
    });
  }

  function _revealPath(path) {
    if (window.n2fElectron && window.n2fElectron.showItemInFolder) {
      window.n2fElectron.showItemInFolder(path);
    } else {
      fetch(API_BASE + '/api/reveal-path', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
      }).catch(function () {});
    }
  }

  function _removeRecentItem(containerId, path) {
    var category = containerId === 'n2f-recent-projects' ? 'project' : 'import';
    fetch(API_BASE + '/api/remove-recent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: category, path: path })
    })
      .then(function () { return _loadRecents(); })
      .then(function () { _renderRecentLists(); })
      .catch(function () {});
  }

  function _escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function _openRecentProject(projDir, name) {
    showProgress('Opening: ' + name + '...', 10);
    fetch(API_BASE + '/api/open-project-path', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ projDir: projDir, lazy: true })
    })
      .then(function (r) {
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Open failed'); });
        var rname = r.headers.get('X-N2D-Name') || name;
        var libs = r.headers.get('X-N2D-Libraries') || '?';
        var projDirHdr = r.headers.get('X-Project-Dir') || projDir;
        var fontsHeader = r.headers.get('X-N2D-Fonts') || '';
        var fonts = null;
        if (fontsHeader) { try { fonts = JSON.parse(fontsHeader); } catch(e) {} }
        updateProgress('Downloading project (' + libs + ' libraries)...', 50);
        return r.blob().then(function (b) { return { blob: b, name: rname, libs: libs, projDir: projDirHdr, fonts: fonts }; });
      })
      .then(function (result) {
        _currentProjectDir = result.projDir;
        _currentProjectName = result.name;
        _setDocumentTitle(result.name, false);
        _markClean();
        _startAutosave();
        _startDirtyPoll();
        _addRecentProject(result.projDir, result.name);
        var refreshBtn = document.getElementById('n2f-refresh-assets');
        if (refreshBtn) refreshBtn.disabled = false;
        _registerEmbeddedFonts(result.fonts);
        _importedN2DBlob = result.blob.slice(0);
        _saveImportedBlobToIDB(_importedN2DBlob);
        window.__n2f_loading_from_welcome = true;
        _feedN2DToTool(result.blob, result.name);
        hideProgress();
        _hideWelcomeWhenTabReady();
        toast('Opened: ' + result.name + ' (' + result.libs + ' libraries)');
        // Start background hydration of lazy library stubs
        _startBackgroundHydration(result.libs);
      })
      .catch(function (err) {
        hideProgress();
        _hideWelcomeScreen();
        _log.error('Open recent project failed:', err.message);
        toast('Open failed: ' + err.message, true);
      });
  }

  function _importRecentSWF(swfPath, name) {
    _log.info('Re-importing SWF:', name, swfPath);
    _importSWFByPath(swfPath);
  }

  /* ================================================================== */
  /*  New Project                                                        */
  /* ================================================================== */
  function _onNewProject() {
    _promptProjectName('untitled').then(function (result) {
      if (!result) return;
      var projName = result.name;
      showProgress('Creating project: ' + projName + '...', 20);
      fetch(API_BASE + '/api/new-project', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: projName, saveFolder: true })
      })
        .then(function (r) {
          if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Create failed'); });
          var rname = r.headers.get('X-N2D-Name') || projName;
          var dir = r.headers.get('X-Project-Dir') || '';
          updateProgress('Loading blank project...', 70);
          return r.blob().then(function (b) { return { blob: b, name: rname, projDir: dir }; });
        })
        .then(function (res) {
          _currentProjectDir = res.projDir;
          _currentProjectName = res.name;
          _setDocumentTitle(res.name, false);
          _markClean();
          _startAutosave();
          _startDirtyPoll();
          if (res.projDir) _addRecentProject(res.projDir, res.name);
          var refreshBtn = document.getElementById('n2f-refresh-assets');
          if (refreshBtn) refreshBtn.disabled = false;
          window.__n2f_loading_from_welcome = true;
          _feedN2DToTool(res.blob, res.name);
          hideProgress();
          _hideWelcomeWhenTabReady();
          toast('New project created: ' + res.name);
        })
        .catch(function (err) {
          hideProgress();
          _hideWelcomeScreen();
          _log.error('New project failed:', err.message);
          toast('New project failed: ' + err.message, true);
        });
    });
  }

  /* ================================================================== */
  /*  Import Asset (image/audio into project folder)                    */
  /* ================================================================== */
  function onImportAsset() {
    if (!_currentProjectDir) {
      toast('Save or open a project first, then import assets.', true);
      return;
    }
    document.getElementById('n2f-asset-input').click();
  }

  function onAssetFileSelected(e) {
    var files = Array.prototype.slice.call(e.target.files);
    if (!files.length) return;
    e.target.value = '';
    _importAssetFiles(files);
  }

  function _importAssetFiles(files) {
    if (!_currentProjectDir) { toast('No active project folder.', true); return; }
    showProgress('Importing ' + files.length + ' asset(s)...', 10);
    var form = new FormData();
    files.forEach(function (f) { form.append('files', f, f.name); });
    fetch(API_BASE + '/api/import-asset', { method: 'POST', body: form })
      .then(function (r) {
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Import failed'); });
        return r.json();
      })
      .then(function (result) {
        hideProgress();
        toast('Imported ' + result.count + ' asset(s) \u2192 ' + result.folder);
        _log.info('Assets imported:', result.files);
      })
      .catch(function (err) {
        hideProgress();
        _log.error('Asset import failed:', err.message);
        toast('Asset import failed: ' + err.message, true);
      });
  }

  /* ================================================================== */
  /*  Boot                                                               */
  /* ================================================================== */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
