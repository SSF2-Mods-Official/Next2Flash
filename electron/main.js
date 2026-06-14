/**
 * Next2Flash — Electron main process.
 *
 * Spawns the Python server.py as a child process, waits for it to be ready,
 * then opens a BrowserWindow pointing at the local server.  All the existing
 * web UI + REST API just works — zero porting required.
 *
 * Gains over the pure-browser setup:
 *   • No V8 string-length limits (Python does all heavy serialization)
 *   • Direct filesystem access via IPC (native Save / Open dialogs)
 *   • No CORS / upload-size limits
 *   • Can increase renderer memory with --max-old-space-size
 */

const { app, BrowserWindow, ipcMain, dialog, Menu, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');
const https = require('https');
const fs = require('fs');

// ── Paths ──────────────────────────────────────────────────────────────────
const isDev = !app.isPackaged;
const APP_DIR = isDev
  ? path.join(__dirname, '..', 'app')
  : path.join(process.resourcesPath, 'app');

// In packaged builds, server.py is compiled to server.exe by PyInstaller.
// In dev, fall back to spawning python directly.
const SERVER_EXE = isDev
  ? null
  : path.join(process.resourcesPath, 'server.exe');
const PYTHON = process.env.N2F_PYTHON || 'python';
const SERVER_SCRIPT = path.join(APP_DIR, 'server.py');
const SERVER_PORT = parseInt(process.env.N2F_PORT || '5000', 10);
const SERVER_URL = `http://127.0.0.1:${SERVER_PORT}`;

// ── Desktop GPU & performance flags (must be set before app.ready) ────────
app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('enable-zero-copy');
app.commandLine.appendSwitch('enable-native-gpu-memory-buffers');
app.commandLine.appendSwitch('canvas-oop-rasterization');
app.commandLine.appendSwitch('disable-renderer-backgrounding');
app.commandLine.appendSwitch('disable-background-timer-throttling');
app.commandLine.appendSwitch('js-flags', '--max-old-space-size=4096');

// ANGLE backend: use D3D11 for best WebGL2 compat on Windows.
// Alternatives: 'd3d11', 'd3d9', 'gl', 'vulkan', 'swiftshader', 'metal'
app.commandLine.appendSwitch('use-angle', 'd3d11');
// Enable GPU process scheduling priority for smoother frame delivery
app.commandLine.appendSwitch('enable-features', 'GpuScheduling');

// ── Single-instance lock ───────────────────────────────────────────────────
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  // Another instance is already running — quit immediately.
  app.quit();
}

let mainWindow = null;
let splashWindow = null;
let profilerWindow = null;
let serverConsoleWindow = null;
let pythonProcess = null;
let profilerLogPath = null;
let profilerLogStream = null;
const consoleLogBuffer = [];  // buffer all server output so Console window can replay history

app.on('second-instance', () => {
  // Someone tried to run a second instance — focus our window instead.
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
  }
});

// ── Python server management ───────────────────────────────────────────────

function startPythonServer() {
  return new Promise((resolve, reject) => {
    // N2F_SKIP_SERVER_SPAWN=1 means the server was pre-started externally
    // (e.g. by Next2Flash-Desktop.bat). Just wait for it to respond.
    if (process.env.N2F_SKIP_SERVER_SPAWN === '1') {
      console.log('[N2F] N2F_SKIP_SERVER_SPAWN set — connecting to pre-started server');
      const startTime = Date.now();
      const TIMEOUT = 30000;
      function pollExternal() {
        if (Date.now() - startTime > TIMEOUT) {
          return reject(new Error('Pre-started server did not respond within 30 s'));
        }
        const req = http.get(`${SERVER_URL}/api/health`, (res) => {
          if (res.statusCode === 200) { console.log('[N2F] External server ready'); resolve(); }
          else { setTimeout(pollExternal, 200); }
        });
        req.on('error', () => setTimeout(pollExternal, 200));
        req.setTimeout(1000, () => { req.destroy(); setTimeout(pollExternal, 200); });
      }
      setTimeout(pollExternal, 200);
      return;
    }

    // Kill any process currently occupying SERVER_PORT (handles multiple orphans and
    // cases where the PID file was missing or stale). Windows-only; on other platforms
    // fall back to the PID file approach.
    const pidFile = path.join(APP_DIR, 'server.pid');
    let spawnDelay = 0;
    if (process.platform === 'win32') {
      try {
        const { execSync } = require('child_process');
        const netout = execSync(
          `netstat -ano 2>nul | findstr ":${SERVER_PORT} " | findstr LISTENING`,
          { shell: true, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }
        );
        const pids = new Set();
        for (const line of netout.split('\n')) {
          const m = line.trim().match(/(\d+)\s*$/);
          if (m) pids.add(m[1]);
        }
        for (const pid of pids) {
          try {
            execSync(`taskkill /PID ${pid} /F`, { stdio: 'ignore' });
            console.log(`[N2F] Killed orphaned server process PID ${pid} on port ${SERVER_PORT}`);
            spawnDelay = 800;
          } catch (_) {}
        }
      } catch (_) {}
    } else {
      // Non-Windows: fall back to PID file
      if (fs.existsSync(pidFile)) {
        try {
          const oldPid = parseInt(fs.readFileSync(pidFile, 'utf8').trim(), 10);
          if (oldPid && !isNaN(oldPid)) {
            try {
              process.kill(oldPid, 0);
              process.kill(oldPid);
              spawnDelay = 800;
            } catch (_) {}
          }
        } catch (_) {}
      }
    }
    // Clean up PID file regardless
    try { fs.unlinkSync(pidFile); } catch (_) {}

    // Packaged: run the bundled server.exe (no Python needed on host).
    // Dev: run `python server.py` as before.
    let cmd, args, cwd;
    if (SERVER_EXE && fs.existsSync(SERVER_EXE)) {
      cmd = SERVER_EXE;
      args = [];
      cwd = APP_DIR;
      console.log(`[N2F] Starting bundled server: ${cmd}`);
    } else {
      cmd = PYTHON;
      args = [SERVER_SCRIPT];
      cwd = APP_DIR;
      console.log(`[N2F] Starting Python server: ${cmd} ${SERVER_SCRIPT}`);
    }
    console.log(`[N2F] APP_DIR = ${APP_DIR}`);

    setTimeout(() => {
    pythonProcess = spawn(cmd, args, {
      cwd,
      env: { ...process.env, N2F_PORT: String(SERVER_PORT), N2F_ELECTRON: '1', N2F_WEB_ROOT: cwd },
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true,
    });

    pythonProcess.stdout.on('data', (data) => {
      process.stdout.write(`[PY] ${data}`);
      sendConsoleLog(data.toString(), 'stdout');
    });

    pythonProcess.stderr.on('data', (data) => {
      process.stderr.write(`[PY] ${data}`);
      sendConsoleLog(data.toString(), 'stderr');
    });

    pythonProcess.on('error', (err) => {
      console.error('[N2F] Failed to start Python:', err.message);
      reject(err);
    });

    pythonProcess.on('exit', (code) => {
      console.log(`[N2F] Python server exited with code ${code}`);
      pythonProcess = null;
      sendConsoleLog(`Server exited with code ${code}`, 'system');
      sendConsoleStatus('stopped', `Exited (code ${code})`);
    });

    // Poll until the server responds.
    // PyInstaller onefile extracts ~33 MB on first run — allow 90 s.
    const startTime = Date.now();
    const TIMEOUT = 90000;

    function poll() {
      if (Date.now() - startTime > TIMEOUT) {
        return reject(new Error('Python server did not start within 15 s'));
      }

      const req = http.get(`${SERVER_URL}/api/health`, (res) => {
        if (res.statusCode === 200) {
          console.log('[N2F] Python server ready');
          resolve();
        } else {
          setTimeout(poll, 200);
        }
      });
      req.on('error', () => setTimeout(poll, 200));
      req.setTimeout(1000, () => { req.destroy(); setTimeout(poll, 200); });
    }

    // Give the process a moment to start before first poll
    setTimeout(poll, 500);
    }, spawnDelay); // delay if we just killed an old server (port release)
  });
}

