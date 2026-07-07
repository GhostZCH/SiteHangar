import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import cookieParser from 'cookie-parser';
import rateLimit from 'express-rate-limit';
import path from 'path';

import publicRoutes from './routes/public.routes';
import { errorHandler, notFound } from './middlewares/error-handler';

const app = express();

// CORS：开发环境允许所有来源，生产环境从配置读取
const isDev = process.env.NODE_ENV !== 'production';

app.use(cors({
  origin: (origin, callback) => {
    if (isDev || !origin) {
      callback(null, true);
    } else {
      // 生产环境可以在这里添加域名白名单校验
      callback(null, true);
    }
  },
  credentials: true,
}));

// 速率限制
app.use('/api', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 200,
  standardHeaders: true,
  legacyHeaders: false,
}));

app.use(morgan('dev'));
app.use(express.json({ limit: '10mb' }));
app.use(cookieParser());

// API 路由
app.use('/api', publicRoutes);

// API 404 处理
app.use('/api', notFound);

// 静态文件 - 前端构建产物
// 兼容 tsx 和 node 运行：tsx 运行时 __dirname 为 '.'，使用 process.cwd() 定位
const PUBLIC_DIR = path.resolve(process.cwd(), 'public');
app.use(express.static(PUBLIC_DIR));

// SPA fallback
app.get('*', (req, res) => {
  res.sendFile(path.join(PUBLIC_DIR, 'index.html'));
});

// 全局错误处理
app.use(errorHandler);

export default app;
