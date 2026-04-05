/**
 * Next2Flash — Profiler window preload script.
 * Exposes a secure bridge for the profiler UI to receive events and export logs.
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('n2fProfiler', {
  onEvent: (callback) => {
    ipcRenderer.on('profiler:event', (_event, data) => callback(data));
  },
  exportLog: () => {
    ipcRenderer.send('profiler:export-log');
  },
});
