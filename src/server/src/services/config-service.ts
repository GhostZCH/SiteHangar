import path from 'path';
import { getSitePath } from '../config/paths';
import { readJsonFile, writeJsonFile } from './fs-utils';

/**
 * 读取站点配置
 */
export async function getSiteConfig(siteSlug: string): Promise<any | null> {
  const configPath = path.join(getSitePath(siteSlug), 'config.json');
  return readJsonFile(configPath);
}

/**
 * 保存站点配置
 */
export async function saveSiteConfig(siteSlug: string, config: any): Promise<void> {
  const configPath = path.join(getSitePath(siteSlug), 'config.json');
  await writeJsonFile(configPath, config);
}