function stopPythonServer() {
  if (pythonProcess) {
    console.log('[N2F] Stopping Python server');
    pythonProcess.kill();
    pythonProcess = null;
  }
}

// ── Update check (GitHub Releases) ─────────────────────────────────────────
const GH_RELEASE_URL = 'https://api.github.com/repos/SSF2-Mods-Official/Next2Flash/releases/latest';
const GH_RELEASE_PAGE = 'https://github.com/SSF2-Mods-Official/Next2Flash/releases/latest';

function getUpdateSkipPath() {
  return path.join(app.getPath('userData'), 'update-skip.json');
}

function getSkippedVersion() {
  try {
    return JSON.parse(fs.readFileSync(getUpdateSkipPath(), 'utf8')).skippedVersion || null;
  } catch (_) { return null; }
}

function setSkippedVersion(v) {
  try {
    fs.writeFileSync(getUpdateSkipPath(), JSON.stringify({ skippedVersion: v }), 'utf8');
  } catch (_) { /* non-fatal */ }
}

// Compare two version strings like "0.1", "v0.1.0", "1.2.3". Returns >0 if a>b,
// <0 if a<b, 0 if equal. Non-numeric segments compared lexicographically.
function compareVersions(a, b) {
  const norm = s => String(s).replace(/^v/i, '').split(/[.\-+]/);
  const A = norm(a), B = norm(b);
  const n = Math.max(A.length, B.length);
  for (let i = 0; i < n; i++) {
    const ai = A[i] ?? '0', bi = B[i] ?? '0';
    const an = parseInt(ai, 10), bn = parseInt(bi, 10);
    if (!isNaN(an) && !isNaN(bn)) {
      if (an !== bn) return an - bn;
    } else if (ai !== bi) {
      return ai < bi ? -1 : 1;
    }
  }
  return 0;
}

function fetchLatestRelease() {
  return new Promise((resolve, reject) => {
    const req = https.get(GH_RELEASE_URL, {
      headers: {
        'User-Agent': 'Next2Flash-Updater',
        'Accept': 'application/vnd.github+json',
      },
      timeout: 5000,
    }, res => {
      // Follow one redirect if needed
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        https.get(res.headers.location, { headers: { 'User-Agent': 'Next2Flash-Updater' } }, r2 => collect(r2, resolve, reject)).on('error', reject);
        return;
      }
      collect(res, resolve, reject);
    });
    req.on('timeout', () => { req.destroy(new Error('timeout')); });
    req.on('error', reject);
  });
}

function collect(res, resolve, reject) {
  if (res.statusCode !== 200) {
    reject(new Error(`HTTP ${res.statusCode}`));
    return;
  }
  let body = '';
  res.setEncoding('utf8');
  res.on('data', c => body += c);
  res.on('end', () => {
    try { resolve(JSON.parse(body)); } catch (e) { reject(e); }
  });
  res.on('error', reject);
}

/**
 * Check GitHub for a newer release.
 *   silent=true  → only show a dialog if a newer version exists & isn't skipped.
 *   silent=false → always show a dialog (used by Help → Check for Updates).
 */
