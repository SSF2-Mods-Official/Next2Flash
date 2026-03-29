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

  var _log = window.__N2F_DEBUG ? window.__N2F_DEBUG.logger('Integration') : { trace:function(){},debug:function(){},info:function(){},warn:function(){},error:function(){},time:function(){},timeEnd:function(){},group:function(){},groupEnd:function(){} };

  var API_BASE = '';  // same origin when served by Next2Flash server
  var serverOnline = false;
  var _importedN2DBlob = null;  // stored for fallback during export

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
      '#n2f-toolbar { display:flex; align-items:center; gap:6px; padding:4px 10px;',
      '  position:fixed; top:0; right:calc(var(--controller-width, 360px) + 14px); z-index:100000;',
      '  background:rgba(30,30,30,.92); border:1px solid #444;',
      '  border-top:none; border-radius:0 0 6px 6px;',
      '  box-shadow:0 2px 12px rgba(0,0,0,.4); }',
      '#n2f-toolbar .n2f-btn { display:inline-flex; align-items:center; gap:4px;',
      '  padding:4px 10px; border:1px solid #555; border-radius:4px; cursor:pointer;',
      '  font:bold 11px/1.4 Arial,sans-serif; color:#ccc; background:#333;',
      '  transition:background .15s, border-color .15s; white-space:nowrap; }',
      '#n2f-toolbar .n2f-btn:hover { background:#444; border-color:#7af; }',
      '#n2f-toolbar .n2f-btn.primary { background:#2a6; border-color:#2a6; color:#fff; }',
      '#n2f-toolbar .n2f-btn.primary:hover { background:#3b7; border-color:#3b7; }',
      '#n2f-toolbar .n2f-dot { width:8px; height:8px; border-radius:50%; background:#2ecc71;',
      '  display:inline-block; margin-right:2px; }',
      '#n2f-toolbar .n2f-label { font:11px/1.4 Arial,sans-serif; color:#888; }',
      '#n2f-progress { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);',
      '  z-index:200000; background:#222; color:#ccc; border:1px solid #555; border-radius:8px;',
      '  padding:24px 32px; font:13px/1.6 Arial,sans-serif; text-align:center;',
      '  box-shadow:0 8px 32px rgba(0,0,0,.5); min-width:280px; }',
      '#n2f-progress .n2f-spinner { display:inline-block; width:24px; height:24px;',
      '  border:3px solid #555; border-top-color:#7af; border-radius:50%;',
      '  animation:n2f-spin .8s linear infinite; margin-bottom:8px; }',
      '@keyframes n2f-spin { to { transform:rotate(360deg); } }',
      '#n2f-overlay { display:none; position:fixed; top:0; left:0; right:0; bottom:0;',
      '  z-index:199999; background:rgba(0,0,0,.4); }',
    ].join('\n');
    document.head.appendChild(style);

    // Create toolbar
    var toolbar = document.createElement('div');
    toolbar.id = 'n2f-toolbar';
    toolbar.innerHTML =
      '<span class="n2f-dot"></span>' +
      '<span class="n2f-label">Next2Flash</span>' +
      '<button class="n2f-btn" id="n2f-import-swf" title="Import SWF into editable project folder (PNG/WAV/AS)">' +
        '\u{1F4E5} Import SWF</button>' +
      '<button class="n2f-btn" id="n2f-open-project" title="Open an N2D file (can be in a project folder with assets)">' +
        '\u{1F4C2} Import Project</button>' +
      '<button class="n2f-btn" id="n2f-refresh-assets" title="Refresh external assets from project folder" disabled>' +
        '\u{1F504} Refresh Assets</button>' +
      '<button class="n2f-btn primary" id="n2f-export-swf" title="Export current project as SWF">' +
        '\u{1F4E4} Export SWF</button>' +
      '<input type="file" id="n2f-swf-input" accept=".swf,.ssf" style="display:none">' +
      '<input type="file" id="n2f-n2d-input" accept=".n2d" style="display:none">';

    // Insert as fixed-position toolbar at top of page
    document.body.appendChild(toolbar);

    // Overlay + progress dialog
    var overlay = document.createElement('div');
    overlay.id = 'n2f-overlay';
    document.body.appendChild(overlay);

    var progress = document.createElement('div');
    progress.id = 'n2f-progress';
    progress.innerHTML = '<div class="n2f-spinner"></div><div id="n2f-status">Processing...</div>';
    document.body.appendChild(progress);

    // Wire events
    document.getElementById('n2f-import-swf').addEventListener('click', onImportSWF);
    document.getElementById('n2f-open-project').addEventListener('click', onOpenProject);
    document.getElementById('n2f-refresh-assets').addEventListener('click', onRefreshAssets);
    document.getElementById('n2f-export-swf').addEventListener('click', onExportSWF);
    document.getElementById('n2f-swf-input').addEventListener('change', onSWFFileSelected);
    document.getElementById('n2f-n2d-input').addEventListener('change', onN2DFileSelected);
  }

  /* ================================================================== */
  /*  Import SWF                                                         */
  /* ================================================================== */
  function onImportSWF() {
    _log.debug('Import SWF button clicked');
    document.getElementById('n2f-swf-input').click();
  }

  function onSWFFileSelected(e) {
    var file = e.target.files[0];
    if (!file) return;
    _log.info('SWF file selected:', file.name, formatBytes(file.size));
    e.target.value = '';  // reset for re-selecting same file

    showProgress('Importing SWF into project folder...\n' + file.name + ' (' + formatBytes(file.size) + ')');

    var form = new FormData();
    form.append('file', file);

    fetch(API_BASE + '/api/swf-to-project', { method: 'POST', body: form })
      .then(function (r) {
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Server error'); });
        var name = r.headers.get('X-N2D-Name') || file.name.replace('.swf', '');
        var libs = r.headers.get('X-N2D-Libraries') || '?';
        var scripts = r.headers.get('X-N2D-Scripts') || '0';
        var projDir = r.headers.get('X-Project-Dir') || '';
        return r.blob().then(function (blob) {
          return { blob: blob, name: name, libs: libs, scripts: scripts, projDir: projDir };
        });
      })
      .then(function (result) {
        hideProgress();
        _currentProjectDir = result.projDir;
        _log.info('Project created at:', _currentProjectDir);

        // Enable refresh button
        var refreshBtn = document.getElementById('n2f-refresh-assets');
        if (refreshBtn) refreshBtn.disabled = false;

        // Store and load into tool
        _importedN2DBlob = result.blob.slice(0);
        _saveImportedBlobToIDB(_importedN2DBlob);

        _feedN2DToTool(result.blob, result.name);
        toast('Project created: ' + result.name + ' (' + result.libs + ' libraries, ' + result.scripts + ' scripts)\nFolder: ' + _currentProjectDir);
      })
      .catch(function (err) {
        hideProgress();
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
    showProgress('Loading N2D file...\n' + file.name + ' (' + formatBytes(file.size) + ')');
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
        return r.blob().then(function (b) {
          console.log('[N2F] received blob size:', b.size);
          return { blob: b, name: name, libs: libs, projDir: projDir };
        });
      })
      .then(function (result) {
        hideProgress();
        if (result.projDir) {
          _currentProjectDir = result.projDir;
          console.log('[N2F] project dir set to:', _currentProjectDir);
          _log.info('Opened project at:', _currentProjectDir);
          var refreshBtn = document.getElementById('n2f-refresh-assets');
          if (refreshBtn) refreshBtn.disabled = false;
        } else {
          console.warn('[N2F] No X-Project-Dir returned — bitmaps were NOT overlaid by server');
        }

        _importedN2DBlob = result.blob.slice(0);
        _saveImportedBlobToIDB(_importedN2DBlob);

        _feedN2DToTool(result.blob, result.name);

        if (onSuccess) onSuccess(result);
        else toast('Opened: ' + result.name + ' (' + result.libs + ' libraries)');
      })
      .catch(function (err) {
        hideProgress();
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

    // Get the stored blob (memory first, then IDB)
    var blobPromise = _importedN2DBlob
      ? Promise.resolve(_importedN2DBlob)
      : _loadImportedBlobFromIDB();

    blobPromise.then(function (storedBlob) {
      if (!storedBlob) {
        toast('No stored project file — please use Import Project first.', true);
        return;
      }

      // Remember which in-app tab is currently active
      var oldTabEl = document.querySelector('#view-tab-area .active[data-tab-id]');
      var oldTabId = oldTabEl ? oldTabEl.dataset.tabId : null;

      // Open a new blank in-app tab so the load goes into it
      var addTabBtn = document.getElementById('view-tab-add');
      if (addTabBtn) addTabBtn.click();

      showProgress('Refreshing project from server...');

      // Re-run the exact same open-project pipeline with the stored file
      _doOpenProjectBlob(storedBlob, _currentProjectDir.split(/[\\/]/).pop() + '.n2d', function (result) {
        // Close the old tab, bypassing the unsaved-data confirm dialog
        if (oldTabId !== null) {
          var closeBtn = document.getElementById('tab-delete-id-' + oldTabId);
          if (closeBtn) {
            var origConfirm = window.confirm;
            window.confirm = function () { return true; };
            try { closeBtn.click(); } finally { window.confirm = origConfirm; }
          }
        }
        toast('Refreshed: ' + result.name + ' (' + result.libs + ' libraries)');
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
  /*  Export SWF                                                         */
  /* ================================================================== */
  function onExportSWF() {
    _log.info('Export SWF requested');
    showProgress('Preparing project for SWF export...');

    var name = getProjectName() || 'output';

    // When a project folder is active, compile directly from the project
    // folder's project.n2d which has externalFile references for scripts,
    // bitmaps and sounds.  This ensures external edits are picked up.
    if (_currentProjectDir) {
      _log.info('Project folder active — compiling from project folder');
      updateProgress('Compiling SWF from project folder...');

      var form = new FormData();
      form.append('fromProject', 'true');

      fetch(API_BASE + '/api/n2d-to-swf', { method: 'POST', body: form })
        .then(function (r) {
          if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Compilation failed'); });
          return r.blob();
        })
        .then(function (blob) {
          hideProgress();
          var url = URL.createObjectURL(blob);
          var a = document.createElement('a');
          a.href = url;
          a.download = name + '.swf';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          setTimeout(function () { URL.revokeObjectURL(url); }, 5000);
          _log.info('SWF export succeeded:', name + '.swf', formatBytes(blob.size));
          toast('Exported: ' + name + '.swf (' + formatBytes(blob.size) + ')');
        })
        .catch(function (err) {
          hideProgress();
          _log.error('SWF export failed:', err.message);
          toast('Export failed: ' + err.message, true);
        });
      return;
    }

    // No project folder — use the legacy browser-blob export pipeline
    saveProjectAsN2D()
      .then(function (n2dBlob) {
        updateProgress('Compiling N2D to SWF...');

        var form = new FormData();
        form.append('file', n2dBlob, name + '.n2d');

        return fetch(API_BASE + '/api/n2d-to-swf', { method: 'POST', body: form })
          .then(function (r) {
            if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Compilation failed'); });
            return r.blob().then(function (blob) { return { blob: blob, name: name }; });
          });
      })
      .then(function (result) {
        hideProgress();

        // Download the SWF
        var url = URL.createObjectURL(result.blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = result.name + '.swf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 5000);

        _log.info('SWF export succeeded:', result.name + '.swf', formatBytes(result.blob.size));
        toast('Exported: ' + result.name + '.swf (' + formatBytes(result.blob.size) + ')');
      })
      .catch(function (err) {
        hideProgress();
        _log.error('SWF export failed:', err.message);
        toast('Export failed: ' + err.message, true);
      });
  }

  /**
   * Capture the current project as an N2D blob with roundtrip data injected.
   * This triggers the tool's internal save pipeline, intercepts the result,
   * then decompresses → injects roundtrip fields → recompresses so the
   * Python compiler receives rawTagBody, rawGlobalTags, scripts, etc.
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
        if (!blobUrl || !blobUrl.startsWith('blob:')) {
          anchor.click = origClick;
          return reject(new Error('No blob URL available'));
        }

        // Restore immediately
        anchor.click = origClick;

        fetch(blobUrl)
          .then(function (r) { return r.arrayBuffer(); })
          .then(function (buf) {
            // Decompress the zlib-compressed N2D data
            var ds = new DecompressionStream('deflate');
            var writer = ds.writable.getWriter();
            writer.write(new Uint8Array(buf));
            writer.close();
            return new Response(ds.readable).text();
          })
          .then(function (text) {
            var json;
            try { json = JSON.parse(decodeURIComponent(text)); }
            catch (ex) { json = JSON.parse(text); }

            // Inject roundtrip data (rawTagBody, rawGlobalTags, scripts, etc.)
            var panel = window.__n2d_as_panel;
            if (panel && typeof panel.injectRoundtripFields === 'function') {
              panel.injectRoundtripFields(json);
            } else {
              _log.warn('AS panel not available — export without roundtrip data');
            }

            // Fallback: if critical fields still missing, re-parse stored N2D blob
            var blobSource = _importedN2DBlob
              ? Promise.resolve(_importedN2DBlob)
              : _loadImportedBlobFromIDB();
            var needsFallback = !json.rootTimelineDefIds
              || !json.scripts || json.scripts.length === 0
              || !json.rawGlobalTags || json.rawGlobalTags.length === 0;
            var fallback = needsFallback
              ? blobSource.then(function (blob) {
                  return blob ? _parseN2DBlob(blob) : null;
                })
              : Promise.resolve(null);

            return fallback.then(function (origJson) {
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
                // Restore rawTagBody for libraries that are missing it
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
                    if (!lib.rawTagBody && orig.rawTagBody) {
                      lib.rawTagBody = orig.rawTagBody;
                      if (orig.rawTagType !== undefined) lib.rawTagType = orig.rawTagType;
                      if (orig.swfCharId !== undefined && !lib.swfCharId) lib.swfCharId = orig.swfCharId;
                      if (orig.fontAuxTags && !lib.fontAuxTags) lib.fontAuxTags = orig.fontAuxTags;
                      restored++;
                    }
                    // Restore totalFrame for any container where tool returned 1 but original had more
                    if ((!lib.totalFrame || lib.totalFrame <= 1) && orig.totalFrame > 1) {
                      lib.totalFrame = orig.totalFrame;
                      framesRestored++;
                    }
                  });
                  if (restored > 0) {
                    _log.info('Restored rawTagBody from blob for', restored, 'libraries');
                  }
                  if (framesRestored > 0) {
                    _log.info('Restored totalFrame from blob for', framesRestored, 'libraries');
                  }
                }
              }

              // Diagnostic logging
              var libsWithRaw = 0, libsTotal = 0;
              if (Array.isArray(json.libraries)) {
                libsTotal = json.libraries.length;
                json.libraries.forEach(function (lib) {
                  if (lib && lib.rawTagBody) libsWithRaw++;
                });
              }
              _log.info('Injected roundtrip data:',
                libsWithRaw + '/' + libsTotal, 'libs have rawTagBody,',
                'swfVersion=' + json.swfVersion,
                'rootTimeline=' + (json.rootTimelineDefIds || []).length + ' ids,',
                'rawGlobalTags=' + (json.rawGlobalTags || []).length,
                'scripts=' + (json.scripts || []).length,
                'scriptsModified=' + !!json.scriptsModified);

              // Re-encode and recompress
              var encoded = encodeURIComponent(JSON.stringify(json));
              var arr = new Uint8Array(encoded.length);
              for (var i = 0; i < encoded.length; i++) arr[i] = encoded.charCodeAt(i);

              var cs = new CompressionStream('deflate');
              var cw = cs.writable.getWriter();
              cw.write(arr);
              cw.close();
              return new Response(cs.readable).arrayBuffer();
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
    // Try to get from the tab area
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
  function _parseN2DBlob(blob) {
    return blob.arrayBuffer()
      .then(function (buf) {
        var bytes = new Uint8Array(buf);
        // Detect ZIP-based N2D format (PK magic bytes)
        if (bytes.length >= 4 && bytes[0] === 0x50 && bytes[1] === 0x4B) {
          return JSZip.loadAsync(buf).then(function (zip) {
            return zip.file('project.json').async('string');
          }).then(function (text) {
            try { return JSON.parse(text); }
            catch (e) { return null; }
          });
        }
        // Legacy zlib-compressed format
        var ds = new DecompressionStream('deflate');
        var writer = ds.writable.getWriter();
        writer.write(bytes);
        writer.close();
        return new Response(ds.readable).text();
      })
      .then(function (result) {
        if (typeof result === 'object') return result;  // already parsed from ZIP path
        try { return JSON.parse(decodeURIComponent(result)); }
        catch (e) { return JSON.parse(result); }
      })
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
  function showProgress(msg) {
    document.getElementById('n2f-overlay').style.display = 'block';
    document.getElementById('n2f-progress').style.display = 'block';
    document.getElementById('n2f-status').textContent = msg;
  }

  function updateProgress(msg) {
    document.getElementById('n2f-status').textContent = msg;
  }

  function hideProgress() {
    document.getElementById('n2f-overlay').style.display = 'none';
    document.getElementById('n2f-progress').style.display = 'none';
  }

  function toast(msg, isErr) {
    var old = document.getElementById('n2f-toast');
    if (old) old.remove();
    var el = document.createElement('div');
    el.id = 'n2f-toast';
    el.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);' +
      'z-index:200001;max-width:500px;padding:12px 24px;border-radius:6px;' +
      'font:13px/1.5 Arial,sans-serif;color:#fff;' +
      'box-shadow:0 4px 16px rgba(0,0,0,.4);transition:opacity .3s;' +
      'background:' + (isErr ? '#e74c3c' : '#2ecc71');
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(function () {
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 300);
    }, isErr ? 6000 : 4000);
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
  /*  Boot                                                               */
  /* ================================================================== */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
