<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, computed } from 'vue';
import { useTheme } from '@/composables/useTheme';
import type { TreeBlockItem, TreeNode } from '@/types/content';

const props = defineProps<{ data?: TreeBlockItem; code?: string }>();
const chartRef = ref<HTMLDivElement | null>(null);
const { currentTheme } = useTheme();
let chartInstance: any = null;
let echartsModule: any = null;

function parseTreeText(text: string): TreeNode | null {
  const rawLines = text.trim().split('\n');
  const stack: { node: TreeNode; level: number }[] = [];
  let root: TreeNode | null = null;

  for (const raw of rawLines) {
    const line = raw.replace(/\r$/, '');
    if (!line.trim()) continue;

    const pattern = /^(│   |    )*(├── |└── )?(.*)$/;
    const match = line.match(pattern);
    if (!match) continue;

    const units = match[1] || '';
    const nodePrefix = match[2] || '';
    const content = match[3].trim();
    if (!content) continue;

    const level = (units.length / 4) + (nodePrefix ? 1 : 0);
    const node: TreeNode = { name: content };

    if (!root) {
      root = node;
      stack.push({ node, level: Math.max(0, level) });
      continue;
    }

    while (stack.length > 0 && stack[stack.length - 1].level >= level) {
      stack.pop();
    }

    if (stack.length === 0) {
      root = node;
      stack.push({ node, level: Math.max(0, level) });
    } else {
      const parent = stack[stack.length - 1].node;
      if (!parent.children) parent.children = [];
      parent.children.push(node);
      stack.push({ node, level: Math.max(0, level) });
    }
  }

  return root;
}

const treeItem = computed<TreeBlockItem | null>(() => {
  if (props.data) return props.data;
  if (!props.code) return null;
  const code = props.code.trim();
  try {
    const parsed = JSON.parse(code);
    if (parsed.data) return parsed as TreeBlockItem;
    if (parsed.name) return { data: parsed as TreeNode };
    return null;
  } catch {
    const root = parseTreeText(code);
    return root ? { data: root } : null;
  }
});

const title = computed(() => treeItem.value?.title || '');
const rootData = computed(() => treeItem.value?.data || null);

async function init() {
  if (!chartRef.value || !rootData.value) return;

  if (!echartsModule) {
    echartsModule = await import('echarts');
  }
  const echarts = echartsModule.default || echartsModule;

  if (chartInstance) {
    chartInstance.dispose();
  }

  chartInstance = echarts.init(chartRef.value);

  const style = getComputedStyle(chartRef.value);
  const onSurface = style.getPropertyValue('--on-surface').trim() || '#212121';
  const accent = style.getPropertyValue('--accent').trim() || '#607d8b';

  const option = {
    title: title.value ? {
      text: title.value,
      left: 'center',
      top: 10,
      textStyle: { fontSize: 16, color: onSurface },
    } : undefined,
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
    },
    series: [
      {
        type: 'tree',
        data: [rootData.value],
        top: title.value ? '12%' : '5%',
        left: '5%',
        bottom: '5%',
        right: '5%',
        symbolSize: 10,
        orient: 'TB',
        roam: true,
        labelLayout: { hideOverlap: true },
        label: {
          position: 'top',
          verticalAlign: 'middle',
          align: 'center',
          fontSize: 12,
          color: onSurface,
          width: 80,
          overflow: 'break',
          lineHeight: 14,
        },
        leaves: {
          label: {
            position: 'bottom',
            verticalAlign: 'middle',
            align: 'center',
            fontSize: 12,
            color: onSurface,
            width: 80,
            overflow: 'break',
            lineHeight: 14,
          },
        },
        expandAndCollapse: true,
        animationDuration: 550,
        animationDurationUpdate: 750,
        lineStyle: {
          color: accent,
          curveness: 0.5,
        },
        itemStyle: {
          color: accent,
          borderColor: accent,
        },
        emphasis: {
          focus: 'descendant',
        },
      },
    ],
  };

  chartInstance.setOption(option);
}

function resize() {
  chartInstance?.resize();
}

onMounted(() => {
  init();
  window.addEventListener('resize', resize);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize);
  chartInstance?.dispose();
});

watch(() => [props.data, props.code], init, { deep: true });
watch(currentTheme, init);
</script>

<template>
  <div class="tree-block card p-4" v-if="rootData">
    <div ref="chartRef" style="width: 100%; height: 500px"></div>
  </div>
  <div v-else class="tree-block card p-4 text-sm text-surface-variant">
    树状数据为空或格式错误
  </div>
</template>

<style scoped>
.tree-block {
  width: 100%;
}

.text-surface-variant {
  color: var(--on-surface-variant);
}
</style>