async function checkForUpdates({ silent = true } = {}) {
  const current = app.getVersion();
  let release;
  try {
    release = await fetchLatestRelease();
  } catch (err) {
    if (!silent) {
      dialog.showMessageBox(mainWindow, {
        type: 'warning',
        title: 'Update check failed',
        message: 'Could not contact GitHub.',
        detail: String(err && err.message || err),
      });
    }
    return;
  }

  const latestTag = String(release.tag_name || '').trim();
  if (!latestTag) {
    if (!silent) {
      dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: 'No releases yet',
        message: 'No published releases were found on GitHub.',
      });
    }
    return;
  }

  const latest = latestTag.replace(/^v/i, '');
  const cmp = compareVersions(latest, current);

  if (cmp <= 0) {
    if (!silent) {
      dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: "You're up to date",
        message: `Next2Flash ${current} is the latest version.`,
      });
    }
    return;
  }

  if (silent && getSkippedVersion() === latest) return;

  const notes = (release.body || '').toString().trim();
  const detail = notes
    ? (notes.length > 1200 ? notes.slice(0, 1200) + '\n…' : notes)
    : 'A new version is available on GitHub.';

  const { response } = await dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'Update available',
    message: `Next2Flash ${latest} is available (you have ${current}).`,
    detail,
    buttons: ['Download', 'Remind me later', 'Skip this version'],
    defaultId: 0,
    cancelId: 1,
    noLink: true,
  });

  if (response === 0) shell.openExternal(release.html_url || GH_RELEASE_PAGE);
  else if (response === 2) setSkippedVersion(latest);
}

// ── Window management ──────────────────────────────────────────────────────

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 1024,
    minHeight: 700,
    title: 'Next2Flash',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      backgroundThrottling: false,
    },
    show: false,
  });

  mainWindow.loadURL(SERVER_URL);

  // Block ad/analytics requests — they're for the web version, not desktop
  mainWindow.webContents.session.webRequest.onBeforeRequest(
    { urls: ['*://pagead2.googlesyndication.com/*', '*://www.googletagmanager.com/*', '*://cdn.ravenjs.com/*'] },
    (details, callback) => { callback({ cancel: true }); }
  );

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Unsaved-changes dialog: fires when the renderer calls event.preventDefault() in beforeunload
  mainWindow.webContents.on('will-prevent-unload', (event) => {
    const choice = dialog.showMessageBoxSync(mainWindow, {
      type: 'question',
      buttons: ['Leave Without Saving', 'Cancel'],
      defaultId: 1,
      cancelId: 1,
      title: 'Unsaved Changes',
      message: 'You have unsaved changes.',
      detail: 'Leave without saving?',
    });
    if (choice === 0) {
      // Override the page's prevention — allow the window to close
      event.preventDefault();
    }
    // choice === 1 (Cancel): do nothing → window stays open
  });

  // Prevent the tool's auto-save from persisting closed projects to IndexedDB.
  // On close, mark Util.$updated = false so the beforeunload handler skips
  // auto-save, then delete the IndexedDB store so no stale project loads on restart.
  mainWindow.on('close', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.executeJavaScript(`
        try { if (window.Util) window.Util.$updated = false; } catch(e) {}
        try {
          var dbName = (window.Util ? window.Util.PREFIX + '@' + window.Util.DATABASE_NAME : null);
          if (dbName) indexedDB.deleteDatabase(dbName);
        } catch(e) {}
      `).catch(() => {});
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    // Closing the main window quits the entire app, including any auxiliary
    // windows (profiler, server console) that would otherwise keep the app
    // process alive because window-all-closed wouldn't fire.
    if (!app.isQuitting) {
      app.quit();
    }
  });

  // Open external links in the OS browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http')) shell.openExternal(url);
    return { action: 'deny' };
  });
}

// ── Splash window ──────────────────────────────────────────────────────────

function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 380,
    height: 220,
    frame: false,
    transparent: false,
    resizable: false,
    alwaysOnTop: true,
    center: true,
    title: 'Next2Flash',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  splashWindow.loadFile(path.join(__dirname, 'splash.html'));

  splashWindow.on('closed', () => {
    splashWindow = null;
  });
}

function closeSplash() {
  if (splashWindow && !splashWindow.isDestroyed()) {
    splashWindow.close();
    splashWindow = null;
  }
}

// ── Server Console window ──────────────────────────────────────────────────

