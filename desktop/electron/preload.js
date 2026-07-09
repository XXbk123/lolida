const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  saveImage: (imageUrl, defaultName) => ipcRenderer.invoke('save-image', imageUrl, defaultName),
  isElectron: true,
})
