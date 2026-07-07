import { listDirs } from '../services/fs-utils';

/**
 * 扫描数据根目录，获取所有站点标识列表
 * DATA_ROOT 下的一级目录名即为站点标识（如 www、ziliudi）
 * 每次请求直接扫描文件系统，不缓存
 */
export async function scanSites(dataRoot: string): Promise<string[]> {
  return listDirs(dataRoot);
}

/**
 * 根据 Host 头解析站点标识（siteSlug）
 * 匹配规则：
 * 1. 提取 host 的子域名部分（如 www.knowledgecube.com -> www）
 * 2. 如果子域名存在于站点列表中，直接匹配
 * 3. 默认返回 'www'
 */
export async function resolveSiteSlugByHost(host: string, dataRoot: string): Promise<string> {
  const normalizedHost = host.toLowerCase().split(':')[0];

  // 提取子域名（host 的第一段）
  const subdomain = normalizedHost.split('.')[0];

  const sites = await scanSites(dataRoot);

  // 精确匹配子域名
  if (subdomain && sites.includes(subdomain)) {
    return subdomain;
  }

  // 默认返回 www（如果存在），否则返回第一个站点
  if (sites.includes('www')) {
    return 'www';
  }

  return sites[0] || 'www';
}

/**
 * 获取所有站点配置（用于后台展示）
 */
export async function getAllSites(dataRoot: string): Promise<{ slug: string; name: string }[]> {
  const sites = await scanSites(dataRoot);
  return sites.map(slug => ({ slug, name: slug }));
}
