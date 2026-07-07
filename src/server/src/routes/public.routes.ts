import { Router } from 'express';
import renderRoutes from './render.routes';
import moduleRoutes from './module.routes';
import configRoutes from './config.routes';
import imageRoutes from './image.routes';

const router = Router();

router.use(configRoutes);
router.use(imageRoutes);
router.use(renderRoutes);
router.use(moduleRoutes);

export default router;