function createServerConsoleWindow() {
  if (serverConsoleWindow) {
    serverConsoleWindow.focus();
    return;
  }

  serverConsoleWindow = new BrowserWindow({
    width: 700,
    height: 500,
    minWidth: 400,
    minHeight: 250,
    title: 'N2F Server Console',
    webPreferences: {
      preload: path.join(__dirname, 'server-console-preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  serverConsoleWindow.loadFile(path.join(__dirname, 'server-console.html'));

  // Replay buffered log history and send current status once the window is ready
  serverConsoleWindow.webContents.once('did-finish-load', () => {
    const state = pythonProcess ? 'running' : 'stopped';
    const text = pythonProcess ? `Running on port ${SERVER_PORT}` : 'Stopped';
    serverConsoleWindow.webContents.send('console:bootstrap', {
      entries: consoleLogBuffer,
      state,
      text,
    });
  });

  serverConsoleWindow.on('closed', () => {
    serverConsoleWindow = null;
  });
}

function sendConsoleLog(text, stream) {
  const entry = { text, stream };
  consoleLogBuffer.push(entry);
  if (serverConsoleWindow && !serverConsoleWindow.isDestroyed()) {
    serverConsoleWindow.webContents.send('console:log', entry);
  }
}

function sendConsoleStatus(state, text) {
  if (serverConsoleWindow && !serverConsoleWindow.isDestroyed()) {
    serverConsoleWindow.webContents.send('console:status', state, text);
  }
}

// ── Profiler window ────────────────────────────────────────────────────────

function createProfilerWindow() {
  if (profilerWindow) {
    profilerWindow.focus();
    return;
  }

  // Set up log file
  const logsDir = path.join(app.getPath('userData'), 'profiler-logs');
  if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  profilerLogPath = path.join(logsDir, `profiler-${ts}.log`);
  profilerLogStream = fs.createWriteStream(profilerLogPath, { flags: 'a' });
  profilerLogStream.write(`=== N2F Profiler Log — ${new Date().toISOString()} ===\n`);

  profilerWindow = new BrowserWindow({
    width: 700,
    height: 600,
    minWidth: 400,
    minHeight: 300,
    title: 'N2F Profiler',
    webPreferences: {
      preload: path.join(__dirname, 'profiler-preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  profilerWindow.loadFile(path.join(__dirname, 'profiler.html'));

  profilerWindow.on('closed', () => {
    profilerWindow = null;
    if (profilerLogStream) {
      profilerLogStream.end();
      profilerLogStream = null;
    }
  });
}

function sendProfilerEvent(event) {
  // Write to log file
  if (profilerLogStream) {
    const ts = new Date().toISOString();
    if (event.type === 'heartbeat') {
      // Compact one-liner for heartbeat: FPS, heap, DOM count, avg frame time
      const fps = event.fps || 0;
      const heap = event.heapMB || 0;
      const dom = event.domNodes || 0;
      const frameMs = event.ms || 0;
      profilerLogStream.write(`${ts}  heartbeat  FPS:${fps} Heap:${heap}MB DOM:${dom} FrameTime:${frameMs}ms\n`);
      // Emit frame-drop warning for severe drops (playback stutter)
      if (fps > 0 && fps < 20) {
        profilerLogStream.write(`${ts}  warn  Frame drop: ${fps} FPS (target 60)\n`);
      }
    } else {
      const ms = event.ms !== undefined ? ` [${event.ms.toFixed(1)}ms]` : '';
      profilerLogStream.write(`${ts}  ${event.type || 'timer'}  ${event.label || event.name || ''}${ms}\n`);
    }
  }
  // Forward to profiler window
  if (profilerWindow && !profilerWindow.isDestroyed()) {
    profilerWindow.webContents.send('profiler:event', event);
  }
}

// ── Application menu ───────────────────────────────────────────────────────

function buildMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Import SWF...',
          accelerator: 'CmdOrCtrl+O',
          click: () => handleImportSWF(),
        },
        {
          label: 'Open Project...',
          accelerator: 'CmdOrCtrl+Shift+O',
          click: () => handleOpenProject(),
        },
        {
          label: 'Open Recent...',
          accelerator: 'CmdOrCtrl+Shift+R',
          click: () => mainWindow?.webContents.send('menu:open-recent'),
        },
        { type: 'separator' },
        {
          label: 'Save Project',
          accelerator: 'CmdOrCtrl+S',
          click: () => mainWindow?.webContents.send('menu:save'),
        },
        {
          label: 'Export SWF',
          accelerator: 'CmdOrCtrl+Shift+E',
          click: () => mainWindow?.webContents.send('menu:export-swf'),
        },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        {
          label: 'Undo',
          accelerator: 'CmdOrCtrl+Z',
          click: () => mainWindow?.webContents.send('menu:undo'),
        },
        {
          label: 'Redo',
          accelerator: 'CmdOrCtrl+Shift+Z',
          click: () => mainWindow?.webContents.send('menu:redo'),
        },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' },
      ],
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Performance Profiler',
          accelerator: 'CmdOrCtrl+Shift+P',
          click: () => createProfilerWindow(),
        },
        {
          label: 'Server Console',
          accelerator: 'CmdOrCtrl+Shift+L',
          click: () => createServerConsoleWindow(),
        },
        {
          label: 'SSF2 Debug Console',
          accelerator: 'CmdOrCtrl+Shift+D',
          click: () => createSsf2ConsoleWindow(),
        },
        { type: 'separator' },
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { role: 'resetZoom' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Debug',
      submenu: [
        {
          label: 'SSF2 Roundtrip and Run ADL',
          accelerator: 'CmdOrCtrl+Shift+T',
          click: () => mainWindow?.webContents.send('menu:ssf2-roundtrip-adl'),
        },
        {
          label: 'Run SSF2 (ADL only)',
          click: () => {
            createSsf2ConsoleWindow();
            launchSsf2Adl({}).catch((e) => console.error('[N2F] ADL:', e));
          },
        },
        {
          label: 'SSF2 Debug Console',
          click: () => createSsf2ConsoleWindow(),
        },
        { type: 'separator' },
        {
          label: 'Stop ADL',
          click: () => { stopSsf2Adl(); stopSsf2LogWatch(); },
        },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Check for Updates…',
          click: () => { checkForUpdates({ silent: false }).catch(() => {}); },
        },
        {
          label: 'Join Discord',
          click: () => { shell.openExternal('https://discord.gg/MaJFnhHpYx'); },
        },
        { type: 'separator' },
        {
          label: 'About Next2Flash',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Next2Flash',
              message: `Next2Flash ${app.getVersion()}`,
              detail: 'Desktop SWF authoring tool.\nPowered by Electron + Next2D + Python.\nMasterWex',
            });
          },
        },
      ],
    },
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// ── Per-dialog last-used directory persistence ────────────────────────────
// Each dialog key maps to the last directory the user navigated to.
// Stored in a small JSON file inside userData so it persists across sessions.

let _settingsPath = null;  // resolved after app.setPath('userData') is called
let _lastDirs = {};        // in-memory cache

function getSettingsPath() {
  if (!_settingsPath) {
    _settingsPath = path.join(app.getPath('userData'), 'dialog-dirs.json');
  }
  return _settingsPath;
}

function loadLastDirs() {
  try {
    const raw = fs.readFileSync(getSettingsPath(), 'utf8');
    _lastDirs = JSON.parse(raw);
  } catch (_) {
    _lastDirs = {};
  }
}

function saveLastDirs() {
  try {
    fs.writeFileSync(getSettingsPath(), JSON.stringify(_lastDirs), 'utf8');
  } catch (_) { /* non-fatal */ }
}

/**
 * Return the last directory used for a named dialog key,
 * or undefined if none has been recorded yet.
 */
function lastDir(key) {
  if (!Object.keys(_lastDirs).length) loadLastDirs();
  return _lastDirs[key] || undefined;
}

/**
 * Record the directory from a chosen file path for a named dialog key.
 */
function rememberDir(key, filePath) {
  if (!filePath) return;
  _lastDirs[key] = path.dirname(filePath);
  saveLastDirs();
}

// ── IPC handlers (native dialogs, filesystem) ──────────────────────────────

async function handleImportSWF() {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Import SWF File',
    defaultPath: lastDir('importSwf'),
    filters: [{ name: 'SWF Files', extensions: ['swf'] }],
    properties: ['openFile'],
  });
  if (!result.canceled && result.filePaths.length > 0) {
    rememberDir('importSwf', result.filePaths[0]);
    mainWindow.webContents.send('file:import-swf', result.filePaths[0]);
  }
}

