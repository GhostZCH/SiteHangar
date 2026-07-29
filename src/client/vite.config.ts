import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import fs from 'fs';
import yaml from 'js-yaml';

// 读取环境变量 CONFIG_FILE 指定的配置文件
function loadConfig() {
  const configFile = process.env.CONFIG_FILE;
  if (!configFile) {
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

// 获取站点数据根目录：读取 config.yaml 的 buildOutputDir
function getDataRoot(): string | undefined {
  const buildOutputDir = config?.buildOutputDir;
  if (buildOutputDir) {
    if (path.isAbsolute(buildOutputDir)) {
      return buildOutputDir;
    }
    return path.resolve('/app', buildOutputDir);
  }
  return undefined;
}

// 扫描数据根目录下的一级目录，作为允许的 Host（站点域名）
function scanSiteHosts(): string[] {
  const dataRoot = getDataRoot();
  if (!dataRoot || !fs.existsSync(dataRoot)) {
    return [];
  }
  try {
    return fs.readdirSync(dataRoot)
      .filter(entry => {
        const fullPath = path.join(dataRoot, entry);
        return fs.statSync(fullPath).isDirectory();
      });
  } catch (err) {
    console.warn('[vite] Failed to scan site hosts:', err);
    return [];
  }
}

const siteHosts = scanSiteHosts();
if (siteHosts.length > 0) {
  console.log('[vite] allowedHosts from data root:', siteHosts);
}

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
    allowedHosts: siteHosts.length > 0 ? siteHosts : true,
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
