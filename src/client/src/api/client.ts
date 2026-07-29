import axios from 'axios';

// Vite 代理会把 /api 转到 http://localhost:3000
// 生产环境也是 /api（Nginx 反代）
export const apiClient = axios.create({
  baseURL: '/api',
  withCredentials: true,
  timeout: 15000,
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    // 401: 未登录
    if (err.response?.status === 401) {
      // 路由守卫会处理跳转
    }
    return Promise.reject(err);
  },
);
