import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  envDir: '../',  // read .env from project root instead of frontend/
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
