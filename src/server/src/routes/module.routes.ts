import { Router } from 'express';
import { getColumns, getColumn } from '../services/column-scanner';
import { getColumnPages } from '../services/page-scanner';

const router = Router();

/**
 * GET /api/sites/:siteSlug/columns
 * 列出某站点的所有栏目
 */
router.get('/sites/:siteSlug/columns', async (req, res, next) => {
  try {
    const columns = await getColumns(req.params.siteSlug);
    res.json({ columns: columns.map(m => ({
      slug: m.slug,
      name: m.name,
      description: m.description,
      icon: m.icon,
    })) });
  } catch (err) {
    next(err);
  }
});

/**
 * GET /api/sites/:siteSlug/columns/:columnSlug/pages
 * 列出某栏目下的所有页面
 */
router.get('/sites/:siteSlug/columns/:columnSlug/pages', async (req, res, next) => {
  try {
    const pages = await getColumnPages(req.params.siteSlug, req.params.columnSlug);
    res.json({ pages: pages.map(p => ({
      slug: p.slug,
      path: p.path,
      title: p.title,
    })) });
  } catch (err) {
    next(err);
  }
});

export default router;
