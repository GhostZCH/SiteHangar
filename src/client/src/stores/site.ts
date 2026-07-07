import { defineStore } from 'pinia';
import { ref } from 'vue';

interface NavColumn {
  slug: string;
  name: string;
  description: string;
  image: string;
}

export const useSiteStore = defineStore('site', () => {
  const siteSlug = ref<string>('');
  const columns = ref<NavColumn[]>([]);
  const loading = ref(false);
  const icp = ref<string>('');
  const siteTitle = ref<string>('');

  function setSiteSlug(slug: string) {
    siteSlug.value = slug;
  }

  async function loadColumns() {
    if (!siteSlug.value) return;
    loading.value = true;
    try {
      const { publicApi } = await import('@/api/public');
      const homeRes = await publicApi.render([]).catch(() => null);

      // 读取站点标题
      siteTitle.value = homeRes?.data?.hero?.title || homeRes?.data?.page?.title || '';
      if (siteTitle.value) {
        document.title = siteTitle.value;
      }

      // 从首页数据直接获取 modules 作为导航栏栏目（与卡片保持一致）
      const modules = homeRes?.data?.modules || [];
      columns.value = modules.map((m: any) => ({
        slug: m.code || m.id || '',
        name: m.title || m.id || '',
        description: m.description || '',
        image: m.image || '',
      })).filter((c: NavColumn) => c.slug);
    } finally {
      loading.value = false;
    }
  }

  async function loadGlobalConfig() {
    try {
      const { publicApi } = await import('@/api/public');
      const { icp: value } = await publicApi.getGlobalConfig();
      icp.value = value;
    } catch {
      // 静默失败，不阻塞页面渲染
    }
  }

  return { siteSlug, columns, loading, icp, siteTitle, setSiteSlug, loadColumns, loadGlobalConfig };
});
