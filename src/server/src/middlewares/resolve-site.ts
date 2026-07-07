import { Request, Response, NextFunction } from 'express';
import { resolveSiteSlugByHost } from '../config/sites';
import { DATA_ROOT } from '../config/paths';

/**
 * 通过 Host 头解析当前请求属于哪个站点
 * 通过扫描 DATA_ROOT 下的一级目录名来匹配子域名
 */
export async function resolveSite(req: Request, _res: Response, next: NextFunction) {
  try {
    const host = (req.headers.host || '').toLowerCase();
    const siteSlug = await resolveSiteSlugByHost(host, DATA_ROOT);

    (req as any).siteSlug = siteSlug;
    (req as any).dataRoot = DATA_ROOT;
    next();
  } catch (err) {
    next(err);
  }
}
