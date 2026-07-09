/** Electron API 类型声明 */
export interface ElectronAPI {
  saveImage: (imageUrl: string, defaultName: string) => Promise<{ success: boolean; path?: string; error?: string }>
  isElectron: boolean
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI
  }
}

export {}
