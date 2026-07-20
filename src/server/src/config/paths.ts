import path from 'path';
import fs from 'fs';
import yaml from 'js-yaml';
import { resolveSiteSlugByHost } from './sites';

/**
 * 加载配置文件
 * 优先使用环境变量 CONFIG_FILE，否则使用项目根目录下的 config.yaml
 */
function loadProjectConfig(): Record<string, any> {
  const configFile = process.env.CONFIG_FILE || path.resolve(__dirname, '../../../config.yaml');
  const configPath = path.resolve(configFile);
  if (fs.existsSync(configPath)) {
    const content = fs.readFileSync(configPath, 'utf-8');
    const parsed = yaml.load(content) as Record<string, any>;
    return parsed || {};
  }
  return {};
}

const projectConfig = loadProjectConfig();

/**
 * 全局配置（来自 config.yaml）
 */
export const GLOBAL_CONFIG = {
  icp: projectConfig.icp || '',
};

/**
 * 数据路径配置
 * 从 config.yaml 中的 dataRoot 读取，默认 /app/my_sites_data/data
 * 相对路径以 /app 为基准（Docker 挂载根目录）
 */
function resolveDataRoot(dataRoot: string | undefined): string {
  if (!dataRoot) return '/app/my_sites_data/data';
  if (path.isAbsolute(dataRoot)) return dataRoot;
  return path.resolve('/app', dataRoot);
}

/** 源数据目录（仅用于兼容旧配置，默认读取 dataRoot） */
export const SRC_DATA_ROOT = resolveDataRoot(projectConfig.dataRoot);

/** 编译输出目录，供 build_service 使用 */
function resolveBuildOutputDir(): string {
  const dir = projectConfig.buildOutputDir;
  if (!dir) return SRC_DATA_ROOT;
  if (path.isAbsolute(dir)) return dir;
  return path.resolve('/app', dir);
}

/** 网站服务数据根目录：从 config.yaml 的 buildOutputDir 解析 */
export const DATA_ROOT = resolveBuildOutputDir();

/**
 * 验证并清理路径片段，防止路径遍历攻击
 * 拒绝包含 .. 或绝对路径的输入
 */
function sanitizePathSegment(segment: string): string {
  // 拒绝包含路径遍历的片段
  if (segment.includes('..') || segment.includes('/') || segment.includes('\\')) {
    throw new Error('INVALID_PATH');
  }
  return segment;
}

/**
 * 验证最终路径是否在 DATA_ROOT 范围内
 */
function assertWithinDataRoot(targetPath: string): void {
  const resolved = path.resolve(targetPath);
  const root = path.resolve(DATA_ROOT);
  if (!resolved.startsWith(root + path.sep) && resolved !== root) {
    throw new Error('PATH_TRAVERSAL');
  }
}

/**
 * 根据 Host 获取站点标识（siteSlug）
 * 通过扫描 DATA_ROOT 下的一级目录名来匹配子域名
 */
export async function getSiteSlugByHost(host: string): Promise<string> {
  return resolveSiteSlugByHost(host, DATA_ROOT);
}

/**
 * 获取站点数据目录
 * @param siteSlug 站点标识，如 'www' 或 'ziliudi'
 */
export function getSitePath(siteSlug: string): string {
  const safeSlug = sanitizePathSegment(siteSlug);
  const target = path.join(DATA_ROOT, safeSlug);
  assertWithinDataRoot(target);
  return target;
}

/**
 * 获取页面数据文件路径（5层目录结构）
 * @param siteSlug 站点标识
 * @param pagePath 页面路径，如 'wiki/social-sciences/economics/macroeconomics'
 */
export function getPagePath(siteSlug: string, pagePath: string): string {
  const safeSlug = sanitizePathSegment(siteSlug);
  // pagePath 允许 / 作为路径分隔符，但不允许 ..
  if (pagePath.includes('..')) throw new Error('INVALID_PATH');
  // 白名单校验：允许小写字母、数字、横线、斜杠、中文和空格
  if (!/^[a-z0-9\-\/\u4e00-\u9fa5\s]+$/.test(pagePath)) throw new Error('INVALID_PATH');
  const target = path.join(DATA_ROOT, safeSlug, pagePath, 'data.json');
  assertWithinDataRoot(target);
  return target;
}

/**
 * 获取栏目首页路径（2层目录结构）
 * @param siteSlug 站点标识
 * @param columnSlug 栏目标识，如 'wiki'
 */
export function getColumnPath(siteSlug: string, columnSlug: string): string {
  const safeSlug = sanitizePathSegment(siteSlug);
  const safeColumn = sanitizePathSegment(columnSlug);
  const target = path.join(DATA_ROOT, safeSlug, safeColumn, 'index.json');
  assertWithinDataRoot(target);
  return target;
}

/**
 * 获取站点首页路径
 * @param siteSlug 站点标识
 */
export function getHomePath(siteSlug: string): string {
  const safeSlug = sanitizePathSegment(siteSlug);
  const target = path.join(DATA_ROOT, safeSlug, 'index.json');
  assertWithinDataRoot(target);
  return target;
}

/**
 * 获取 info 文件夹路径
 * @param siteSlug 站点标识
 */
export function getInfoDirPath(siteSlug: string): string {
  const safeSlug = sanitizePathSegment(siteSlug);
  const target = path.join(DATA_ROOT, safeSlug, 'info');
  assertWithinDataRoot(target);
  return target;
}

/**
 * 获取编译输出目录路径
 */
export function getBuildOutputDir(): string {
  const dir = projectConfig.buildOutputDir;
  if (!dir) return SRC_DATA_ROOT; // 默认原地写入
  if (path.isAbsolute(dir)) return dir;
  // 相对路径以 /app 为基准（Docker 挂载根目录）
  return path.resolve('/app', dir);
}
