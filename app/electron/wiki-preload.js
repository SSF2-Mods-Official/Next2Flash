const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('wiki', {
  author: () => ipcRenderer.invoke('wiki-author'),
  history: (file) => ipcRenderer.invoke('wiki-history', file),
});