async function handleOpenProject() {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Open N2D Project',
    defaultPath: lastDir('openProject'),
    filters: [{ name: 'N2D Files', extensions: ['n2d'] }],
    properties: ['openFile'],
  });
  if (!result.canceled && result.filePaths.length > 0) {
    rememberDir('openProject', result.filePaths[0]);
    mainWindow.webContents.send('file:open-project', result.filePaths[0]);
  }
}

// IPC: native file dialogs for the renderer
ipcMain.handle('dialog:open-file', async (_event, options) => {
  return dialog.showOpenDialog(mainWindow, options);
});

ipcMain.handle('dialog:save-file', async (_event, options) => {
  return dialog.showSaveDialog(mainWindow, options);
});

ipcMain.handle('dialog:save-swf', async (_event, defaultName) => {
  const dir = lastDir('exportSwf');
  const result = await dialog.showSaveDialog(mainWindow, {
    title: 'Export SWF',
    defaultPath: dir ? path.join(dir, defaultName || 'output.swf') : (defaultName || 'output.swf'),
    filters: [
      { name: 'SWF Files', extensions: ['swf'] },
      { name: 'SSF Files', extensions: ['ssf'] },
    ],
  });
  if (!result.canceled && result.filePath) {
    rememberDir('exportSwf', result.filePath);
  }
  return result.canceled ? null : result.filePath;
});

ipcMain.handle('dialog:open-swf', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Import SWF File',
    defaultPath: lastDir('importSwf'),
    filters: [
      { name: 'SWF Files', extensions: ['swf', 'ssf'] },
      { name: 'All Files', extensions: ['*'] },
    ],
    properties: ['openFile'],
  });
  if (!result.canceled && result.filePaths.length) {
    rememberDir('importSwf', result.filePaths[0]);
  }
  return (result.canceled || !result.filePaths.length) ? null : result.filePaths[0];
});

// IPC: direct filesystem read/write (avoids HTTP upload/download)
ipcMain.handle('fs:read-file', async (_event, filePath) => {
  return fs.promises.readFile(filePath);
});

ipcMain.handle('fs:write-file', async (_event, filePath, data) => {
  await fs.promises.writeFile(filePath, Buffer.from(data));
});

ipcMain.handle('fs:exists', async (_event, filePath) => {
  return fs.existsSync(filePath);
});

ipcMain.handle('shell:show-item-in-folder', (_event, filePath) => {
  shell.showItemInFolder(filePath);
});

// ── SSF2 roundtrip / ADL debug ─────────────────────────────────────────────

const SSF2_DEFAULT_SOURCE = String.raw`C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\PSB 1.4 v2\SSF2.swf`;
const SSF2_DEFAULT_ADL_ROOT = String.raw`C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1`;
const SSF2_DEFAULT_GAME_ROOT = String.raw`C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\PSB 1.4 v2`;
/** Matches IDK VS Code launch.json extdir (ADL 32 allows only one -extdir). */
const SSF2_DEFAULT_ADL_EXTDIR = '.as3mxml-unpackaged-anes';

function resolveSsf2AdlExtDir(adlRoot, extRel) {
  const rel = extRel || SSF2_DEFAULT_ADL_EXTDIR;
  const abs = path.join(adlRoot, rel);
  if (fs.existsSync(abs)) {
    const anes = fs.readdirSync(abs).filter((f) => f.toLowerCase().endsWith('.ane'));
    return { rel, abs, anes };
  }
  const rootAnes = fs.existsSync(adlRoot)
    ? fs.readdirSync(adlRoot).filter((f) => f.toLowerCase().endsWith('.ane'))
    : [];
  if (rootAnes.length) {
    return { rel: '.', abs: adlRoot, anes: rootAnes };
  }
  return { rel, abs, anes: [] };
}

let ssf2ConsoleWindow = null;
let ssf2AdlProcess = null;
let ssf2AdlPid = null;
let ssf2AdlStatusTimer = null;
let ssf2LogWatcher = null;
let ssf2LogOffset = 0;
const ssf2ConsoleBuffer = [];

