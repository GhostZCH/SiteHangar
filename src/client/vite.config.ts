import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import fs from 'fs';
import yaml from 'js-yaml';

// 读取环境变量 CONFIG_FILE 指定的配置文件
function loadConfig() {
  const configFile = process.env.CONFIG_FILE;
  if (!configFile) {
    console.warn('[vite] CONFIG_FILE environment variable not set, using empty allowedHosts');
    return {};
  }
  
  const configPath = path.resolve(configFile);
  if (!fs.existsSync(configPath)) {
    console.warn(`[vite] Config file not found: ${configPath}`);
    return {};
  }
  
  const content = fs.readFileSync(configPath, 'utf-8');
  return yaml.load(content) as Record<string, any>;
}

const config = loadConfig();

// Vite 仅用于本地开发调试（HMR）。
// Docker 部署时由 Node 进程直接托管 client/dist/ 静态文件。
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    allowedHosts: config.allowedHosts || [],
    hmr: false,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
});
