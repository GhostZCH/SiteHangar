import path from 'path';
import { getHomePath } from '../config/paths';
import { readJsonFile } from './fs-utils';

/**
 * 获取站点下的所有栏目（模块）
 * 从站点根目录的 index.json 中的 modules 字段读取
 */
export async function getColumns(siteSlug: string): Promise<any[]> {
  const homePath = getHomePath(siteSlug);
  const indexData = await readJsonFile(homePath);

  // 从 index.json 的 modules 字段读取栏目配置
  if (indexData?.modules) {
    return indexData.modules.map((m: any) => ({
      slug: m.id || '',
      name: m.title || m.id || '',
      description: m.description || '',
      image: m.image || '',
      order: m.order ?? 0,
    })).filter((c: any) => c.slug); // 过滤掉没有 slug 的
  }

  return [];
}

/**
 * 获取单个栏目数据
 * 从站点根目录的 index.json 中的 columns 字段读取
 */
export async function getColumn(siteSlug: string, columnSlug: string): Promise<any | null> {
  const homePath = getHomePath(siteSlug);
  const indexData = await readJsonFile(homePath);
  
  if (!indexData?.columns) return null;
  
  const columnData = indexData.columns[columnSlug];
  if (!columnData) return null;
  
  return columnData;
}
