import path from 'path';
import fs from 'fs/promises';
import { getColumnPath } from '../config/paths';
import { readJsonFile } from './fs-utils';

const LOG_PREFIX = '[page-scanner]';

function log(level: 'info' | 'warn' | 'error', message: string, meta?: Record<string, unknown>) {
  const timestamp = new Date().toISOString();
  const metaStr = meta ? ' ' + JSON.stringify(meta) : '';
  console.log(`${timestamp} ${LOG_PREFIX} [${level.toUpperCase()}] ${message}${metaStr}`);
}

/**
 * 获取栏目下的所有页面
 * 递归扫描栏目目录下的所有子目录，查找包含 data.json 的页面目录
 */
export async function getColumnPages(siteSlug: string, columnSlug: string): Promise<any[]> {
  log('info', '开始扫描栏目页面', { siteSlug, columnSlug });

  const columnIndexPath = getColumnPath(siteSlug, columnSlug);
  const fullColumnPath = columnIndexPath.substring(0, columnIndexPath.lastIndexOf('/index.json'));

  const pages: any[] = [];
  let scannedDirs = 0;
  let foundPages = 0;
  let skippedFiles = 0;

  async function scanDir(dirPath: string, relativePath: string) {
    scannedDirs++;

    let entries;
    try {
      entries = await fs.readdir(dirPath, { withFileTypes: true });
      entries.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
    } catch (err: any) {
      log('warn', '目录读取失败，跳过', { dirPath, error: err.message, code: err.code });
      return;
    }

    const subDirs = entries.filter(e => e.isDirectory());

    // 并行读取当前目录下所有子目录的 data.json
    const readPromises = subDirs.map(async (entry) => {
      const subPath = relativePath ? `${relativePath}/${entry.name}` : entry.name;
      const dataPath = path.join(dirPath, entry.name, 'data.json');
      const data = await readJsonFile(dataPath);
      return { subPath, entry, data, dataPath };
    });

    const results = await Promise.all(readPromises);

    // 处理结果并串行递归子目录
    for (const { subPath, entry, data, dataPath } of results) {
      if (data) {
        pages.push({
          slug: subPath,
          path: subPath,
          title: data.page?.title || entry.name,
        });
        foundPages++;
      } else {
        skippedFiles++;
        log('warn', 'data.json 为空或不存在', { subPath, dataPath });
      }
      // 串行递归扫描子目录，避免并发爆炸
      await scanDir(path.join(dirPath, entry.name), subPath);
    }
  }

  await scanDir(fullColumnPath, '');

  log('info', '栏目扫描完成', {
    siteSlug,
    columnSlug,
    scannedDirs,
    foundPages,
    skippedFiles,
    totalPages: pages.length,
  });

  return pages;
}
