<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { publicApi } from '@/api/public';
import type { RenderResponse } from '@/types/content';
import { usePageSections } from '@/composables/usePageSections';
import SectionRenderer from '@/components/content/SectionRenderer.vue';
import PageLoading from '@/components/content/PageLoading.vue';
import PageError from '@/components/content/PageError.vue';

const data = ref<RenderResponse | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

async function load() {
  loading.value = true;
  error.value = null;
  try {
    data.value = await publicApi.render(['info']);
  } catch (e: any) {
    error.value = e.response?.data?.error || e.message || '加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(load);

const sections = computed(() => data.value?.data.sections || []);
usePageSections(sections);
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <PageLoading v-if="loading" />
    <PageError v-else-if="error" :message="error" />
    <div v-else-if="data">
      <header class="mb-8 border-b border-slate-200 pb-6">
        <h1 class="text-3xl font-bold text-slate-900">
          {{ data.data.hero?.title || '关于' }}
        </h1>
      </header>
      <div class="space-y-12">
        <SectionRenderer
          v-for="(s, idx) in data.data.sections || []"
          :key="s.id"
          :section="s"
          :index="idx"
        />
      </div>
    </div>
  </div>
</template>
