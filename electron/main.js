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
  });
}

function stopPythonServer() {
  if (pythonProcess) {
    console.log('[N2F] Stopping Python server');
    pythonProcess.kill();
    pythonProcess = null;
  }
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
      label: 'Help',
      submenu: [
        {
          label: 'About Next2Flash',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Next2Flash',
              message: 'Next2Flash v1.0.0',
              detail: 'Desktop SWF authoring tool.\nPowered by Electron + Next2D + Python.',
            });
          },
        },
      ],
    },
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// ── IPC handlers (native dialogs, filesystem) ──────────────────────────────

async function handleImportSWF() {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Import SWF File',
    filters: [{ name: 'SWF Files', extensions: ['swf'] }],
    properties: ['openFile'],
  });
  if (!result.canceled && result.filePaths.length > 0) {
    mainWindow.webContents.send('file:import-swf', result.filePaths[0]);
  }
}

async function handleOpenProject() {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Open N2D Project',
    filters: [{ name: 'N2D Files', extensions: ['n2d'] }],
    properties: ['openFile'],
  });
  if (!result.canceled && result.filePaths.length > 0) {
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
  const result = await dialog.showSaveDialog(mainWindow, {
    title: 'Export SWF',
    defaultPath: defaultName || 'output.swf',
    filters: [
      { name: 'SWF Files', extensions: ['swf'] },
      { name: 'SSF Files', extensions: ['ssf'] },
    ],
  });
  return result.canceled ? null : result.filePath;
});

ipcMain.handle('dialog:open-swf', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Import SWF File',
    filters: [
      { name: 'SWF Files', extensions: ['swf', 'ssf'] },
      { name: 'All Files', extensions: ['*'] },
    ],
    properties: ['openFile'],
  });
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

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  stopPythonServer();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  stopPythonServer();
});
