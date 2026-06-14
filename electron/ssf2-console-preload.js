/**
 * SSF2 debug console preload — ADL log tail + launch status.
 */
const { contextBridge, ipcRenderer, clipboard } = require('electron');

contextBridge.exposeInMainWorld('n2fSsf2Console', {
  onLog: (callback) => {
    ipcRenderer.on('ssf2:log', (_event, data) => callback(data));
  },
  onBootstrap: (callback) => {
    ipcRenderer.on('ssf2:bootstrap', (_event, payload) => callback(payload));
  },
  onAdlStatus: (callback) => {
    ipcRenderer.on('ssf2:adl-status', (_event, payload) => callback(payload));
  },
  copyText: (text) => clipboard.writeText(String(text || '')),
  stopAdl: () => ipcRenderer.invoke('ssf2:stop-adl'),
  runAdl: (opts) => ipcRenderer.invoke('ssf2:run-adl', opts || {}),
  adlStatus: () => ipcRenderer.invoke('ssf2:adl-status'),
  restoreBackups: () => ipcRenderer.invoke('ssf2:restore-backups'),
});
