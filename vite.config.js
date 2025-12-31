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
          'Referer': 'https://panelharga.badanpangan.go.id/',
          'Accept': 'application/json',
          'x-api-key': 'zHWbt7U2qvPoUDkiUgvnOqYrtj3zClR7unnH2G4apE7HcMV4QyNC6BSD0yV3uvSHqS91TxwE8aMDTiCznmGceEX3zQmO1Xwq7TJblotIt2CpwvK6YjRKDJwcgMJwav9p4RshM3nfuFyurSQQv9BhueMJ0HJ778oD'
        },
        rewrite: (path) => path.replace(/^\/api-bapanas/, '')
      }
    }
  }
})
