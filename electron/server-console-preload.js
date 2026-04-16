/**
 * Next2Flash — Server Console preload script.
 * Exposes a secure bridge for the server console UI to receive log lines.
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('n2fConsole', {
  onLog: (callback) => {
    ipcRenderer.on('console:log', (_event, data) => callback(data));
  },
  onStatus: (callback) => {
    ipcRenderer.on('console:status', (_event, state, text) => callback(state, text));
  },
});
