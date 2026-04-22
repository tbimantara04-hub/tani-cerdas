import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    allowedHosts: true,
    proxy: {
      // 1. Ubah key proxy agar sesuai dengan endpoint yang dipanggil di frontend
      '/api-bapanas': {
        target: 'https://api-panelhargav2.badanpangan.go.id',
        changeOrigin: true,
        // 2. Ubah secure ke false jika server target memiliki masalah sertifikat SSL di local development
        secure: false,
        // 3. Hapus '/api-bapanas' dari URL sebelum diteruskan ke target
        rewrite: (path) => path.replace(/^\/api-bapanas/, ''),
        headers: {
          Origin: 'https://panelharga.badanpangan.go.id',
          Referer: 'https://panelharga.badanpangan.go.id/',
          Accept: 'application/json',
          'x-api-key': '***REMOVED***'
        }
      }
    }
  }
})