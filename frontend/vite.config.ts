import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

function toPort(value: string | undefined): number {
  const port = Number(value)

  return Number.isInteger(port) && port > 0 && port <= 65535 ? port : 5173
}

function toOrigins(value: string | undefined): string[] {
  return (value ?? '')
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean)
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', 'VITE_')
  const allowedOrigins = toOrigins(env.VITE_DEV_ALLOWED_ORIGINS)

  return {
    plugins: [react(), tailwindcss()],
    server: {
      host: env.VITE_DEV_HOST || 'localhost',
      port: toPort(env.VITE_DEV_PORT),
      strictPort: true,
      cors: allowedOrigins.length > 0 ? { origin: allowedOrigins } : false,
    },
  }
})
