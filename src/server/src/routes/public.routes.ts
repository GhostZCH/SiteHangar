import { Router } from 'express';
import { resolveSite } from '../middlewares/resolve-site';
import renderRoutes from './render.routes';
import moduleRoutes from './module.routes';
import configRoutes from './config.routes';
import imageRoutes from './image.routes';

const router = Router();

// 所有 API 请求先通过 Host 解析站点，未匹配站点时返回 404
router.use(resolveSite);

router.use(configRoutes);
router.use(imageRoutes);
router.use(renderRoutes);
router.use(moduleRoutes);

export default router;
