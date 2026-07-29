import { listDirs } from '../services/fs-utils';
import { HttpError } from '../middlewares/error-handler';

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
 * 1. 优先使用完整 host（去掉端口）精确匹配数据目录名，如 travel.test.local
 * 2. 兼容旧逻辑：提取第一段子域名匹配
 * 3. 未匹配任何站点时返回 undefined，由调用方决定是否返回 404
 */
export async function resolveSiteSlugByHost(host: string, dataRoot: string): Promise<string | undefined> {
  const normalizedHost = host.toLowerCase().split(':')[0];
  if (!normalizedHost) {
    return undefined;
  }

  const sites = await scanSites(dataRoot);

  // 优先完整域名匹配
  if (sites.includes(normalizedHost)) {
    return normalizedHost;
  }

  // 兼容旧逻辑：提取子域名（host 的第一段）
  const subdomain = normalizedHost.split('.')[0];
  if (subdomain && sites.includes(subdomain)) {
    return subdomain;
  }

  return undefined;
}

/**
 * 根据 Host 头解析站点标识，未匹配时抛出 404 HttpError
 */
export async function resolveSiteSlugByHostOrThrow(host: string, dataRoot: string): Promise<string> {
  const slug = await resolveSiteSlugByHost(host, dataRoot);
  if (!slug) {
    throw new HttpError(404, 'SITE_NOT_FOUND');
  }
  return slug;
}

/**
 * 获取所有站点配置（用于后台展示）
 */
export async function getAllSites(dataRoot: string): Promise<{ slug: string; name: string }[]> {
  const sites = await scanSites(dataRoot);
  return sites.map(slug => ({ slug, name: slug }));
}
