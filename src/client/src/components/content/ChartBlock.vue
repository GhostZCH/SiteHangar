<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import type { ChartItem } from '@/types/content';
import { buildOption } from './charts/ChartOptionBuilder';

const props = defineProps<{ items: ChartItem[] }>();
const refs = ref<Record<string, HTMLDivElement | null>>({});
const charts = ref<Record<string, any>>({});
let echartsModule: any = null;

async function init() {
  if (!echartsModule) {
    echartsModule = await import('echarts');
  }
  const echarts = echartsModule.default || echartsModule;

  for (const c of props.items) {
    const el = refs.value[c.id];
    if (!el) continue;
    if (charts.value[c.id]) charts.value[c.id].dispose();
    const chart = echarts.init(el);
    chart.setOption(buildOption(c));
    charts.value[c.id] = chart;
  }
}

function resize() {
  Object.values(charts.value).forEach((c) => c.resize());
}

onMounted(() => {
  init();
  window.addEventListener('resize', resize);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize);
  Object.values(charts.value).forEach((c) => c.dispose());
});

watch(() => props.items, init, { deep: true });
</script>

<template>
  <div class="space-y-6">
    <div v-for="c in items" :key="c.id" class="card p-4">
      <div :ref="(el) => (refs[c.id] = el as HTMLDivElement)" style="width: 100%; height: 360px"></div>
    </div>
  </div>
</template>
