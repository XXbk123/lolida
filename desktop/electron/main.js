const { app, BrowserWindow, dialog, ipcMain } = require('electron')
const path = require('path')
const fs = require('fs/promises')

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged

/** 创建主窗口 */
function createWindow() {
  const win = new BrowserWindow({
    width: 960,
    height: 720,
    minWidth: 800,
    minHeight: 600,
    title: '萝莉dao - 今天的兄弟还会是兄弟吗？嘿嘿~',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    backgroundColor: '#fff0f5',
  })

  if (isDev) {
    win.loadURL('http://localhost:5174')
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

/** 注册 IPC 处理器 */
function registerIpc() {
  ipcMain.handle('save-image', async (_event, imageUrl, defaultName) => {
    const result = await dialog.showSaveDialog({
      title: '保存变身图片',
      defaultPath: defaultName,
      filters: [{ name: 'PNG 图片', extensions: ['png'] }],
    })
    if (result.canceled || !result.filePath) return { success: false }

    try {
      const resp = await fetch(imageUrl)
      const buffer = Buffer.from(await resp.arrayBuffer())
      await fs.writeFile(result.filePath, buffer)
      return { success: true, path: result.filePath }
    } catch (e) {
      return { success: false, error: String(e) }
    }
  })
}

app.whenReady().then(() => {
  registerIpc()
  createWindow()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
