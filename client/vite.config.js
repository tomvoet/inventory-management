import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    // The API's CORS allowlist only covers :3000, so fail loudly instead of silently moving ports
    strictPort: true
  }
})
