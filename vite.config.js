import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3002,
    open: true,
    strictPort: true,  // Don't try other ports, fail loudly if 3002 is taken
    proxy: {
      // Proxy all /api requests to the Flask backend on port 5001
      // This avoids CORS issues since the browser sees same-origin requests
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        secure: false
      }
    }
  }
});