function isSsf2AdlAlive() {
  if (ssf2AdlProcess) {
    return ssf2AdlProcess.exitCode === null && !ssf2AdlProcess.killed;
  }
  if (!ssf2AdlPid) return false;
  try {
    process.kill(ssf2AdlPid, 0);
    return true;
  } catch {
    return false;
  }
}

function startSsf2AdlStatusPoll() {
  stopSsf2AdlStatusPoll();
  ssf2AdlStatusTimer = setInterval(() => {
    if (isSsf2AdlAlive()) {
      sendSsf2AdlStatus('running', 'ADL running');
      return;
    }
    if (ssf2AdlPid || ssf2AdlProcess) {
      sendSsf2Log('[ssf2] ADL process ended (game closed or crashed)', 'log-system');
      sendSsf2AdlStatus('idle', 'ADL not running');
      ssf2AdlPid = null;
      ssf2AdlProcess = null;
    }
  }, 2000);
}

function stopSsf2AdlStatusPoll() {
  if (ssf2AdlStatusTimer) {
    clearInterval(ssf2AdlStatusTimer);
    ssf2AdlStatusTimer = null;
  }
}

function sendSsf2Log(text, stream = 'log-game') {
  const entry = { text, stream };
  ssf2ConsoleBuffer.push(entry);
  if (ssf2ConsoleWindow && !ssf2ConsoleWindow.isDestroyed()) {
    ssf2ConsoleWindow.webContents.send('ssf2:log', entry);
  }
}

function sendSsf2AdlStatus(state, text) {
  if (ssf2ConsoleWindow && !ssf2ConsoleWindow.isDestroyed()) {
    ssf2ConsoleWindow.webContents.send('ssf2:adl-status', { state, text });
  }
}

