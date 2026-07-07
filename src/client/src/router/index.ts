import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // ============ 静态路由（必须在前，否则被 /:moduleSlug 吞掉）============
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/info', name: 'info', component: () => import('@/views/DetailView.vue') },

    // ============ 动态路由（按站点slug匹配模块和页面）============
    { path: '/:moduleSlug', name: 'module', component: () => import('@/views/CategoryView.vue') },
    { path: '/:moduleSlug/:path(.*)*', name: 'detail', component: () => import('@/views/DetailView.vue') },

    // ============ 404 ============
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
  scrollBehavior(to, from, saved) {
    if (saved) return saved;
    if (to.hash) return { el: to.hash, behavior: 'smooth' };
    return { top: 0 };
  },
});

export default router;
