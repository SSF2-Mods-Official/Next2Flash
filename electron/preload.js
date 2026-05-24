/**
 * Next2Flash — Electron preload script.
 *
 * Exposes a secure bridge (`window.n2fElectron`) so the renderer can use
 * native dialogs, filesystem access, and receive menu events — without
 * enabling full Node.js integration in the renderer context.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('n2fElectron', {
  /** True when running inside Electron (renderer can feature-detect). */
  isElectron: true,

  // ── Native dialogs ─────────────────────────────────────────────────────
  openFileDialog: (options) => ipcRenderer.invoke('dialog:open-file', options),
  saveFileDialog: (options) => ipcRenderer.invoke('dialog:save-file', options),

  // ── Direct filesystem (skips HTTP upload/download) ─────────────────────
  readFile: (filePath) => ipcRenderer.invoke('fs:read-file', filePath),
  writeFile: (filePath, data) => ipcRenderer.invoke('fs:write-file', filePath, data),
  fileExists: (filePath) => ipcRenderer.invoke('fs:exists', filePath),

  // ── Electron-specific shortcuts ────────────────────────────────────────
  /** Show native "Save As" dialog and return the chosen path (or null). */
  showSaveSWFDialog: (defaultName) => ipcRenderer.invoke('dialog:save-swf', defaultName),
  /** Show native "Open SWF" dialog and return the chosen path (or null). */
  showOpenSWFDialog: () => ipcRenderer.invoke('dialog:open-swf'),

  // ── Menu events (main → renderer) ─────────────────────────────────────
  onMenuSave: (callback) => {
    ipcRenderer.on('menu:save', () => callback());
  },
  onMenuExportSWF: (callback) => {
    ipcRenderer.on('menu:export-swf', () => callback());
  },
  onMenuUndo: (callback) => {
    ipcRenderer.on('menu:undo', () => callback());
  },
  onMenuRedo: (callback) => {
    ipcRenderer.on('menu:redo', () => callback());
  },
  onImportSWF: (callback) => {
    ipcRenderer.on('file:import-swf', (_event, filePath) => callback(filePath));
  },
  onOpenProject: (callback) => {
    ipcRenderer.on('file:open-project', (_event, filePath) => callback(filePath));
  },

  // ── Debug logging (renderer → main process stdout) ────────────────────
  logDebug: (msg) => ipcRenderer.send('debug:log', msg),
  // ── Server console ────────────────────────────────────────────────
  showServerConsole: () => ipcRenderer.send('show-server-console'),
  // ── Profiler bridge ───────────────────────────────────────────────────
  sendProfilerEvent: (event) => {
    ipcRenderer.send('profiler:send-event', event);
  },
});
