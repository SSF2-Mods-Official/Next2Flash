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
      '<div class="n2f-header"><span class="n2f-dot"></span>' +
      '<span class="n2f-label">Next2Flash</span></div>' +
      '<button class="n2f-btn" id="n2f-import-swf" title="Import SWF into editable project folder (PNG/WAV/AS)">' +
        '\u{1F4E5} Import SWF</button>' +
      '<button class="n2f-btn" id="n2f-open-project" title="Open an N2D file (can be in a project folder with assets)">' +
        '\u{1F4C2} Import Project</button>' +
      '<button class="n2f-btn" id="n2f-refresh-assets" title="Refresh external assets from project folder" disabled>' +
        '\u{1F504} Refresh Assets</button>' +
      '<button class="n2f-btn" id="n2f-save-project" title="Save current project to server folder" disabled>' +
        '\u{1F4BE} Save Project</button>' +
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
    document.getElementById('n2f-save-project').addEventListener('click', onSaveProject);
    document.getElementById('n2f-export-swf').addEventListener('click', onExportSWF);
    document.getElementById('n2f-swf-input').addEventListener('change', onSWFFileSelected);
    document.getElementById('n2f-n2d-input').addEventListener('change', onN2DFileSelected);

    // Wire Electron menu events
    if (window.n2fElectron) {
      window.n2fElectron.onMenuSave(onSaveProject);
      window.n2fElectron.onMenuExportSWF(onExportSWF);
      window.n2fElectron.onImportSWF(function (swfPath) { _importSWFByPath(swfPath); });
      _log.info('Electron bridge detected — native menu/dialogs active');
    }
  }

  /* ================================================================== */
  /*  Import SWF                                                         */
  /* ================================================================== */
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
    _log.info('Importing SWF by path:', swfPath);
    showProgress('Importing SWF...\n' + fileName);

    fetch(API_BASE + '/api/import-swf-path', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ swfPath: swfPath, lazy: true }),
    })
      .then(function (r) {
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Server error'); });
        var name = r.headers.get('X-N2D-Name') || fileName.replace(/\.\w+$/, '');
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

        var refreshBtn = document.getElementById('n2f-refresh-assets');
        if (refreshBtn) refreshBtn.disabled = false;
        var saveBtn = document.getElementById('n2f-save-project');
        if (saveBtn) saveBtn.disabled = false;

        _importedN2DBlob = result.blob.slice(0);
        _saveImportedBlobToIDB(_importedN2DBlob);
        _feedN2DToTool(result.blob, result.name);

        toast('Project created: ' + result.name + ' (' + result.libs + ' libraries, ' + result.scripts + ' scripts)\nFolder: ' + _currentProjectDir);

        // Start background hydration of lazy libraries
        _startBackgroundHydration(result.libs);
      })
      .catch(function (err) {
        hideProgress();
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

      var ws = Util.$currentWorkSpace && Util.$currentWorkSpace();
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
                if (!Util || !Util.$currentWorkSpace) {
                  if (attempt === 1 || attempt === maxAttempts) {
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
                    _serverLog('INFO', '[LazyDiag] redraw attempt ' + attempt + ': scene/stage not ready');
                  }
                  if (attempt < maxAttempts) {
                    return setTimeout(function() { triggerHydrationRedraw(attempt + 1); }, 250);
                  }
                  _log.warn('[Lazy] Redraw skipped: scene/stage not ready after retries');
                  _serverLog('WARN', '[Lazy] Redraw skipped: scene/stage not ready after retries');
                  return;
                }

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
                    _log.info('[Lazy] Canvas re-render triggered at frame ' + frame + ' (attempt ' + attempt + ')');
                    _serverLog('INFO', '[Lazy] Canvas re-render triggered at frame ' + frame + ' (attempt ' + attempt + ')');
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

    if (window.N2FProfiler) {
      window.N2FProfiler.startSession('swf-import-client');
      window.N2FProfiler.size('swf_file', file.size);
      window.N2FProfiler.note('file: ' + file.name);
      window.N2FProfiler.startTimer('server_convert');
    }

    showProgress('Importing SWF...\n' + file.name + ' (' + formatBytes(file.size) + ')');

    var form = new FormData();
    form.append('file', file);

    fetch(API_BASE + '/api/swf-to-project', { method: 'POST', body: form })
      .then(function (r) {
        if (window.N2FProfiler) window.N2FProfiler.stopTimer();
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Server error'); });
        var name = r.headers.get('X-N2D-Name') || file.name.replace('.swf', '');
        var libs = r.headers.get('X-N2D-Libraries') || '?';
        var scripts = r.headers.get('X-N2D-Scripts') || '0';
        var projDir = r.headers.get('X-Project-Dir') || '';
        if (window.N2FProfiler) {
          window.N2FProfiler.count('libraries', parseInt(libs) || 0);
          window.N2FProfiler.count('scripts', parseInt(scripts) || 0);
          window.N2FProfiler.startTimer('read_blob');
        }
        return r.blob().then(function (blob) {
          if (window.N2FProfiler) {
            window.N2FProfiler.stopTimer();
            window.N2FProfiler.size('n2d_blob', blob.size);
          }
          return { blob: blob, name: name, libs: libs, scripts: scripts, projDir: projDir };
        });
      })
      .then(function (result) {
        hideProgress();
        _currentProjectDir = result.projDir;
        _log.info('Project created at:', _currentProjectDir);

        var refreshBtn = document.getElementById('n2f-refresh-assets');
        if (refreshBtn) refreshBtn.disabled = false;
        var saveBtn = document.getElementById('n2f-save-project');
        if (saveBtn) saveBtn.disabled = false;

        _importedN2DBlob = result.blob.slice(0);
        _saveImportedBlobToIDB(_importedN2DBlob);

        if (window.N2FProfiler) window.N2FProfiler.startTimer('load_into_tool');
        _feedN2DToTool(result.blob, result.name);

        // End session after a delay to capture loading time
        if (window.N2FProfiler) {
          setTimeout(function() {
            window.N2FProfiler.stopTimer();
            window.N2FProfiler.endSession('swf-import-client');
          }, 8000);
        }

        toast('Project created: ' + result.name + ' (' + result.libs + ' libraries, ' + result.scripts + ' scripts)\nFolder: ' + _currentProjectDir);
      })
      .catch(function (err) {
        hideProgress();
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
          var saveBtn = document.getElementById('n2f-save-project');
          if (saveBtn) saveBtn.disabled = false;
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

      showProgress('Refreshing project from server...');

      // Re-run the exact same open-project pipeline with the stored file.
      // The tool creates its own new tab when loading an N2D (via the unzlib
      // worker onmessage handler), so we must NOT close the old tab until the
      // new workspace has fully loaded — otherwise we corrupt workspace state.
      _doOpenProjectBlob(storedBlob, _currentProjectDir.split(/[\\/]/).pop() + '.n2d', function (result) {
        // Poll until the new tab becomes active in the DOM, then close the old one.
        var attempts = 0;
        function waitAndCloseOldTab() {
          var activeEl = document.querySelector('#view-tab-area .active[data-tab-id]');
          var activeId = activeEl ? activeEl.dataset.tabId : null;
          if (activeId !== null && activeId !== oldTabId) {
            // New workspace is loaded and active — safe to close old tab
            if (oldTabId !== null) {
              var closeBtn = document.getElementById('tab-delete-id-' + oldTabId);
              if (closeBtn) {
                var origConfirm = window.confirm;
                window.confirm = function () { return true; };
                try { closeBtn.click(); } finally { window.confirm = origConfirm; }
              }
            }
            toast('Refreshed: ' + result.name + ' (' + result.libs + ' libraries)');
          } else if (++attempts < 100) {
            setTimeout(waitAndCloseOldTab, 100);
          } else {
            // Timed out (10s) — don't close the old tab to avoid corruption
            _log.warn('Refresh: timed out waiting for new tab');
            toast('Refreshed: ' + result.name + ' (old tab may still be open)');
          }
        }
        setTimeout(waitAndCloseOldTab, 100);
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
  function onSaveProject() {
    if (!_currentProjectDir) {
      toast('No project folder active — import an SWF or open a project first.', true);
      return;
    }
    _log.info('Save Project requested');
    showProgress('Saving project...');

    saveProjectAsN2D()
      .then(function (n2dBlob) {
        updateProgress('Uploading project to server...');
        var form = new FormData();
        form.append('n2d', n2dBlob, 'project.n2d');
        return fetch(API_BASE + '/api/save-project', { method: 'POST', body: form });
      })
      .then(function (r) {
        if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Save failed'); });
        return r.json();
      })
      .then(function (result) {
        hideProgress();
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
  /*  Export SWF                                                         */
  /* ================================================================== */
  function onExportSWF() {
    _log.info('Export SWF requested');
    showProgress('Preparing project for SWF export...');

    if (window.N2FProfiler) {
      window.N2FProfiler.startSession('swf-export-client');
      window.N2FProfiler.startTimer('prepare_export');
    }

    var name = getProjectName() || 'output';

    // When a project folder is active, capture the current editor state first
    // (so timeline edits like position/filter changes are included), save it
    // to the project folder, then compile from there.
    if (_currentProjectDir) {

      // ── ELECTRON FAST PATH: compile from disk, save via native dialog ──
      if (window.n2fElectron) {
        _log.info('Electron — compile from disk, native save dialog');
        window.n2fElectron.showSaveSWFDialog(name + '.swf').then(function (outputPath) {
          if (!outputPath) { hideProgress(); return; }
          updateProgress('Compiling SWF...');
          return fetch(API_BASE + '/api/compile-disk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ projectDir: _currentProjectDir, outputPath: outputPath }),
          })
            .then(function (r) {
              if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Compilation failed'); });
              return r.json();
            })
            .then(function (result) {
              hideProgress();
              _log.info('SWF compiled to:', result.swfPath, formatBytes(result.size));
              toast('Exported: ' + outputPath.split(/[\\/]/).pop() + ' (' + formatBytes(result.size) + ')');
            });
        }).catch(function (err) {
          hideProgress();
          _log.error('SWF export failed:', err.message);
          toast('Export failed: ' + err.message, true);
        });
        return;
      }

      // ── BROWSER PATH: use HTTP blob transfer ──
      _log.info('Project folder active — fast export via server-side merge');
      updateProgress('Capturing editor state...');

      // Fast path: try to capture the tool blob, but if the tool's
      // internal JSON.stringify crashes (RangeError for huge projects),
      // fall back to compiling directly from disk data.
      function _sendCompileRequest(rawBlob) {
        updateProgress('Compiling SWF...');
        var form = new FormData();
        if (rawBlob) {
          form.append('editorBlob', rawBlob, 'editor.bin');
        } else {
          // Disk-only: tell server to compile from existing project.n2d
          form.append('diskOnly', '1');
        }
        return fetch(API_BASE + '/api/save-and-compile', { method: 'POST', body: form })
          .then(function (r) {
            if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || 'Compilation failed'); });
            return r.blob();
          })
          .then(function (blob) {
            hideProgress();
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

        if (window.N2FProfiler) {
          window.N2FProfiler.stopTimer();
          window.N2FProfiler.size('output_swf', result.blob.size);
          window.N2FProfiler.endSession('swf-export-client');
        }
        _log.info('SWF export succeeded:', result.name + '.swf', formatBytes(result.blob.size));
        toast('Exported: ' + result.name + '.swf (' + formatBytes(result.blob.size) + ')');
      })
      .catch(function (err) {
        hideProgress();
        if (window.N2FProfiler) window.N2FProfiler.endSession('swf-export-client');
        _log.error('SWF export failed:', err.message);
        toast('Export failed: ' + err.message, true);
      });
  }

  /**
   * Capture the raw tool save blob without any processing.
   * Returns the zlib-compressed blob straight from the tool's save pipeline.
   * This is fast because it avoids decompress/parse/merge/stringify/recompress.
   */
  function _captureToolBlob() {
    return new Promise(function (resolve, reject) {
      var anchor = document.getElementById('save-anchor');
      if (!anchor) return reject(new Error('save-anchor not found'));

      var origClick = anchor.click;
      anchor.click = function () {
        var blobUrl = this.href;
        anchor.click = origClick;

        if (!blobUrl || !blobUrl.startsWith('blob:')) {
          return reject(new Error('No blob URL available'));
        }

        fetch(blobUrl)
          .then(function (r) { return r.blob(); })
          .then(function (blob) {
            _log.info('[PERF] captured tool blob: ' + (blob.size / 1048576).toFixed(1) + 'MB');
            resolve(blob);
          })
          .catch(reject);
      };

      var saveBtn = document.getElementById('tools-save');
      if (saveBtn) {
        saveBtn.click();
      } else {
        anchor.click = origClick;
        reject(new Error('tools-save button not found'));
      }
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

            // Inject roundtrip data (rawTagBody, rawGlobalTags, scripts, etc.)
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
              : _loadImportedBlobFromIDB();
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
