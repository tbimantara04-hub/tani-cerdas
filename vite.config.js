import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api-bapanas': {
        target: 'https://api-panelhargav2.badanpangan.go.id',
        changeOrigin: true,
        headers: {
          'Origin': 'https://panelharga.badanpangan.go.id',
          'Referer': 'https://panelharga.badanpangan.go.id/'
        },
        rewrite: (path) => path.replace(/^\/api-bapanas/, '')
      }
    }
  }
})
