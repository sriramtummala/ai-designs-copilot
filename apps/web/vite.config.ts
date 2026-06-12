import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@ai-designops/ui': path.resolve(import.meta.dirname, '../../libs/ui/src/index.ts'),
    },
  },
})
