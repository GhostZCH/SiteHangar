import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { publicApi } from '@/api/public';
import type { RenderResponse } from '@/types/content';

const LOG_PREFIX = '[usePageData]';

function log(level: 'info' | 'warn' | 'error', message: string, meta?: Record<string, unknown>) {
  const timestamp = new Date().toISOString();
  const metaStr = meta ? ' ' + JSON.stringify(meta) : '';
  console.log(`${timestamp} ${LOG_PREFIX} [${level.toUpperCase()}] ${message}${metaStr}`);
}

export function usePageData() {
  const route = useRoute();
  const router = useRouter();
  const data = ref<RenderResponse | null>(null);
  const loading = ref(true);
  const error = ref<string | null>(null);
  // 记录最新一次请求 id，用于丢弃过期的响应（防止路由快速切换时旧请求覆盖新数据）
  let latestRequestId = '';

  async function load(pathParts: string[]) {
    const requestId = Math.random().toString(36).slice(2, 8);
    latestRequestId = requestId;
    const cleanPath = pathParts.filter(Boolean);

    log('info', '开始加载页面数据', { requestId, pathParts: cleanPath, currentRoute: route.path });

    loading.value = true;
    error.value = null;

    try {
      log('info', '发送 API 请求', { requestId, apiPath: '/render/' + cleanPath.join('/') });
      const startTime = performance.now();

      const result = await publicApi.render(cleanPath);

      // 若期间发起了更新的请求，丢弃本次过期响应
      if (requestId !== latestRequestId) {
        log('info', '丢弃过期响应', { requestId, latestRequestId });
        return;
      }

      data.value = result;

      const duration = Math.round(performance.now() - startTime);
      log('info', 'API 请求成功', {
        requestId,
        durationMs: duration,
        responseType: data.value?.type,
        hasSections: !!data.value?.data?.sections?.length,
        sectionCount: data.value?.data?.sections?.length ?? 0,
        hasHero: !!data.value?.data?.hero,
        heroTitle: data.value?.data?.hero?.title,
      });
    } catch (e: any) {
      // 过期请求的错误也丢弃（尤其是旧页面的 404 跳转）
      if (requestId !== latestRequestId) {
        log('info', '丢弃过期请求的错误', { requestId, latestRequestId });
        return;
      }

      const status = e.response?.status;
      const errorCode = e.response?.data?.error;
      const errorMessage = e.message;

      log('error', 'API 请求失败', {
        requestId,
        status,
        errorCode,
        errorMessage,
        pathParts: cleanPath,
        responseData: e.response?.data,
      });

      if (status === 404) {
        log('info', '页面未找到，跳转到 404', { requestId, pathParts: cleanPath });
        router.replace({ name: 'not-found' });
        return;
      }

      error.value = errorCode || errorMessage || '加载失败';
      log('warn', '设置错误状态', { requestId, error: error.value });
    } finally {
      // 只有最新请求才复位 loading，避免旧请求提前结束 loading
      if (requestId === latestRequestId) {
        loading.value = false;
      }
      log('info', '加载完成', { requestId, loading: loading.value, hasError: !!error.value });
    }
  }

  return { data, loading, error, load };
}

export function useDetailPageData() {
  const route = useRoute();
  const router = useRouter();
  const { data, loading, error, load } = usePageData();

  async function loadDetail() {
    let fullPath: string[];

    if (route.name === 'info') {
      fullPath = ['info'];
    } else {
      const moduleSlug = route.params.moduleSlug as string;
      const pathParam = route.params.path;
      const pathRest = Array.isArray(pathParam) ? pathParam : pathParam ? [pathParam] : [];
      fullPath = [moduleSlug, ...pathRest];
    }

    log('info', '详情页路由变化，准备加载', {
      fullPath,
      routeName: route.name,
      routePath: route.path,
    });

    await load(fullPath);
  }

  onMounted(() => {
    log('info', '详情页组件挂载', { routePath: route.path, routeName: route.name });
    loadDetail();
  });

  watch(
    () => [route.name, route.params.moduleSlug, route.params.path],
    (newVal, oldVal) => {
      // 避免初始 undefined 触发，以及确保值真正变化
      if (oldVal === undefined) {
        log('info', 'watch 初始触发，跳过', { newVal, routePath: route.path });
        return;
      }
      // 将数组转为字符串比较，避免引用不同导致重复触发
      const newStr = JSON.stringify(newVal);
      const oldStr = JSON.stringify(oldVal);
      if (newStr === oldStr) {
        log('info', 'watch 值未变化，跳过', { newVal, oldVal, routePath: route.path });
        return;
      }
      log('info', '路由参数变化', { newVal, oldVal, routePath: route.path });
      loadDetail();
    },
    { deep: true }
  );

  return { data, loading, error };
}
