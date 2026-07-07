import { Router } from 'express';
import path from 'path';
import fs from 'fs/promises';
import { DATA_ROOT } from '../config/paths';

const router = Router();

/**
 * GET /image/:site/:filename
 * 从站点数据目录的 image/ 子目录提供图片
 * 例如 /image/www/wiki.jpg → DATA_ROOT/www/image/wiki.jpg
 */
router.get('/image/:site/:filename', async (req, res, next) => {
  try {
    const { site, filename } = req.params;

    // 安全校验：拒绝路径遍历
    if (site.includes('..') || filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
      return res.status(400).json({ error: 'INVALID_PATH' });
    }

    const imagePath = path.join(DATA_ROOT, site, 'image', filename);

    // 校验最终路径在 DATA_ROOT 内
    const resolved = path.resolve(imagePath);
    const root = path.resolve(DATA_ROOT);
    if (!resolved.startsWith(root + path.sep)) {
      return res.status(403).json({ error: 'FORBIDDEN' });
    }

    const data = await fs.readFile(resolved);
    const ext = path.extname(filename).toLowerCase();
    const mimeMap: Record<string, string> = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.gif': 'image/gif',
      '.webp': 'image/webp',
      '.svg': 'image/svg+xml',
    };
    res.setHeader('Content-Type', mimeMap[ext] || 'application/octet-stream');
    res.setHeader('Cache-Control', 'public, max-age=86400');
    res.send(data);
  } catch (err: any) {
    if (err.code === 'ENOENT') return res.status(404).json({ error: 'IMAGE_NOT_FOUND' });
    next(err);
  }
});

/**
 * GET /page-asset/:site/:path(*)
 * 从页面目录下提供静态资源（图片、数据文件等）
 * 例如 /page-asset/www/tools/工具/演示/single-md-example/image/landscape.jpg
 * → DATA_ROOT/www/tools/工具/演示/single-md-example/image/landscape.jpg
 */
router.get('/page-asset/:site/:path(*)', async (req, res, next) => {
  try {
    const { site, path: assetPath } = req.params;

    // 调试日志
    console.log('[page-asset] site:', site);
    console.log('[page-asset] assetPath:', assetPath);
    console.log('[page-asset] DATA_ROOT:', DATA_ROOT);

    // 安全校验：拒绝路径遍历
    if (site.includes('..') || assetPath.includes('..')) {
      return res.status(400).json({ error: 'INVALID_PATH' });
    }

    const filePath = path.join(DATA_ROOT, site, assetPath);
    console.log('[page-asset] filePath:', filePath);

    // 校验最终路径在 DATA_ROOT 内
    const resolved = path.resolve(filePath);
    const root = path.resolve(DATA_ROOT);
    console.log('[page-asset] resolved:', resolved);
    console.log('[page-asset] root:', root);
    console.log('[page-asset] startsWith:', resolved.startsWith(root + path.sep));

    if (!resolved.startsWith(root + path.sep)) {
      return res.status(403).json({ error: 'FORBIDDEN' });
    }

    const data = await fs.readFile(resolved);
    const ext = path.extname(assetPath).toLowerCase();
    const mimeMap: Record<string, string> = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.gif': 'image/gif',
      '.webp': 'image/webp',
      '.svg': 'image/svg+xml',
      '.json': 'application/json',
      '.md': 'text/markdown',
    };
    res.setHeader('Content-Type', mimeMap[ext] || 'application/octet-stream');
    res.setHeader('Cache-Control', 'public, max-age=86400');
    res.send(data);
  } catch (err: any) {
    if (err.code === 'ENOENT') return res.status(404).json({ error: 'ASSET_NOT_FOUND' });
    next(err);
  }
});

export default router;
