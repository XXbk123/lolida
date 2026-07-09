import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

/** Electron 桌面端 Vite 配置 */
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  base: './',
  server: {
    port: 5174,
    strictPort: true,
    host: true,
    proxy: {
      '/api': 'http://127.0.0.1:8765',
      '/static': 'http://127.0.0.1:8765',
    },
  },
  build: {
    outDir: 'dist',
  },
})
