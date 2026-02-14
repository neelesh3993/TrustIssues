import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'public',
    emptyOutDir: false,
    rollupOptions: {
      input: {
        popup: path.resolve(__dirname, 'src/popup.tsx'),
        background: path.resolve(__dirname, 'src/background/service-worker.ts'),
        content: path.resolve(__dirname, 'src/content/content-script.ts'),
      },
      output: {
        entryFileNames: 'src/[name].js',
        chunkFileNames: 'src/chunks/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]'
      }
    },
    target: 'es2020'
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname)
    }
  }
})
