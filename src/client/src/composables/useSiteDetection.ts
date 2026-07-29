import { useSiteStore } from '@/stores/site';

/**
 * 初始化站点标识
 * 后端 API 会根据 Host 头自动解析 siteSlug，前端无需推断
 */
export function initSiteSlug(): void {
  const site = useSiteStore();
  // 设置一个默认值，实际站点数据由后端 API 根据 Host 头返回
  site.setSiteSlug('default');
}
