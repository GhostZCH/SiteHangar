import { Router } from 'express';
import { GLOBAL_CONFIG } from '../config/paths';

const router = Router();

/**
 * GET /api/config
 * 返回全局配置（如 ICP 备案号）
 */
router.get('/config', (_req, res) => {
  res.json({
    icp: GLOBAL_CONFIG.icp,
  });
});

export default router;