function createSsf2ConsoleWindow() {
  if (ssf2ConsoleWindow) {
    ssf2ConsoleWindow.focus();
    return;
  }
  ssf2ConsoleWindow = new BrowserWindow({
    width: 800,
    height: 520,
    minWidth: 480,
    minHeight: 280,
    title: 'SSF2 Debug Console',
    webPreferences: {
      preload: path.join(__dirname, 'ssf2-console-preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });
  ssf2ConsoleWindow.loadFile(path.join(__dirname, 'ssf2-console.html'));
  ssf2ConsoleWindow.webContents.once('did-finish-load', () => {
    ssf2ConsoleWindow.webContents.send('ssf2:bootstrap', {
      lines: ssf2ConsoleBuffer.slice(-500),
      adl: {
        state: isSsf2AdlAlive() ? 'running' : 'idle',
        text: isSsf2AdlAlive() ? 'ADL running' : 'ADL not running',
      },
    });
  });
  ssf2ConsoleWindow.on('closed', () => {
    ssf2ConsoleWindow = null;
  });
}

function stopSsf2LogWatch() {
  if (ssf2LogWatcher) {
    fs.unwatchFile(ssf2LogWatcher);
    ssf2LogWatcher = null;
  }
  ssf2LogOffset = 0;
}

function startSsf2LogWatch(logPath) {
  stopSsf2LogWatch();
  if (!logPath || !fs.existsSync(logPath)) {
    sendSsf2Log(`[ssf2] Log file not found yet: ${logPath}`, 'log-system');
    return;
  }
  try {
    ssf2LogOffset = fs.statSync(logPath).size;
  } catch {
    ssf2LogOffset = 0;
  }
  sendSsf2Log(`[ssf2] Tailing ${logPath}`, 'log-system');
  ssf2LogWatcher = logPath;
  fs.watchFile(logPath, { interval: 200 }, () => {
    try {
      const st = fs.statSync(logPath);
      if (st.size <= ssf2LogOffset) return;
      const fd = fs.openSync(logPath, 'r');
      const len = st.size - ssf2LogOffset;
      const buf = Buffer.alloc(len);
      fs.readSync(fd, buf, 0, len, ssf2LogOffset);
      fs.closeSync(fd);
      ssf2LogOffset = st.size;
      const chunk = buf.toString('utf8');
      if (chunk) sendSsf2Log(chunk.trimEnd(), 'log-game');
    } catch (e) {
      sendSsf2Log(`[ssf2] Log read error: ${e.message}`, 'log-stderr');
    }
  });
}

function stopSsf2Adl() {
  stopSsf2AdlStatusPoll();
  if (ssf2AdlProcess) {
    try {
      ssf2AdlProcess.kill();
    } catch (e) {
      console.warn('[N2F] stopSsf2Adl:', e.message);
    }
    ssf2AdlProcess = null;
  }
  if (ssf2AdlPid) {
    try {
      process.kill(ssf2AdlPid);
    } catch (e) {
      console.warn('[N2F] stopSsf2Adl pid:', e.message);
    }
    ssf2AdlPid = null;
  }
  sendSsf2AdlStatus('idle', 'ADL stopped');
}

const SSF2_ADL_FATAL_RE =
  /Error #\d+|TypeError:|ReferenceError:|SecurityError:|cannot be loaded|could not be found|The -extdir argument/i;

function reportSsf2AdlFailure(message, opts = {}) {
  const text = String(message || 'ADL failed').trim();
  const firstLine = text.split(/\r?\n/)[0] || text;
  sendSsf2Log(`[ssf2] ${text}`, 'log-stderr');
  sendSsf2AdlStatus('error', firstLine.slice(0, 120));
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('ssf2:adl-error', { message: text });
  }
  if (!opts.silentDialog) {
    dialog.showErrorBox('SSF2 ADL', text.slice(0, 4000));
  }
}

function launchSsf2Adl(opts) {
  const adlRoot = path.normalize(opts.adlRoot || SSF2_DEFAULT_ADL_ROOT);
  const airSdk = path.normalize(opts.airSdk || process.env.N2F_AIR_SDK || 'C:\\aflex_sdk');
  const adlExe = path.join(airSdk, 'bin', 'adl.exe');
  const appXml = path.join(adlRoot, 'SSF2-app.xml');
  const swfPath = path.join(adlRoot, 'SSF2.swf');
  const logPath = path.join(adlRoot, 'ssf2_debug.log');

  createSsf2ConsoleWindow();
  sendSsf2Log(`[ssf2] adlRoot=${adlRoot}`, 'log-system');
  sendSsf2Log(`[ssf2] airSdk=${airSdk}`, 'log-system');

  if (!fs.existsSync(adlExe)) {
    reportSsf2AdlFailure(`adl.exe not found:\n${adlExe}`);
    return Promise.resolve({ ok: false, error: 'adl.exe not found' });
  }
  if (!fs.existsSync(appXml)) {
    reportSsf2AdlFailure(`SSF2-app.xml missing in:\n${adlRoot}`);
    return Promise.resolve({ ok: false, error: 'SSF2-app.xml missing' });
  }
  if (!fs.existsSync(swfPath)) {
    reportSsf2AdlFailure('SSF2.swf missing in adlRoot — run roundtrip deploy first.');
    return Promise.resolve({ ok: false, error: 'SSF2.swf missing' });
  }

  const ext = resolveSsf2AdlExtDir(adlRoot, opts.adlExtDir);
  if (!ext.anes.length) {
    reportSsf2AdlFailure(
      `No .ane files in extdir (${ext.rel}).\n` +
        'Run IDK asconfig with --unpackage-anes=true, or copy ANEs into .as3mxml-unpackaged-anes.',
    );
    return Promise.resolve({ ok: false, error: 'ANE extdir empty' });
  }

  const discordDll = path.join(path.dirname(adlExe), 'discord_game_sdk.dll');
  if (!fs.existsSync(discordDll)) {
    sendSsf2Log(
      `[ssf2] Warning: 32-bit discord_game_sdk.dll not in AIR SDK bin — Discord ANE may fail at runtime. ` +
        'Copy from IDK src folder per README.',
      'log-stderr',
    );
  }

  stopSsf2Adl();
  startSsf2LogWatch(logPath);

  sendSsf2Log(`[ssf2] Launching: ${adlExe} -extdir ${ext.rel} ${path.basename(appXml)}`, 'log-system');
  sendSsf2Log(`[ssf2] ANEs: ${ext.anes.join(', ')}`, 'log-system');
  sendSsf2AdlStatus('running', 'Starting ADL…');

  return new Promise((resolve) => {
    let settled = false;
    const stderrChunks = [];
    const base = {
      adlExe,
      appXml,
      adlRoot,
      logPath,
      adlExtDir: ext.rel,
      adlExtDirAbs: ext.abs,
      pid: null,
    };

    function finish(result) {
      if (settled) return;
      settled = true;
      resolve(result);
    }

    // Detached + visible window: piped stdio alone can prevent AIR GUI on Windows.
    ssf2AdlProcess = spawn(adlExe, ['-extdir', ext.abs, path.basename(appXml)], {
      cwd: adlRoot,
      env: { ...process.env },
      detached: true,
      windowsHide: false,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    ssf2AdlPid = ssf2AdlProcess.pid;
    base.pid = ssf2AdlPid;
    startSsf2AdlStatusPoll();

    let stderrStartup = true;
    const stderrStartupTimer = setTimeout(() => {
      stderrStartup = false;
    }, 8000);

    ssf2AdlProcess.stdout.on('data', (buf) => {
      sendSsf2Log(buf.toString(), 'log-stdout');
    });
    ssf2AdlProcess.stderr.on('data', (buf) => {
      const text = buf.toString();
      if (stderrStartup) stderrChunks.push(text);
      sendSsf2Log(text, 'log-stderr');
      if (stderrStartup && SSF2_ADL_FATAL_RE.test(text)) {
        clearTimeout(stderrStartupTimer);
        stderrStartup = false;
        reportSsf2AdlFailure(text);
        stopSsf2Adl();
        finish({ ok: false, error: text.trim(), ...base });
      }
    });
    ssf2AdlProcess.on('error', (err) => {
      clearTimeout(stderrStartupTimer);
      reportSsf2AdlFailure(`ADL spawn error: ${err.message}`);
      ssf2AdlProcess = null;
      ssf2AdlPid = null;
      finish({ ok: false, error: err.message, ...base });
    });
    ssf2AdlProcess.on('close', (code) => {
      clearTimeout(stderrStartupTimer);
      const errText = stderrChunks.join('').trim();
      sendSsf2Log(`[ssf2] ADL exited with code ${code}`, 'log-system');
      ssf2AdlProcess = null;
      ssf2AdlPid = null;
      if (code !== 0 && code !== null) {
        const msg = errText || `ADL exited with code ${code}`;
        if (!settled) {
          reportSsf2AdlFailure(msg);
          finish({ ok: false, error: msg, exitCode: code, ...base });
        } else {
          sendSsf2AdlStatus('error', `ADL exited (${code})`);
        }
      } else if (!settled) {
        finish({ ok: true, exitCode: code, ...base });
      } else {
        sendSsf2AdlStatus('idle', 'ADL not running');
      }
    });

    if (ssf2ConsoleWindow && !ssf2ConsoleWindow.isDestroyed()) {
      ssf2ConsoleWindow.webContents.send('ssf2:bootstrap', {
        adlRoot,
        logPath,
        sourceSwf: opts.sourceSwf || '',
        adl: { state: 'running', text: 'ADL running' },
      });
    }

    // ADL often exits quickly on startup failure; if still running, report success to caller.
    setTimeout(() => {
      if (!settled && ssf2AdlProcess) {
        finish({ ok: true, running: true, ...base });
      }
    }, 2500);
  });
}

ipcMain.handle('ssf2:run-adl', async (_event, opts = {}) => {
  return launchSsf2Adl(opts);
});

ipcMain.handle('ssf2:adl-status', async () => {
  const alive = isSsf2AdlAlive();
  return { running: alive, pid: alive ? ssf2AdlPid : null };
});

ipcMain.handle('ssf2:stop-adl', async () => {
  stopSsf2Adl();
  stopSsf2LogWatch();
  return { ok: true };
});

ipcMain.handle('ssf2:restore-backups', async (_event, opts = {}) => {
  const roots = [opts.adlRoot || SSF2_DEFAULT_ADL_ROOT, opts.gameRoot || SSF2_DEFAULT_GAME_ROOT];
  const restored = [];
  for (const root of roots) {
    const dest = path.join(root, 'SSF2.swf');
    const bak = dest + '.n2f-backup';
    if (fs.existsSync(bak)) {
      fs.copyFileSync(bak, dest);
      restored.push(dest);
    }
  }
  return { ok: true, restored };
});

ipcMain.handle('ssf2:show-console', async () => {
  createSsf2ConsoleWindow();
  return { ok: true };
});

ipcMain.on('menu:ssf2-roundtrip-adl', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('menu:ssf2-roundtrip-adl');
  }
});

ipcMain.on('menu:ssf2-run-adl', () => {
  launchSsf2Adl({});
});

// ── Debug log file ─────────────────────────────────────────────────────────
const debugLogsDir = path.join(app.getPath('userData'), 'debug-logs');
if (!fs.existsSync(debugLogsDir)) fs.mkdirSync(debugLogsDir, { recursive: true });
const debugLogPath = path.join(debugLogsDir, 'n2f-debug.log');
// Truncate on each launch so the file always reflects the current session
const debugLogStream = fs.createWriteStream(debugLogPath, { flags: 'w' });
debugLogStream.write(`=== N2F Debug Log - ${new Date().toISOString()} ===\n`);
console.log(`[N2F] Debug log: ${debugLogPath}`);

// IPC: debug logging from renderer → main process stdout + log file
ipcMain.on('debug:log', (_event, msg) => {
  const line = msg + '\n';
  process.stdout.write(line);
  debugLogStream.write(line);
  sendConsoleLog(line, 'system');
});

// IPC: open server console from renderer (e.g. on error)
ipcMain.on('show-server-console', () => {
  createServerConsoleWindow();
  // Send a signal to scroll to bottom and highlight last error
  if (serverConsoleWindow && !serverConsoleWindow.isDestroyed()) {
    serverConsoleWindow.webContents.once('did-finish-load', () => {
      serverConsoleWindow.webContents.send('console:scroll-to-error');
    });
    // If already loaded, send immediately too
    serverConsoleWindow.webContents.send('console:scroll-to-error');
  }
});

// IPC: auto-show server console during import/open; track if we opened it
let _consoleAutoOpened = false;
ipcMain.on('show-server-console-auto', () => {
  _consoleAutoOpened = !serverConsoleWindow || serverConsoleWindow.isDestroyed();
  createServerConsoleWindow();
});

// IPC: auto-hide server console after import/open finishes (only if we opened it)
ipcMain.on('hide-server-console-auto', () => {
  if (_consoleAutoOpened && serverConsoleWindow && !serverConsoleWindow.isDestroyed()) {
    serverConsoleWindow.close();
  }
  _consoleAutoOpened = false;
});

// IPC: profiler events from renderer → profiler window + log file
ipcMain.on('profiler:send-event', (_event, data) => {
  sendProfilerEvent(data);
});

ipcMain.on('profiler:export-log', () => {
  if (profilerLogPath && fs.existsSync(profilerLogPath)) {
    shell.showItemInFolder(profilerLogPath);
  }
});

// ── App lifecycle ──────────────────────────────────────────────────────────

app.commandLine.appendSwitch('js-flags', '--max-old-space-size=8192');

// Set a dedicated userData path so Electron doesn't conflict with other instances
const userDataPath = path.join(app.getPath('appData'), 'Next2Flash');
app.setPath('userData', userDataPath);

app.whenReady().then(async () => {
  createSplashWindow();

  try {
    await startPythonServer();
    sendConsoleStatus('running', `Running on port ${SERVER_PORT}`);
  } catch (err) {
    closeSplash();
    const hint = app.isPackaged
      ? 'The bundled server failed to start. Try running Next2Flash.exe as Administrator\nor check that your antivirus is not blocking server.exe.'
      : 'Make sure Python 3.10+ is installed and on PATH.\nOr set the N2F_PYTHON environment variable.';
    dialog.showErrorBox(
      'Failed to start server',
      `${err.message}\n\n${hint}`
    );
    app.quit();
    return;
  }

  buildMenu();
  createWindow();
  closeSplash();

  // Check for a new GitHub release ~3s after the window opens.
  // Silent: if up-to-date, offline, or user skipped this version, show nothing.
  setTimeout(() => { checkForUpdates({ silent: true }).catch(() => {}); }, 3000);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  stopPythonServer();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  app.isQuitting = true;
  // Force-close auxiliary windows (profiler, server console) so the process can
  // actually exit. Without this, closing them via [X] after a quit signal could
  // hang on their renderer's beforeunload.
  for (const win of BrowserWindow.getAllWindows()) {
    if (win !== mainWindow && !win.isDestroyed()) {
      win.destroy();
    }
  }
  stopPythonServer();
});
