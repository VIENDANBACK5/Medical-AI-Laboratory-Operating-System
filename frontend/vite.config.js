import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Zero-config dev server for the MedAI-OS viewer. The app talks to the FastAPI
// backend at the URL entered in the sidebar (default http://localhost:8000/api/v1),
// and CORS is open on the backend, so no proxy is required.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, open: true },
});
