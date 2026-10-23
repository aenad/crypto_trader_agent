import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const apiTarget = process.env.QUANTPILOT_DASHBOARD_API ?? 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    include: ['src/dashboard/**/*.test.tsx'],
    setupFiles: ['src/dashboard/setup-tests.ts'],
    maxWorkers: 2,
  },
  server: {
    proxy: {
      '/api': apiTarget,
    },
  },
  preview: { proxy: { '/api': apiTarget } },
});
