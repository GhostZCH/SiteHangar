import { Router } from 'express';
import { resolveSite } from '../middlewares/resolve-site';
import { getPage, getHomePage, getInfoPage } from '../services/page-service';
import { getColumn } from '../services/column-scanner';
import type { Request, Response, NextFunction } from 'express';

const router = Router();

/**
 * GET /api/render/*path
 * 通配渲染：把 path 解析为 siteSlug/column/category/subcategory/page
 */
router.get('/render/:path(*)', resolveSite, async (req: Request, res: Response, next: NextFunction) => {
  try {
    const segments = String(req.params.path || '').split('/').filter(Boolean);
    const siteSlug = (req as any).siteSlug as string;

    // 没有路径 → 首页
    if (segments.length === 0) {
      const data = await getHomePage(siteSlug);
      if (!data) {
        return res.status(404).json({ error: 'HOME_NOT_FOUND' });
      }
      return res.json({
        site: { slug: siteSlug },
        type: 'home',
        data,
      });
    }

    const [first, ...rest] = segments;
    const remainingPath = rest.join('/');

    // info → 关于页（与普通详情页共用渲染逻辑）
    if (first === 'info') {
      const infoData = await getInfoPage(siteSlug);
      if (infoData) {
        return res.json({
          site: { slug: siteSlug },
          column: { slug: 'info' },
          page: {
            slug: 'index',
            title: infoData.page?.title || '关于',
          },
          type: 'detail',
          data: infoData,
        });
      }
      return res.status(404).json({ error: 'INFO_NOT_FOUND' });
    }

    // 尝试作为页面路径读取
    const pagePath = segments.join('/');
    const pageData = await getPage(siteSlug, pagePath);

    if (pageData) {
      return res.json({
        site: { slug: siteSlug },
        column: { slug: first },
        page: {
          slug: remainingPath || 'index',
          title: pageData.page?.title,
        },
        type: 'detail',
        data: pageData,
      });
    }

    // 尝试作为栏目首页
    if (rest.length === 0) {
      const columnData = await getColumn(siteSlug, first);
      if (columnData) {
        return res.json({
          site: { slug: siteSlug },
          column: { slug: first, name: columnData.page?.title },
          type: 'category',
          data: columnData,
        });
      }
    }

    res.status(404).json({ error: 'NOT_FOUND', path: pagePath });
  } catch (err) {
    next(err);
  }
});

export default router;
