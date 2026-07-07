import { apiClient } from './client';
import type { RenderResponse } from '@/types/content';
import type { Column } from '@/types/api';

/**
 * 公开 API
 */
export const publicApi = {
  /** 渲染任意 path */
  render(path: string[]): Promise<RenderResponse> {
    const encodedPath = path.filter(Boolean).map(encodeURIComponent).join('/');
    return apiClient.get('/render/' + encodedPath).then((r) => r.data);
  },

  /** 列出某站点的栏目 */
  listColumns(siteSlug: string): Promise<{ columns: Column[] }> {
    return apiClient.get('/sites/' + siteSlug + '/columns').then((r) => r.data);
  },

  /** 读取全局配置（如 ICP 备案号） */
  getGlobalConfig(): Promise<{ icp: string }> {
    return apiClient.get('/config').then((r) => r.data);
  },
};
