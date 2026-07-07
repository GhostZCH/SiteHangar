import path from 'path';
import { getPagePath, getHomePath, getSitePath, getInfoDirPath } from '../config/paths';
import { readJsonFile, writeJsonFile, removePath } from './fs-utils';
import { cacheKey, clearCached } from './cache';

/**
 * 获取页面数据（直接读取文件，不缓存）
 */
export async function getPage(siteSlug: string, pagePath: string): Promise<any | null> {
  return readJsonFile(getPagePath(siteSlug, pagePath));
}

/**
 * 保存页面数据
 */
export async function savePage(siteSlug: string, pagePath: string, data: any): Promise<void> {
  await writeJsonFile(getPagePath(siteSlug, pagePath), data);
  clearCached(cacheKey(siteSlug, 'page', pagePath));
}

/**
 * 删除页面
 */
export async function deletePage(siteSlug: string, pagePath: string): Promise<void> {
  const pageFilePath = getPagePath(siteSlug, pagePath);
  const fullPath = pageFilePath.substring(0, pageFilePath.lastIndexOf('/data.json'));
  await removePath(fullPath);
  clearCached(cacheKey(siteSlug, 'page', pagePath));
}

/**
 * 获取首页数据（直接读取文件，不缓存）
 * 从站点根目录的 index.json 读取，包含 modules 和 columns 数据
 */
export async function getHomePage(siteSlug: string): Promise<any | null> {
  return readJsonFile(getHomePath(siteSlug));
}

/**
 * 获取关于页数据（直接读取文件，不缓存）
 * 读取 info 文件夹编译出的 data.json
 */
export async function getInfoPage(siteSlug: string): Promise<any | null> {
  const infoDirPath = getInfoDirPath(siteSlug);
  const infoDirJsonPath = path.join(infoDirPath, 'data.json');
  return readJsonFile(infoDirJsonPath);
}
