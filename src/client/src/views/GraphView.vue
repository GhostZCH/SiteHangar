<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { publicApi } from '@/api/public';
import type { ModuleCard } from '@/types/content';
import ColumnNetworkSphere from '@/components/content/ColumnNetworkSphere.vue';

const modules = ref<ModuleCard[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const hasModules = computed(() => modules.value.length > 0);

onMounted(async () => {
  try {
    const res = await publicApi.render([]);
    modules.value = res.data.modules || [];
  } catch (e: any) {
    error.value = e.response?.data?.error || e.message || '加载失败';
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="graph-view">
    <div v-if="loading" class="graph-state">加载中…</div>
    <div v-else-if="error" class="graph-state">{{ error }}</div>
    <div v-else-if="!hasModules" class="graph-state">暂无数据</div>
    <ColumnNetworkSphere v-else :modules="modules" fullscreen />
  </div>
</template>

<style scoped>
.graph-view {
  position: fixed;
  inset: 0;
  z-index: 10;
  background: #000;
  overflow: hidden;
}
.graph-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}
</style>
