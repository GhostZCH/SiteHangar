import fs from 'fs/promises';
import { DATA_ROOT, getSitePath } from '../config/paths';
import { listDirs } from './fs-utils';

/**
 * 获取所有站点列表
 */
export async function getSites(): Promise<string[]> {
  return listDirs(DATA_ROOT);
}

/**
 * 检查站点是否存在
 */
export async function siteExists(siteSlug: string): Promise<boolean> {
  try {
    const stat = await fs.stat(getSitePath(siteSlug));
    return stat.isDirectory();
  } catch {
    return false;
  }
}
