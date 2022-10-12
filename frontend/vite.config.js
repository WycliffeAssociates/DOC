import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import EnvironmentPlugin from 'vite-plugin-environment'

// https://vitejs.dev/config/
export default defineConfig({
  // Specify default for BACKEND_API_URL which can be overridden
  // in the environment.
  // e.g.,
  // 'https://irgdev.walink.org'
  plugins: [svelte(), EnvironmentPlugin(['BACKEND_API_URL'], { loadEnvFiles: false })],
  server: {
    host: '0.0.0.0'
  },
  }
})
