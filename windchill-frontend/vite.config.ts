import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// BACKEND_HOST wird per docker-compose environment gesetzt:
//   Produktion: "backend"  (Docker-Service-Name im Bridge-Netzwerk)
//   Lokal:      "host.docker.internal"  (Host-Netzwerk via Override)
const backendHost = process.env.BACKEND_HOST || 'backend'
const backendUrl = `http://${backendHost}:8001`

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': backendUrl,
      '/health': backendUrl,
    },
  },
})